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
PUT_PATH = 'gwtm_api.core._client_factory.put'
DELETE_PATH = 'gwtm_api.core._client_factory.delete'


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

    def test_doi_params_absent_when_not_provided(self):
        with patch(POST_PATH, return_value={'pointing_ids': [42]}) as mock_post, \
             patch(GET_PATH, return_value=[POINTING_FIXTURE]):
            p = gwtm_api.Pointing(ra=10.0, dec=-20.0, instrumentid=10,
                                  time=datetime.datetime(2025, 1, 1),
                                  status='planned', depth=18.0,
                                  depth_unit='ab_mag', band='r')
            p.post(graceid='S190425z')
        body = mock_post.call_args.kwargs['json']
        assert 'request_doi' not in body
        assert 'doi_url' not in body
        assert 'creators' not in body
        assert 'doi_group_id' not in body

    def test_doi_params_sent_when_provided(self):
        with patch(POST_PATH, return_value={'pointing_ids': [42]}) as mock_post, \
             patch(GET_PATH, return_value=[POINTING_FIXTURE]):
            p = gwtm_api.Pointing(ra=10.0, dec=-20.0, instrumentid=10,
                                  time=datetime.datetime(2025, 1, 1),
                                  status='planned', depth=18.0,
                                  depth_unit='ab_mag', band='r')
            p.post(graceid='S190425z', request_doi=True,
                   doi_url='https://doi.org/10.1234', doi_group_id=5)
        body = mock_post.call_args.kwargs['json']
        assert body['request_doi'] is True
        assert body['doi_url'] == 'https://doi.org/10.1234'
        assert body['doi_group_id'] == 5

    def test_central_wave_and_bandwidth_not_in_get_params(self):
        with patch(GET_PATH, return_value=[]) as mock:
            gwtm_api.Pointing.get(graceid='S190425z', central_wave=5000.0, bandwidth=100.0)
        params = mock.call_args.kwargs['params']
        assert 'central_wave' not in params
        assert 'bandwidth' not in params


class TestRequestDoi:

    def test_calls_correct_endpoint(self):
        with patch(POST_PATH, return_value={'doi_url': 'https://doi.org/10.1234'}) as mock:
            result = gwtm_api.Pointing.request_doi(graceid='S190425z')
        assert mock.call_args.args[0] == '/request_doi'

    def test_returns_doi_url(self):
        with patch(POST_PATH, return_value={'doi_url': 'https://doi.org/10.1234'}):
            result = gwtm_api.Pointing.request_doi(graceid='S190425z')
        assert result == 'https://doi.org/10.1234'

    def test_raises_without_graceid_id_or_ids(self):
        with pytest.raises(Exception, match="Must specify"):
            gwtm_api.Pointing.request_doi()

    def test_doi_group_id_sent_as_string(self):
        with patch(POST_PATH, return_value={'doi_url': 'https://doi.org/10.1234'}) as mock:
            gwtm_api.Pointing.request_doi(graceid='S190425z', doi_group_id='42')
        body = mock.call_args.kwargs['json']
        assert isinstance(body['doi_group_id'], str)


class TestPointingUpdate:

    def _make_pointing(self):
        with patch(GET_PATH, return_value=[POINTING_FIXTURE]):
            return gwtm_api.Pointing.get(id=42)[0]

    def test_update_calls_put_endpoint(self):
        p = self._make_pointing()
        with patch(PUT_PATH, return_value={'message': 'ok'}) as mock_put, \
             patch(GET_PATH, return_value=[POINTING_FIXTURE]):
            p.update(status='cancelled')
        assert mock_put.call_args.args[0] == '/pointings/42'

    def test_update_sends_only_provided_fields(self):
        p = self._make_pointing()
        with patch(PUT_PATH, return_value={'message': 'ok'}) as mock_put, \
             patch(GET_PATH, return_value=[POINTING_FIXTURE]):
            p.update(depth=22.5)
        body = mock_put.call_args.kwargs['json']
        assert body['depth'] == 22.5
        assert 'status' not in body
        assert 'band' not in body

    def test_update_serialises_enum_to_name(self):
        import gwtm_api.core.apimodels as m
        p = self._make_pointing()
        with patch(PUT_PATH, return_value={'message': 'ok'}) as mock_put, \
             patch(GET_PATH, return_value=[POINTING_FIXTURE]):
            p.update(status=m.pointing_status.cancelled)
        body = mock_put.call_args.kwargs['json']
        assert body['status'] == 'cancelled'

    def test_update_serialises_datetime_to_isoformat(self):
        p = self._make_pointing()
        t = datetime.datetime(2025, 6, 1, 12, 0, 0)
        with patch(PUT_PATH, return_value={'message': 'ok'}) as mock_put, \
             patch(GET_PATH, return_value=[POINTING_FIXTURE]):
            p.update(time=t)
        body = mock_put.call_args.kwargs['json']
        assert body['time'] == '2025-06-01T12:00:00'

    def test_update_refreshes_self_from_get(self):
        p = self._make_pointing()
        updated = {**POINTING_FIXTURE, 'depth': 22.5}
        with patch(PUT_PATH, return_value={'message': 'ok'}), \
             patch(GET_PATH, return_value=[updated]):
            p.update(depth=22.5)
        assert p.depth == 22.5

    def test_update_raises_without_id(self):
        p = self._make_pointing()
        p.id = None
        with pytest.raises(Exception, match="no id"):
            p.update(status='cancelled')


class TestPointingDelete:

    def _make_pointing(self):
        with patch(GET_PATH, return_value=[POINTING_FIXTURE]):
            return gwtm_api.Pointing.get(id=42)[0]

    def test_delete_calls_delete_endpoint(self):
        p = self._make_pointing()
        with patch(DELETE_PATH, return_value={'message': 'ok'}) as mock_del:
            p.delete()
        assert mock_del.call_args.args[0] == '/pointings'

    def test_delete_sends_own_id(self):
        p = self._make_pointing()
        with patch(DELETE_PATH, return_value={'message': 'ok'}) as mock_del:
            p.delete()
        assert mock_del.call_args.kwargs['json'] == {'ids': [42]}

    def test_delete_raises_without_id(self):
        p = self._make_pointing()
        p.id = None
        with pytest.raises(Exception, match="no id"):
            p.delete()

    def test_batch_delete_calls_delete_endpoint(self):
        with patch(DELETE_PATH, return_value={'message': 'ok'}) as mock_del:
            gwtm_api.Pointing.batch_delete(ids=[1, 2, 3])
        assert mock_del.call_args.args[0] == '/pointings'
        assert mock_del.call_args.kwargs['json'] == {'ids': [1, 2, 3]}

    def test_batch_delete_raises_on_empty_list(self):
        with pytest.raises(Exception):
            gwtm_api.Pointing.batch_delete(ids=[])
