"""Unit tests for Candidate wrapper — no live server required."""
import datetime
from unittest.mock import patch

import pytest

import sys
sys.path.insert(0, 'src')

import gwtm_api

CANDIDATE_FIXTURE = {
    'id': 1, 'graceid': 'S190425z',
    'position': 'POINT (15.0 -24.0)',
    'candidate_name': 'AT2019abc',
    'discovery_date': '2019-04-25T08:00:00',
    'discovery_magnitude': 18.5,
    'magnitude_unit': 'ab_mag',
}

GET_PATH = 'gwtm_api.core._client_factory.get'
POST_PATH = 'gwtm_api.core._client_factory.post'
PUT_PATH = 'gwtm_api.core._client_factory.put'
DELETE_PATH = 'gwtm_api.core._client_factory.delete'


class TestCandidateGet:

    def test_returns_list_of_candidates(self):
        with patch(GET_PATH, return_value=[CANDIDATE_FIXTURE]):
            result = gwtm_api.Candidate.get(graceid='S190425z')
        assert len(result) == 1
        assert isinstance(result[0], gwtm_api.Candidate)
        assert result[0].id == 1
        assert result[0].ra == 15.0
        assert result[0].dec == -24.0

    def test_ids_list_sent_to_server(self):
        with patch(GET_PATH, return_value=[]) as mock:
            gwtm_api.Candidate.get(ids=[1, 2, 3])
        assert mock.call_args.kwargs['params']['ids'] == '[1, 2, 3]'

    def test_single_id_sent_to_server(self):
        with patch(GET_PATH, return_value=[]) as mock:
            gwtm_api.Candidate.get(id=42)
        assert mock.call_args.kwargs['params']['id'] == 42

    def test_correct_endpoint_called(self):
        with patch(GET_PATH, return_value=[]) as mock:
            gwtm_api.Candidate.get(graceid='S190425z')
        assert mock.call_args.args[0] == '/candidate'

    def test_backwards_compat_api_token(self):
        import gwtm_api.core._client_factory as t
        with patch(GET_PATH, return_value=[]):
            gwtm_api.Candidate.get(graceid='S190425z', api_token='legacy')
        assert t._token == 'legacy'


class TestCandidatePost:

    def test_post_calls_correct_endpoint(self):
        with patch(POST_PATH, return_value={'candidate_ids': [1]}), \
             patch(GET_PATH, return_value=[CANDIDATE_FIXTURE]) as mock_get:
            c = gwtm_api.Candidate(
                ra=15.0, dec=-24.0, candidate_name='AT2019abc',
                discovery_date=datetime.datetime(2019, 4, 25),
                discovery_magnitude=18.5, magnitude_unit='ab_mag',
            )
            c.post(graceid='S190425z')
        assert mock_get.call_args.args[0] == '/candidate'

    def test_batch_post_sends_ids_to_get(self):
        with patch(POST_PATH, return_value={'candidate_ids': [1, 2]}), \
             patch(GET_PATH, return_value=[CANDIDATE_FIXTURE, {**CANDIDATE_FIXTURE, 'id': 2}]) as mock_get:
            candidates = [
                gwtm_api.Candidate(ra=15.0, dec=-24.0, candidate_name='AT2019abc',
                                   discovery_date=datetime.datetime(2019, 4, 25),
                                   discovery_magnitude=18.5, magnitude_unit='ab_mag'),
                gwtm_api.Candidate(ra=16.0, dec=-25.0, candidate_name='AT2019def',
                                   discovery_date=datetime.datetime(2019, 4, 25),
                                   discovery_magnitude=19.0, magnitude_unit='ab_mag'),
            ]
            gwtm_api.Candidate.batch_post(candidates=candidates, graceid='S190425z')
        assert mock_get.call_args.kwargs['params']['ids'] == '[1, 2]'


class TestCandidatePutDelete:

    def test_put_calls_correct_endpoint(self):
        c = gwtm_api.Candidate(kwdict={**CANDIDATE_FIXTURE})
        with patch(PUT_PATH, return_value={}), \
             patch(GET_PATH, return_value=[CANDIDATE_FIXTURE]):
            c.put(payload={'tns_name': 'AT2019abc'})
        # no exception = correct endpoint reached

    def test_delete_calls_correct_endpoint(self):
        c = gwtm_api.Candidate(kwdict={**CANDIDATE_FIXTURE})
        with patch(DELETE_PATH, return_value={}) as mock:
            c.delete()
        assert mock.call_args.args[0] == '/candidate'
        assert mock.call_args.kwargs['json']['id'] == 1

    def test_batch_delete_sends_ids(self):
        with patch(DELETE_PATH, return_value={}) as mock:
            gwtm_api.Candidate.batch_delete(ids=[1, 2, 3])
        assert mock.call_args.kwargs['json']['ids'] == [1, 2, 3]

    def test_delete_raises_without_id(self):
        c = gwtm_api.Candidate(kwdict={**CANDIDATE_FIXTURE, 'id': None})
        with pytest.raises(Exception, match="does not have an id"):
            c.delete()

    def test_put_raises_without_id(self):
        c = gwtm_api.Candidate(kwdict={**CANDIDATE_FIXTURE, 'id': None})
        with pytest.raises(Exception, match="does not have an id"):
            c.put()
