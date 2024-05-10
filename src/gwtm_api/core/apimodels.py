import datetime
from dateutil.parser import parse as date_parse

from .enums import (
    pointing_status, depth_unit, bandpass, wavelength_units, 
    energy_units, frequency_units, instrument_type, ENUM_TYPES
)

class _TableKeysField():
    def __init__(self, name, ftype, required=False, regex=None):
        self.name = name
        self.type = ftype
        self.required = required
        self.regex = None


class _TableKeys():
    Models = [
        {
            "clsname":"Pointing",
            'fields':[
                _TableKeysField('id', int, False),
                _TableKeysField('position', str, False),
                _TableKeysField('ra', float, False),
                _TableKeysField('dec', float, False),
                _TableKeysField('instrumentid', int, True),
                _TableKeysField('time', datetime.datetime, True),
                _TableKeysField('status', pointing_status, True),
                _TableKeysField('depth', float, True),
                _TableKeysField('depth_unit', depth_unit, True), 
                _TableKeysField('band', bandpass, False),
                _TableKeysField('wavelength_regime', list, False),
                _TableKeysField('wavelength_unit', wavelength_units, False),
                _TableKeysField('energy_regime', list, False),
                _TableKeysField('energy_unit', energy_units, False),
                _TableKeysField('frequency_regime', list, False),
                _TableKeysField('frequency_unit', frequency_units, False),
                _TableKeysField('pos_angle', float, False),
                _TableKeysField('depth_err', float, False),
                _TableKeysField('doi_url', str, False),
                _TableKeysField('doi_id', int, False),
                _TableKeysField('submitterid', int, False),
                _TableKeysField('central_wave', float, False),
                _TableKeysField('bandwidth', float, False)
            ]
        },{
            "clsname":"Candidate",
            'fields':[
                _TableKeysField('id', int, False),
                _TableKeysField('datecreated', datetime.datetime, False),
                _TableKeysField('graceid', str, False),
                _TableKeysField('candidate_name', str, True),
                _TableKeysField('tns_name', str, False),
                _TableKeysField('tns_url', str, False),
                _TableKeysField('position', str, False),
                _TableKeysField('ra', float, False),
                _TableKeysField('dec', float, False),
                _TableKeysField('discovery_date', datetime.datetime, True),
                _TableKeysField('discovery_magnitude', float, True),
                _TableKeysField('magnitude_central_wave', float, False),
                _TableKeysField('magnitude_bandwidth', float, False),
                _TableKeysField('magnitude_bandpass', bandpass, False),
                _TableKeysField('magnitude_unit', depth_unit, True), 
                _TableKeysField('wavelength_regime', list, False),
                _TableKeysField('wavelength_unit', wavelength_units, False),
                _TableKeysField('energy_regime', list, False),
                _TableKeysField('energy_unit', energy_units, False),
                _TableKeysField('frequency_regime', list, False),
                _TableKeysField('frequency_unit', frequency_units, False),
                _TableKeysField('associated_galaxy', str, False),
                _TableKeysField('associated_galaxy_redshift', float, False),
                _TableKeysField('associated_galaxy_distance', float, False),
                _TableKeysField('submitterid', int, False)
            ]
        },
        {
            "clsname":"Instrument",
            "fields":[
                _TableKeysField('id', int, False),
                _TableKeysField('instrument_name', str, False),
                _TableKeysField("nickname", str, False),
                _TableKeysField("instrument_type", instrument_type, False),
                _TableKeysField("datecreated", datetime.datetime, False),
                _TableKeysField("submitterid", int, False)
            ]
        },
        {
            "clsname":"Footprint",
            "fields":[
                _TableKeysField('id', int, False),
                _TableKeysField("instrumentid", int, False),
                _TableKeysField("footprint", str, False)
            ]
        },
        {
            "clsname":"Alert",
            "fields":[
                _TableKeysField("id", int),
                _TableKeysField("graceid", str),
                _TableKeysField("alternateid", str),
                _TableKeysField("role", str),
                _TableKeysField("timesent", datetime.datetime),
                _TableKeysField("time_of_signal", datetime.datetime),
                _TableKeysField("packet_type", int),
                _TableKeysField("alert_type", str),
                _TableKeysField("detectors", str),
                _TableKeysField("far", float),
                _TableKeysField("skymap_fits_url", str),
                _TableKeysField("distance", float),
                _TableKeysField("distance_error", float),
                _TableKeysField("prob_bns", float),
                _TableKeysField("prob_nsbh", float),
                _TableKeysField("prob_gap", float),
                _TableKeysField("prob_bbh", float),
                _TableKeysField("prob_terrestrial", float),
                _TableKeysField("prob_hasns", float),
                _TableKeysField("prob_hasremenant", float),
                _TableKeysField("datecreated", datetime.datetime),
                _TableKeysField("group", str),
                _TableKeysField("centralfreq", float),
                _TableKeysField("duration", float),
                _TableKeysField("avgra", float),
                _TableKeysField("avgdec", float),
                _TableKeysField("observing_run", str),
                _TableKeysField("pipeline", str),
                _TableKeysField("search", str),
                _TableKeysField("gcn_notice_id", int),
                _TableKeysField("ext_coinc_observatory", str),
                _TableKeysField("ext_coinc_search", str),
                _TableKeysField("time_difference", float),
                _TableKeysField("time_coincidence_far", float),
                _TableKeysField("time_sky_position_coincidence_far", float),
                _TableKeysField("area_90", float),
                _TableKeysField("area_50", float),
            ]
        }
    ]


class _TableValidation():
    def __init__(self):
        self.valid = False
        self.errors = []
        self.valid_inst = {}
 
    def validate_on_init(self, payload, instance):
        self.validate_payload(payload, instance) 
 
    def validate_payload(self, payload, instance):
        clsname = instance.__class__.__name__
        modelfields = [x['fields'] for x in _TableKeys.Models if x['clsname'] == clsname][0]
        modelkeys = [x.name for x in modelfields]
        payloadkeys = payload.keys()
        requiredfields = [x for x in modelfields if x.required]
        missingfields = [rf for rf in requiredfields if rf.name not in payloadkeys]
 
        for mf in missingfields:
            self.errors.append('Required Field: {}\n '.format(mf.name))
 
        for key, value in payload.items():
            if str(key).lower() in modelkeys:
                mf = [x for x in modelfields if x.name == str(key).lower()][0]
                try:
                    if isinstance(value, mf.type):
                        self.valid_inst[key] = value

                    elif mf.type == datetime.datetime:
                        dateval = date_parse(value)
                        self.valid_inst[key] = dateval

                    elif (mf.type == float or mf.type == int) and (value is None or value == ''):
                        self.valid_inst[key] = None

                    elif mf.type in ENUM_TYPES:
                        if isinstance(value, str) and (value is not None and value != ""):
                            eval = mf.type[value].name
                            self.valid_inst[key] = eval
                        if isinstance(value, int):
                            eval = mf.type(value).name
                            self.valid_inst[key] = eval
                    else:
                        _ = mf.type(value)
                        self.valid_inst[key] = mf.type(value)
                except:  # noqa: E722
                    self.errors.append('Field: {}. Value: {}. Value Type: {}. Intended Type: {}'.format(key, value, type(value), mf.type))
                 
        self.valid = len(self.errors) == 0
 

class _Table(): 
    _errors = []
    _verbose = True
 
    def __init__(self, payload={}):
        v = _TableValidation()
        v.validate_on_init(payload, self)
        if v.valid:
            self.__dict__.update(v.valid_inst)
        elif self._verbose:
            for e in v.errors:
                assert False, e
        else:
            self._errors = v.errors

    def dump(self):
        for key, value in self.__dict__.items():
            print('{}: {}'.format(key, value))
        print()