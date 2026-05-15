"""Unit tests for Instrument and Footprint wrappers — no live server required."""
from unittest.mock import patch

import sys
sys.path.insert(0, 'src')

import gwtm_api

INSTRUMENT_FIXTURE = {'id': 10, 'instrument_name': 'ZTF', 'instrument_type': 1}
FOOTPRINT_FIXTURE = {'id': 1, 'instrumentid': 10, 'footprint': 'POLYGON (1.0 2.0,3.0 4.0,5.0 6.0,1.0 2.0)'}

GET_PATH = 'gwtm_api.core._client_factory.get'


class TestInstrumentGet:

    def test_returns_list_of_instruments(self):
        with patch(GET_PATH, return_value=[INSTRUMENT_FIXTURE]):
            result = gwtm_api.Instrument.get()
        assert len(result) == 1
        assert isinstance(result[0], gwtm_api.Instrument)
        assert result[0].instrument_name == 'ZTF'

    def test_names_list_is_json_encoded(self):
        with patch(GET_PATH, return_value=[]) as mock:
            gwtm_api.Instrument.get(names=['ZTF', 'DECam'])
        assert mock.call_args.kwargs['params']['names'] == '["ZTF", "DECam"]'

    def test_ids_list_is_json_encoded(self):
        with patch(GET_PATH, return_value=[]) as mock:
            gwtm_api.Instrument.get(ids=[10, 38])
        assert mock.call_args.kwargs['params']['ids'] == '[10, 38]'

    def test_include_footprint_fetches_footprints(self):
        with patch(GET_PATH, side_effect=[[INSTRUMENT_FIXTURE], [FOOTPRINT_FIXTURE]]):
            result = gwtm_api.Instrument.get(include_footprint=True)
        assert result[0].footprint is not None
        assert len(result[0].footprint) == 1

    def test_auth_header_sent_correctly(self):
        from unittest.mock import MagicMock
        gwtm_api.configure(api_token='my_token')
        mock_resp = MagicMock()
        mock_resp.json.return_value = []
        mock_resp.raise_for_status.return_value = None
        with patch('httpx.get', return_value=mock_resp) as mock:
            gwtm_api.Instrument.get()
        assert mock.call_args.kwargs['headers']['api_token'] == 'my_token'

    def test_approximate_footprint_uses_substitution(self):
        from gwtm_api.instrument import APPROXIMATION_DICT
        ztf_instrument = {**INSTRUMENT_FIXTURE, 'id': 47}
        ztf_footprint = {**FOOTPRINT_FIXTURE, 'instrumentid': 47}

        calls = []
        def fake_get(path, params=None):
            calls.append((path, params))
            if path == '/instruments':
                return [ztf_instrument]
            if path == '/footprints':
                return [ztf_footprint]
            return []

        with patch(GET_PATH, side_effect=fake_get):
            gwtm_api.Instrument.get(include_footprint=True)

        footprint_call = next(c for c in calls if c[0] == '/footprints')
        assert footprint_call[1]['id'] == APPROXIMATION_DICT[47]

    def test_correct_endpoint_called(self):
        with patch(GET_PATH, return_value=[]) as mock:
            gwtm_api.Instrument.get()
        assert mock.call_args.args[0] == '/instruments'

    def test_type_enum_serialised_as_int(self):
        from gwtm_api.core.apimodels import instrument_type
        with patch(GET_PATH, return_value=[]) as mock:
            gwtm_api.Instrument.get(type=instrument_type.photometric)
        assert mock.call_args.kwargs['params']['type'] == 1

    def test_type_string_serialised_as_int(self):
        with patch(GET_PATH, return_value=[]) as mock:
            gwtm_api.Instrument.get(type='photometric')
        assert mock.call_args.kwargs['params']['type'] == 1
