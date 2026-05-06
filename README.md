# gwtm_api

A Python wrapper for the [Gravitational Wave Treasure Map](https://treasuremap.space).

To interact with the API, [register](https://treasuremap.space/register) an account. Once verified you will receive an `API_TOKEN` shown on your profile page.

**Using pip:**
```bash
python -m venv gwtm_env
source gwtm_env/bin/activate   # Windows: gwtm_env\Scripts\activate
pip install gwtm_api
```

**Using conda:**
```bash
conda create -n gwtm_api python=3.11
conda activate gwtm_api
pip install gwtm_api
```

Full API documentation and parameter reference is available at [https://treasuremap.space/docs](https://treasuremap.space/docs).

---

## Configuration

Call `configure()` once at the start of your script. All subsequent API calls use the client created here — no need to pass credentials to every method.

```python
import gwtm_api

gwtm_api.configure(api_token='YOUR_API_TOKEN')
```

To point at a different server (e.g. a development instance), pass `base_url`:

```python
gwtm_api.configure(api_token='YOUR_API_TOKEN', base_url='https://dev.treasuremap.space')
```

Passing `api_token` directly to any method also works and is provided for backwards compatibility with older code. Note that doing so permanently updates the configured token — subsequent calls without an explicit `api_token` will reuse it:

```python
# Legacy style — still works
pointings = gwtm_api.Pointing.get(api_token='YOUR_API_TOKEN', graceid='GW190814')
```

You can also set credentials via environment variables and call `configure()` with no arguments:

```bash
export GWTM_API_TOKEN=YOUR_API_TOKEN
export GWTM_BASE_URL=https://treasuremap.space  # optional, this is the default
```

```python
gwtm_api.configure()
```

---

## Pointings

### GET

```python
import gwtm_api

gwtm_api.configure(api_token='YOUR_API_TOKEN')

pointings = gwtm_api.Pointing.get(
    graceid='GW190814',
    instruments=['ZTF'],
)
```

Filters can be combined freely — by instrument, status, time range, band, depth, and spectral regime. All list parameters accept Python lists directly.

### POST

Submit a single pointing or a batch:

```python
import datetime
import gwtm_api

gwtm_api.configure(api_token='YOUR_API_TOKEN')

# Single pointing
p = gwtm_api.Pointing(
    ra=15.0,
    dec=-24.0,
    instrumentid=10,
    time=datetime.datetime.now(),
    status='completed',
    depth=18.5,
    depth_unit='ab_mag',
    pos_angle=50,
    band='r'
)
p.post(graceid='GRACEID')

# Batch
batch = [
    gwtm_api.Pointing(...),
    gwtm_api.Pointing(...)
]
gwtm_api.Pointing.batch_post(pointings=batch, graceid='GRACEID')
```

---

## Candidates

### GET

```python
import gwtm_api

gwtm_api.configure(api_token='YOUR_API_TOKEN')

candidates = gwtm_api.Candidate.get(graceid='GW190814')
```

### POST

```python
import datetime
import gwtm_api

gwtm_api.configure(api_token='YOUR_API_TOKEN')

# Single candidate
candidate = gwtm_api.Candidate(
    ra=15.0,
    dec=-24.0,
    discovery_date=datetime.datetime.now(),
    discovery_magnitude=18,
    magnitude_bandpass='r',
    magnitude_unit='ab_mag',
    associated_galaxy='some galaxy name',
    associated_galaxy_redshift=0.3
)
candidate.post(graceid='GRACEID')

# Batch
batch = [
    gwtm_api.Candidate(...),
    gwtm_api.Candidate(...)
]
gwtm_api.Candidate.batch_post(candidates=batch, graceid='GRACEID')
```

### PUT

```python
import gwtm_api

gwtm_api.configure(api_token='YOUR_API_TOKEN')

candidate = gwtm_api.Candidate.get(id=CANDIDATE_ID)[0]
candidate.put(payload={
    'tns_name': 'AT2017gfo',
    'tns_url': 'https://www.wis-tns.org/object/2017gfo',
    'associated_galaxy': 'NGC 4993',
    'associated_galaxy_redshift': 0.009727
})
```

### DELETE

```python
import gwtm_api

gwtm_api.configure(api_token='YOUR_API_TOKEN')

candidate = gwtm_api.Candidate.get(id=CANDIDATE_ID)[0]
candidate.delete()

# Batch delete
gwtm_api.Candidate.batch_delete(ids=[id1, id2, ...])
```

---

## Instruments

```python
import gwtm_api

gwtm_api.configure(api_token='YOUR_API_TOKEN')

instruments = gwtm_api.Instrument.get(names=['ZTF'])
```

Pass `include_footprint=True` to receive polygon data for the instrument footprint, and project it onto the sky at any pointing:

```python
ztf = gwtm_api.Instrument.get(names=['ZTF'], include_footprint=True)[0]
projected = ztf.project(ra, dec, pos_angle)
```

---

## Event Tools

For a given GW event, you can use the `event_tools` library to perform analytics with the data on the Treasure Map.

### Visualizing coverage

```python
import gwtm_api

gwtm_api.configure(api_token='YOUR_API_TOKEN')

gwtm_api.event_tools.plot_coverage(graceid='GW190814')
```

<img width="627" alt="image" src="https://github.com/TheTreasureMap/gwtm_api/assets/25805244/a6c0fa96-d991-46dc-a75e-472658dde873">

Pass in your own pointings and enable caching to avoid repeated API calls:

```python
pointings = gwtm_api.Pointing.get(
    graceid='GW190814',
    instruments=['ZTF'],
    status='completed',
)
gwtm_api.event_tools.plot_coverage(
    graceid='GW190814',
    pointings=pointings,
    cache=True
)
```

### Coverage calculation

Returns total probability and total area (deg²) covered by the pointings:

```python
total_prob, total_area = gwtm_api.event_tools.calculate_coverage(
    graceid='GW190814',
    pointings=pointings,
    cache=True
)
```

### Renormalize skymap

Sets overlapping skymap pixel probability to zero for observed regions and renormalises. Returns an NDArray compatible with healpy:

```python
renormalized_skymap = gwtm_api.event_tools.renormalize_skymap(
    graceid='GW190814',
    pointings=pointings,
    cache=True
)
```

### Candidate coverage

Find which instrument pointings overlap with a candidate's position:

```python
my_candidate = gwtm_api.Candidate.get(graceid='GW190814')[0]
covering_pointings = gwtm_api.event_tools.candidate_coverage(candidate=my_candidate)
```

---

## For contributors

The package has a simple two-layer architecture:

- **`src/gwtm_api/{pointing,alert,instrument,candidate}.py`** — hand-written, user-facing classes with a stable, friendly interface
- **`src/gwtm_api/core/_client_factory.py`** — thin httpx transport layer; configured once via `gwtm_api.configure()`

### Setup after cloning

```bash
pip install -e '.[dev]'
```

### When the server API changes

Update the relevant wrapper methods in `src/gwtm_api/`, bump the version in `pyproject.toml`, and create a GitHub Release — publishing to PyPI happens automatically.
