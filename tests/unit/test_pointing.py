"""Unit tests for Pointing wrapper — no live server required."""
import datetime
from unittest.mock import patch, MagicMock

import pytest

import sys
sys.path.insert(0, 'src')

import gwtm_api

POINTING_FIXTURE = {
    'id': 42, 'position': 'POINT (10.0 -20.0)', 'instrumentid': 10,
    'time': '2025-01-01T00:00:00', 'status': 'completed',
    'depth': 18.5, 'depth_unit': 'ab_mag', 'band': 'r',
    'submitterid': 1,
}

GET_PATH = 'gwtm_api.core._client_factory.get'
POST_PATH = 'gwtm_api.core._client_factory.post'


class TestPointingGet:

    def test_returns_list_of_pointing_objects(self):
        with patch(GET_PATH, return_value=[POINTING_FIXTURE]):
            result = gwtm_api.Pointing.get(graceid='S190425z')
        assert len(result) == 1
        assert isinstance(result[0], gwtm_api.Pointing)
        assert result[0].id == 42
        assert result[0].ra == 10.0
        assert result[0].dec == -20.0

    def test_list_params_are_json_encoded(self):
        with patch(GET_PATH, return_value=[]) as mock:
            gwtm_api.Pointing.get(instruments=['ZTF', 'DECam'])
        params = mock.call_args.kwargs['params']
        assert params['instruments'] == '["ZTF", "DECam"]'

    def test_ids_list_is_json_encoded(self):
        with patch(GET_PATH, return_value=[]) as mock:
            gwtm_api.Pointing.get(ids=[1, 2, 3])
        assert mock.call_args.kwargs['params']['ids'] == '[1, 2, 3]'

    def test_enum_status_converted_to_string(self):
        import gwtm_api.core.apimodels as m
        with patch(GET_PATH, return_value=[]) as mock:
            gwtm_api.Pointing.get(status=m.pointing_status.completed)
        assert mock.call_args.kwargs['params']['status'] == 'completed'

    def test_urlencode_param_silently_ignored(self):
        with patch(GET_PATH, return_value=[POINTING_FIXTURE]):
            result = gwtm_api.Pointing.get(graceid='S190425z', urlencode=True)
        assert len(result) == 1

    def test_auth_header_sent_correctly(self):
        gwtm_api.configure(api_token='my_secret_token')
        mock_resp = MagicMock()
        mock_resp.json.return_value = []
        mock_resp.raise_for_status.return_value = None
        with patch('httpx.get', return_value=mock_resp) as mock:
            gwtm_api.Pointing.get()
        assert mock.call_args.kwargs['headers']['api_token'] == 'my_secret_token'
        assert 'Bearer' not in str(mock.call_args.kwargs['headers'])

    def test_none_params_not_sent(self):
        with patch(GET_PATH, return_value=[]) as mock:
            gwtm_api.Pointing.get(graceid='S190425z')
        # _clean() strips None values before httpx sees them; instruments was not passed
        params = mock.call_args.kwargs['params']
        assert params.get('instruments') is None

    def test_bands_list_of_enums_converted(self):
        import gwtm_api.core.apimodels as m
        with patch(GET_PATH, return_value=[]) as mock:
            gwtm_api.Pointing.get(bands=[m.bandpass.r, m.bandpass.g])
        assert mock.call_args.kwargs['params']['bands'] == '["r", "g"]'

    def test_correct_endpoint_called(self):
        with patch(GET_PATH, return_value=[]) as mock:
            gwtm_api.Pointing.get(graceid='S190425z')
        assert mock.call_args.args[0] == '/pointings'


class TestBackwardsCompat:

    def test_api_token_kwarg_configures_client(self):
        import gwtm_api.core._client_factory as t
        with patch(GET_PATH, return_value=[]):
            gwtm_api.Pointing.get(graceid='S190425z', api_token='legacy_token')
        assert t._token == 'legacy_token'

    def test_api_token_on_post_configures_client(self):
        import gwtm_api.core._client_factory as t
        with patch(POST_PATH, return_value={'pointing_ids': [42]}), \
             patch(GET_PATH, return_value=[POINTING_FIXTURE]):
            p = gwtm_api.Pointing(ra=10.0, dec=-20.0, instrumentid=10,
                                  time=datetime.datetime(2025, 1, 1),
                                  status='planned', depth=18.0,
                                  depth_unit='ab_mag', band='r')
            p.post(graceid='S190425z', api_token='legacy_token')
        assert t._token == 'legacy_token'


class TestPointingPost:

    def test_post_calls_add_endpoint(self):
        with patch(POST_PATH, return_value={'pointing_ids': [99]}), \
             patch(GET_PATH, return_value=[{**POINTING_FIXTURE, 'id': 99}]):
            p = gwtm_api.Pointing(ra=10.0, dec=-20.0, instrumentid=10,
                                  time=datetime.datetime(2025, 1, 1),
                                  status='planned', depth=18.0,
                                  depth_unit='ab_mag', band='r')
            p.post(graceid='S190425z')
        assert p.id == 99

    def test_post_correct_endpoint(self):
        with patch(POST_PATH, return_value={'pointing_ids': [42]}), \
             patch(GET_PATH, return_value=[POINTING_FIXTURE]) as mock_get:
            p = gwtm_api.Pointing(ra=10.0, dec=-20.0, instrumentid=10,
                                  time=datetime.datetime(2025, 1, 1),
                                  status='planned', depth=18.0,
                                  depth_unit='ab_mag', band='r')
            p.post(graceid='S190425z')
        assert mock_get.call_args.args[0] == '/pointings'
