from __future__ import annotations
import json
import datetime
from typing import List, Union
from .core import baseapi
from .core import apimodels
from .core import util

class Candidate(apimodels._Table):
    id: int = None
    created_date: datetime.datetime = None
    graceid: str = None
    candidate_name: str = None
    tns_name: str = None
    tns_url: str = None
    position: str = None
    ra: float = None
    dec: float = None
    discovery_date: Union[datetime.datetime, str] = None
    discovery_magnitude: float = None
    magnitude_central_wave: float = None
    magnitude_bandwidth: float = None
    magnitude_bandpass: apimodels.bandpass = None
    magnitude_unit: apimodels.depth_unit = None
    wavelength_regime: List[float] = None
    wavelength_unit: apimodels.wavelength_units = None
    energy_regime: List[float] = None
    energy_unit: apimodels.energy_units = None
    frequency_regime: List[float] = None
    frequency_unit: apimodels.frequency_units = None
    associated_galaxy: str = None
    associated_galaxy_redshift: float = None
    associated_galaxy_distance: float = None

    def __init__(
            self, 
            id: int = None,
            created_date: datetime.datetime = None,
            graceid: str = None,
            candidate_name: str = None,
            tns_name: str = None,
            tns_url: str = None,
            position: str = None,
            ra: float = None,
            dec: float = None,
            discovery_date: datetime.datetime = None,
            discovery_magnitude: float = None,
            magnitude_central_wave: float = None,
            magnitude_bandwidth: float = None,
            magnitude_bandpass: apimodels.bandpass = None,
            magnitude_unit: apimodels.depth_unit = None,
            wavelength_regime: List[float] = None,
            wavelength_unit: apimodels.wavelength_units = None,
            energy_regime: List[float] = None,
            energy_unit: apimodels.energy_units = None,
            frequency_regime: List[float] = None,
            frequency_unit: apimodels.frequency_units = None,
            associated_galaxy: str = None,
            associated_galaxy_redshift: float = None,
            associated_galaxy_distance: float = None,
            api_token: str = None,
            kwdict=None
        ):

        self.position = position

        if kwdict is not None:
            selfdict = kwdict
        else:
            selfdict = util.non_none_locals(locals=locals())

        #if user passes in an ID, then prepopulate with a get request
        if id:
            if api_token:
                payload = Candidate.get(api_token=api_token, id=id)
                if len(payload):
                    selfdict = payload[0].__dict__
                else:
                    raise Exception(f"No candidate found with id: {id}")
            else:
                raise Exception("api_token required")
            
        super().__init__(payload=selfdict)

        if "position" in selfdict.keys():
            self._sanatize_pointing()
        elif all([x in selfdict.keys() for x in ["ra", "dec"]]):
            self._sanatize_ra_dec()
        else:
            raise Exception("Positional arguments are required. Must be decimal format ra, dec, or geometry type \"POINT(ra dec)\"")


    def _sanatize_pointing(self):
        if self.position is not None:
            try:
                self.ra = float(self.position.split('(')[1].split(')')[0].split()[0])
                self.dec = float(self.position.split('(')[1].split(')')[0].split()[1])
            except:  # noqa: E722
                raise Exception("Invalid position argument. Must be 'POINT (\{ra\} \{dec\})'.")


    def _sanatize_ra_dec(self):
        if self.position is None:
            if all([isinstance(x, float) for x in [self.ra, self.dec]]):
                self.position = f"POINT ({self.ra} {self.dec})"
            else:
                raise Exception("Invalid format for ra/dec. Both must be float")


    def post(
            self, api_token: str, graceid: str = None,
            base: str = "https://treasuremap.space/api/", api_version: str ="v1",
            verbose = False
        ) -> Candidate:
        if graceid is None:
            graceid = self.graceid
        
        post_dict = util.non_none_locals(locals=locals())

        self.discovery_date = self.discovery_date.strftime("%Y-%m-%dT%H:%M:%S.%f")
        post_dict["candidates"]=[self.__dict__]
        post_dict["graceid"]=graceid

        r_json = {
            "d_json":post_dict
        }

        api = baseapi.api(target="candidate")
        req = api._post(r_json=r_json)

        if req.status_code == 200:
            request_json = json.loads(req.text)
            if verbose:
                print(request_json)
            id = request_json["candidate_ids"][0]
            return Candidate.get(api_token=api_token, id=id)[0]
        else:
            raise Exception(f"Error in Candidate.post(). Request: {req.text[0:1000]}")


    @staticmethod
    def batch_post(
            candidates: List[Candidate], api_token: str, graceid: str = None,
            base: str = "https://treasuremap.space/api/", api_version: str ="v1",
            verbose = False
        ) -> List[Candidate]:
        
        post_dict = util.non_none_locals(locals=locals())

        batch = []
        for p in candidates:
            if not isinstance(p, Candidate):
                raise Exception("Input candidate must be a list of Candidate")
            p.discovery_date = p.discovery_date.strftime("%Y-%m-%dT%H:%M:%S.%f")
            batch.append(p.__dict__)
        
        if graceid is None:
            graceids = list(set([x.graceid for x in candidates]))
            if len(graceids) > 1:
                raise Exception("You can only post candidates for a single GW Event graceid at a time")
            post_dict["graceid"] = graceids[0]

        post_dict['candidates'] = batch

        r_json = {
            "d_json":post_dict
        }

        api = baseapi.api(target="candidate")
        req = api._post(r_json=r_json)

        if req.status_code == 200:
            request_json = json.loads(req.text)
            ids = request_json["candidate_ids"]
            if verbose:
                print(request_json)
            return Candidate.get(api_token=api_token, ids=ids)
        else:
            raise Exception(f"Error in Candidate.post(). Request: {req.text[0:1000]}")


    @staticmethod
    def get(
        api_token: str, graceid: str = None, id: int = None, ids: List[int] = None,
        submitted_date_after: datetime.datetime = None, submitted_date_before: datetime.datetime = None,
        discovery_date_after: datetime.datetime = None, discovery_date_before: datetime.datetime = None,
        userid: int =  None, discovery_magnitude_gt: float = None, discovery_magnitude_lt: float = None,
        associated_galaxy_redshift_gt: float = None, associated_galaxy_redshift_lt: float = None, 
        associated_galaxy_distance_gt: float = None, associated_galaxy_distance_lt: float = None, 
        associated_galaxy_name: str = None, 
        urlencode=False, base: str = "https://treasuremap.space/api/", api_version: str ="v1"
    ) -> list[Candidate]:
        
        get_dict = util.non_none_locals(locals=locals())

        r_json = {
            "d_json":get_dict
        }

        api = baseapi.api(target="candidate", base=base, api_version=api_version)
        req = api._get(r_json=r_json, urlencode=urlencode)

        if req.status_code == 200:
            ret = []
            request_json = json.loads(req.text)
            for p in request_json:
                if 'v0' in api.base:
                    json_value = json.loads(p)
                else:
                    json_value = p
                ret.append(Candidate(kwdict=json_value))
            return ret
        else:
            raise Exception(f"Error in Candidate.get(). Request: {req.text[0:1000]}")
    

    def put(
            self, api_token: str, payload: dict = None, base: str = "https://treasuremap.space/api/", 
            api_version: str ="v1", verbose: bool = False
        ) -> Candidate:
        '''
            Candidate PUT endpoint
        '''
        if payload:
            if "id" in payload.keys() and isinstance(payload["id"], int):
                self.id = payload["id"]
        else:
            payload = self.__dict__
        if not self.id:
            raise Exception("Candidate does not have an id")
        
        if self.discovery_date:
            self.discovery_date = self.discovery_date.strftime("%Y-%m-%dT%H:%M:%S.%f")

        put_dict = {
            "api_token": api_token,
            "id": self.id,
            "payload": payload
        }

        r_json = {
            "d_json": put_dict
        }

        api = baseapi.api(target="candidate", base=base, api_version=api_version)
        req = api._put(r_json=r_json)
        if req.status_code == 200:
            request_json = json.loads(req.text)
            if verbose:
                print(request_json)
            return Candidate(id=self.id, api_token=api_token)
        else:
            raise Exception(f"Error in Candidate.get(). Request: {req.text[0:1000]}")


    def delete(
            self, api_token: str, base: str = "https://treasuremap.space/api/", 
            api_version: str ="v1", verbose: bool =False
        ) -> dict:
        '''
            Candidate DELETE endpoint
        '''
        if not self.id:
            raise Exception("Candidate does not have an id")
        
        del_dict = {
            "api_token": api_token,
            "id": self.id
        }
        r_json = {
            "d_json": del_dict
        }

        api = baseapi.api(target="candidate", base=base, api_version=api_version)
        req = api._delete(r_json=r_json)
        if req.status_code == 200:
            request_json = json.loads(req.text)
            if verbose:
                print(request_json)
        else:
            raise Exception(f"Error in Candidate.get(). Request: {req.text[0:1000]}")
    
    @staticmethod
    def batch_delete(
            api_token: str, ids: List[int], base: str = "https://treasuremap.space/api/", api_version: str ="v1",
            verbose: bool = False
        ):
        '''
            Canididates DELETE endpoint
        '''
        del_dict = {
            "api_token": api_token,
            "ids": ids
        }
        r_json = {
            "d_json": del_dict
        }

        api = baseapi.api(target="candidate", base=base, api_version=api_version)
        req = api._delete(r_json=r_json)
        if req.status_code == 200:
            request_json = json.loads(req.text)
            if verbose:
                print(request_json)
        else:
            raise Exception(f"Error in Candidate.get(). Request: {req.text[0:1000]}")