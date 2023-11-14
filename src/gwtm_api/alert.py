import json
import numpy as np
import healpy as hp

from .core import baseapi
from .core import apimodels
from .core import util 
from . import GWTM_GET_ALERT_KEYS

class Alert(apimodels._Table):
    id = None
    graceid = None
    alternateid = None
    role = None
    timesent = None
    time_of_signal = None
    packet_type = None
    alert_type = None
    detectors = None
    description = None
    far = None
    skymap_fits_url = None
    distance = None
    distance_error = None
    prob_bns = None
    prob_nsbh = None
    prob_gap = None
    prob_bbh = None
    prob_terrestrial = None
    prob_hasns = None
    prob_hasremenant = None
    datecreated = None
    group = None
    centralfreq = None
    duration = None
    avgra = None
    avgdec = None
    observing_run = None
    pipeline = None
    search = None
    gcn_notice_id = None
    ivorn = None
    ext_coinc_observatory = None
    ext_coinc_search = None
    time_difference = None
    time_coincidence_far = None
    time_sky_position_coincidence_far = None
    area_90 = None
    area_50 = None

    def __init__(self, kwdict=None, **kwargs):

        if kwdict is not None:
            selfdict = kwdict
        else:
            selfdict = kwargs

        super().__init__(payload=selfdict)


    def validate(self):
        pass


    @staticmethod
    def get(urlencode=False, **kwargs):
        get_keys = list(GWTM_GET_ALERT_KEYS)
        get_dict = {}

        get_dict.update(
            (str(key).lower(), value) for key, value in kwargs.items() if str(key).lower() in get_keys
        )

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
    def fetch_contours(urlencode=False, **kwargs):
        get_keys = list(GWTM_GET_ALERT_KEYS)
        get_dict = {}

        get_dict.update(
            (str(key).lower(), value) for key, value in kwargs.items() if str(key).lower() in get_keys
        )

        r_json = {
            "d_json":get_dict
        }

        api = baseapi.api(target="gw_contour")
        req = api._get(r_json=r_json, urlencode=urlencode)

        ret = []
        if req.status_code == 200:
            request_json = json.loads(req.text)
        else:
            raise Exception(f"Error in Alert.fetch_contours(). Request: {req.text[0:1000]}")

        return request_json
