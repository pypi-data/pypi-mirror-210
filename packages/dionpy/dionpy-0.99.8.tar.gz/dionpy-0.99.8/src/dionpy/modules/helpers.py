from __future__ import annotations

import os
from typing import Iterable, Sequence

import healpy as hp
import numpy as np
from ffmpeg_progress_yield import FfmpegProgress
from pymap3d import aer2geodetic, Ellipsoid
from tqdm import tqdm

from .ion_tools import srange

R_EARTH = 6378100.0


class TextColor:
    """
    Provides formatters for terminal text coloring.
    """

    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"

def none_or_array(vals: None | Iterable) -> np.ndarray | None:
    """
    Used for data loading from HDF files. Converts not None values to np.arrays.
    """
    if vals is None:
        return None
    return np.array(vals)


def is_iterable(x):
    if isinstance(x, list) or isinstance(x, np.ndarray):
        return True
    return False


def check_elaz_shape(el: float | np.ndarray, az: float | np.ndarray):
    """
    Checks shape and type of input elevation and azimuth.
    """
    if not isinstance(el, float) and not isinstance(az, float):
        if isinstance(el, np.ndarray) and isinstance(el, np.ndarray):
            if not el.shape == az.shape:
                raise ValueError("Elevation and azimuth must be the same length.")
        else:
            raise ValueError(
                "Elevation and azimuth must be either floats or numpy arrays."
            )


def sky2ll(
    el: float | np.ndarray,
    az: float | np.ndarray,
    height: float,
    pos: Sequence[float, float, float],
) -> [float | np.ndarray, float | np.ndarray]:
    """
    Converts visible elevation and azimuth to geographic coordinates with given height of the visible point.

    :param el: Elevation of observation(s) in deg.
    :param az: Azimuth of observation(s) in deg.
    :param height: Height of observable point(s) in km.
    :param pos: Geographical coordinates and height in m of the telescope
    :return: Observable geographical latitude and longitude.
    """
    d_srange = srange(np.deg2rad(90 - el), height * 1e3)
    obs_lat, obs_lon, _ = aer2geodetic(az, el, d_srange, *pos, ell=Ellipsoid(R_EARTH, R_EARTH))
    return obs_lat, obs_lon


def elaz_mesh(gridsize: int) -> [np.ndarray, np.ndarray]:
    """
    :param gridsize: Grid resolution.
    :return: Meshgrid of elevation and azimuth for all visible sky.
    """
    el = np.linspace(0, 90, gridsize, endpoint=True)
    az = np.linspace(0, 360, gridsize)
    els, azs = np.meshgrid(el, az)
    return els, azs


def eval_layer(
    el: float | np.ndarray,
    az: float | np.ndarray,
    nside: int,
    position: Sequence[float, float, float],
    hbot: float,
    htop: float,
    nlayers: int,
    obs_pixels: Sequence[int],
    data: float | np.ndarray,
    layer: int | None = None,
):
    """
    Calculates interpolated values on healpix grid.

    :param el: Elevation.
    :param az: Azimuth.
    :param nside: Resolution of healpix grid.
    :param position:
    :param hbot: Lower limit in [km] of the layer.
    :param htop: Upper limit in [km] of the layer.
    :param nlayers: Number of sub-layers used for intermediate calculations.
    :param obs_pixels: List of pixel indices inside the visible disk on healpix sphere.
    :param data: A data to interpolate.
    :param layer: Number of sublayer from the precalculated sublayers.
                  If None - an average over all layers is returned.
    :return: Interpolated values at specified elevation and azimuth.
    """
    check_elaz_shape(el, az)
    heights = np.linspace(hbot, htop, nlayers)
    map_ = np.zeros(hp.nside2npix(nside)) + hp.UNSEEN
    if layer is None:
        res = np.empty((*el.shape, nlayers))
        for i in range(nlayers):
            map_[obs_pixels] = data[:, i]
            obs_lat, obs_lon = sky2ll(el, az, heights[i], position)
            res[:, :, i] = hp.pixelfunc.get_interp_val(
                map_, obs_lon, obs_lat, lonlat=True
            )
        return res.mean(axis=2)
    elif isinstance(layer, int) and layer < nlayers + 1:
        map_[obs_pixels] = data[:, layer]
        obs_lat, obs_lon = sky2ll(el, az, heights[layer], position)
        res = hp.pixelfunc.get_interp_val(map_, obs_lon, obs_lat, lonlat=True)
        return res
    else:
        raise ValueError(
            f"The layer value must be integer and be in range [0, {nlayers - 1}]"
        )


def pic2vid(
    imdir: str,
    saveto: str,
    fps: int = 20,
    desc: str | None = None,
    codec: str = "libx264",
):
    """
    Renders existing set of pictures to mp4 video.
    :param imdir: Location of images.
    :param saveto: Path with name to where save the file.
    :param fps: Framerate - frames per second.
    :param desc: Description of a progressbar. If None - the progressbar will not appear.
    :param codec: Codec to use for video rendering.
    """
    if not saveto.endswith(".mp4"):
        saveto += ".mp4"
    desc = desc or "Rendering video"
    cmd = [
        "ffmpeg",
        "-r",
        f"{fps}",
        "-i",
        os.path.join(imdir, "%06d.png"),
        "-vcodec",
        codec,
        "-y",
        saveto,
    ]
    ff = FfmpegProgress(cmd)
    with tqdm(total=100, position=0, desc=desc, leave=True) as pbar:
        for progress in ff.run_command_with_progress():
            pbar.update(progress - pbar.n)


def get_atten_from_frame(args):
    return args[0].atten(*args[1:])


def get_refr_from_frame(args):
    return args[0].refr(*args[1:])
