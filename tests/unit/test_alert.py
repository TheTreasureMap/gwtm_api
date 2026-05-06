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
