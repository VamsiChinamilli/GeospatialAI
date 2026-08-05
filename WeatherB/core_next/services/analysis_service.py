
"""
analysis_service.py

Analysis layer for the Urban Climate AI backend.

Responsibilities
----------------
- Consume predictions from AIProcessingService.
- Interpret land-cover segmentation masks.
- Calculate land-cover percentages.
- Identify dominant land-cover class.
- Pass land-cover information to the LST Expert System.
- Produce a clean, JSON-friendly climate analysis result.

This service does NOT:
- Download satellite imagery.
- Communicate with Earth Engine.
- Load model checkpoints.
- Run PyTorch inference.
- Call LLMs.
- Handle HTTP requests.
- Handle WebSockets.
- Use the experimental LST U-Net prediction as the final LST estimate.
"""

from typing import Dict, Any

import numpy as np

from .lst_expert_system import LSTExpertSystem


class AnalysisService:
    """
    Converts raw AI predictions into meaningful
    application-level climate analysis.
    """

    # ---------------------------------------------------
    # WorldCover classes
    # ---------------------------------------------------

    WORLDCOVER_CLASSES = {
        0: "Tree Cover",
        1: "Shrubland",
        2: "Grassland",
        3: "Cropland",
        4: "Built-up",
        5: "Bare / Sparse Vegetation",
        6: "Snow and Ice",
        7: "Permanent Water Bodies",
        8: "Herbaceous Wetland",
        9: "Mangroves",
        10: "Moss and Lichen",
    }

    # ===================================================
    # Initialization
    # ===================================================

    def __init__(self):

        self.lst_expert_system = LSTExpertSystem()

    # ===================================================
    # Land-cover analysis
    # ===================================================

    @classmethod
    def analyze_land_cover(
        cls,
        mask
    ) -> Dict[str, Any]:
        """
        Analyze a predicted land-cover mask.

        Expected shapes:

            (H, W)
            (1, H, W)
        """

        mask = np.asarray(mask)

        # ------------------------------------------------
        # Remove batch dimension
        # ------------------------------------------------

        if mask.ndim == 3:

            if mask.shape[0] == 1:

                mask = mask[0]

            else:

                raise ValueError(
                    "Land-cover mask contains multiple "
                    f"batch dimensions. Shape: {mask.shape}"
                )

        if mask.ndim != 2:

            raise ValueError(
                "Land-cover mask must have shape "
                f"(H, W). Received: {mask.shape}"
            )

        mask = mask.astype(
            np.int64,
            copy=False
        )

        total_pixels = mask.size

        if total_pixels == 0:

            raise ValueError(
                "Land-cover mask contains no pixels."
            )

        # ------------------------------------------------
        # Count classes
        # ------------------------------------------------

        unique_classes, counts = np.unique(
            mask,
            return_counts=True
        )

        class_percentages = {}

        for class_id, count in zip(
            unique_classes,
            counts
        ):

            class_id = int(class_id)

            percentage = (
                float(count)
                /
                float(total_pixels)
                *
                100.0
            )

            class_name = cls.WORLDCOVER_CLASSES.get(
                class_id,
                f"Unknown class {class_id}"
            )

            class_percentages[class_name] = round(
                percentage,
                4
            )

        # ------------------------------------------------
        # Dominant class
        # ------------------------------------------------

        dominant_index = int(
            np.argmax(counts)
        )

        dominant_class_id = int(
            unique_classes[dominant_index]
        )

        dominant_class = cls.WORLDCOVER_CLASSES.get(
            dominant_class_id,
            f"Unknown class {dominant_class_id}"
        )

        return {

            "class_percentages":
                class_percentages,

            "dominant_class_id":
                dominant_class_id,

            "dominant_class":
                dominant_class,

            "pixel_count":
                int(total_pixels),

        }

    # ===================================================
    # LST Expert System analysis
    # ===================================================

    def analyze_lst(
        self,
        land_cover_analysis: Dict[str, Any],
        environmental_context: Dict[str, float] | None = None
    ) -> Dict[str, Any]:
        """
        Estimate Land Surface Temperature using the
        rule-based LST Expert System.

        The expert system uses:

            Land-cover composition
            +
            Environmental modifiers

        instead of relying on the experimental LST U-Net.

        Parameters
        ----------
        land_cover_analysis:
            Output from analyze_land_cover().

        environmental_context:
            Optional environmental modifiers.

            Example:

            {
                "season": 1.5,
                "solar": 0.8,
                "vegetation": -0.3
            }

        Returns
        -------
        dict
            Expert-system LST analysis.
        """

        if not isinstance(
            land_cover_analysis,
            dict
        ):

            raise TypeError(
                "land_cover_analysis must be a dictionary."
            )

        class_percentages = (
            land_cover_analysis.get(
                "class_percentages",
                {}
            )
        )

        if not isinstance(
            class_percentages,
            dict
        ):

            raise TypeError(
                "class_percentages must be a dictionary."
            )

        # ------------------------------------------------
        # Run Expert System
        # ------------------------------------------------

        result = self.lst_expert_system.estimate(
    land_cover=class_percentages,
    environment=environmental_context
)

        return result

    # ===================================================
    # Complete analysis
    # ===================================================

    def analyze(
        self,
        ai_result,
        environmental_context: Dict[str, float] | None = None
    ) -> Dict[str, Any]:
        """
        Convert the complete AIProcessingService result
        into an application-level climate analysis.

        Expected input:

        {
            "land_cover": {
                "logits": ...,
                "probabilities": ...,
                "mask": ...
            },

            "lst": {
                "temperature_prediction": ...
            },

            "bbox": [...]
        }

        The "lst" model result is retained for compatibility
        and experimentation, but it is NOT used as the final
        production LST estimate.

        Returns
        -------
        dict
        """

        if not isinstance(
            ai_result,
            dict
        ):

            raise TypeError(
                "ai_result must be a dictionary."
            )

        if "land_cover" not in ai_result:

            raise KeyError(
                "ai_result is missing 'land_cover'."
            )

        land_cover_result = ai_result[
            "land_cover"
        ]

        if "mask" not in land_cover_result:

            raise KeyError(
                "Land-cover result is missing 'mask'."
            )

        # ------------------------------------------------
        # Analyze land cover
        # ------------------------------------------------

        land_cover_analysis = (
            self.analyze_land_cover(
                land_cover_result["mask"]
            )
        )

        # ------------------------------------------------
        # Expert-system LST
        # ------------------------------------------------

        lst_analysis = self.analyze_lst(
            land_cover_analysis=
                land_cover_analysis,

            environmental_context=
                environmental_context
        )

        # ------------------------------------------------
        # Optional experimental model information
        # ------------------------------------------------

        experimental_lst = None

        if "lst" in ai_result:

            lst_result = ai_result["lst"]

            if (
                isinstance(lst_result, dict)
                and
                "temperature_prediction"
                in lst_result
            ):

                experimental_prediction = np.asarray(
                    lst_result[
                        "temperature_prediction"
                    ],
                    dtype=np.float32
                )

                experimental_prediction = np.squeeze(
                    experimental_prediction
                )

                if (
                    experimental_prediction.ndim == 2
                    and
                    experimental_prediction.size > 0
                    and
                    np.all(
                        np.isfinite(
                            experimental_prediction
                        )
                    )
                ):

                    experimental_lst = {

                        "min":
                            float(
                                np.min(
                                    experimental_prediction
                                )
                            ),

                        "max":
                            float(
                                np.max(
                                    experimental_prediction
                                )
                            ),

                        "mean":
                            float(
                                np.mean(
                                    experimental_prediction
                                )
                            ),

                        "median":
                            float(
                                np.median(
                                    experimental_prediction
                                )
                            ),

                        "std":
                            float(
                                np.std(
                                    experimental_prediction
                                )
                            ),

                        "unit":
                            "Kelvin",

                        "status":
                            "experimental_only"

                    }

        # ------------------------------------------------
        # Final structured result
        # ------------------------------------------------

        result = {

            "bbox":
                ai_result.get(
                    "bbox"
                ),

            "land_cover":
                land_cover_analysis,

            "lst":
                lst_analysis,

        }

        # ------------------------------------------------
        # Keep experimental U-Net result separate.
        #
        # This lets us compare the old model against
        # the expert system without allowing the broken
        # model to contaminate the final answer.
        # ------------------------------------------------

        if experimental_lst is not None:

            result[
                "experimental_lst_unet"
            ] = experimental_lst

        return result
