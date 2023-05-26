from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy import units as u
import ligo.skymap.plot
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge, Polygon
from matplotlib.collections import PatchCollection

from .pointing import Pointing as Pointing
from .instrument import Instrument as Instrument

def plot_coverage(api_token: str = None, graceid: str = None, pointings: list = []):
    
    if len(pointings) == 0 and graceid is None:
        raise Exception("Pointings list or graceid is required")
    if len(pointings) == 0 and graceid is not None:
        pointings = Pointing.get(graceid = graceid, api_token=api_token, status='completed')

    instrument_ids = list(set([x.instrumentid for x in pointings]))
    inst_footprints =  Instrument.get(ids=instrument_ids, include_footprint=True, api_token=api_token)

    ax = plt.axes(projection='astro mollweide')

    footprints = []
    for p in pointings:
        inst_footprint = [x for x in inst_footprints if x.id == p.instrumentid][0]
        projected_footprint = inst_footprint.project(p.ra, p.dec, p.pos_angle)
        
        for ccd in projected_footprint:
            poly = Polygon(ccd, facecolor='green', edgecolor='green', alpha=0.4, closed=True, transform=ax.get_transform('fk5'))
            footprints.append(poly)

    p = PatchCollection(footprints)
    ax.add_collection(p)

    plt.show()