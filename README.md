# gwtm_api

A python wrapper for the [Gravitational Wave Treasure Map](http://treasuremap.space).
In order to interact with the web API, you will need to [register](http://treasuremap.space/register) an account with the GWTM. Once verified you will recieve an `API_TOKEN` to pass into all api endpoints.

```bash
git clone https://github.com/TheTreasureMap/gwtm_api.git
cd gwtm_api
conda create -n gwtm python=3.10
source activate gwtm
python -m pip install -r requirments.txt
python -m pip install -e .
```


## Pointings:
Full api documentation with detailed examples can be found at [GWTM API Documentation](http://treasuremap.space/documentation).
### Get
```python
import gwtm_api

pointings = gwtm_api.Pointing(graceid="GW190814", instruments=["ZTF"], api_token=API_TOKEN)
```

### Post
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
