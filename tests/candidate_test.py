import sys
import datetime
import os

sys.path.insert(0, '../src')

import gwtm_api


API_TOKEN = os.getenv('GWTM_API_TOKEN', None)
if API_TOKEN is None:
    print('export API token')

def test_get():
    candidates = gwtm_api.Candidate.get(api_token = API_TOKEN, graceid = "MS181101ab")
    for c in candidates:
        c.dump()

def test_post():

    candidate = gwtm_api.Candidate(
        candidate_name = "test_candidate_name",
        discovery_date = datetime.datetime.now(),
        discovery_magnitude = 12, 
        magnitude_unit = "ab_mag",
        ra = 195,
        dec = -20,
        magnitude_bandpass = "r"
    )
    
    candidate.post(api_token=API_TOKEN, graceid="MS181101ab")
    candidate.dump()


def test_batch_post():
    
    batch = [
        gwtm_api.Candidate(
            candidate_name = "test_candidate_name2",
            discovery_date = datetime.datetime.now(),
            discovery_magnitude = 12, 
            magnitude_unit = "ab_mag",
            ra = 196,
            dec = -21,
            magnitude_bandpass = "r"
        ),
        gwtm_api.Candidate(
            candidate_name = "test_candidate_name3",
            discovery_date = datetime.datetime.now(),
            discovery_magnitude = 12, 
            magnitude_unit = "ab_mag",
            ra = 197,
            dec = -20.5,
            magnitude_bandpass = "r"
        )
    ]
    cs = gwtm_api.Candidate.batch_post(candidates=batch, api_token=API_TOKEN, graceid="MS181101ab")
    for c in cs:
        c.dump()

def put_test():
    candidate = gwtm_api.Candidate.get(api_token=API_TOKEN, id = 30)
    my_candidate = candidate[0]
    my_candidate.candidate_name = "test_update_candidate_name"
    my_candidate.put(api_token=API_TOKEN, base="http://127.0.0.1:5000/api/")
    updated = gwtm_api.Candidate.get(api_token=API_TOKEN, id = 30)
    print("")
    updated[0].dump()

    candidate = gwtm_api.Candidate(id=30, api_token=API_TOKEN)
    candidate.put(api_token=API_TOKEN, payload={"tns_name": "bingbango"}, base="http://127.0.0.1:5000/api/")
    candidate.dump()

def del_test():
    candidate = gwtm_api.Candidate(id=21, api_token=API_TOKEN)
    candidate.delete(api_token=API_TOKEN, base="http://127.0.0.1:5000/api/")

def batch_delete():
    gwtm_api.Candidate.batch_delete(api_token=API_TOKEN, ids=list(range(0, 100)), verbose=True)

if __name__ == "__main__":
    #test_post()
    #test_batch_post()
    #test_get()
    #put_test()
    #del_test()
    batch_delete()