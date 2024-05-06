import json
import datetime
from typing import List
from .core import baseapi
from .core import apimodels
from . import GWTM_GET_CANDIDATE_KEYS, GWTM_POST_CANDIDATE_KEYS

class Candidate(apimodels._Table):
    id: int = None
    created_date: datetime.datetime = None
    candidate_name: str = None
    tns_name: str = None
    tns_url: str = None
    position: str = None
    ra: float = None
    dec: float = None
    discovery_date: datetime.datetime = None
    discovery_magnitude: float = None
    magnitude_central_wave: float = None
    magnitude_bandwidth: float = None
    magnitude_bandpass: apimodels.bandpass = None
    magnitude_unit: apimodels.depth_unit = None
    wavelength_regime: List[int] = None
    wavelength_unit: apimodels.wavelength_units = None
    energy_regime: List[int] = None
    energy_unit: apimodels.energy_units = None
    frequency_regime: List[list] = None
    frequency_unit: apimodels.frequency_units = None
    associated_galaxy: str = None
    associated_galaxy_redshift: float = None
    associated_galaxy_distance: float = None

    def __init__(self, kwdict=None, **kwargs):

        if kwdict is not None:
            selfdict = kwdict
        else:
            selfdict = kwargs

        super().__init__(payload=selfdict)

        self.sanatize_position()

    def validate(self):
        pass

    def sanatize_position(self):
        if self.position is not None:
            try:
                self.ra = float(self.position.split('(')[1].split(')')[0].split()[0])
                self.dec = float(self.position.split('(')[1].split(')')[0].split()[1])
            except:  # noqa: E722
                raise Exception("Invalid position argument. Must be 'POINT (RA DEC)'.")

    def post(self, **kwargs):
        post_keys = list(GWTM_POST_CANDIDATE_KEYS)
        post_dict = {}

        post_dict.update(
            (str(key).lower(), value) for key, value in kwargs.items() if str(key).lower() in post_keys
        )

        self.discovery_date = self.discovery_date.strftime("%Y-%m-%dT%H:%M:%S.%f")
        post_dict["candidates"]=[self.__dict__]

        r_json = {
            "d_json":post_dict
        }

        api = baseapi.api(target="candidate")
        req = api._post(r_json=r_json)

        if req.status_code == 200:
            request_json = json.loads(req.text)
            print(request_json)
        else:
            raise Exception(f"Error in Candidate.post(). Request: {req.text[0:1000]}")


    @staticmethod
    def batch_post(candidates: List, **kwargs):
        post_keys = GWTM_POST_CANDIDATE_KEYS
        post_dict = {}

        post_dict.update(
            (str(key).lower(), value) for key, value in kwargs.items() if str(key).lower() in post_keys
        )

        batch = []
        for p in candidates:
            p.discovery_date = p.discovery_date.strftime("%Y-%m-%dT%H:%M:%S.%f")
            batch.append(p.__dict__)
        
        post_dict['candidates'] = batch

        r_json = {
            "d_json":post_dict
        }

        api = baseapi.api(target="candidate")
        req = api._post(r_json=r_json)

        if req.status_code == 200:
            request_json = json.loads(req.text)
            print(request_json)
        else:
            raise Exception(f"Error in Candidate.post(). Request: {req.text[0:1000]}")


    @staticmethod
    def get(urlencode=False, **kwargs):
        get_keys = list(GWTM_GET_CANDIDATE_KEYS)
        get_dict = {}

        get_dict.update(
            (str(key).lower(), value) for key, value in kwargs.items() if str(key).lower() in get_keys
        )

        r_json = {
            "d_json":get_dict
        }

        api = baseapi.api(target="candidate", base='v1')
        req = api._get(r_json=r_json, urlencode=urlencode)

        if req.status_code == 200:
            ret = []
            request_json = json.loads(req.text)
            for p in request_json:
                if 'v0' in api.base:
                    pointing_json = json.loads(p)
                else:
                    pointing_json = p
                ret.append(Candidate(kwdict=pointing_json))
            return ret
        else:
            raise Exception(f"Error in Candidate.get(). Request: {req.text[0:1000]}")
        
        