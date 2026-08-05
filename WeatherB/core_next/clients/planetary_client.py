
# WeatherB/core_next/clients/planetary_client.py

"""
planetary_client.py

Client for Microsoft Planetary Computer STAC API.

Responsibilities
----------------
- Connect to the Planetary Computer STAC catalog.
- Search satellite scenes using spatial and temporal constraints.
- Apply cloud-cover filtering.
- Select the best available scene.
- Keep STAC-specific implementation details away from services.

This client does NOT:
- Load raster data.
- Preprocess imagery.
- Run AI models.
- Calculate climate metrics.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional, Sequence

import planetary_computer
import pystac_client


class PlanetaryClient:
    """
    Thin client around the Microsoft Planetary Computer
    STAC API.
    """

    STAC_URL = (
        "https://planetarycomputer.microsoft.com/"
        "api/stac/v1"
    )

    # ---------------------------------------------------
    # Supported collections
    # ---------------------------------------------------

    SENTINEL_COLLECTION = "sentinel-2-l2a"

    LANDSAT_COLLECTION = "landsat-c2-l2"

    # ---------------------------------------------------
    # Initialization
    # ---------------------------------------------------

    def __init__(self):

        self.catalog = pystac_client.Client.open(
            self.STAC_URL,
            modifier=planetary_computer.sign_inplace,
        )

    # ===================================================
    # Validation
    # ===================================================

    @staticmethod
    def _validate_bbox(
        bbox: Sequence[float],
    ) -> List[float]:

        if len(bbox) != 4:

            raise ValueError(
                "bbox must contain exactly four values: "
                "[min_lon, min_lat, max_lon, max_lat]"
            )

        try:

            min_lon = float(bbox[0])
            min_lat = float(bbox[1])
            max_lon = float(bbox[2])
            max_lat = float(bbox[3])

        except (TypeError, ValueError) as exc:

            raise ValueError(
                "bbox values must be numeric."
            ) from exc

        if not -180 <= min_lon <= 180:
            raise ValueError("min_lon must be between -180 and 180.")

        if not -180 <= max_lon <= 180:
            raise ValueError("max_lon must be between -180 and 180.")

        if not -90 <= min_lat <= 90:
            raise ValueError("min_lat must be between -90 and 90.")

        if not -90 <= max_lat <= 90:
            raise ValueError("max_lat must be between -90 and 90.")

        if min_lon >= max_lon:

            raise ValueError(
                "min_lon must be smaller than max_lon."
            )

        if min_lat >= max_lat:

            raise ValueError(
                "min_lat must be smaller than max_lat."
            )

        return [
            min_lon,
            min_lat,
            max_lon,
            max_lat,
        ]

    # ===================================================
    # Generic Search
    # ===================================================

    def search(
        self,
        bbox,
        collection: str,
        cloud_limit: Optional[float] = None,
        days_back: int = 30,
        max_items: Optional[int] = 10,
    ) -> List:
        """
        Search Planetary Computer for satellite scenes.

        Parameters
        ----------
        bbox:
            [min_lon, min_lat, max_lon, max_lat]

        collection:
            STAC collection ID.

        cloud_limit:
            Maximum allowed eo:cloud_cover percentage.

        days_back:
            Number of days to search backwards from now.

        max_items:
            Maximum number of scenes to retrieve.

        Returns
        -------
        list
            Matching pystac.Item objects.
        """

        bbox = self._validate_bbox(bbox)

        if not collection:
            raise ValueError(
                "collection must be provided."
            )

        if days_back <= 0:
            raise ValueError(
                "days_back must be greater than zero."
            )

        if cloud_limit is not None:

            if not 0 <= cloud_limit <= 100:

                raise ValueError(
                    "cloud_limit must be between 0 and 100."
                )

        if max_items is not None:

            if max_items <= 0:

                raise ValueError(
                    "max_items must be greater than zero."
                )

        # ------------------------------------------------
        # UTC time range
        # ------------------------------------------------

        end_date = datetime.now(timezone.utc)

        start_date = (
            end_date -
            timedelta(days=days_back)
        )

        datetime_range = (
            f"{start_date:%Y-%m-%dT%H:%M:%SZ}"
            f"/"
            f"{end_date:%Y-%m-%dT%H:%M:%SZ}"
        )

        # ------------------------------------------------
        # STAC query
        # ------------------------------------------------

        search_kwargs = {

            "collections": [
                collection
            ],

            "bbox": bbox,

            "datetime": datetime_range,
        }

        if cloud_limit is not None:

            search_kwargs["query"] = {

                "eo:cloud_cover": {

                    "lt": cloud_limit

                }

            }

        if max_items is not None:

            search_kwargs["max_items"] = max_items

        try:

            search = self.catalog.search(
                **search_kwargs
            )

            return list(
                search.items()
            )

        except Exception as exc:

            raise RuntimeError(
                "Planetary Computer STAC search failed. "
                f"Collection='{collection}', "
                f"bbox={bbox}, "
                f"days_back={days_back}, "
                f"cloud_limit={cloud_limit}."
            ) from exc

    # ===================================================
    # Sentinel-2 Search
    # ===================================================

    def search_sentinel(
        self,
        bbox,
        cloud_limit: float = 10,
        days_back: int = 30,
        max_items: int = 10,
    ) -> List:
        """
        Search Sentinel-2 L2A scenes.
        """

        return self.search(

            bbox=bbox,

            collection=self.SENTINEL_COLLECTION,

            cloud_limit=cloud_limit,

            days_back=days_back,

            max_items=max_items,
        )

    # ===================================================
    # Landsat Search
    # ===================================================

    def search_landsat(
        self,
        bbox,
        cloud_limit: float = 20,
        days_back: int = 30,
        max_items: int = 10,
    ) -> List:
        """
        Search Landsat Collection 2 Level-2 scenes.
        """

        return self.search(

            bbox=bbox,

            collection=self.LANDSAT_COLLECTION,

            cloud_limit=cloud_limit,

            days_back=days_back,

            max_items=max_items,
        )

    # ===================================================
    # Best Scene Selection
    # ===================================================

    @staticmethod
    def _select_best_scene(
        items,
    ):
        """
        Select the best scene.

        Priority
        --------
        1. Lowest cloud cover.
        2. Most recent acquisition date.

        Returns
        -------
        pystac.Item or None
        """

        if not items:
            return None

        def sort_key(item):

            cloud_cover = item.properties.get(
                "eo:cloud_cover",
                100.0,
            )

            if cloud_cover is None:
                cloud_cover = 100.0

            acquisition_time = (

                item.datetime.timestamp()

                if item.datetime is not None

                else 0

            )

            return (
                float(cloud_cover),
                -acquisition_time,
            )

        return min(
            items,
            key=sort_key,
        )

    # ===================================================
    # Best Sentinel-2 Scene
    # ===================================================

    def get_best_sentinel_scene(
        self,
        bbox,
        cloud_limit: float = 10,
        days_back: int = 30,
    ):
        """
        Find the best Sentinel-2 scene.
        """

        items = self.search_sentinel(

            bbox=bbox,

            cloud_limit=cloud_limit,

            days_back=days_back,

            max_items=10,
        )

        return self._select_best_scene(
            items
        )

    # ===================================================
    # Best Landsat Scene
    # ===================================================

    def get_best_landsat_scene(
        self,
        bbox,
        cloud_limit: float = 20,
        days_back: int = 30,
    ):
        """
        Find the best Landsat scene.
        """

        items = self.search_landsat(

            bbox=bbox,

            cloud_limit=cloud_limit,

            days_back=days_back,

            max_items=10,
        )

        return self._select_best_scene(
            items
        )

    # ===================================================
    # Generic Best Scene
    # ===================================================

    def get_best_scene(
        self,
        bbox,
        collection: str,
        cloud_limit: Optional[float] = None,
        days_back: int = 30,
    ):
        """
        Generic best-scene selector.

        Higher-level providers can use this method
        when they explicitly specify a collection.
        """

        items = self.search(

            bbox=bbox,

            collection=collection,

            cloud_limit=cloud_limit,

            days_back=days_back,

            max_items=10,
        )

        return self._select_best_scene(
            items
        )