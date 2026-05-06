from __future__ import annotations
import datetime
from typing import List, Union

from .core import apimodels
from .core import util
from .core.util import _encode_list_param
from .core import _client_factory as transport
from .pointing import _enum_name


class Candidate(apimodels._Table):
    id: int = None
    datecreated: Union[datetime.datetime, str] = None
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

    def __init__(self,
            id: int = None,
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
        if api_token:
            transport.configure(api_token=api_token)

        self.position = position
        selfdict = kwdict if kwdict is not None else util.non_none_locals(locals=locals())

        if id:
            payload = Candidate.get(id=id)
            if payload:
                selfdict = payload[0].__dict__
            else:
                raise Exception(f"No candidate found with id: {id}")

        super().__init__(payload=selfdict)

        if "position" in selfdict:
            self._sanatize_pointing()
        elif "ra" in selfdict and "dec" in selfdict:
            self._sanatize_ra_dec()
        else:
            raise Exception("Positional arguments are required: ra/dec or POINT(ra dec)")

    def _sanatize_pointing(self):
        if self.position is not None:
            try:
                self.ra = float(self.position.split('(')[1].split(')')[0].split()[0])
                self.dec = float(self.position.split('(')[1].split(')')[0].split()[1])
            except:  # noqa: E722
                raise Exception("Invalid position. Must be 'POINT ({ra} {dec})'.")

    def _sanatize_ra_dec(self):
        if self.position is None:
            if all(isinstance(x, float) for x in [self.ra, self.dec]):
                self.position = f"POINT ({self.ra} {self.dec})"
            else:
                raise Exception("ra and dec must be floats")

    def _to_dict(self) -> dict:
        dd = (self.discovery_date.strftime("%Y-%m-%dT%H:%M:%S.%f")
              if isinstance(self.discovery_date, datetime.datetime) else self.discovery_date)
        return {
            'candidate_name': self.candidate_name or '',
            'discovery_date': dd,
            'discovery_magnitude': self.discovery_magnitude or 0.0,
            'magnitude_unit': _enum_name(self.magnitude_unit) or 'ab_mag',
            'position': self.position,
            'ra': self.ra,
            'dec': self.dec,
            'tns_name': self.tns_name,
            'tns_url': self.tns_url,
            'magnitude_bandpass': _enum_name(self.magnitude_bandpass),
            'magnitude_bandwidth': self.magnitude_bandwidth,
            'wavelength_regime': self.wavelength_regime,
            'wavelength_unit': _enum_name(self.wavelength_unit),
            'frequency_regime': self.frequency_regime,
            'frequency_unit': _enum_name(self.frequency_unit),
            'energy_regime': self.energy_regime,
            'energy_unit': _enum_name(self.energy_unit),
            'associated_galaxy': self.associated_galaxy,
            'associated_galaxy_redshift': self.associated_galaxy_redshift,
            'associated_galaxy_distance': self.associated_galaxy_distance,
        }

    def post(self, graceid: str = None, verbose=False, api_token: str = None):
        if api_token:
            transport.configure(api_token=api_token)
        if graceid is None:
            graceid = self.graceid
        result = transport.post('/candidate', json={'graceid': graceid, 'candidate': self._to_dict()})
        if verbose:
            print(result)
        fetched = Candidate.get(id=result['candidate_ids'][0])
        self.__init__(kwdict=fetched[0].__dict__)

    @staticmethod
    def batch_post(candidates: List[Candidate], graceid: str = None,
                   verbose=False, api_token: str = None) -> List[Candidate]:
        if api_token:
            transport.configure(api_token=api_token)
        if graceid is None:
            graceids = list(set(c.graceid for c in candidates if c.graceid))
            if len(graceids) != 1:
                raise Exception("All candidates must share a single graceid, or provide it explicitly")
            graceid = graceids[0]
        result = transport.post('/candidate', json={
            'graceid': graceid,
            'candidates': [c._to_dict() for c in candidates],
        })
        if verbose:
            print(result)
        return Candidate.get(ids=result['candidate_ids'])

    @staticmethod
    def get(graceid: str = None, id: int = None, ids: List[int] = None,
            submitted_date_after: datetime.datetime = None,
            submitted_date_before: datetime.datetime = None,
            discovery_date_after: datetime.datetime = None,
            discovery_date_before: datetime.datetime = None,
            userid: int = None,
            discovery_magnitude_gt: float = None,
            discovery_magnitude_lt: float = None,
            associated_galaxy_redshift_gt: float = None,
            associated_galaxy_redshift_lt: float = None,
            associated_galaxy_distance_gt: float = None,
            associated_galaxy_distance_lt: float = None,
            associated_galaxy_name: str = None,
            urlencode=None,
            api_token: str = None) -> list[Candidate]:
        if api_token:
            transport.configure(api_token=api_token)
        result = transport.get('/candidate', params={
            'graceid': graceid,
            'id': id,
            'userid': userid,
            'submitted_date_after': submitted_date_after,
            'submitted_date_before': submitted_date_before,
            'discovery_date_after': discovery_date_after,
            'discovery_date_before': discovery_date_before,
            'discovery_magnitude_gt': discovery_magnitude_gt,
            'discovery_magnitude_lt': discovery_magnitude_lt,
            'associated_galaxy_name': associated_galaxy_name,
            'associated_galaxy_redshift_gt': associated_galaxy_redshift_gt,
            'associated_galaxy_redshift_lt': associated_galaxy_redshift_lt,
            'associated_galaxy_distance_gt': associated_galaxy_distance_gt,
            'associated_galaxy_distance_lt': associated_galaxy_distance_lt,
        })
        if not isinstance(result, list):
            raise Exception("Error in Candidate.get(): unexpected response from server")
        return [Candidate(kwdict=c) for c in result]

    def put(self, payload: dict = None, verbose: bool = False,
            api_token: str = None):
        if api_token:
            transport.configure(api_token=api_token)
        if not self.id:
            raise Exception("Candidate does not have an id")
        result = transport.put('/candidate', json={'candidate': payload or self._to_dict()})
        if verbose:
            print(result)
        fetched = Candidate.get(id=self.id)
        self.__init__(kwdict=fetched[0].__dict__)

    def delete(self, verbose: bool = False, api_token: str = None) -> dict:
        if api_token:
            transport.configure(api_token=api_token)
        if not self.id:
            raise Exception("Candidate does not have an id")
        result = transport.delete('/candidate', json={'id': self.id})
        if verbose:
            print(result)
        return result

    @staticmethod
    def batch_delete(ids: List[int], verbose: bool = False,
                     api_token: str = None) -> dict:
        if api_token:
            transport.configure(api_token=api_token)
        result = transport.delete('/candidate', json={'ids': ids})
        if verbose:
            print(result)
        return result
