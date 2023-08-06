"""Raster to Matrix conversion."""
from pathlib import Path

import rasterio
from rasterio.io import DatasetReader


def load_raster(path: str | Path) -> DatasetReader:
    """Load the raster at path using rasterio.

    Parameters
    ----------
    path : string | pathlib.Path
        Path to raster

    Returns
    -------
    rasterio.io.DatasetReader
        The raster as a DatasetReader instance
    """
    return rasterio.open(path)
