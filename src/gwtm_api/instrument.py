from __future__ import annotations
import datetime
import hashlib
import json
from typing import List
import numpy as np

from .pointing import Pointing
from .core import apimodels
from .core import util
from .core import tmcache
from .core.util import _encode_list_param
from .core import _client_factory as transport

APPROXIMATION_DICT = {
    47: 76,  # ZTF
    38: 98,  # DECAM
}


class Footprint(apimodels._Table):
    id = None
    footprint = None
    polygon = None

    def __init__(self, kwdict=None, **kwargs):
        selfdict = kwdict if kwdict is not None else kwargs
        super().__init__(payload=selfdict)
        self.sanatize_polygon()

    def __repr__(self) -> str:
        return str(self.polygon)

    @staticmethod
    def get(instrumentid: int, approximate_footprint: bool = True,
            api_token: str = None):
        if api_token:
            transport.configure(api_token=api_token)
        inst_id = APPROXIMATION_DICT.get(instrumentid, instrumentid) if approximate_footprint else instrumentid
        result = transport.get('/footprints', params={'id': inst_id})
        if not isinstance(result, list):
            raise Exception("Error in Footprint.get(): unexpected response from server")
        return [Footprint(kwdict=f) for f in result]

    def sanatize_polygon(self):
        sanitized = self.footprint.strip('POLYGON ').strip(')(').split(',')
        self.polygon = [[float(v) for v in vertex.split()] for vertex in sanitized]

    def project(self, ra: float, dec: float, pos_angle: float):
        if pos_angle is None:
            pos_angle = 0.0
        fp_ra = np.asarray([pt[0] for pt in self.polygon])
        fp_dec = np.asarray([pt[1] for pt in self.polygon])
        x, y, z = util.ra_dec_to_uvec(fp_ra, fp_dec)
        proj = []
        for i in range(x.shape[0]):
            vec = np.asarray([x[i], y[i], z[i]])
            nx, ny, nz = (vec @ util.x_rot(-pos_angle) @ util.y_rot(dec) @ util.z_rot(-ra)).flat
            pt_ra, pt_dec = util.uvec_to_ra_dec(nx, ny, nz)
            proj.append([round(pt_ra, 3), round(pt_dec, 3)])
        return proj

    @staticmethod
    def get_cached_footprints(graceid=None, instrument_id=None, pointings=None):
        h = hashlib.sha1(json.dumps([x.id for x in pointings]).encode()).hexdigest()
        return tmcache.TMCache(filename=f"footprints_{graceid}_{instrument_id}_{h}", cache_type="json").get()

    @staticmethod
    def put_cached_footprints(footprints, graceid=None, instrument_id=None, pointings=None):
        h = hashlib.sha1(json.dumps([x.id for x in pointings]).encode()).hexdigest()
        tmcache.TMCache(filename=f"footprints_{graceid}_{instrument_id}_{h}", cache_type="json").put(payload=footprints)


class Instrument(apimodels._Table):
    id: int = None
    instrument_name: str = None
    instrument_type: apimodels.instrument_type = None
    datecreated: datetime.datetime = None
    submitterid: int = None
    nickname: str = None
    footprint: List[Footprint] = None

    def __init__(self, id=None, instrument_name=None, instrument_type=None,
                 datecreated=None, submitterid=None, nickname=None,
                 footprint=None, kwdict=None):
        selfdict = kwdict if kwdict is not None else util.non_none_locals(locals=locals())
        super().__init__(payload=selfdict)

    def project(self, ra: float, dec: float, pos_angle: float):
        if self.footprint is None:
            raise Exception("Footprint not included — pass include_footprint=True to Instrument.get()")
        return [ccd.project(ra, dec, pos_angle) for ccd in self.footprint]

    @staticmethod
    def get(id: int = None, ids: List[int] = None,
            name: str = None, names: List[str] = None,
            type: apimodels.instrument_type = None,
            include_footprint: bool = False,
            approximate_footprint: bool = True,
            urlencode=None,
            api_token: str = None) -> List[Instrument]:
        if api_token:
            transport.configure(api_token=api_token)
        result = transport.get('/instruments', params={
            'id': id,
            'ids': _encode_list_param(ids),
            'name': name,
            'names': _encode_list_param(names),
            'type': type,
        })
        if not isinstance(result, list):
            raise Exception("Error in Instrument.get(): unexpected response from server")
        instruments = [Instrument(kwdict=i) for i in result]

        if include_footprint:
            for inst in instruments:
                inst.footprint = Footprint.get(
                    instrumentid=inst.id,
                    approximate_footprint=approximate_footprint,
                )
        return instruments
