"""Unit tests for event_tools — no live server required."""
import numpy as np
from unittest.mock import patch

import sys
sys.path.insert(0, 'src')

import gwtm_api.event_tools as event_tools

SKYMAP = np.array([0.1, 0.2, 0.3, 0.4])

POINTING_GET_PATH = 'gwtm_api.event_tools.Pointing.get'
SKYMAP_PATH = 'gwtm_api.event_tools.Alert.fetch_skymap'


class TestCalculateCoverageEmptyCase:

    def test_no_pointings_returns_zero_prob_and_area(self):
        with patch(POINTING_GET_PATH, return_value=[]), \
             patch(SKYMAP_PATH, return_value=SKYMAP):
            prob, area = event_tools.calculate_coverage(graceid='S190425z')
        assert prob == 0.0
        assert area == 0.0

    def test_return_type_is_tuple_of_floats(self):
        with patch(POINTING_GET_PATH, return_value=[]), \
             patch(SKYMAP_PATH, return_value=SKYMAP):
            result = event_tools.calculate_coverage(graceid='S190425z')
        assert len(result) == 2
        assert all(isinstance(v, float) for v in result)

    def test_raises_without_graceid_or_pointings(self):
        import pytest
        with pytest.raises(Exception, match="required"):
            event_tools.calculate_coverage(graceid=None, pointings=[])


class TestRenormalizeSkymapEmptyCase:

    def test_no_pointings_returns_original_skymap(self):
        with patch(POINTING_GET_PATH, return_value=[]), \
             patch(SKYMAP_PATH, return_value=SKYMAP.copy()):
            result = event_tools.renormalize_skymap(graceid='S190425z')
        np.testing.assert_array_equal(result, SKYMAP)

    def test_raises_without_graceid_or_pointings(self):
        import pytest
        with pytest.raises(Exception, match="required"):
            event_tools.renormalize_skymap(graceid=None, pointings=[])
