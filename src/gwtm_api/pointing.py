from __future__ import annotations
import datetime
from typing import List

from .core import apimodels
from .core import util
from .core.util import _encode_list_param
from .core import _client_factory as transport


def _enum_name(value):
    if value is None:
        return None
    return value.name if hasattr(value, 'name') else value


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
            api_token: str = None,
        ):
        if api_token:
            transport.configure(api_token=api_token)

        self.position = position
        self.time = time

        if kwdict is not None:
            selfdict = kwdict
        else:
            selfdict = util.non_none_locals(locals=locals())

        if id:
            payload = Pointing.get(id=id)
            if payload:
                selfdict = payload[0].__dict__
            else:
                raise Exception(f"No pointing found with id: {id}")

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
        return {
            'ra': self.ra,
            'dec': self.dec,
            'instrumentid': self.instrumentid,
            'time': self.time.isoformat() if isinstance(self.time, datetime.datetime) else None,
            'status': _enum_name(self.status) or 'planned',
            'depth': self.depth,
            'depth_unit': _enum_name(self.depth_unit),
            'band': _enum_name(self.band),
            'pos_angle': self.pos_angle,
            'depth_err': self.depth_err,
            'central_wave': self.central_wave,
            'bandwidth': self.bandwidth,
        }

    def post(self, graceid: str, request_doi: bool = None,
             doi_url: str = None, creators: List[dict] = None,
             doi_group_id: int = None, verbose: bool = False,
             api_token: str = None):
        if api_token:
            transport.configure(api_token=api_token)
        payload = {'graceid': graceid, 'pointing': self._to_dict()}
        if request_doi:
            payload['request_doi'] = request_doi
        if doi_url is not None:
            payload['doi_url'] = doi_url
        if creators is not None:
            payload['creators'] = creators
        if doi_group_id is not None:
            payload['doi_group_id'] = doi_group_id
        result = transport.post('/pointings', json=payload)
        if verbose:
            print(result)
        fetched = Pointing.get(id=result['pointing_ids'][0])
        self.__init__(kwdict=fetched[0].__dict__)

    @staticmethod
    def batch_post(graceid: str, pointings: List[Pointing],
                   request_doi: bool = False, doi_url: str = None,
                   creators: List[dict] = None, doi_group_id: int = None,
                   verbose: bool = False, api_token: str = None) -> List[Pointing]:
        if api_token:
            transport.configure(api_token=api_token)
        payload = {'graceid': graceid, 'pointings': [p._to_dict() for p in pointings]}
        if request_doi:
            payload['request_doi'] = request_doi
        if doi_url is not None:
            payload['doi_url'] = doi_url
        if creators is not None:
            payload['creators'] = creators
        if doi_group_id is not None:
            payload['doi_group_id'] = doi_group_id
        result = transport.post('/pointings', json=payload)
        if verbose:
            print(result)
        return Pointing.get(ids=result['pointing_ids'])

    @staticmethod
    def get(graceid: str = None,
            graceids: List[str] = None,
            instrument: str = None,
            instruments: List[str] = None,
            id: int = None,
            ids: List[int] = None,
            status: apimodels.pointing_status = None,
            completed_after: datetime.datetime = None,
            completed_before: datetime.datetime = None,
            planned_after: datetime.datetime = None,
            planned_before: datetime.datetime = None,
            user: str = None,
            users: List[str] = None,
            band: apimodels.bandpass = None,
            bands: List[apimodels.bandpass] = None,
            central_wave: float = None,
            bandwidth: float = None,
            wavelength_regime: List[float] = None,
            wavelength_unit: apimodels.wavelength_units = None,
            energy_regime: List[float] = None,
            energy_unit: apimodels.energy_units = None,
            frequency_regime: List[float] = None,
            frequency_unit: apimodels.frequency_units = None,
            depth_gt: float = None,
            depth_lt: float = None,
            depth_unit: apimodels.depth_unit = None,
            urlencode=None,
            api_token: str = None,
        ) -> List[Pointing]:
        if api_token:
            transport.configure(api_token=api_token)
        result = transport.get('/pointings', params={
            'graceid': graceid,
            'graceids': _encode_list_param(graceids),
            'id': id,
            'ids': _encode_list_param(ids),
            'status': _enum_name(status),
            'instrument': instrument,
            'instruments': _encode_list_param(instruments),
            'completed_after': completed_after,
            'completed_before': completed_before,
            'planned_after': planned_after,
            'planned_before': planned_before,
            'user': user,
            'users': _encode_list_param(users),
            'band': _enum_name(band),
            'bands': _encode_list_param([_enum_name(b) for b in bands] if bands else None),
            'depth_gt': depth_gt,
            'depth_lt': depth_lt,
            'depth_unit': _enum_name(depth_unit),
            'wavelength_regime': _encode_list_param(wavelength_regime),
            'wavelength_unit': _enum_name(wavelength_unit),
            'energy_regime': _encode_list_param(energy_regime),
            'energy_unit': _enum_name(energy_unit),
            'frequency_regime': _encode_list_param(frequency_regime),
            'frequency_unit': _enum_name(frequency_unit),
        })
        return [Pointing(kwdict=p) for p in result]

    @staticmethod
    def request_doi(graceid: str = None, id: int = None,
                    ids: List[int] = None, creators: dict = None,
                    doi_group_id: str = None, api_token: str = None) -> str:
        if api_token:
            transport.configure(api_token=api_token)
        if all(x is None for x in [graceid, id, ids]):
            raise Exception("Must specify 'graceid', 'id', or 'ids'")
        result = transport.post('/request_doi', json={
            'graceid': graceid, 'id': id, 'ids': ids,
            'creators': creators, 'doi_group_id': doi_group_id,
        })
        return result.get('doi_url', str(result))
