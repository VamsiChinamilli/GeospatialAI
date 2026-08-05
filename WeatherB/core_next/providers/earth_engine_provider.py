# WeatherB/core_next/providers/earth_engine_provider.py

"""
earth_engine_provider.py

Earth Engine data provider for the Urban Climate AI pipeline.

Responsibilities
----------------
- Initialize Google Earth Engine.
- Search Sentinel-2 imagery.
- Search Landsat 8 thermal imagery.
- Select suitable scenes.
- Download small raster regions as NumPy arrays.
- Return imagery + metadata to the service layer.

This provider does NOT:
- Run PyTorch models.
- Preprocess model tensors.
- Calculate land-cover percentages.
- Calculate LST predictions.
- Call LLMs.
- Handle WebSockets.
"""

from datetime import datetime, timedelta
from io import BytesIO
from typing import Optional

import ee
import numpy as np
import requests


class EarthEngineProvider:
    """
    Provider responsible for retrieving satellite imagery
    from Google Earth Engine.
    """

    # ---------------------------------------------------
    # Earth Engine configuration
    # ---------------------------------------------------

    PROJECT_ID = "thefirstproject-496908"

    # Sentinel-2 Surface Reflectance
    SENTINEL_COLLECTION = (
        "COPERNICUS/S2_SR_HARMONIZED"
    )

    # Landsat 8 Collection 2 Level-2
    LANDSAT_COLLECTION = (
        "LANDSAT/LC08/C02/T1_L2"
    )

    # Sentinel bands used by the trained model.
    #
    # Model training order:
    # B4, B3, B2, B8
    #
    # Therefore:
    # [Red, Green, Blue, NIR]
    SENTINEL_BANDS = [
        "B4",
        "B3",
        "B2",
        "B8",
    ]

    # Landsat thermal band
    THERMAL_BAND = "ST_B10"

    # ---------------------------------------------------
    # Initialization
    # ---------------------------------------------------

    def __init__(self):

        self._initialize()

    # ---------------------------------------------------
    # Earth Engine initialization
    # ---------------------------------------------------

    @classmethod
    def _initialize(cls):

        try:

            ee.Initialize(
                project=cls.PROJECT_ID
            )

        except Exception as exc:

            raise RuntimeError(
                "Failed to initialize Google Earth Engine."
            ) from exc

    # ===================================================
    # Validation
    # ===================================================

    @staticmethod
    def _validate_bbox(bbox):

        if bbox is None:

            raise ValueError(
                "bbox cannot be None."
            )

        if len(bbox) != 4:

            raise ValueError(
                "bbox must be "
                "[min_lon, min_lat, max_lon, max_lat]."
            )

        min_lon, min_lat, max_lon, max_lat = bbox

        if min_lon >= max_lon:

            raise ValueError(
                "min_lon must be smaller than max_lon."
            )

        if min_lat >= max_lat:

            raise ValueError(
                "min_lat must be smaller than max_lat."
            )

        if not (
            -180 <= min_lon <= 180
            and
            -180 <= max_lon <= 180
            and
            -90 <= min_lat <= 90
            and
            -90 <= max_lat <= 90
        ):

            raise ValueError(
                "bbox coordinates are outside valid "
                "longitude/latitude ranges."
            )

    # ===================================================
    # Geometry
    # ===================================================

    @staticmethod
    def _geometry_from_bbox(bbox):

        return ee.Geometry.Rectangle(
            [
                bbox[0],
                bbox[1],
                bbox[2],
                bbox[3],
            ]
        )

    # ===================================================
    # Date range
    # ===================================================

    @staticmethod
    def _date_range(days_back):

        if days_back <= 0:

            raise ValueError(
                "days_back must be greater than zero."
            )

        end_date = datetime.utcnow()

        start_date = (
            end_date -
            timedelta(days=days_back)
        )

        return (
            f"{start_date:%Y-%m-%d}",
            f"{end_date:%Y-%m-%d}"
        )

    # ===================================================
    # Sentinel-2 search
    # ===================================================

    def search_sentinel(
        self,
        bbox,
        cloud_limit=10,
        days_back=90,
    ):
        """
        Search Sentinel-2 imagery intersecting bbox.

        Returns
        -------
        ee.ImageCollection
        """

        self._validate_bbox(bbox)

        geometry = self._geometry_from_bbox(
            bbox
        )

        start_date, end_date = (
            self._date_range(days_back)
        )

        collection = (

            ee.ImageCollection(
                self.SENTINEL_COLLECTION
            )

            .filterBounds(
                geometry
            )

            .filterDate(
                start_date,
                end_date
            )

            .filter(
                ee.Filter.lt(
                    "CLOUDY_PIXEL_PERCENTAGE",
                    cloud_limit
                )
            )

            .sort(
                "CLOUDY_PIXEL_PERCENTAGE"
            )
        )

        return collection

    # ===================================================
    # Best Sentinel scene
    # ===================================================

    def get_best_sentinel_scene(
        self,
        bbox,
        cloud_limit=10,
        days_back=90,
    ):
        """
        Return the least-cloudy Sentinel-2 image.
        """

        collection = self.search_sentinel(

            bbox=bbox,

            cloud_limit=cloud_limit,

            days_back=days_back,
        )

        count = collection.size().getInfo()

        if count == 0:

            return None

        return ee.Image(
            collection.first()
        )

    # ===================================================
    # Landsat thermal search
    # ===================================================

    def search_landsat(
        self,
        bbox,
        cloud_limit=20,
        days_back=90,
    ):
        """
        Search Landsat 8 Collection 2 Level-2
        imagery for thermal information.
        """

        self._validate_bbox(bbox)

        geometry = self._geometry_from_bbox(
            bbox
        )

        start_date, end_date = (
            self._date_range(days_back)
        )

        collection = (

            ee.ImageCollection(
                self.LANDSAT_COLLECTION
            )

            .filterBounds(
                geometry
            )

            .filterDate(
                start_date,
                end_date
            )

            .filter(
                ee.Filter.lt(
                    "CLOUD_COVER",
                    cloud_limit
                )
            )

            .sort(
                "CLOUD_COVER"
            )
        )

        return collection

    # ===================================================
    # Best Landsat thermal scene
    # ===================================================

    def get_best_landsat_scene(
        self,
        bbox,
        cloud_limit=20,
        days_back=90,
    ):
        """
        Return the least-cloudy Landsat 8 scene.
        """

        collection = self.search_landsat(

            bbox=bbox,

            cloud_limit=cloud_limit,

            days_back=days_back,
        )

        count = collection.size().getInfo()

        if count == 0:

            return None

        return ee.Image(
            collection.first()
        )

    # ===================================================
    # Download NumPy array
    # ===================================================

    @staticmethod
    def _download_numpy(
        image,
        bbox,
        bands,
        scale,
    ):
        """
        Download a small Earth Engine image region
        directly into a NumPy array.

        Returns
        -------
        numpy.ndarray
        """

        geometry = ee.Geometry.Rectangle(
            bbox
        )

        url = image.getDownloadURL({

            "bands": bands,

            "region": geometry,

            "scale": scale,

            "format": "NPY",

        })

        response = requests.get(
            url,
            timeout=300
        )

        response.raise_for_status()

        data = np.load(
            BytesIO(response.content)
        )

        return data

    # ===================================================
    # Sentinel raster
    # ===================================================

    def get_sentinel_raster(
        self,
        bbox,
        cloud_limit=10,
        days_back=90,
        scale=10,
    ):
        """
        Retrieve Sentinel-2 raster data.

        Returns
        -------
        dict
            {
                "bands": np.ndarray,
                "scene": ee.Image,
                "metadata": dict
            }
        """

        scene = self.get_best_sentinel_scene(

            bbox=bbox,

            cloud_limit=cloud_limit,

            days_back=days_back,
        )

        if scene is None:

            raise RuntimeError(
                "No suitable Sentinel-2 imagery "
                "was found for the requested bbox."
            )

        bands = self._download_numpy(

            image=scene,

            bbox=bbox,

            bands=self.SENTINEL_BANDS,

            scale=scale,
        )

        return {

            "bands": bands,

            "scene": scene,

            "metadata": {

                "provider":
                    "Google Earth Engine",

                "sensor":
                    "Sentinel-2 SR Harmonized",

                "bands":
                    self.SENTINEL_BANDS,

                "resolution":
                    scale,

            },

        }

    # ===================================================
    # Landsat thermal raster
    # ===================================================

    def get_thermal_raster(
        self,
        bbox,
        cloud_limit=20,
        days_back=90,
        scale=30,
    ):
        """
        Retrieve Landsat 8 Surface Temperature.

        The ST_B10 scale factor and offset are applied
        here so that the returned raster is in Kelvin.

        Returns
        -------
        dict
            {
                "thermal": np.ndarray,
                "scene": ee.Image,
                "metadata": dict
            }
        """

        scene = self.get_best_landsat_scene(

            bbox=bbox,

            cloud_limit=cloud_limit,

            days_back=days_back,
        )

        if scene is None:

            raise RuntimeError(
                "No suitable Landsat thermal imagery "
                "was found for the requested bbox."
            )

        thermal_image = (

            scene

            .select(
                self.THERMAL_BAND
            )

            .multiply(
                0.00341802
            )

            .add(
                149.0
            )

            .rename(
                "temperature"
            )
        )

        thermal = self._download_numpy(

            image=thermal_image,

            bbox=bbox,

            bands=["temperature"],

            scale=scale,
        )

        # NPY output may be structured depending
        # on Earth Engine response.
        if thermal.dtype.names:

            thermal = thermal[
                "temperature"
            ]

        if thermal.ndim == 3:

            thermal = thermal[0]

        return {

            "thermal": thermal,

            "scene": scene,

            "metadata": {

                "provider":
                    "Google Earth Engine",

                "sensor":
                    "Landsat 8 Collection 2 Level-2",

                "band":
                    "ST_B10",

                "resolution":
                    scale,

                "temperature_unit":
                    "Kelvin",

            },

        }

    # ===================================================
    # Combined climate input
    # ===================================================

    def get_climate_data(
        self,
        bbox,
        sentinel_cloud_limit=10,
        thermal_cloud_limit=20,
        days_back=90,
    ):
        """
        Retrieve all satellite inputs required by
        the AI processing pipeline.

        Returns
        -------
        dict
        """

        sentinel = self.get_sentinel_raster(

            bbox=bbox,

            cloud_limit=sentinel_cloud_limit,

            days_back=days_back,

            scale=10,
        )

        thermal = self.get_thermal_raster(

            bbox=bbox,

            cloud_limit=thermal_cloud_limit,

            days_back=days_back,

            scale=30,
        )

        return {

            "sentinel": sentinel,

            "thermal": thermal,

            "bbox": bbox,

        }