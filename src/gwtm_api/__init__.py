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

GWTM_POST_CANDIDATE_KEYS = [
    'api_token', 'graceid', 'candidate', 'candidates'
]

GWTM_GET_CANDIDATE_KEYS = [
    'api_token', 'graceid', 'id', 'ids', 'submitted_date_after', 
    'submitted_date_before', 'discovery_date_after', 'discovery_date_before', 
    'userid', 'discovery_magnitude_gt', 'discovery_magnitude_lt', 
    'associated_galaxy_name', 'associated_galaxy_redshift_gt', 'associated_galaxy_redshift_lt',
    'associated_galaxy_distance_gt', 'associated_galaxy_distance_lt'
]

GWTM_GET_INSTRUMENT_KEYS = [
    'api_token', 'id', 'ids', 'name', 'names', 'type'
]

GWTM_GET_ALERT_KEYS = [
    'api_token', 'id', 'graceid'
]

from .pointing import Pointing as Pointing  # noqa: E402
from.candidate import Candidate as Candidate  #noqa: E402
from .instrument import Instrument as Instrument  # noqa: E402
from .alert import Alert as Alert  # noqa: E402
from .event_tools import plot_coverage, calculate_coverage, renormalize_skymap  # noqa: E402, F401