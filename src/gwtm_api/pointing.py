import json

from .core import baseapi
from .core import apimodels
from . import GWTM_GET_POINTING_KEYS, GWTM_POST_POINTING_KEYS

class Pointing(apimodels._Table):
    id = None
    position = None
    ra = None
    dec = None
    instrumentid = None
    time = None
    status = None
    depth = None
    depth_unit = None
    band = None
    wavelength_regime = None
    wavelength_unit = None
    energy_regime = None
    energy_unit = None
    frequency_regime = None
    frequency_unit = None
    pos_angle = None
    depth_err = None
    doi_url = None
    doi_id = None
    submitterid = None
    central_wave = None
    bandwidth = None

    def __init__(self, kwdict=None, **kwargs):

        if kwdict is not None:
            selfdict = kwdict
        else:
            selfdict = kwargs

        super().__init__(payload=selfdict)

        self.sanatize_pointing()

    def validate(self):
        pass

    def sanatize_pointing(self):
        if self.position is not None:
            try:
                self.ra = float(self.position.split('(')[1].split(')')[0].split()[0])
                self.dec = float(self.position.split('(')[1].split(')')[0].split()[1])
            except:  # noqa: E722
                raise Exception("Invalid position argument. Must be 'POINT (RA DEC)'.")

    def post(self, **kwargs):
        post_keys = list(GWTM_POST_POINTING_KEYS)
        post_dict = {}

        post_dict.update(
            (str(key).lower(), value) for key, value in kwargs.items() if str(key).lower() in post_keys
        )

        self.time = self.time.strftime("%Y-%m-%dT%H:%M:%S.%f")
        post_dict["pointings"]=[self.__dict__]

        r_json = {
            "d_json":post_dict
        }

        api = baseapi.api(target="pointings")
        req = api._post(r_json=r_json)

        if req.status_code == 200:
            request_json = json.loads(req.text)
            print(request_json)
        else:
            raise Exception(f"Error in Pointing.post(). Request: {req.text[0:1000]}")


    @staticmethod
    def batch_post(pointings: list, **kwargs):
        post_keys = list(GWTM_POST_POINTING_KEYS)
        post_dict = {}

        post_dict.update(
            (str(key).lower(), value) for key, value in kwargs.items() if str(key).lower() in post_keys
        )

        batch_pointings = []
        for p in pointings:
            if not isinstance(p, Pointing):
                raise Exception("Input pointing must be a list of Pointings")
            p.time = p.time.strftime("%Y-%m-%dT%H:%M:%S.%f")
            batch_pointings.append(p.__dict__)
        
        post_dict['pointings'] = batch_pointings

        r_json = {
            "d_json":post_dict
        }

        api = baseapi.api(target="pointings")
        req = api._post(r_json=r_json)

        if req.status_code == 200:
            request_json = json.loads(req.text)
            print(request_json)
        else:
            raise Exception(f"Error in Pointing.post(). Request: {req.text[0:1000]}")


    @staticmethod
    def get(urlencode=False, **kwargs):
        get_keys = list(GWTM_GET_POINTING_KEYS)
        get_dict = {}

        get_dict.update(
            (str(key).lower(), value) for key, value in kwargs.items() if str(key).lower() in get_keys
        )

        r_json = {
            "d_json":get_dict
        }

        api = baseapi.api(target="pointings", base='v1')
        req = api._get(r_json=r_json, urlencode=urlencode)

        if req.status_code == 200:
            ret = []
            request_json = json.loads(req.text)
            for p in request_json:
                if 'v0' in api.base:
                    pointing_json = json.loads(p)
                else:
                    pointing_json = p
                ret.append(Pointing(kwdict=pointing_json))
            return ret
        else:
            raise Exception(f"Error in Pointing.get(). Request: {req.text[0:1000]}")
        
        