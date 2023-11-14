GWTM_POST_POINTING_KEYS = [
    'graceid', 'api_token', 'pointings', 'request_doi', 
    'doi_url', 'creators', 'doi_group_id'
]

GWTM_GET_POINTING_KEYS = [
    'api_token', 'graceid', 'graceids', 'instrument', 'instruments',
    'id', 'ids', 'status', 'statuses', 'completed_after', 
    'completed_before', 'planed_after', 'planned_before', 
    'user', 'users', 'band', 'bands', 'central_wave', 'bandwidth',
    'wavelength_regime', 'wavelength_unit','energy_regime', 
    'energy_unit', 'frequency_regime', 'frequency_unit'
]

GWTM_GET_INSTRUMENT_KEYS = [
    'api_token', 'id', 'ids', 'name', 'names', 'type'
]

GWTM_GET_ALERT_KEYS = [
    'api_token', 'id', 'graceid'
]

from .pointing import Pointing as Pointing
from .instrument import Instrument as Instrument
from .alert import Alert as Alert
from .event_tools import plot_coverage