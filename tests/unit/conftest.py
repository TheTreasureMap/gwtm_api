import pytest
import sys
sys.path.insert(0, 'src')

import gwtm_api
import gwtm_api.core._client_factory as transport


@pytest.fixture(autouse=True)
def reset_transport():
    """Reset transport state before each test and configure a default token."""
    transport._token = ''
    transport._base_url = transport.DEFAULT_BASE_URL
    gwtm_api.configure(api_token='tok')
    yield
    transport._token = ''
    transport._base_url = transport.DEFAULT_BASE_URL
