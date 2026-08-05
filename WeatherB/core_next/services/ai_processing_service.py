
"""
ai_processing_service.py

AI processing layer for the Urban Climate AI backend.

Responsibilities
----------------
- Receive raw satellite data from the raster/provider layer.
- Normalize Sentinel and thermal data using the same
  preprocessing used during Land-Cover U-Net training.
- Prepare the 5-channel model input.
- Run Land-Cover U-Net inference.
- Return JSON-friendly model output.

Land-Cover U-Net input:

    B4
    B3
    B2
    B8
    Thermal

Shape:

    (1, 5, 256, 256)

This service does NOT:
- Run LST U-Net.
- Estimate final LST.
- Run the LST Expert System.
- Call LLMs.
- Handle HTTP requests.
- Handle WebSockets.
"""

import numpy as np
import torch
from pathlib import Path
import sys
import torch.nn.functional as F


from ..utils.model_loader import ModelLoader


class AIProcessingService:
    """
    Handles preprocessing and inference for the
    trained Land-Cover U-Net.
    """

    PATCH_SIZE = 256

    NUM_CLASSES = 11

    SENTINEL_CHANNELS = 4

    TOTAL_INPUT_CHANNELS = 5

    # ============================================================
    # Initialization
    # ============================================================

    def __init__(self):

        self.device = torch.device("cpu")

        # Only Land-Cover U-Net is loaded.
        #
        # LST U-Net has been removed because final LST
        # estimation is now handled by the LST Expert System.
        self.unet = ModelLoader.load_unet()

        self.unet.to(self.device)

        self.unet.eval()

    # ============================================================
    # Sentinel normalization
    # ============================================================

    @staticmethod
    def _normalize_sentinel(
        sentinel
    ):
        """
        Normalize Sentinel-2 data.

        Expected source representation:

            structured array containing:

                B4
                B3
                B2
                B8

        Output:

            (4, H, W)

        Channel order:

            B4, B3, B2, B8
        """

        # --------------------------------------------------------
        # Structured Sentinel array
        # --------------------------------------------------------

        if getattr(
            sentinel.dtype,
            "names",
            None
        ):

            required_fields = (
                "B4",
                "B3",
                "B2",
                "B8",
            )

            available_fields = sentinel.dtype.names

            for field in required_fields:

                if field not in available_fields:

                    raise ValueError(
                        "Sentinel data is missing "
                        f"required band '{field}'. "
                        f"Available bands: "
                        f"{available_fields}"
                    )

            sentinel = np.stack(
                [
                    sentinel["B4"],
                    sentinel["B3"],
                    sentinel["B2"],
                    sentinel["B8"],
                ],
                axis=0
            )

        else:

            sentinel = np.asarray(
                sentinel
            )

            if sentinel.ndim != 3:

                raise ValueError(
                    "Sentinel raster must have shape "
                    "(4, H, W). "
                    f"Received: {sentinel.shape}"
                )

        sentinel = sentinel.astype(
            np.float32,
            copy=False
        )

        if sentinel.shape[0] != 4:

            raise ValueError(
                "Sentinel raster must contain exactly "
                f"4 channels. Received: {sentinel.shape}"
            )

        # --------------------------------------------------------
        # Sentinel-2 reflectance normalization
        # --------------------------------------------------------

        sentinel /= 10000.0

        sentinel = np.clip(
            sentinel,
            0.0,
            1.0
        )

        return sentinel

    # ============================================================
    # Thermal normalization
    # ============================================================

    @staticmethod
    def _normalize_thermal(
        thermal
    ):
        """
        Normalize Landsat thermal data using the
        same normalization used during training.

        Training:

            clip(250, 350)

            (thermal - 250) / 100

        Output:

            (H, W)
        """

        thermal = np.asarray(
            thermal,
            dtype=np.float32
        )

        # --------------------------------------------------------
        # Remove single channel dimension if present
        # --------------------------------------------------------

        if thermal.ndim == 3:

            if thermal.shape[0] == 1:

                thermal = thermal[0]

            else:

                raise ValueError(
                    "Thermal raster contains multiple "
                    "channels. Expected one thermal band."
                )

        if thermal.ndim != 2:

            raise ValueError(
                "Thermal raster must have shape "
                "(H, W). "
                f"Received: {thermal.shape}"
            )

        # --------------------------------------------------------
        # Training normalization
        # --------------------------------------------------------

        thermal = np.clip(
            thermal,
            250.0,
            350.0
        )

        thermal = (
            thermal - 250.0
        ) / 100.0

        return thermal.astype(
            np.float32
        )

    # ============================================================
    # Resize tensor
    # ============================================================

    @classmethod
    def _resize_tensor(
        cls,
        tensor
    ):
        """
        Resize a tensor from:

            (C, H, W)

        to:

            (C, 256, 256)
        """

        if tensor.ndim != 3:

            raise ValueError(
                "Expected tensor with shape "
                "(C, H, W). "
                f"Received: {tensor.shape}"
            )

        tensor = tensor.unsqueeze(0)

        tensor = F.interpolate(
            tensor,
            size=(
                cls.PATCH_SIZE,
                cls.PATCH_SIZE
            ),
            mode="bilinear",
            align_corners=False
        )

        return tensor.squeeze(0)

    # ============================================================
    # Prepare Sentinel
    # ============================================================

    @classmethod
    def _prepare_sentinel(
        cls,
        sentinel
    ):
        """
        Prepare normalized Sentinel data.

        Output:

            (4, 256, 256)
        """

        sentinel = cls._normalize_sentinel(
            sentinel
        )

        tensor = torch.from_numpy(
            sentinel
        ).float()

        tensor = cls._resize_tensor(
            tensor
        )

        return tensor

    # ============================================================
    # Prepare Thermal
    # ============================================================

    @classmethod
    def _prepare_thermal(
        cls,
        thermal
    ):
        """
        Prepare normalized thermal data.

        Output:

            (1, 256, 256)
        """

        thermal = cls._normalize_thermal(
            thermal
        )

        tensor = torch.from_numpy(
            thermal
        ).float()

        tensor = tensor.unsqueeze(0)

        tensor = cls._resize_tensor(
            tensor
        )

        return tensor

    # ============================================================
    # Build 5-channel U-Net input
    # ============================================================

    @classmethod
    def _prepare_unet_input(
        cls,
        sentinel,
        thermal
    ):
        """
        Build the 5-channel Land-Cover U-Net input.

        Channel order:

            0 -> B4
            1 -> B3
            2 -> B2
            3 -> B8
            4 -> Thermal

        Output:

            (1, 5, 256, 256)
        """

        sentinel_tensor = cls._prepare_sentinel(
            sentinel
        )

        thermal_tensor = cls._prepare_thermal(
            thermal
        )

        combined = torch.cat(
            [
                sentinel_tensor,
                thermal_tensor,
            ],
            dim=0
        )

        if combined.shape[0] != (
            cls.TOTAL_INPUT_CHANNELS
        ):

            raise RuntimeError(
                "Land-Cover U-Net requires exactly "
                f"{cls.TOTAL_INPUT_CHANNELS} channels. "
                f"Received: {combined.shape}"
            )

        return combined.unsqueeze(0)

    # ============================================================
    # Land-Cover inference
    # ============================================================

    @torch.no_grad()
    def predict_land_cover(
        self,
        sentinel,
        thermal
    ):
        """
        Run Land-Cover U-Net inference.

        Input:

            Sentinel:
                B4, B3, B2, B8

            Thermal:
                one thermal band

        Model input:

            (1, 5, 256, 256)

        Returns:

            logits
            probabilities
            mask
        """

        inputs = self._prepare_unet_input(
            sentinel=sentinel,
            thermal=thermal
        ).to(self.device)

        # --------------------------------------------------------
        # Safety check BEFORE model inference
        # --------------------------------------------------------

        if inputs.shape[1] != 5:

            raise RuntimeError(
                "Invalid Land-Cover U-Net input. "
                f"Expected 5 channels, got "
                f"{inputs.shape[1]}."
            )

        logits = self.unet(
            inputs
        )

        probabilities = torch.softmax(
            logits,
            dim=1
        )

        mask = torch.argmax(
            probabilities,
            dim=1
        )

        return {

            "logits":
                logits
                .cpu()
                .numpy(),

            "probabilities":
                probabilities
                .cpu()
                .numpy(),

            "mask":
                mask
                .cpu()
                .numpy(),

        }

    # ============================================================
    # Complete AI processing
    # ============================================================

    @torch.no_grad()
    def process(
        self,
        climate_data
    ):
        """
        Run Land-Cover U-Net inference.

        Expected input:

        {
            "sentinel": {
                "bands": ...
            },

            "thermal": {
                "thermal": ...
            },

            "bbox": [...]
        }

        Returns:

        {
            "land_cover": {
                "logits": ...,
                "probabilities": ...,
                "mask": ...
            },

            "bbox": [...]
        }

        LST is intentionally NOT generated here.
        The LST Expert System handles that later
        inside AnalysisService.
        """

        if not isinstance(
            climate_data,
            dict
        ):

            raise TypeError(
                "climate_data must be a dictionary."
            )

        # --------------------------------------------------------
        # Validate top-level data
        # --------------------------------------------------------

        if "sentinel" not in climate_data:

            raise KeyError(
                "climate_data is missing 'sentinel'."
            )

        if "thermal" not in climate_data:

            raise KeyError(
                "climate_data is missing 'thermal'."
            )

        sentinel_data = climate_data[
            "sentinel"
        ]

        thermal_data = climate_data[
            "thermal"
        ]

        if "bands" not in sentinel_data:

            raise KeyError(
                "Sentinel data is missing 'bands'."
            )

        if "thermal" not in thermal_data:

            raise KeyError(
                "Thermal data is missing 'thermal'."
            )

        sentinel = sentinel_data[
            "bands"
        ]

        thermal = thermal_data[
            "thermal"
        ]

        # --------------------------------------------------------
        # Land-Cover U-Net
        # --------------------------------------------------------

        land_cover = self.predict_land_cover(
            sentinel=sentinel,
            thermal=thermal
        )

        # --------------------------------------------------------
        # Final result
        # --------------------------------------------------------

        return {

            "land_cover":
                land_cover,

            "bbox":
                climate_data.get(
                    "bbox"
                ),

        }
