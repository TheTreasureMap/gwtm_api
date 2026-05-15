import datetime
import healpy as hp
import tempfile

from .core import apimodels
from .core.tmcache import TMCache
from .core import util
from .core import _client_factory as transport


class Alert(apimodels._Table):
    id: int = None
    graceid: str = None
    alternateid: str = None
    role: str = None
    timesent: datetime.datetime = None
    time_of_signal: datetime.datetime = None
    packet_type: int = None
    alert_type: str = None
    detectors: str = None
    description: str = None
    far: float = None
    skymap_fits_url: str = None
    distance: float = None
    distance_error: float = None
    prob_bns: float = None
    prob_nsbh: float = None
    prob_gap: float = None
    prob_bbh: float = None
    prob_terrestrial: float = None
    prob_hasns: float = None
    prob_hasremenant: float = None
    datecreated: datetime.datetime = None
    group: float = None
    centralfreq: float = None
    duration: float = None
    avgra: float = None
    avgdec: float = None
    observing_run: str = None
    pipeline: str = None
    search: str = None
    gcn_notice_id: int = None
    ivorn: str = None
    ext_coinc_observatory: str = None
    ext_coinc_search: str = None
    time_difference: float = None
    time_coincidence_far: float = None
    time_sky_position_coincidence_far: float = None
    area_90: float = None
    area_50: float = None

    def __init__(self,
            id: int = None,
            graceid: str = None,
            alternateid: str = None,
            role: str = None,
            timesent: datetime.datetime = None,
            time_of_signal: datetime.datetime = None,
            packet_type: int = None,
            alert_type: str = None,
            detectors: str = None,
            description: str = None,
            far: float = None,
            skymap_fits_url: str = None,
            distance: float = None,
            distance_error: float = None,
            prob_bns: float = None,
            prob_nsbh: float = None,
            prob_gap: float = None,
            prob_bbh: float = None,
            prob_terrestrial: float = None,
            prob_hasns: float = None,
            prob_hasremenant: float = None,
            datecreated: datetime.datetime = None,
            group: float = None,
            centralfreq: float = None,
            duration: float = None,
            avgra: float = None,
            avgdec: float = None,
            observing_run: str = None,
            pipeline: str = None,
            search: str = None,
            gcn_notice_id: int = None,
            ivorn: str = None,
            ext_coinc_observatory: str = None,
            ext_coinc_search: str = None,
            time_difference: float = None,
            time_coincidence_far: float = None,
            time_sky_position_coincidence_far: float = None,
            area_90: float = None,
            area_50: float = None,
            kwdict: dict = None
        ):
        selfdict = kwdict if kwdict is not None else util.non_none_locals(locals=locals())
        super().__init__(payload=selfdict)

    @staticmethod
    def get(id: int = None, graceid: str = None, api_token: str = None) -> "Alert":
        alerts = Alert.get_all(id=id, graceid=graceid, api_token=api_token)
        if alerts:
            return alerts[0]
        raise Exception(f"No alert found for graceid={graceid}, id={id}")

    @staticmethod
    def get_all(id: int = None, graceid: str = None, api_token: str = None):
        if api_token:
            transport.configure(api_token=api_token)
        result = transport.get('/query_alerts', params={'graceid': graceid})
        if not isinstance(result, list):
            raise Exception("Error in Alert.get_all(): unexpected response from server")
        return [Alert(kwdict=a) for a in result]

    @staticmethod
    def fetch_contours(id: int = None, graceid: str = None,
                       cache=False, api_token: str = None):
        if api_token:
            transport.configure(api_token=api_token)
        request_json = None
        if cache:
            cache_obj = TMCache(filename=f"{graceid}_gw_contour.json", cache_type="json")
            request_json = cache_obj.get()

        if request_json is None:
            request_json = transport.get('/gw_contour', params={'graceid': graceid})

        if cache:
            cache_obj.put(payload=request_json)

        contour_polygons = []
        for contour in request_json['features']:
            contour_polygons.extend(contour['geometry']['coordinates'])
        return contour_polygons

    @staticmethod
    def fetch_skymap(id: int = None, graceid: str = None,
                     cache=False, api_token: str = None):
        if api_token:
            transport.configure(api_token=api_token)
        request_map = None
        if cache:
            cache_obj = TMCache(filename=f"{graceid}_gw_skymap.fits", cache_type="fits")
            request_map = cache_obj.get()

        if request_map is None:
            response = transport.get_raw('/gw_skymap', params={'graceid': graceid})
            if response.status_code != 200:
                raise Exception(f"Error in Alert.fetch_skymap(): status {response.status_code}")
            with tempfile.NamedTemporaryFile(suffix=".fits") as tmp:
                tmp.write(response.content)
                tmp.flush()
                request_map = hp.read_map(tmp.name)

        if cache:
            cache_obj.put(payload=request_map)
        return request_map
