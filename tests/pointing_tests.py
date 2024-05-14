import sys
import os
import datetime

sys.path.insert(0, '../src')

import gwtm_api

API_TOKEN = os.getenv('GWTM_API_TOKEN', None)
if API_TOKEN is None:
    print('export API token')

def get_pointing_test():

    #need to test:
    #   ids xx
    #   graceids xx
    #   users xx
    #   statuses xx
    #   bands xx
    #   wavelength_regimes xx
    #   frequency_regimes 
    #   energy_regimes

    #testing graceids
    # pointings = gwtm_api.Pointing.get(graceids=["GW190814", "S190425z"], api_token=API_TOKEN)
    
    # users_t = [6,7]
    # pointings = gwtm_api.Pointing.get(users=users_t, api_token=API_TOKEN)

    # statuses = ['completed']
    # pointings = gwtm_api.Pointing.get(status=statuses, graceid="GW190814", api_token=API_TOKEN)

    # bands = ['XRT', 'u', 'V']
    # pointings = gwtm_api.Pointing.get(bands=bands, graceid="GW190814", api_token=API_TOKEN)

    # ids = [3811, 3812, 3813, 3814, 3815, 3816, 3817, 3818, 3819, 3820, 3821, 3822, 3823, 3824, 3825, 3826, 3827, 3828, 3829, 3830]
    # pointings = gwtm_api.Pointing.get(ids=ids, graceid="GW190814", api_token=API_TOKEN)
    # pointings = gwtm_api.Pointing.get(id=ids[0], graceid="GW190814", api_token=API_TOKEN)

    # pointings = gwtm_api.Pointing.get(wavelength_regime=["0", 45], wavelength_unit='nanometer', graceid='GW190814', api_token=API_TOKEN)
    # pointings = gwtm_api.Pointing.get(energy_regime="[0,5200]", energy_unit='keV', graceid='GW190814', api_token=API_TOKEN)
    # pointings = gwtm_api.Pointing.get(frequency_regime=[0, 500], frequency_unit='THz', graceid='GW190814', api_token=API_TOKEN, urlencode=True)

    pointings = gwtm_api.Pointing.get(depth_lt=15, graceid="MS181101ab", api_token=API_TOKEN, base="http://127.0.0.1:5000/api/")
    print(len(pointings))

    for p in pointings[0:2]:
        p.dump()
    #testing users
    return 

def post_pointing_test():

    pointing = gwtm_api.Pointing(
        ra=15,
        dec=-24,
        instrumentid = 10,
        time = datetime.datetime.now(),
        status = 'completed',
        depth = 18.5,
        depth_unit = 'ab_mag', 
        pos_angle=50,
        band = 'r'
    )

    pointing.post(graceid='MS181101ab', api_token=API_TOKEN, base="http://127.0.0.1:5000/api/")
    pointing.dump()

def batch_pointing_post():
    batch = [
        gwtm_api.Pointing(
            ra=15,
            dec=-24,
            instrumentid = 10,
            time = datetime.datetime.now(),
            status = 'completed',
            depth = 18.5,
            depth_unit = 'ab_mag', 
            pos_angle=50,
            band = 'r'
        ),
        gwtm_api.Pointing(
            ra=18,
            dec=-30,
            instrumentid = 10,
            time = datetime.datetime.now()-datetime.timedelta(hours=1),
            status = 'completed',
            depth = 18.5,
            depth_unit = 'ab_mag', 
            pos_angle=50,
            band = 'r'
        )
    ]

    batch = gwtm_api.Pointing.batch_post(pointings=batch, graceid='MS181101ab', api_token=API_TOKEN)
    for b in batch:
        b.dump()

def request_doi_test():
    doi_url = gwtm_api.Pointing.request_doi(api_token=API_TOKEN, graceid='MS181101ab')
    print(doi_url)

#get_pointing_test()
#post_pointing_test()
#batch_pointing_post()
request_doi_test()