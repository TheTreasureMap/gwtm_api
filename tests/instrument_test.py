import sys
import os

sys.path.insert(0, '../src')

import gwtm_api

API_TOKEN = os.getenv('GWTM_API_TOKEN', None)
if API_TOKEN is None:
    print('export API token')

def get_instrument_test():
    insts = gwtm_api.Instrument.get(
        include_footprint = True, type="photometric", ids=[13, 90, 88],
        api_token=API_TOKEN
    )

    feet = gwtm_api.Footprint.get(
        api_token=API_TOKEN, instrumentid=13
    )
    for f in feet:
        f.dump()

    for f in insts:
        f.dump()

get_instrument_test()