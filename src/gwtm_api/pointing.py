from __future__ import annotations
import json
import datetime
from typing import List

from .core import baseapi
from .core import apimodels
from .core import util

class Pointing(apimodels._Table):
    id: int = None
    position: str = None
    ra: float = None
    dec: float = None
    instrumentid: int = None
    time: datetime.datetime = None
    status: apimodels.pointing_status = None
    depth: float = None
    depth_unit: apimodels.depth_unit = None
    band: apimodels.bandpass = None
    wavelength_regime: List[float] = None
    wavelength_unit: apimodels.wavelength_units = None
    energy_regime: List[float] = None
    energy_unit: apimodels.energy_units = None
    frequency_regime: List[float] = None
    frequency_unit: apimodels.frequency_units = None
    pos_angle: float = None
    depth_err: float = None
    doi_url: str = None
    doi_id: int = None
    submitterid: int = None
    central_wave: float = None
    bandwidth: float = None

    def __init__(self, kwdict=None, 
        id: int = None,
        position: str = None,
        ra: float = None,
        dec: float = None,
        instrumentid: int = None,
        time: datetime.datetime = None,
        status: apimodels.pointing_status = None,
        depth: float = None,
        depth_unit: apimodels.depth_unit = None,
        band: apimodels.bandpass = None,
        wavelength_regime: List[float] = None,
        wavelength_unit: apimodels.wavelength_units = None,
        energy_regime: List[float] = None,
        energy_unit: apimodels.energy_units = None,
        frequency_regime: List[float] = None,
        frequency_unit: apimodels.frequency_units = None,
        pos_angle: float = None,
        depth_err: float = None,
        doi_url: str = None,
        doi_id: int = None,
        submitterid: int = None,
        central_wave: float = None,
        bandwidth: float = None,
        api_token: str = None
    ):

        self.position = position
        self.time = time

        if kwdict is not None:
            selfdict = kwdict
        else:
            selfdict = util.non_none_locals(locals=locals())

        #if user passes in an ID, then prepopulate with a get request
        if id:
            if api_token:
                payload = Pointing.get(api_token=api_token, id=id)
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
            self, api_token: str, graceid: str, request_doi: bool = None, 
            doi_url: str = None, creators: List[dict] = None, doi_group_id: int = None,
            base: str = "https://treasuremap.space/api/", api_version: str ="v1",
            verbose: bool = False
        ):
        
        post_dict = util.non_none_locals(locals=locals())

        self.time = self.time.strftime("%Y-%m-%dT%H:%M:%S.%f")
        post_dict["pointings"]=[self.__dict__]

        r_json = {
            "d_json":post_dict
        }

        api = baseapi.api(target="pointings", base=base)
        req = api._post(r_json=r_json)

        if req.status_code == 200:
            request_json = json.loads(req.text)
            if verbose:
                print(request_json)
            id = request_json["pointing_ids"][0]
            self.__init__(kwdict=Pointing.get(api_token=api_token, id=id)[0].__dict__)
        else:
            raise Exception(f"Error in Pointing.post(). Request: {req.text[0:1000]}")


    @staticmethod
    def batch_post(
        api_token: str, graceid: str, pointings: List[Pointing], request_doi: bool = False, 
            doi_url: str = None, creators: List[dict] = None, doi_group_id: int = None,
            base: str = "https://treasuremap.space/api/", api_version="v1",
            verbose: bool = False
        ) -> List[Pointing]:
        
        post_dict = util.non_none_locals(locals=locals())

        batch_pointings = []
        for p in pointings:
            if not isinstance(p, Pointing):
                raise Exception("Input \'pointings\' must be type List[Pointing]")
            p.time = p.time.strftime("%Y-%m-%dT%H:%M:%S.%f")
            batch_pointings.append(p.__dict__)
        
        post_dict['pointings'] = batch_pointings

        r_json = {
            "d_json":post_dict
        }

        api = baseapi.api(target="pointings", base=base, api_version=api_version)
        req = api._post(r_json=r_json)

        if req.status_code == 200:
            request_json = json.loads(req.text)
            ids = request_json["pointing_ids"]
            if verbose:
                print(request_json)
            return Pointing.get(api_token=api_token, ids=ids)
        else:
            raise Exception(f"Error in Pointing.post(). Request: {req.text[0:1000]}")


    @staticmethod
    def get(
            api_token: str, graceid: str = None, graceids: List[str] = None, instrument: str = None,
            instruments: List[str] = None, id: int = None, ids: List[int] = None, status: apimodels.pointing_status = None,
            completed_after: datetime.datetime = None, completed_before: datetime.datetime = None,
            planned_after: datetime.datetime = None, planned_before: datetime.datetime = None,
            user: str = None, users: List[str] = None, band: apimodels.bandpass = None, 
            bands: List[apimodels.bandpass] = None, central_wave: float = None, bandwidth: float = None, 
            wavelength_regime: List[float] = None, wavelength_unit: apimodels.wavelength_units = None,
            energy_regime: List[float] = None, energy_unit: apimodels.energy_units = None,
            frequency_regime: List[float] = None, frequency_unit: apimodels.frequency_units = None,
            depth_gt: float = None, depth_lt: float = None, depth_unit: apimodels.depth_unit = None,
            base: str = "https://treasuremap.space/api/", api_version: str ="v1", urlencode: bool = False, 
        ) -> List[Pointing]:

        get_dict = util.non_none_locals(locals=locals())

        r_json = {
            "d_json":get_dict
        }

        api = baseapi.api(target="pointings", base=base, api_version=api_version)
        req = api._get(r_json=r_json, urlencode=urlencode)

        if req.status_code == 200:
            ret: List[Pointing] = []
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
        
    
    @staticmethod
    def request_doi(
            api_token: str, graceid: str = None, id: int = None, ids: List[int] = None, creators: dict = None, 
            doi_group_id: int = None, base: str = "https://treasuremap.space/api/", api_version: str ="v1"
    ) -> str:
        if all([x is None for x in [graceid, id, ids]]):
            raise Exception("Invalid parameters to request DOI. Must specify \'graceid\', pointing \'id\', or list of \'ids\'")
        
        get_dict = util.non_none_locals(locals=locals())

        r_json = {
            "d_json":get_dict
        }

        api = baseapi.api(target="request_doi", base=base, api_version=api_version)
        req = api._post(r_json=r_json)

        if req.status_code == 200:
            request_json = json.loads(req.text)
            return request_json["DOI URL"]
        else:
            raise Exception(f"Error in Pointing.get(). Request: {req.text[0:1000]}")

        return ""