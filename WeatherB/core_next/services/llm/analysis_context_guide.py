"""
analysis_context_guide.py

Builds the structured context that will be provided to the LLM.

Responsibilities
----------------
- Prepare current geospatial analysis for the LLM.
- Include conversation history when appropriate.
- Keep experimental model output away from the LLM.
- Separate NEW_LOCATION and FOLLOW_UP context.
- Produce a clean, predictable dictionary.

This guide does NOT:
- Call Ollama.
- Call cloud LLM APIs.
- Query Django models.
- Detect whether the BBOX changed.
- Generate the final natural-language response.
"""

from typing import Any, Dict, List, Optional


class AnalysisContextGuide:
    """
    Converts application state into a controlled LLM context.
    """

    # =========================================================
    # Initialization
    # =========================================================

    def __init__(self):
        pass

    # =========================================================
    # Public API
    # =========================================================

    def build(
        self,
        request_type: str,
        user_question: str,
        analysis: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Build the context that will later be given to Qwen
        or another LLM provider.

        Parameters
        ----------
        request_type:
            NEW_LOCATION or FOLLOW_UP

        user_question:
            Current user's question.

        analysis:
            Current geospatial analysis.

        conversation_history:
            Previous messages from the same session.

        Returns
        -------
        dict
        """

        if request_type not in {
            "NEW_LOCATION",
            "FOLLOW_UP",
        }:
            raise ValueError(
                f"Unsupported request_type: {request_type}"
            )

        if not isinstance(user_question, str):
            raise TypeError(
                "user_question must be a string."
            )

        if not isinstance(analysis, dict):
            raise TypeError(
                "analysis must be a dictionary."
            )

        if conversation_history is None:
            conversation_history = []

        if not isinstance(conversation_history, list):
            raise TypeError(
                "conversation_history must be a list."
            )

        # -----------------------------------------------------
        # NEW LOCATION
        # -----------------------------------------------------

        if request_type == "NEW_LOCATION":

            return self._build_new_location_context(
                user_question=user_question,
                analysis=analysis,
            )

        # -----------------------------------------------------
        # FOLLOW UP
        # -----------------------------------------------------

        return self._build_follow_up_context(
            user_question=user_question,
            analysis=analysis,
            conversation_history=conversation_history,
        )

    # =========================================================
    # NEW LOCATION
    # =========================================================

    def _build_new_location_context(
        self,
        user_question: str,
        analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Context for the first question about a BBOX.
        """

        return {
            "request_type": "NEW_LOCATION",

            "user_question": user_question,

            "analysis": self._clean_analysis(
                analysis
            ),

            "conversation_history": [],

            "instructions": {
                "use_current_analysis": True,
                "use_conversation_history": False,
                "experimental_lst_unet": False,
            },
        }

    # =========================================================
    # FOLLOW UP
    # =========================================================

    def _build_follow_up_context(
        self,
        user_question: str,
        analysis: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """
        Context for subsequent questions about the same BBOX.
        """

        return {
            "request_type": "FOLLOW_UP",

            "user_question": user_question,

            "analysis": self._clean_analysis(
                analysis
            ),

            "conversation_history": self._clean_history(
                conversation_history
            ),

            "instructions": {
                "use_current_analysis": True,
                "use_conversation_history": True,
                "experimental_lst_unet": False,
            },
        }

    # =========================================================
    # Analysis Sanitization
    # =========================================================

    @staticmethod
    def _clean_analysis(
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Keep only information that is useful for the LLM.

        Experimental LST U-Net output is intentionally excluded.
        """

        cleaned = {}

        # -----------------------------------------------------
        # BBOX
        # -----------------------------------------------------

        if "bbox" in analysis:

            cleaned["bbox"] = analysis["bbox"]

        # -----------------------------------------------------
        # Land Cover
        # -----------------------------------------------------

        if "land_cover" in analysis:

            land_cover = analysis["land_cover"]

            cleaned["land_cover"] = {
                "class_percentages":
                    land_cover.get(
                        "class_percentages",
                        {}
                    ),

                "dominant_class":
                    land_cover.get(
                        "dominant_class"
                    ),

                "pixel_count":
                    land_cover.get(
                        "pixel_count"
                    ),
            }

        # -----------------------------------------------------
        # Expert-System LST
        # -----------------------------------------------------

        if "lst" in analysis:

            lst = analysis["lst"]

            cleaned["lst"] = {
                "estimated_lst_celsius":
                    lst.get(
                        "estimated_lst_celsius"
                    ),

                "expected_range_celsius":
                    lst.get(
                        "expected_range_celsius"
                    ),

                "classification":
                    lst.get(
                        "classification"
                    ),

                "confidence":
                    lst.get(
                        "confidence"
                    ),

                "baseline_temperature":
                    lst.get(
                        "baseline_temperature"
                    ),

                "land_cover_effects":
                    lst.get(
                        "land_cover_effects",
                        {}
                    ),

                "environmental_effects":
                    lst.get(
                        "environmental_effects",
                        {}
                    ),

                "total_land_cover_effect":
                    lst.get(
                        "total_land_cover_effect"
                    ),

                "total_environmental_effect":
                    lst.get(
                        "total_environmental_effect"
                    ),

                "main_contributors":
                    lst.get(
                        "main_contributors",
                        []
                    ),
            }

        return cleaned

    # =========================================================
    # Conversation History Sanitization
    # =========================================================

    @staticmethod
    def _clean_history(
        conversation_history: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        Keep only the most recent conversation messages.

        The database may eventually contain more messages,
        but the LLM guide only forwards a small context window.
        """

        cleaned = []

        for message in conversation_history[-2:]:

            if not isinstance(message, dict):
                continue

            role = message.get("role")
            content = message.get("content")

            if role not in {
                "user",
                "assistant",
            }:
                continue

            if not isinstance(content, str):
                continue

            cleaned.append({
                "role": role,
                "content": content,
            })

        return cleaned