import datetime
from enum import IntEnum

DATETIME_FORMAT1 = "%Y-%m-%dT%H:%M:%S.%f"
DATETIME_FORMAT2 = "%Y-%m-%dT%H:%M:%S"

class depth_unit(IntEnum):
    ab_mag = 1
    vega_mag = 2
    flux_erg = 3
    flux_jy = 4

    def __str__(self):
        split_name = str(self.name).split('_')
        return str.upper(split_name[0]) + ' ' + split_name[1]


class pointing_status(IntEnum):
    planned = 1
    completed = 2
    cancelled = 3


class instrument_type(IntEnum):
    photometric = 1
    spectroscopic = 2


class bandpass(IntEnum):
    U = 1
    B = 2
    V = 3
    R = 4
    I = 5
    J = 6
    H = 7
    K = 8
    u = 9
    g = 10
    r = 11
    i = 12
    z = 13
    UVW1 = 14
    UVW2 = 15
    UVM2 = 16
    XRT = 17
    clear = 18
    open = 19
    UHF = 20
    VHF = 21
    L = 22
    S = 23
    C = 24
    X = 25
    other = 26
    TESS = 27
    BAT = 28
    HESS = 29
    WISEL = 30
    q = 31


class wavelength_units(IntEnum):
    nanometer = 1
    angstrom = 2
    micron = 3

    @staticmethod
    def get_scale(unit):
        if unit == wavelength_units.nanometer:
            return 10.0
        if unit == wavelength_units.angstrom:
            return 1.0
        if unit == wavelength_units.micron:
            return 10000.0


class energy_units(IntEnum):
    eV = 1
    keV = 2
    MeV = 3
    GeV = 4
    TeV = 5

    @staticmethod
    def get_scale(unit):
        if unit == energy_units.eV:
            return 1.0
        if unit == energy_units.keV:
            return 1000.0
        if unit == energy_units.MeV:
            return 1000000.0
        if unit == energy_units.GeV:
            return 1000000000.0
        if unit == energy_units.TeV:
            return 1000000000000.0


class frequency_units(IntEnum):
    Hz = 1
    kHz = 2
    GHz = 3
    MHz = 4
    THz = 5

    @staticmethod
    def get_scale(unit):
        if unit == frequency_units.Hz:
            return 1.0
        if unit == frequency_units.kHz:
            return 1000.0
        if unit == frequency_units.MHz:
            return 1000000.0
        if unit == frequency_units.GHz:
            return 1000000000.0
        if unit == frequency_units.THz:
            return 1000000000000.0


ENUM_TYPES = [
    depth_unit, 
    pointing_status,
    instrument_type,
    bandpass,
    wavelength_units,
    energy_units,
    frequency_units
]

class gw_galaxy_score_type(IntEnum):
    default = 1


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
                _TableKeysField('energy_uni', energy_units, False),
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
                        try:
                            dateval = datetime.datetime.strptime(value, DATETIME_FORMAT1)
                            self.valid_inst[key] = dateval
                        except:
                            dateval = datetime.datetime.strptime(value, DATETIME_FORMAT2)
                            self.valid_inst[key] = dateval

                    elif (mf.type == float or mf.type == int) and (value == None or value == ''):
                        self.valid_inst[key] = None

                    elif mf.type in ENUM_TYPES:
                        if isinstance(value, str) and (value != None and value != ""):
                            eval = mf.type[value].name
                            self.valid_inst[key] = eval
                        if isinstance(value, int):
                            eval = mf.type(value).name
                            self.valid_inst[key] = eval
                            
                    else:
                        tmpval = mf.type(value)
                        self.valid_inst[key] = mf.type(value)
                except:
                    print(payload)
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