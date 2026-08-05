"""
raster_service.py

Raster acquisition layer for the Urban Climate AI backend.

Responsibilities
----------------
- Request satellite raster data from EarthEngineProvider.
- Validate the returned raster structure.
- Validate Sentinel and thermal dimensions/channels.
- Return raw raster data to AIProcessingService.

This service does NOT:
- Normalize model inputs.
- Resize model inputs.
- Convert NumPy arrays to PyTorch tensors.
- Run ML models.
- Calculate land-cover percentages.
- Estimate LST.
- Generate LLM responses.
- Handle HTTP requests.
- Handle WebSocket connections.

Architecture
------------

EarthEngineProvider
        ↓
RasterService
        ↓
raw validated raster
        ↓
AIProcessingService
        ↓
preprocessing + inference
"""


from typing import Any, Dict

import numpy as np

from core_next.providers.earth_engine_provider import (
    EarthEngineProvider,
)


class RasterService:
    """
    Fetches and validates raw satellite raster data.

    Model-specific preprocessing belongs to
    AIProcessingService.
    """

    # ============================================================
    # Initialization
    # ============================================================

    def __init__(self):

        self.provider = EarthEngineProvider()

    # ============================================================
    # Public API
    # ============================================================

    def fetch_raster(
        self,
        bbox,
        sentinel_cloud_limit=10,
        thermal_cloud_limit=20,
        days_back=90,
    ) -> Dict[str, Any]:
        """
        Fetch raw climate raster data.

        Parameters
        ----------
        bbox:
            Bounding box in the form:

                [min_lon, min_lat, max_lon, max_lat]

        Returns
        -------
        dict

            {
                "sentinel": {
                    "bands": np.ndarray,
                    "metadata": ...
                },

                "thermal": {
                    "thermal": np.ndarray,
                    "metadata": ...
                },

                "bbox": [...]
            }

        Important
        ---------
        No normalization or resizing occurs here.

        AIProcessingService owns all model-specific
        preprocessing.
        """

        # --------------------------------------------------------
        # Validate BBOX
        # --------------------------------------------------------

        self._validate_bbox(
            bbox
        )

        # --------------------------------------------------------
        # Fetch raw data from provider
        # --------------------------------------------------------

        data = self.provider.get_climate_data(

            bbox=bbox,

            sentinel_cloud_limit=(
                sentinel_cloud_limit
            ),

            thermal_cloud_limit=(
                thermal_cloud_limit
            ),

            days_back=days_back,
        )

        # --------------------------------------------------------
        # Validate provider response
        # --------------------------------------------------------

        if not isinstance(
            data,
            dict,
        ):

            raise RuntimeError(
                "EarthEngineProvider returned "
                "an invalid response."
            )

        if "sentinel" not in data:

            raise RuntimeError(
                "Provider response is missing "
                "'sentinel' data."
            )

        if "thermal" not in data:

            raise RuntimeError(
                "Provider response is missing "
                "'thermal' data."
            )

        # --------------------------------------------------------
        # Validate Sentinel data
        # --------------------------------------------------------

        sentinel_data = data[
            "sentinel"
        ]

        if not isinstance(
            sentinel_data,
            dict,
        ):

            raise RuntimeError(
                "Sentinel data must be a dictionary."
            )

        if "bands" not in sentinel_data:

            raise RuntimeError(
                "Sentinel data is missing "
                "'bands'."
            )

        sentinel = np.asarray(
            sentinel_data["bands"]
        )

        self._validate_sentinel(
            sentinel
        )

        # --------------------------------------------------------
        # Validate thermal data
        # --------------------------------------------------------

        thermal_data = data[
            "thermal"
        ]

        if not isinstance(
            thermal_data,
            dict,
        ):

            raise RuntimeError(
                "Thermal data must be a dictionary."
            )

        if "thermal" not in thermal_data:

            raise RuntimeError(
                "Thermal data is missing "
                "'thermal'."
            )

        thermal = np.asarray(
            thermal_data["thermal"],
            dtype=np.float32,
        )

        self._validate_thermal(
            thermal
        )

        # --------------------------------------------------------
        # Return raw validated data
        # --------------------------------------------------------

        return {

            "bbox": data.get(
                "bbox",
                bbox,
            ),

            "sentinel": {

                "bands": sentinel,

                "metadata": sentinel_data.get(
                    "metadata",
                    {},
                ),

            },

            "thermal": {

                "thermal": thermal,

                "metadata": thermal_data.get(
                    "metadata",
                    {},
                ),

            },

        }

    # ============================================================
    # Sentinel Validation
    # ============================================================

    @staticmethod
    def _validate_sentinel(sentinel: np.ndarray,) -> None:
        if getattr(sentinel.dtype,"names",None):
            required_fields = ("B4","B3","B2","B8",)
            available_fields = sentinel.dtype.names

            for field in required_fields:
                if field not in available_fields:

                    raise RuntimeError(
                    "Sentinel raster is missing "
                    f"required band '{field}'. "
                    f"Available bands: "
                    f"{available_fields}"
                )

            if sentinel.ndim != 2:

                raise RuntimeError(
                "Structured Sentinel raster must have "
                "shape (height, width). "
                f"Received: {sentinel.shape}"
            )

            height = sentinel.shape[0]
            width = sentinel.shape[1]

            if height <= 0 or width <= 0:

                raise RuntimeError(
                "Sentinel raster has invalid "
                "spatial dimensions."
            )

        # Validate every required band

            for field in required_fields:

                band = sentinel[field]

                if not np.all(
                np.isfinite(band)
            ):

                    raise RuntimeError(
                    f"Sentinel band '{field}' contains "
                    "NaN or infinite values."
                )

            return

    # --------------------------------------------------------
    # Normal 4-channel array
    # --------------------------------------------------------

        if sentinel.ndim != 3:

            raise RuntimeError(
            "Sentinel raster must have shape "
            "(bands, height, width). "
            f"Received: {sentinel.shape}"
        )

        if sentinel.shape[0] != 4:

            raise RuntimeError(
            "Sentinel raster must contain "
            f"exactly 4 bands. "
            f"Received: {sentinel.shape[0]}"
        )

        height = sentinel.shape[1]
        width = sentinel.shape[2]

        if height <= 0 or width <= 0:

            raise RuntimeError(
            "Sentinel raster has invalid "
            "spatial dimensions."
        )

        if not np.all(
        np.isfinite(sentinel)
    ):

            raise RuntimeError(
            "Sentinel raster contains "
            "NaN or infinite values."
        )
    # ============================================================
    # Thermal Validation
    # ============================================================

    @staticmethod
    def _validate_thermal(
        thermal: np.ndarray,
    ) -> None:
        """
        Validate thermal raster.

        Expected:

            (H, W)
        """

        # --------------------------------------------------------
        # Remove a possible single-channel dimension
        # --------------------------------------------------------

        if thermal.ndim == 3:

            if thermal.shape[0] == 1:

                thermal = thermal[0]

            else:

                raise RuntimeError(

                    "Thermal raster contains multiple "
                    "channels. Only one thermal band "
                    "is expected."
                )

        if thermal.ndim != 2:

            raise RuntimeError(

                "Thermal raster must have shape "
                "(height, width). "

                f"Received: {thermal.shape}"
            )

        height = thermal.shape[0]
        width = thermal.shape[1]

        if height <= 0 or width <= 0:

            raise RuntimeError(
                "Thermal raster has invalid "
                "spatial dimensions."
            )

        if not np.all(
            np.isfinite(thermal)
        ):

            raise RuntimeError(
                "Thermal raster contains "
                "NaN or infinite values."
            )

    # ============================================================
    # BBOX Validation
    # ============================================================

    @staticmethod
    def _validate_bbox(
        bbox,
    ) -> None:
        """
        Validate:

            [min_lon, min_lat, max_lon, max_lat]
        """

        if bbox is None:

            raise ValueError(
                "bbox cannot be None."
            )

        if not isinstance(
            bbox,
            (list, tuple),
        ):

            raise TypeError(
                "bbox must be a list or tuple."
            )

        if len(bbox) != 4:

            raise ValueError(

                "bbox must contain exactly "
                "four values: "

                "[min_lon, min_lat, "
                "max_lon, max_lat]"
            )

        try:

            min_lon = float(
                bbox[0]
            )

            min_lat = float(
                bbox[1]
            )

            max_lon = float(
                bbox[2]
            )

            max_lat = float(
                bbox[3]
            )

        except (
            TypeError,
            ValueError,
        ) as exc:

            raise ValueError(
                "bbox values must be numeric."
            ) from exc

        if min_lon >= max_lon:

            raise ValueError(
                "min_lon must be smaller "
                "than max_lon."
            )

        if min_lat >= max_lat:

            raise ValueError(
                "min_lat must be smaller "
                "than max_lat."
            )

        if not (
            -180.0 <= min_lon <= 180.0
            and
            -180.0 <= max_lon <= 180.0
        ):

            raise ValueError(
                "Longitude must be between "
                "-180 and 180."
            )

        if not (
            -90.0 <= min_lat <= 90.0
            and
            -90.0 <= max_lat <= 90.0
        ):

            raise ValueError(
                "Latitude must be between "
                "-90 and 90."
            )