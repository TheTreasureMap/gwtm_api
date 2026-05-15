"""Unit tests for configure() and the list encoding utility."""
from unittest.mock import patch, MagicMock
import sys
sys.path.insert(0, 'src')

import gwtm_api
import gwtm_api.core._client_factory as transport
from gwtm_api.core.util import _encode_list_param


class TestEncodeListParam:

    def test_list_becomes_json_string(self):
        assert _encode_list_param(['ZTF', 'DECam']) == '["ZTF", "DECam"]'

    def test_int_list_encoded(self):
        assert _encode_list_param([1, 2, 3]) == '[1, 2, 3]'

    def test_none_returns_none(self):
        assert _encode_list_param(None) is None

    def test_string_passed_through(self):
        assert _encode_list_param('ZTF') == 'ZTF'

    def test_single_item_list(self):
        assert _encode_list_param(['ZTF']) == '["ZTF"]'


class TestConfigure:

    def test_sets_token(self):
        gwtm_api.configure(api_token='my_token')
        assert transport._token == 'my_token'

    def test_default_base_url(self):
        gwtm_api.configure(api_token='tok')
        assert transport._base_url == 'https://treasuremap.space/api/v1'

    def test_custom_base_url(self):
        gwtm_api.configure(api_token='tok', base_url='https://dev.treasuremap.space/api/v1')
        assert transport._base_url == 'https://dev.treasuremap.space/api/v1'

    def test_trailing_slash_stripped(self):
        gwtm_api.configure(api_token='tok', base_url='https://treasuremap.space/api/v1/')
        assert transport._base_url == 'https://treasuremap.space/api/v1'

    def test_reconfigure_updates_token(self):
        gwtm_api.configure(api_token='first')
        gwtm_api.configure(api_token='second')
        assert transport._token == 'second'

    def test_headers_include_api_token(self):
        gwtm_api.configure(api_token='secret')
        assert transport._headers() == {'api_token': 'secret'}

    def test_get_passes_auth_header(self):
        gwtm_api.configure(api_token='tok123')
        mock_resp = MagicMock()
        mock_resp.json.return_value = []
        mock_resp.raise_for_status.return_value = None
        with patch('httpx.get', return_value=mock_resp) as mock:
            transport.get('/pointings')
        assert mock.call_args.kwargs['headers']['api_token'] == 'tok123'

    def test_get_strips_none_params(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = []
        mock_resp.raise_for_status.return_value = None
        with patch('httpx.get', return_value=mock_resp) as mock:
            transport.get('/pointings', params={'graceid': 'S190425z', 'status': None})
        sent_params = mock.call_args.kwargs['params']
        assert 'status' not in sent_params
        assert sent_params['graceid'] == 'S190425z'
