import json
import numpy as np

from .core import baseapi
from .core import apimodels
from .core import util 
from . import GWTM_GET_INSTRUMENT_KEYS

class Instrument(apimodels._Table):
    id = None
    footprint = None

    def __init__(self, kwdict=None, **kwargs):

        if kwdict is not None:
            selfdict = kwdict
        else:
            selfdict = kwargs

        super().__init__(payload=selfdict)


    def validate(self):
        pass

    
    def project(self, ra, dec, pos_angle):
        if self.footprint is None:
            raise Exception("Footprint Polygon is not included")
        
        proj_footprint = []
        for ccd in self.footprint:
            proj_footprint.append(ccd.project(ra, dec, pos_angle))

        return proj_footprint

    @staticmethod
    def get(include_footprint=False, urlencode=False, **kwargs):
        get_keys = list(GWTM_GET_INSTRUMENT_KEYS)
        get_dict = {}

        get_dict.update(
            (str(key).lower(), value) for key, value in kwargs.items() if str(key).lower() in get_keys
        )

        r_json = {
            "d_json":get_dict
        }

        api = baseapi.api(target="instruments", base="v0")
        req = api._get(r_json=r_json, urlencode=urlencode)

        ret = []
        if req.status_code == 200:
            request_json = json.loads(req.text)
            for i in request_json:
                instrument_json = json.loads(i)
                ret.append(Instrument(kwdict=instrument_json))
        else:
            raise Exception(f"Error in Instrument.get(). Request: {req.text[0:1000]}")
        
        if include_footprint:
            api = baseapi.api(target="footprints")
            for inst in ret:
                r_json = { 
                    "d_json": {
                        "id": inst.id, 
                        "api_token": get_dict["api_token"] 
                    }
                }
                req = api._get(r_json=r_json)
                request_json = json.loads(req.text)
                inst_footprints = []
                for f in request_json:
                    footprint_json = json.loads(f)
                    inst_footprints.append(Footprint(kwdict=footprint_json))
                inst.footprint = inst_footprints
        return ret
    

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


    def sanatize_polygon(self):
        sanitized = self.footprint.strip('POLYGON ').strip(')(').split(',')
        polygon = []
        for vertex in sanitized:
            obj = vertex.split()
            ra = float(obj[0])
            dec = float(obj[1])
            polygon.append([ra,dec])
        self.polygon = polygon

    def project(self, ra, dec, pos_angle):
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
            proj_footprint.append([pt_ra, pt_dec])

        return proj_footprint