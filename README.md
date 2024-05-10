# gwtm_api

A python wrapper for the [Gravitational Wave Treasure Map](http://treasuremap.space).
In order to interact with the web API, you will need to [register](http://treasuremap.space/register) an account with the GWTM. Once verified you will recieve an `API_TOKEN` to pass into all api endpoints.

```bash
conda create -n gwtm_api python=3.11
conda activate gwtm_api
python -m pip install gwtm_api
```


## Pointings:
Full api documentation with detailed examples can be found at [GWTM API Documentation](http://treasuremap.space/documentation).
### GET
```python
import gwtm_api

pointings = gwtm_api.Pointing.get(graceid="GW190814", instruments=["ZTF"], api_token=API_TOKEN)
```

### POST
Submit single, or list of `gwtm_api.Pointing` objects.
```python
import gwtm_api

#submit single
p = gwtm_api.Pointing(
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
p.post(graceid="GRACEID", api_token=API_TOKEN)

#submit list
batch = [
  gwtm_api.Pointing(...),
  gwtm_api.Pointing(...)
]
gwtm_api.Pointing.batch_post(pointings=batch, graceid="GRACEID", api_token=API_TOKEN)
```

## Candidates
Get and Post Event Candidates through the API:
### GET
```python
import gwtm_api
from datetime import datetime

candidates = gwtm_api.Candidate.get(graceid="GW190814", api_token=API_TOKEN)
```
### POST
Submit single, or list of `gwtm_api.Candidate` objects.
```python
import gwtm_api

#submit single
candidate = gwtm_api.Candidate(
    ra=15,
    dec=-24,
    discovery_date=datetime.datetime.now(),
    discovery_magnitude = 18,
    magnitude_bandpass = "r",
    magnitude_unit = "ab_mag",
    associated_galaxy = "some galaxy name",
    associated_galaxy_redshift = 0.3
)
candidate.post(graceid="GRACEID", api_token=API_TOKEN)

#submit list
batch = [
  gwtm_api.Candidate(...),
  gwtm_api.Candidate(...)
]
gwtm_api.Pointing.batch_post(candidates=batch, graceid="GRACEID", api_token=API_TOKEN)
```

### PUT
Update a GWTM candidate record
```python
import gwtm_api
candidate = gwtm_api.Candidate.get(api_token=API_TOKEN, id=CANDIDATE_ID)
my_candidate = candidate[0]
update_payload = {
    "tns_name": "AT2017gfo",
    "tns_url": "https://www.wis-tns.org/object/2017gfo"
    "associated_galaxy": "NGC 4993"
    "associated_galaxy_redshift": 0.009727
}
my_candidate.put(api_token=API_TOKEN, payload=update_payload)

#or similarly
candidate = gwtm_api.Candidate(id=CANDIDATE_ID, api_token=API_TOKEN) #this will envoke the GET endpoint if it has an id and api token
candidate.tns_name = "AT2017gfo"
candidate.tns_url = "https://www.wis-tns.org/object/2017gfo"
candidate.associated_galaxy = "NGC 4993"
candidate.associated_galaxy_redshift = 0.009727
candidate.put(api_token=API_TOKEN)
```

### Delete
```python
candidate = gwtm_api.Candidate(id=21, api_token=API_TOKEN)
candidate.delete(api_token=API_TOKEN)

#or batch delete with a list of ids
gwtm_api.Candidate.batch_delete(api_token=API_TOKEN, ids=[id1, id2....], verbose=True)
```

## Instruments
Query for instrument information that have been submitted to the Treasure Map
```python
import gwtm_api

instruments = gwtm_api.Instrument.get(name="ZTF", api_token=API_TOKEN)
```
You can pass the parameter `include_footprint=True` into the get request, and receive the polygon information for the instrument footprint.
We've included basic polygon manipulation functionality with this footprint class as well. When combined with the pointing information you can project the footprint on the sky, and simulate reported coverage yourself.
```python
import gwtm_api

ztf = gwtm_api.Instrument.get(name="ZTF", include_footprint=True, api_token=API_TOKEN)[0]
ztf.project(ra, dec, pos_angle)
```

## Event Tools
For a given GW event, you can utlize the the `event_tools` library to perform some analytics of a GW event with the data supported on the Treasure Map.

### Visualizing coverage
```python
import gwtm_api

gwtm_api.event_tools.plot_coverage(graceid="GW190814", api_token=API_TOKEN)
```
<img width="627" alt="image" src="https://github.com/TheTreasureMap/gwtm_api/assets/25805244/a6c0fa96-d991-46dc-a75e-472658dde873">

The `plot_coverage` function allows you to pass in your own list of pointings, along with caching the queried results so you don't have to hit the API for large queries every time.

```python
pointings = gwtm_api.Pointing.get(graceid = "GW190814", instrument="ZTF", api_token=API_TOKEN, status='completed')
gwtm_api.event_tools.plot_coverage(
    graceid="GW190814",
    api_token=API_TOKEN,
    pointings=pointings,
    cache=True
)
```

### Coverage Calculation
Calculate the total probability covered for a given GW Event. You can pass in a list of pointings for the event, or it will default to all pointings for the event. Returns the total probability and total area (deg^2) covered by the list of pointings

```python
total_prob, total_area = gwtm_api.event_tools.calculate_coverage(
    graceid="GW190814",
    api_token=API_TOKEN,
    pointings=pointings,
    cache=True
)
```

### Renormalize Skymap
Renormalize an event's skymap based on a list of pointings (or the entire GW event's completed pointings). It takes the list of pointings and sets the overlapping skymap pixel probability to zero, then renormalizes the skymap. Returns an NDArray that can be imported into healpy

```python
renormalized_skymap = gwtm_api.event_tools.renormalize_skymap(
    graceid="GW190814",
    api_token=API_TOKEN,
    pointings=pointings,
    cache=True
)
```
