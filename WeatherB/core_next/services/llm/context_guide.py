"""
context_guide.py

Guide 2 — LLM Context Preparation
----------------------------------

Prepares structured information for the LLM layer.

Responsibilities
----------------
- Receive the state from RequestStateGuide.
- Select the information Qwen actually needs.
- Prepare NEW_LOCATION context.
- Prepare FOLLOW_UP context.
- Keep experimental/unreliable model output away from Qwen.
- Keep the context structured and JSON-friendly.

This guide does NOT:
- call Ollama
- call Qwen
- generate text
- manage database sessions
- handle HTTP requests
- handle WebSockets
"""

from typing import Any, Dict, List, Optional


class ContextGuide:
    """
    Prepares climate-analysis context for the future LLM service.
    """

    # =====================================================
    # Initialization
    # =====================================================

    def __init__(self):
        pass

    # =====================================================
    # Safe analysis extraction
    # =====================================================

    @staticmethod
    def _extract_analysis(
        analysis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract only the trusted application-level analysis.

        The experimental LST U-Net result is intentionally
        excluded.
        """

        if not isinstance(
            analysis_result,
            dict
        ):
            raise TypeError(
                "analysis_result must be a dictionary."
            )

        if "land_cover" not in analysis_result:

            raise KeyError(
                "analysis_result is missing 'land_cover'."
            )

        if "lst" not in analysis_result:

            raise KeyError(
                "analysis_result is missing 'lst'."
            )

        return {

            "bbox":
                analysis_result.get("bbox"),

            "land_cover":
                analysis_result["land_cover"],

            "lst":
                analysis_result["lst"],

        }

    # =====================================================
    # New-location context
    # =====================================================

    def build_new_location_context(
        self,
        analysis_result: Dict[str, Any],
        user_question: str,
    ) -> Dict[str, Any]:
        """
        Build context for the first question at a new BBOX.
        """

        if not isinstance(
            user_question,
            str
        ):
            raise TypeError(
                "user_question must be a string."
            )

        user_question = user_question.strip()

        if not user_question:

            raise ValueError(
                "user_question cannot be empty."
            )

        analysis = self._extract_analysis(
            analysis_result
        )

        return {

            "request_type":
                "NEW_LOCATION",

            "user_question":
                user_question,

            "analysis":
                analysis,

            "conversation_history":
                [],

            "instructions": {

                "use_current_analysis":
                    True,

                "use_conversation_history":
                    False,

                "experimental_lst_unet":
                    False,

            },

        }

    # =====================================================
    # Follow-up context
    # =====================================================

    def build_follow_up_context(
        self,
        analysis_result: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
        user_question: str,
    ) -> Dict[str, Any]:
        """
        Build context for a follow-up question about
        the same BBOX.
        """

        if not isinstance(
            conversation_history,
            list
        ):
            raise TypeError(
                "conversation_history must be a list."
            )

        if not isinstance(
            user_question,
            str
        ):
            raise TypeError(
                "user_question must be a string."
            )

        user_question = user_question.strip()

        if not user_question:

            raise ValueError(
                "user_question cannot be empty."
            )

        analysis = self._extract_analysis(
            analysis_result
        )

        return {

            "request_type":
                "FOLLOW_UP",

            "user_question":
                user_question,

            "analysis":
                analysis,

            "conversation_history":
                conversation_history,

            "instructions": {

                "use_current_analysis":
                    True,

                "use_conversation_history":
                    True,

                "experimental_lst_unet":
                    False,

            },

        }

    # =====================================================
    # Unified context builder
    # =====================================================

    def build(
        self,
        request_type: str,
        analysis_result: Dict[str, Any],
        user_question: str,
        conversation_history: Optional[
            List[Dict[str, str]]
        ] = None,
    ) -> Dict[str, Any]:
        """
        Build the correct context based on request state.
        """

        if request_type == "NEW_LOCATION":

            return self.build_new_location_context(

                analysis_result=
                    analysis_result,

                user_question=
                    user_question,

            )

        if request_type == "FOLLOW_UP":

            return self.build_follow_up_context(

                analysis_result=
                    analysis_result,

                conversation_history=
                    conversation_history or [],

                user_question=
                    user_question,

            )

        raise ValueError(
            f"Unknown request_type: {request_type}"
        )


# =========================================================
# Standalone test
# =========================================================

if __name__ == "__main__":

    guide = ContextGuide()

    analysis_result = {

        "bbox": [
            80.60,
            16.48,
            80.62,
            16.50
        ],

        "land_cover": {

            "class_percentages": {

                "Built-up": 42.0,
                "Tree Cover": 28.0,
                "Permanent Water Bodies": 18.0,
                "Cropland": 8.0,
                "Grassland": 4.0,

            },

            "dominant_class_id":
                4,

            "dominant_class":
                "Built-up",

            "pixel_count":
                65536,

        },

        "lst": {

            "estimated_lst_celsius":
                32.72,

            "expected_range_celsius": {

                "min":
                    31.22,

                "max":
                    34.22,

            },

            "classification":
                "Warm",

            "confidence":
                0.85,

            "baseline_temperature":
                30.0,

            "land_cover_effects": {

                "Built-up":
                    4.20,

                "Tree Cover":
                    -1.68,

                "Permanent Water Bodies":
                    -1.44,

                "Cropland":
                    -0.24,

                "Grassland":
                    -0.12,

            },

            "environmental_effects": {

                "season":
                    1.50,

                "solar":
                    0.80,

                "vegetation":
                    -0.30,

            },

            "total_land_cover_effect":
                0.72,

            "total_environmental_effect":
                2.0,

            "main_contributors": [

                {

                    "class":
                        "Built-up",

                    "effect_celsius":
                        4.20,

                    "direction":
                        "warming",

                },

                {

                    "class":
                        "Tree Cover",

                    "effect_celsius":
                        -1.68,

                    "direction":
                        "cooling",

                },

            ],

        },

        # This should NEVER reach Qwen.
        "experimental_lst_unet": {

            "mean":
                290.5,

            "unit":
                "Kelvin",

            "status":
                "experimental_only",

        },

    }

    print("\n" + "=" * 70)
    print("CONTEXT GUIDE TEST")
    print("=" * 70)

    # -----------------------------------------------------
    # NEW LOCATION
    # -----------------------------------------------------

    new_context = guide.build(

        request_type=
            "NEW_LOCATION",

        analysis_result=
            analysis_result,

        user_question=
            "Why is this area warm?",

    )

    print("\nNEW LOCATION CONTEXT")
    print("-" * 70)

    print(new_context)

    # -----------------------------------------------------
    # FOLLOW UP
    # -----------------------------------------------------

    history = [

        {

            "role":
                "user",

            "content":
                "Why is this area warm?",

        },

        {

            "role":
                "assistant",

            "content":
                "The built-up surfaces are the strongest "
                "warming contributor.",

        },

    ]

    follow_up_context = guide.build(

        request_type=
            "FOLLOW_UP",

        analysis_result=
            analysis_result,

        conversation_history=
            history,

        user_question=
            "Would more trees reduce the temperature?",

    )

    print("\nFOLLOW-UP CONTEXT")
    print("-" * 70)

    print(follow_up_context)

    print("\n" + "=" * 70)
    print("CONTEXT GUIDE TEST COMPLETED")
    print("=" * 70)