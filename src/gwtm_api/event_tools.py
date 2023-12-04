from matplotlib import pyplot as plt
from matplotlib.patches import Circle, Wedge, Polygon
import numpy as np
from astropy.coordinates import SkyCoord

import healpy as hp
from ligo.skymap import distance
from ligo.skymap.postprocess.util import find_greedy_credible_levels
import ligo.skymap.plot
from ligo.skymap.plot.poly import cut_dateline
from ligo.gracedb.rest import GraceDb
import matplotlib
from matplotlib import colors

from .pointing import Pointing as Pointing
from .instrument import Instrument as Instrument
from .instrument import Footprint as Footprint
from .alert import Alert as Alert
from .core.util import instrument_color

# MVP TODO'S:
#   MVP+ plot mwe info

def plot_coverage(api_token: str = None, graceid: str = None, pointings: list = [],
    cache=False, projection='astro hours mollweide'):
    
    if len(pointings) == 0 and graceid is None:
        raise Exception("Pointings list or graceid is required")

    if len(pointings) == 0 and graceid is not None:
        pointings = Pointing.get(graceid = graceid, api_token=api_token, status='completed')

    #fetch skymap data
    skymap_data = Alert.fetch_skymap(graceid=graceid, api_token=api_token, cache=cache)

    #fetch contour data
    contour_polygons = Alert.fetch_contours(graceid=graceid, api_token=api_token, cache=cache)

    #query for latest alert information
    alert_info = Alert.get(graceid=graceid, api_token=api_token)

    #query for footprint info
    instrument_ids = list(set([x.instrumentid for x in pointings]))
    inst_footprints =  Instrument.get(ids=instrument_ids, include_footprint=True, api_token=api_token)

    #set up the plot
    subplot_kw = {
        'projection': projection,
        'center': SkyCoord(alert_info.avgra, alert_info.avgdec, unit="deg")
    }
    fig, ax = plt.subplots(1, 1, layout="constrained", subplot_kw=subplot_kw)
    ax.grid()

    #plot each of the instrument footprints
    instrument_enumeration_dict = {}
    for i, iid in enumerate(instrument_ids):
        instrument_enumeration_dict[iid] = i

    for i in instrument_ids:
        polygon_arr = []
        instrument_pointings = [x for x in pointings if x.instrumentid == i]

        if cache:
            cached_footprints = Footprint.get_cached_footprints(
                graceid=graceid,
                instrument_id=i,
                pointings=instrument_pointings
            )
            if cached_footprints:
                polygon_arr.extend(
                    cached_footprints
                )

        inst_footprint = [x for x in inst_footprints if x.id == i][0]
        
        if len(polygon_arr) == 0:
            for p in instrument_pointings:
                projected_footprint = inst_footprint.project(p.ra, p.dec, p.pos_angle)
                for ccd in projected_footprint:
                    ra_deg, dec_deg = zip(*[(coord_deg[0], coord_deg[1])
                                            for coord_deg in ccd])
                    
                    list_o_coords = []
                    for x, y in zip(ra_deg, dec_deg):
                        list_o_coords.append((x, y))
                    polygon_arr.append(list_o_coords)

        if cache:
            Footprint.put_cached_footprints(
                polygon_arr,
                graceid=graceid,
                instrument_id=i,
                pointings=instrument_pointings
            )

        for j,arr in enumerate(polygon_arr):
            if j == 0:
                label = inst_footprint.nickname if inst_footprint.nickname is not None else inst_footprint.name
            else:
                label = None

            #cut_dateline(arr)[0]
            poly = Polygon(
                np.asarray(arr), 
                transform=ax.get_transform('world'),
                edgecolor=instrument_color(instrument_enumeration_dict[i]), 
                facecolor='None', 
                linewidth=0.5, 
                alpha=1.0,
                zorder=9900,
                label=label
            )
            ax.add_patch(poly)

    #plot thee 90/50 contoturs
    for contour_polygon in contour_polygons:
        ra_deg, dec_deg = zip(*[(coord_deg[0], coord_deg[1])
                                for coord_deg in contour_polygon])
                                
        list_o_coords = []
        for x, y in zip(ra_deg, dec_deg):
                list_o_coords.append((x, y))
        arr = np.asarray(list_o_coords)

        poly = Polygon(
            arr, 
            transform=ax.get_transform('world'),
            edgecolor='r', 
            facecolor='None', 
            linewidth=0.5,
            alpha=1.0,
            zorder=9900
        )
        ax.add_patch(poly)

    #plot the skymap:
    if skymap_data is not None:

        _90_50_levels = find_greedy_credible_levels(np.asarray(skymap_data))
        ax.contourf_hpx(
            _90_50_levels, 
            cmap='OrRd_r', 
            levels=[0.0, 0.5, 0.9], 
            alpha=0.75
        )

    plt.legend(bbox_to_anchor=(0, 0), loc="lower left",
                bbox_transform=fig.transFigure,  ncol=4)
    plt.title(f"Reported Coverage for {graceid}")
    plt.show()