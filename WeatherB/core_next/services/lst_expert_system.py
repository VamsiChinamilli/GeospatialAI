"""
lst_expert_system.py

Rule-based expert system for estimating Land Surface Temperature (LST)
from land-cover composition and environmental conditions.

This is NOT a machine-learning model.

The system uses interpretable expert rules:

    Base temperature
        + Built-up warming
        - Vegetation cooling
        - Water cooling
        + Environmental modifiers
        = Estimated LST

Responsibilities
----------------
- Receive land-cover percentages from AnalysisService.
- Estimate a physically reasonable LST.
- Calculate individual land-cover effects.
- Apply environmental modifiers.
- Produce an expected temperature range.
- Estimate confidence.
- Explain the major contributors.

Does NOT:
- Run neural networks.
- Download satellite imagery.
- Communicate with Earth Engine.
- Call an LLM.
"""

from typing import Dict, Any


class LSTExpertSystem:

    # ==========================================================
    # BASELINE
    # ==========================================================

    BASE_TEMPERATURE = 30.0

    # ==========================================================
    # LAND-COVER EFFECT COEFFICIENTS
    #
    # Effect = percentage * coefficient
    #
    # Example:
    #
    # Built-up = 42%
    # 42 * 0.10 = +4.2°C
    # ==========================================================

    LAND_COVER_EFFECTS = {

        "Built-up": 0.10,

        "Tree Cover": -0.06,

        "Water": -0.08,

        "Permanent Water Bodies": -0.08,

        "Cropland": -0.03,

        "Grassland": -0.03,

        "Shrubland": -0.04,

        "Mangroves": -0.06,

        "Bare / Sparse Vegetation": 0.04,

        "Bare Land": 0.04,

    }

    # ==========================================================
    # DEFAULT ENVIRONMENTAL MODIFIERS
    # ==========================================================

    DEFAULT_ENVIRONMENT = {

        "season": 1.5,

        "solar": 0.8,

        "vegetation": -0.3,

    }

    # ==========================================================
    # TEMPERATURE RANGE
    # ==========================================================

    RANGE_MARGIN = 1.5

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def __init__(
        self,
        base_temperature: float = BASE_TEMPERATURE
    ):

        self.base_temperature = float(
            base_temperature
        )

    # ==========================================================
    # LAND-COVER EFFECT
    # ==========================================================

    def calculate_land_cover_effects(
        self,
        land_cover: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate temperature contribution from each
        land-cover class.

        Parameters
        ----------
        land_cover:
            Dictionary containing class percentages.

        Example:

            {
                "Built-up": 42,
                "Tree Cover": 28,
                "Water": 18
            }

        Returns
        -------
        dict
            Individual temperature effects.
        """

        effects = {}

        for class_name, percentage in land_cover.items():

            coefficient = self.LAND_COVER_EFFECTS.get(
                class_name,
                0.0
            )

            effect = (
                float(percentage)
                * coefficient
            )

            effects[class_name] = effect

        return effects

    # ==========================================================
    # ENVIRONMENTAL EFFECTS
    # ==========================================================

    def calculate_environmental_effects(
        self,
        environment: Dict[str, float] | None = None
    ) -> Dict[str, float]:
        """
        Calculate environmental modifiers.

        Supported modifiers:

            season
            solar
            vegetation

        Missing values use defaults.
        """

        if environment is None:
            environment = {}

        return {

            "season":
                float(
                    environment.get(
                        "season",
                        self.DEFAULT_ENVIRONMENT["season"]
                    )
                ),

            "solar":
                float(
                    environment.get(
                        "solar",
                        self.DEFAULT_ENVIRONMENT["solar"]
                    )
                ),

            "vegetation":
                float(
                    environment.get(
                        "vegetation",
                        self.DEFAULT_ENVIRONMENT["vegetation"]
                    )
                ),

        }

    # ==========================================================
    # ESTIMATE TEMPERATURE
    # ==========================================================

    def estimate(
        self,
        land_cover: Dict[str, float],
        environment: Dict[str, float] | None = None
    ) -> Dict[str, Any]:
        """
        Estimate Land Surface Temperature.

        Formula:

            LST =
                Base temperature
                + land-cover effects
                + environmental effects
        """

        # ------------------------------------------------------
        # Land-cover effects
        # ------------------------------------------------------

        land_cover_effects = (
            self.calculate_land_cover_effects(
                land_cover
            )
        )

        # ------------------------------------------------------
        # Environmental effects
        # ------------------------------------------------------

        environmental_effects = (
            self.calculate_environmental_effects(
                environment
            )
        )

        # ------------------------------------------------------
        # Sum effects
        # ------------------------------------------------------

        total_land_cover_effect = sum(
            land_cover_effects.values()
        )

        total_environmental_effect = sum(
            environmental_effects.values()
        )

        # ------------------------------------------------------
        # Final estimate
        # ------------------------------------------------------

        estimated_temperature = (

            self.base_temperature

            + total_land_cover_effect

            + total_environmental_effect

        )

        # ------------------------------------------------------
        # Expected range
        # ------------------------------------------------------

        expected_min = (
            estimated_temperature
            - self.RANGE_MARGIN
        )

        expected_max = (
            estimated_temperature
            + self.RANGE_MARGIN
        )

        # ------------------------------------------------------
        # Confidence
        # ------------------------------------------------------

        confidence = self._calculate_confidence(
            land_cover=land_cover,
            estimated_temperature=estimated_temperature
        )

        # ------------------------------------------------------
        # Classification
        # ------------------------------------------------------

        classification = (
            self._classify_temperature(
                estimated_temperature
            )
        )

        # ------------------------------------------------------
        # Contributors
        # ------------------------------------------------------

        contributors = (
            self._identify_contributors(
                land_cover_effects
            )
        )

        # ------------------------------------------------------
        # Return
        # ------------------------------------------------------

        return {

            "estimated_lst_celsius":
                round(
                    estimated_temperature,
                    2
                ),

            "expected_range_celsius": {

                "min":
                    round(
                        expected_min,
                        2
                    ),

                "max":
                    round(
                        expected_max,
                        2
                    ),

            },

            "classification":
                classification,

            "confidence":
                round(
                    confidence,
                    2
                ),

            "baseline_temperature":
                self.base_temperature,

            "land_cover_effects":
                land_cover_effects,

            "environmental_effects":
                environmental_effects,

            "total_land_cover_effect":
                round(
                    total_land_cover_effect,
                    2
                ),

            "total_environmental_effect":
                round(
                    total_environmental_effect,
                    2
                ),

            "main_contributors":
                contributors,

        }

    # ==========================================================
    # CONFIDENCE
    # ==========================================================

    def _calculate_confidence(
        self,
        land_cover: Dict[str, float],
        estimated_temperature: float
    ) -> float:
        """
        Estimate confidence based on how much land-cover
        information is available.

        This is rule-based confidence, NOT statistical
        model probability.
        """

        total_percentage = sum(
            float(value)
            for value in land_cover.values()
        )

        # ------------------------------------------------------
        # Basic coverage confidence
        # ------------------------------------------------------

        if total_percentage >= 95:
            confidence = 0.85

        elif total_percentage >= 80:
            confidence = 0.75

        elif total_percentage >= 60:
            confidence = 0.65

        else:
            confidence = 0.50

        # ------------------------------------------------------
        # Penalize extreme estimates
        # ------------------------------------------------------

        if estimated_temperature < 15:
            confidence -= 0.10

        elif estimated_temperature > 45:
            confidence -= 0.10

        confidence = max(
            0.0,
            min(
                confidence,
                0.95
            )
        )

        return confidence

    # ==========================================================
    # TEMPERATURE CLASSIFICATION
    # ==========================================================

    @staticmethod
    def _classify_temperature(
        temperature: float
    ) -> str:

        if temperature < 20:
            return "Cool"

        if temperature < 27:
            return "Moderate"

        if temperature < 35:
            return "Warm"

        if temperature < 42:
            return "Hot"

        return "Very Hot"

    # ==========================================================
    # MAIN CONTRIBUTORS
    # ==========================================================

    @staticmethod
    def _identify_contributors(
        effects: Dict[str, float]
    ):

        sorted_effects = sorted(
            effects.items(),
            key=lambda item: abs(item[1]),
            reverse=True
        )

        contributors = []

        for class_name, effect in sorted_effects[:5]:

            if effect > 0:

                direction = "warming"

            elif effect < 0:

                direction = "cooling"

            else:

                direction = "neutral"

            contributors.append({

                "class":
                    class_name,

                "effect_celsius":
                    round(
                        effect,
                        2
                    ),

                "direction":
                    direction,

            })

        return contributors