import json
from typing import Any, List, Tuple
import ligo.skymap.plot  # noqa: F401
from matplotlib import pyplot as plt
from matplotlib.patches import Polygon
import numpy as np
import pandas as pd
import astropy

import healpy as hp
from ligo.skymap.postprocess.util import find_greedy_credible_levels
import ligo.skymap.postprocess

from . import Pointing, Instrument, Footprint, Candidate
from .alert import Alert as Alert
from .core.util import instrument_color, gc_dist


def plot_coverage(graceid: str, pointings: List[Pointing] = [],
    cache=False, projection='astro hours mollweide') -> None:

    if len(pointings) == 0 and graceid is None:
        raise Exception("Pointings list or graceid is required")

    if len(pointings) == 0 and graceid is not None:
        pointings = Pointing.get(graceid=graceid, status='completed')

    skymap_data = Alert.fetch_skymap(graceid=graceid, cache=cache)
    contour_polygons = Alert.fetch_contours(graceid=graceid, cache=cache)

    instrument_ids = list(set([x.instrumentid for x in pointings]))
    inst_footprints = Instrument.get(ids=instrument_ids, include_footprint=True)

    subplot_kw = {'projection': projection}
    fig, ax = plt.subplots(1, 1, layout="constrained", subplot_kw=subplot_kw)
    ax.grid()

    instrument_enumeration_dict = {}
    for i, iid in enumerate(instrument_ids):
        instrument_enumeration_dict[iid] = i

    for i in instrument_ids:
        polygon_arr = []
        instrument_pointings = [x for x in pointings if x.instrumentid == i]

        if cache:
            cached_footprints = Footprint.get_cached_footprints(
                graceid=graceid, instrument_id=i, pointings=instrument_pointings)
            if cached_footprints:
                polygon_arr.extend(cached_footprints)

        inst_footprint = [x for x in inst_footprints if x.id == i][0]

        if len(polygon_arr) == 0:
            for p in instrument_pointings:
                projected_footprint = inst_footprint.project(p.ra, p.dec, p.pos_angle)
                for ccd in projected_footprint:
                    ra_deg, dec_deg = zip(*[(coord_deg[0], coord_deg[1]) for coord_deg in ccd])
                    polygon_arr.append(list(zip(ra_deg, dec_deg)))

        if cache:
            Footprint.put_cached_footprints(
                polygon_arr, graceid=graceid, instrument_id=i, pointings=instrument_pointings)

        for j, arr in enumerate(polygon_arr):
            label = (inst_footprint.nickname if inst_footprint.nickname is not None
                     else inst_footprint.name) if j == 0 else None
            poly = Polygon(
                np.asarray(arr),
                transform=ax.get_transform('world'),
                edgecolor=instrument_color(instrument_enumeration_dict[i]),
                facecolor='None', linewidth=0.5, alpha=1.0, zorder=9900, label=label
            )
            ax.add_patch(poly)

    for contour_polygon in contour_polygons:
        ra_deg, dec_deg = zip(*[(coord_deg[0], coord_deg[1]) for coord_deg in contour_polygon])
        poly = Polygon(
            np.asarray(list(zip(ra_deg, dec_deg))),
            transform=ax.get_transform('world'),
            edgecolor='r', facecolor='None', linewidth=0.5, alpha=1.0, zorder=9900
        )
        ax.add_patch(poly)

    if skymap_data is not None:
        _90_50_levels = find_greedy_credible_levels(np.asarray(skymap_data))
        ax.contourf_hpx(_90_50_levels, cmap='OrRd_r', levels=[0.0, 0.5, 0.9], alpha=0.75)

    plt.legend(bbox_to_anchor=(0, 0), loc="lower left", bbox_transform=fig.transFigure, ncol=4)
    plt.title(f"Reported Coverage for {graceid}")
    plt.show()


def calculate_coverage(graceid: str, pointings: List[Pointing] = [],
    cache=False, approximate=True) -> Tuple[float, float]:
    DECam_id = 38
    if len(pointings) == 0 and graceid is None:
        raise Exception("Pointings list or graceid is required")

    if len(pointings) == 0 and graceid is not None:
        pointings = Pointing.get(graceid=graceid, status='completed')

    skymap = Alert.fetch_skymap(graceid=graceid, cache=cache)

    instrument_ids = list(set([x.instrumentid for x in pointings]))

    if DECam_id in instrument_ids:
        print("Warning: DECam footprint will be automatically approximated")
        approximate = True

    inst_footprints = Instrument.get(ids=instrument_ids, include_footprint=True,
                                     approximate_footprint=approximate)

    instrument_enumeration_dict = {}
    for i, iid in enumerate(instrument_ids):
        instrument_enumeration_dict[iid] = i

    skymap_nside = hp.npix2nside(len(skymap))

    qps = []
    NSIDE4area = 512
    pixarea = hp.nside2pixarea(NSIDE4area, degrees=True)

    for i in instrument_ids:
        polygon_arr = []
        instrument_pointings = [x for x in pointings if x.instrumentid == i]

        if cache:
            cached_footprints = Footprint.get_cached_footprints(
                graceid=graceid, instrument_id=i, pointings=instrument_pointings)
            if cached_footprints:
                polygon_arr.extend(cached_footprints)

        inst_footprint = [x for x in inst_footprints if x.id == i][0]

        if len(polygon_arr) == 0:
            for p in instrument_pointings:
                projected_footprint = inst_footprint.project(p.ra, p.dec, p.pos_angle)
                for ccd in projected_footprint:
                    ra_deg, dec_deg = zip(*[(coord_deg[0], coord_deg[1]) for coord_deg in ccd])
                    polygon_arr.append(list(zip(ra_deg, dec_deg)))

        if cache:
            Footprint.put_cached_footprints(
                polygon_arr, graceid=graceid, instrument_id=i, pointings=instrument_pointings)

        for arr in polygon_arr:
            ras_poly = [x[0] for x in arr][:-1]
            decs_poly = [x[1] for x in arr][:-1]
            xyzpoly = astropy.coordinates.spherical_to_cartesian(
                1, np.deg2rad(decs_poly), np.deg2rad(ras_poly))
            qp = hp.query_polygon(skymap_nside, np.array(xyzpoly).T, inclusive=True)
            qps.extend(qp)
            deduped_indices = list(dict.fromkeys(qps))

    prob = np.sum(skymap[deduped_indices])
    area = pixarea * len(deduped_indices)
    return prob, area


def renormalize_skymap(graceid: str, pointings: List[Pointing] = [],
    cache=False) -> Any:

    if len(pointings) == 0 and graceid is None:
        raise Exception("Pointings list or graceid is required")

    if len(pointings) == 0 and graceid is not None:
        pointings = Pointing.get(graceid=graceid, status='completed')

    skymap = Alert.fetch_skymap(graceid=graceid, cache=cache)

    instrument_ids = list(set([x.instrumentid for x in pointings]))
    inst_footprints = Instrument.get(ids=instrument_ids, include_footprint=True)

    skymap_nside = hp.npix2nside(len(skymap))
    qps = []

    for i in instrument_ids:
        polygon_arr = []
        instrument_pointings = [x for x in pointings if x.instrumentid == i]

        if cache:
            cached_footprints = Footprint.get_cached_footprints(
                graceid=graceid, instrument_id=i, pointings=instrument_pointings)
            if cached_footprints:
                polygon_arr.extend(cached_footprints)

        inst_footprint = [x for x in inst_footprints if x.id == i][0]

        if len(polygon_arr) == 0:
            for p in instrument_pointings:
                projected_footprint = inst_footprint.project(p.ra, p.dec, p.pos_angle)
                for ccd in projected_footprint:
                    ra_deg, dec_deg = zip(*[(coord_deg[0], coord_deg[1]) for coord_deg in ccd])
                    polygon_arr.append(list(zip(ra_deg, dec_deg)))

        if cache:
            Footprint.put_cached_footprints(
                polygon_arr, graceid=graceid, instrument_id=i, pointings=instrument_pointings)

        for arr in polygon_arr:
            ras_poly = [x[0] for x in arr][:-1]
            decs_poly = [x[1] for x in arr][:-1]
            xyzpoly = astropy.coordinates.spherical_to_cartesian(
                1, np.deg2rad(decs_poly), np.deg2rad(ras_poly))
            qp = hp.query_polygon(skymap_nside, np.array(xyzpoly).T)
            qps.extend(qp)
            deduped_indices = list(dict.fromkeys(qps))

    skymap[deduped_indices] = 0
    normed_skymap = skymap / np.sum(skymap)
    return normed_skymap


def renormed_skymap_contours(graceid: str, pointings: List[Pointing] = [],
    cache=False) -> Any:

    normed_skymap = renormalize_skymap(graceid=graceid, pointings=pointings, cache=cache)

    i = np.flipud(np.argsort(normed_skymap))
    cumsum = np.cumsum(normed_skymap[i])
    cls = np.empty_like(normed_skymap)
    cls[i] = cumsum * 100
    paths = list(ligo.skymap.postprocess.contour(cls, [50, 90], nest=False, degrees=True, simplify=True))

    return json.dumps({
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'properties': {'credible_level': contour},
                'geometry': {'type': 'MultiLineString', 'coordinates': path}
            }
            for contour, path in zip([50, 90], paths)
        ]
    })


def candidate_coverage(candidate: Candidate, pointings: List[Pointing] = None,
                       distance_thresh: float = 5.0) -> List[Pointing]:
    """
    Find which instrument pointings overlap with a candidate's position.

    Args:
        candidate: the Candidate to evaluate coverage for
        pointings: pre-fetched pointings to evaluate; defaults to all pointings for the event
        distance_thresh: search radius in degrees (default 5.0)

    Returns all pointings whose footprint contains the candidate position.
    """
    skymap_nside = 1024
    candidate_healpix = hp.ang2pix(skymap_nside, candidate.ra, candidate.dec,
                                   lonlat=True, nest=True)

    if not pointings:
        pointings = Pointing.get(graceid=candidate.graceid)

    pointings_df = pd.DataFrame([x.__dict__ for x in pointings])
    pointings_df["_DIST"] = gc_dist(
        pointings_df["ra"], pointings_df["dec"], candidate.ra, candidate.dec
    )
    culled_pointings = pointings_df.loc[pointings_df["_DIST"] < distance_thresh]

    if len(culled_pointings) == 0:
        return []

    instrument_ids = culled_pointings["instrumentid"].values.tolist()
    instruments = Instrument.get(ids=instrument_ids, include_footprint=True)

    vals = zip(
        culled_pointings["ra"].values,
        culled_pointings["dec"].values,
        culled_pointings["pos_angle"].values,
        culled_pointings["id"].values,
        culled_pointings["instrumentid"].values
    )

    return_ids = []
    for pra, pdec, ppos_angle, pid, pinstid in vals:
        instrument = [x for x in instruments if x.id == pinstid][0]
        projected = instrument.project(pra, pdec, ppos_angle)

        for ccd in projected:
            ra_deg, dec_deg = zip(*[(coord_deg[0], coord_deg[1]) for coord_deg in ccd])
            list_o_coords = list(zip(ra_deg, dec_deg))
            ras_poly = [x[0] for x in list_o_coords][:-1]
            decs_poly = [x[1] for x in list_o_coords][:-1]
            xyzpoly = astropy.coordinates.spherical_to_cartesian(
                1, np.deg2rad(decs_poly), np.deg2rad(ras_poly))
            qp = hp.query_polygon(skymap_nside, np.array(xyzpoly).T, nest=True)
            if candidate_healpix in qp:
                return_ids.append(pid)

    return [x for x in pointings if x.id in return_ids]
