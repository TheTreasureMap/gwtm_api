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

GWTM_INSTRUMENT_KEYS = []

from .pointing import Pointing as Pointing