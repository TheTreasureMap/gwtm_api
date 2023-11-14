from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy import units as u
import ligo.skymap.plot
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge, Polygon
from matplotlib.collections import PatchCollection
from mpl_toolkits.basemap import Basemap
import numpy as np

from .pointing import Pointing as Pointing
from .instrument import Instrument as Instrument
from .alert import Alert as Alert

def plot_coverage(api_token: str = None, graceid: str = None, pointings: list = [],
    contour_data: dict = None):
    
    if len(pointings) == 0 and graceid is None:
        raise Exception("Pointings list or graceid is required")

    if len(pointings) == 0 and graceid is not None:
        pointings = Pointing.get(graceid = graceid, api_token=api_token, status='completed')

    if contour_data is None:
        contour_data = Alert.fetch_contours(graceid=graceid, api_token=api_token)
    contour_polygons = []
    try:
        for contour in contour_data['features']:
            contour_polygons.extend(contour['geometry']['coordinates'])
    except:
        raise ValueError("contour data must be an output of ligo.skymap.postprocess")

            

    instrument_ids = list(set([x.instrumentid for x in pointings]))
    inst_footprints =  Instrument.get(ids=instrument_ids, include_footprint=True, api_token=api_token)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    m = Basemap(projection='moll',lon_0=0,resolution='c')
    m.drawparallels(np.arange(-90.,120.,30.))
    m.drawmeridians(np.arange(0.,420.,60.))
    plt.title("Mollweide Projection")

    footprints = []
    for p in pointings:
        inst_footprint = [x for x in inst_footprints if x.id == p.instrumentid][0]
        projected_footprint = inst_footprint.project(p.ra, p.dec, p.pos_angle)
        
        for ccd in projected_footprint:
            ra_deg, dec_deg = zip(*[(coord_deg[0], coord_deg[1])
                                    for coord_deg in ccd])
            
            x2, y2 = m(ra_deg, dec_deg)
            lat_lons = np.vstack([x2, y2]).transpose()
            poly = Polygon(lat_lons, edgecolor='r', facecolor='None', linewidth=0.5, alpha=1.0,
                       zorder=9900)
            ax.add_patch(poly)

    for contour_polygon in contour_polygons:
        ra_deg, dec_deg = zip(*[(coord_deg[0], coord_deg[1])
                                for coord_deg in contour_polygon])
        
        x2, y2 = m(ra_deg, dec_deg)
        lat_lons = np.vstack([x2, y2]).transpose()
        poly = Polygon(lat_lons, edgecolor='r', facecolor='None', linewidth=0.5, alpha=1.0,
                    zorder=9900)
        ax.add_patch(poly)
    

    plt.show()