import datetime
import json
import healpy as hp
import tempfile

from .core import baseapi
from .core import apimodels
from .core.tmcache import TMCache
from .core import util

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
    description: float = None
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
    avgdec : float = None
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
            description: float = None,
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
            avgdec : float = None,
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

        if kwdict is not None:
            selfdict = kwdict
        else:
            selfdict = util.non_none_locals(locals=locals())

        super().__init__(payload=selfdict)

    @staticmethod
    def get(api_token: str, id: int = None, graceid: str = None, urlencode=False):

        get_dict = util.non_none_locals(locals=locals())

        r_json = {
            "d_json":get_dict
        }

        api = baseapi.api(target="query_alerts")
        req = api._get(r_json=r_json, urlencode=urlencode)

        if req.status_code == 200:
            request_json = json.loads(req.text)
            for i in request_json:
                if isinstance(i, str):
                    alert_json = json.loads(i)
                else:
                    alert_json = i
                #only return the first since it is the most recent
                return Alert(kwdict=alert_json)
        else:
            raise Exception(f"Error in Alert.get(). Request: {req.text[0:1000]}")


    @staticmethod
    def get_all(api_token: str, id: int = None, graceid: str = None, urlencode=False):

        get_dict = util.non_none_locals(locals=locals())

        r_json = {
            "d_json":get_dict
        }

        api = baseapi.api(target="query_alerts")
        req = api._get(r_json=r_json, urlencode=urlencode)

        ret = []
        if req.status_code == 200:
            request_json = json.loads(req.text)
            for i in request_json:
                if isinstance(i, str):
                    alert_json = json.loads(i)
                else:
                    alert_json = i
                ret.append(Alert(kwdict=alert_json))
        else:
            raise Exception(f"Error in Alert.get(). Request: {req.text[0:1000]}")

        return ret


    @staticmethod
    def fetch_contours(api_token: str, id: int = None, graceid: str = None, urlencode=False, cache=False):

        get_dict = util.non_none_locals(locals=locals())

        r_json = {
            "d_json":get_dict
        }

        request_json = None
        if cache:
            cache_name = f"{graceid}_gw_contour.json"
            contour_cache = TMCache(filename=cache_name, cache_type="json")
            request_json = contour_cache.get()

        if request_json is None:
            api = baseapi.api(target="gw_contour")
            req = api._get(r_json=r_json, urlencode=urlencode)

            if req.status_code == 200:
                request_json = json.loads(req.text)
            else:
                raise Exception(f"Error in Alert.fetch_contours(). Request: {req.text[0:1000]}")

        if cache:
            contour_cache.put(payload=request_json)

        contour_polygons = []
        for contour in request_json['features']:
            contour_polygons.extend(contour['geometry']['coordinates'])
        return contour_polygons


    @staticmethod
    def fetch_skymap(api_token: str, id: int = None, graceid: str = None, urlencode=False, cache=False):

        get_dict = util.non_none_locals(locals=locals())

        r_json = {
            "d_json":get_dict
        }

        request_map = None
        if cache:
            cache_name = f"{graceid}_gw_skymap.fits"
            skymap_cache = TMCache(filename=cache_name, cache_type="fits")
            request_map = skymap_cache.get()

        if request_map is None:
            api = baseapi.api(target="gw_skymap")
            req = api._get(r_json=r_json, urlencode=urlencode)

            if req.status_code == 200:
                with tempfile.NamedTemporaryFile() as _tmp_file:
                    _tmp_file.write(req.content)
                    request_map = hp.read_map(_tmp_file.name)
            else:
                raise Exception(f"Error in Alert.fetch_skymap(). Request: {req.text[0:1000]}")
        if cache:
            skymap_cache.put(payload=request_map)

        return request_map