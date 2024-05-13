from __future__ import annotations
import datetime
import json
import hashlib
from typing import List
import numpy as np

from .pointing import Pointing

from .core import baseapi
from .core import apimodels
from .core import util 
from .core import tmcache

#approximated instrument footprints are faster for computation
APPROXIMATION_DICT = {
    47 : 76, #ZTF
    38 : 98, #DECAM
}

class Footprint(apimodels._Table):
    id = None
    footprint = None
    polygon = None

    def __init__(self, kwdict=None, **kwargs):

        if kwdict is not None:
            selfdict = kwdict
        else:
            selfdict = kwargs

        super().__init__(payload=selfdict)

        self.sanatize_polygon()

    def __repr__(self) -> str:
        return str(self.polygon)

 
    @staticmethod
    def get(api_token: str, instrumentid: int, approximate_footprint: bool = True):

        api = baseapi.api(target="footprints")

        if approximate_footprint and instrumentid in APPROXIMATION_DICT.keys():
            inst_id = APPROXIMATION_DICT[instrumentid]
        else:
            inst_id = instrumentid

        get_dict = {
            "id": inst_id,
            "api_token": api_token
        }

        r_json = { 
            "d_json": get_dict
        }

        req = api._get(r_json=r_json)
        request_json = json.loads(req.text)
        inst_footprints = []
        for f in request_json:
            if isinstance(f, str):
                footprint_json = json.loads(f)
            else:
                footprint_json = f
            inst_footprints.append(Footprint(kwdict=footprint_json))

        return inst_footprints


    def sanatize_polygon(self):
        sanitized = self.footprint.strip('POLYGON ').strip(')(').split(',')
        polygon = []
        for vertex in sanitized:
            obj = vertex.split()
            ra = float(obj[0])
            dec = float(obj[1])
            polygon.append([ra,dec])
        self.polygon = polygon


    def project(self, ra: float, dec: float, pos_angle: float):
        if pos_angle is None:
            pos_angle = 0.0

        footprint_zero_center_ra = np.asarray([pt[0] for pt in self.polygon])
        footprint_zero_center_dec = np.asarray([pt[1] for pt in self.polygon])
        footprint_zero_center_uvec = util.ra_dec_to_uvec(footprint_zero_center_ra, footprint_zero_center_dec)
        footprint_zero_center_x, footprint_zero_center_y, footprint_zero_center_z = footprint_zero_center_uvec

        proj_footprint = []
        for idx in range(footprint_zero_center_x.shape[0]):
            vec = np.asarray([footprint_zero_center_x[idx], footprint_zero_center_y[idx], footprint_zero_center_z[idx]])
            new_vec = vec @ util.x_rot(-pos_angle) @ util.y_rot(dec) @ util.z_rot(-ra)
            new_x, new_y, new_z = new_vec.flat
            pt_ra, pt_dec = util.uvec_to_ra_dec(new_x, new_y, new_z)
            proj_footprint.append([round(pt_ra, 3), round(pt_dec, 3)])

        return proj_footprint


    @staticmethod
    def get_cached_footprints(graceid: str = None, instrument_id: int = None, pointings: List[Pointing] = None):
        pointingids = [x.id for x in pointings]
        hashpointingids =  hashlib.sha1(json.dumps(pointingids).encode()).hexdigest()
        cache_name = f"footprints_{graceid}_{instrument_id}_{hashpointingids}"
        cache = tmcache.TMCache(filename=cache_name, cache_type="json")
        return cache.get()

    @staticmethod
    def put_cached_footprints(footprints, graceid: str = None, instrument_id: int = None, pointings: List[Pointing] = None):
        pointingids = [x.id for x in pointings]
        hashpointingids =  hashlib.sha1(json.dumps(pointingids).encode()).hexdigest()
        cache_name = f"footprints_{graceid}_{instrument_id}_{hashpointingids}"
        cache = tmcache.TMCache(filename=cache_name, cache_type="json")
        cache.put(payload=footprints)


class Instrument(apimodels._Table):
    id: int = None
    instrument_name: str = None
    instrument_type: apimodels.instrument_type = None
    datecreated: datetime.datetime = None
    submitterid: int = None,
    nickname: str = None
    footprint: List[Footprint] = None

    def __init__(
        self, 
        id: int = None, 
        instrument_name: str = None, 
        instrument_type: apimodels.instrument_type = None,
        datecreated: datetime.datetime = None, 
        submitterid: int = None, 
        nickname: str = None,
        footprint: List[Footprint] = None, 
        kwdict=None
    ):

        if kwdict is not None:
            selfdict = kwdict
        else:
            selfdict = util.non_none_locals(locals=locals())

        super().__init__(payload=selfdict)

    
    def project(self, ra: float, dec: float, pos_angle: float):
        if self.footprint is None:
            raise Exception("Footprint Polygon is not included")
        
        proj_footprint = []
        for ccd in self.footprint:
            proj_footprint.append(ccd.project(ra, dec, pos_angle))

        return proj_footprint


    @staticmethod
    def get(
            api_token: str, id: int = None, ids: List[int] = None, name: str = None,
            names: List[str] = None, type: apimodels.instrument_type = None,
            include_footprint=False, approximate_footprint=True, urlencode=False
        ) -> List[Instrument]:
        get_dict = util.non_none_locals(locals=locals())

        r_json = {
            "d_json":get_dict
        }

        api = baseapi.api(target="instruments")
        req = api._get(r_json=r_json, urlencode=urlencode)

        ret = []
        if req.status_code == 200:
            request_json = json.loads(req.text)
            for i in request_json:
                if isinstance(i, str):
                    instrument_json = json.loads(i)
                else:
                    instrument_json = i
                ret.append(Instrument(kwdict=instrument_json))
        else:
            raise Exception(f"Error in Instrument.get(). Request: {req.text[0:1000]}")
        
        if include_footprint:
            for inst in ret:
                inst.footprint = Footprint.get(
                    api_token=api_token, instrumentid=inst.id, approximate_footprint=approximate_footprint
                )

        return ret
        