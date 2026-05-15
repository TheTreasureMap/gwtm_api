"""Unit tests for Alert wrapper — no live server required."""
from unittest.mock import patch, MagicMock

import pytest

import sys
sys.path.insert(0, 'src')

import gwtm_api

ALERT_FIXTURE = {
    'id': 1, 'graceid': 'S190425z', 'role': 'observation',
    'alert_type': 'Initial', 'far': 4.5e-13,
    'timesent': '2019-04-25T08:18:05',
}

GET_PATH = 'gwtm_api.core._client_factory.get'


class TestAlertGet:

    def test_get_returns_first_alert(self):
        with patch(GET_PATH, return_value=[ALERT_FIXTURE, {**ALERT_FIXTURE, 'id': 2}]):
            result = gwtm_api.Alert.get(graceid='S190425z')
        assert isinstance(result, gwtm_api.Alert)
        assert result.id == 1

    def test_get_all_returns_list(self):
        with patch(GET_PATH, return_value=[ALERT_FIXTURE, {**ALERT_FIXTURE, 'id': 2}]):
            result = gwtm_api.Alert.get_all(graceid='S190425z')
        assert len(result) == 2
        assert all(isinstance(a, gwtm_api.Alert) for a in result)

    def test_alert_fields_populated(self):
        with patch(GET_PATH, return_value=[ALERT_FIXTURE]):
            result = gwtm_api.Alert.get_all(graceid='S190425z')
        assert result[0].graceid == 'S190425z'
        assert result[0].far == pytest.approx(4.5e-13)

    def test_auth_header_sent_correctly(self):
        gwtm_api.configure(api_token='my_token')
        mock_resp = MagicMock()
        mock_resp.json.return_value = []
        mock_resp.raise_for_status.return_value = None
        with patch('httpx.get', return_value=mock_resp) as mock:
            gwtm_api.Alert.get_all(graceid='S190425z')
        assert mock.call_args.kwargs['headers']['api_token'] == 'my_token'

    def test_get_raises_when_no_alerts(self):
        with patch(GET_PATH, return_value=[]):
            with pytest.raises(Exception, match="No alert found"):
                gwtm_api.Alert.get(graceid='NONEXISTENT')

    def test_correct_endpoint_called(self):
        with patch(GET_PATH, return_value=[]) as mock:
            try:
                gwtm_api.Alert.get(graceid='S190425z')
            except Exception:
                pass
        assert mock.call_args.args[0] == '/query_alerts'

    def test_id_param_not_sent_to_server(self):
        """API has no id filter on query_alerts — must not be forwarded."""
        with patch(GET_PATH, return_value=[ALERT_FIXTURE]) as mock:
            gwtm_api.Alert.get_all(id=99, graceid='S190425z')
        assert 'id' not in mock.call_args.kwargs['params']


class TestAlertFetchContours:

    CONTOUR_FIXTURE = {
        'type': 'FeatureCollection',
        'features': [
            {'geometry': {'coordinates': [[[10.0, -20.0], [11.0, -21.0]]]}},
        ]
    }

    def test_calls_correct_endpoint(self):
        with patch(GET_PATH, return_value=self.CONTOUR_FIXTURE) as mock:
            gwtm_api.Alert.fetch_contours(graceid='S190425z')
        assert mock.call_args.args[0] == '/gw_contour'

    def test_graceid_sent_as_param(self):
        with patch(GET_PATH, return_value=self.CONTOUR_FIXTURE) as mock:
            gwtm_api.Alert.fetch_contours(graceid='S190425z')
        assert mock.call_args.kwargs['params']['graceid'] == 'S190425z'

    def test_returns_polygon_list(self):
        with patch(GET_PATH, return_value=self.CONTOUR_FIXTURE):
            result = gwtm_api.Alert.fetch_contours(graceid='S190425z')
        assert isinstance(result, list)
        assert result[0] == [[10.0, -20.0], [11.0, -21.0]]

    def test_cache_hit_skips_api_call(self):
        from unittest.mock import MagicMock
        from gwtm_api.core.tmcache import TMCache
        with patch.object(TMCache, 'get', return_value=self.CONTOUR_FIXTURE), \
             patch(GET_PATH) as mock_get:
            gwtm_api.Alert.fetch_contours(graceid='S190425z', cache=True)
        mock_get.assert_not_called()


class TestAlertFetchSkymap:

    def test_calls_correct_endpoint(self):
        from unittest.mock import MagicMock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b''
        with patch('gwtm_api.core._client_factory.get_raw', return_value=mock_response) as mock, \
             patch('healpy.read_map', return_value=[0.1, 0.2]):
            gwtm_api.Alert.fetch_skymap(graceid='S190425z')
        assert mock.call_args.args[0] == '/gw_skymap'

    def test_graceid_sent_as_param(self):
        from unittest.mock import MagicMock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b''
        with patch('gwtm_api.core._client_factory.get_raw', return_value=mock_response) as mock, \
             patch('healpy.read_map', return_value=[0.1, 0.2]):
            gwtm_api.Alert.fetch_skymap(graceid='S190425z')
        assert mock.call_args.kwargs['params']['graceid'] == 'S190425z'

    def test_raises_on_non_200(self):
        from unittest.mock import MagicMock
        mock_response = MagicMock()
        mock_response.status_code = 404
        with patch('gwtm_api.core._client_factory.get_raw', return_value=mock_response):
            with pytest.raises(Exception, match="status 404"):
                gwtm_api.Alert.fetch_skymap(graceid='NONEXISTENT')
