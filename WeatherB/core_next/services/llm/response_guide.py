
"""
response_guide.py

Guide 3 — Response Guidance
---------------------------

Controls how the LLM should communicate the prepared
urban-climate analysis.

Responsibilities
----------------
- Enforce scientific caution.
- Prevent unsupported claims.
- Define a consistent response structure.
- Tell the LLM how to communicate uncertainty.
- Keep explanations grounded in supplied analysis.

This guide does NOT:
- analyze satellite imagery.
- calculate LST.
- decide NEW_LOCATION vs FOLLOW_UP.
- prepare the analysis context.
- call Ollama.
- call Qwen.
- manage database sessions.
- handle HTTP requests.
- handle WebSockets.
"""


from typing import Any, Dict


class ResponseGuide:
    """
    Produces response instructions for the LLM.

    The guide controls communication behavior rather
    than the underlying scientific analysis.
    """

    # ==================================================
    # Initialization
    # ==================================================

    def __init__(self):
        pass

    # ==================================================
    # Scientific safety rules
    # ==================================================

    @staticmethod
    def scientific_rules() -> list[str]:
        """
        Return rules that prevent unsupported scientific
        claims.
        """

        return [

            # ------------------------------------------
            # Evidence
            # ------------------------------------------

            "Use only information supplied in the "
            "analysis context.",

            "Do not invent measurements, observations, "
            "environmental conditions, or statistics.",

            "Do not introduce numerical values that are "
            "not present in the supplied analysis.",

            # ------------------------------------------
            # LST interpretation
            # ------------------------------------------

            "Treat the LST value as an estimate produced "
            "by the application's expert system.",

            "Do not describe the estimated LST as a "
            "direct ground measurement.",

            "Do not claim that the estimate represents "
            "air temperature.",

            "Do not claim that the estimate is an exact "
            "physical temperature.",

            "When discussing uncertainty, use the supplied "
            "expected range and confidence rather than "
            "inventing additional uncertainty.",

            # ------------------------------------------
            # Causality
            # ------------------------------------------

            "Do not claim that a land-cover effect proves "
            "causation.",

            "Prefer wording such as 'the analysis associates "
            "this surface with warming' or 'the supplied "
            "estimate assigns a warming effect'.",

            "Do not claim that changing one land-cover type "
            "will definitely produce a specific real-world "
            "temperature change unless the supplied analysis "
            "explicitly supports that conclusion.",

            # ------------------------------------------
            # Missing information
            # ------------------------------------------

            "If the supplied analysis does not contain enough "
            "information to answer the question, explicitly "
            "state that limitation.",

            "Never fill missing scientific information with "
            "a guessed value.",

            # ------------------------------------------
            # Experimental models
            # ------------------------------------------

            "Do not use experimental or untrusted model "
            "outputs when the context marks them as excluded.",

            "Do not mention experimental model results unless "
            "the user explicitly asks about them.",

        ]

    # ==================================================
    # Response structure
    # ==================================================

    @staticmethod
    def response_structure() -> list[str]:
        """
        Define the preferred structure for the generated
        response.
        """

        return [

            "Start with a short direct answer.",

            "Use clear section headings when the answer "
            "contains multiple points.",

            "Explain the most relevant evidence from the "
            "current analysis.",

            "Separate warming contributors from cooling "
            "contributors when relevant.",

            "Mention the estimated LST and expected range "
            "when relevant to the question.",

            "Mention confidence when it materially helps "
            "interpret the estimate.",

            "For follow-up questions, connect the answer "
            "to the previous conversation naturally.",

            "End with a concise interpretation or practical "
            "takeaway when appropriate.",

            "Do not repeat the complete raw analysis object.",

        ]

    # ==================================================
    # Build instructions
    # ==================================================

    def build(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add response guidance to the prepared LLM context.

        Parameters
        ----------
        context:
            Context produced by ContextGuide.

        Returns
        -------
        dict
            Context containing response instructions.
        """

        if not isinstance(
            context,
            dict
        ):

            raise TypeError(
                "context must be a dictionary."
            )

        if not context:

            raise ValueError(
                "context cannot be empty."
            )

        # --------------------------------------------------
        # Do not mutate the original context.
        # --------------------------------------------------

        prepared_context = dict(
            context
        )

        # --------------------------------------------------
        # Existing instructions
        # --------------------------------------------------

        existing_instructions = prepared_context.get(
            "instructions",
            {}
        )

        if not isinstance(
            existing_instructions,
            dict
        ):

            raise TypeError(
                "context['instructions'] must be a dictionary."
            )

        instructions = dict(
            existing_instructions
        )

        # --------------------------------------------------
        # Add response guidance
        # --------------------------------------------------

        instructions[
            "scientific_caution"
        ] = True

        instructions[
            "avoid_unsupported_claims"
        ] = True

        instructions[
            "structured_response"
        ] = True

        instructions[
            "scientific_rules"
        ] = self.scientific_rules()

        instructions[
            "response_structure"
        ] = self.response_structure()

        # --------------------------------------------------
        # Store final instructions
        # --------------------------------------------------

        prepared_context[
            "instructions"
        ] = instructions

        return prepared_context


# ==========================================================
# Standalone test
# ==========================================================

if __name__ == "__main__":

    guide = ResponseGuide()

    test_context = {

        "request_type":
            "NEW_LOCATION",

        "user_question":
            "Why is this area warm?",

        "analysis": {

            "bbox": [
                80.60,
                16.48,
                80.62,
                16.50
            ],

            "land_cover": {

                "class_percentages": {

                    "Built-up":
                        42.0,

                    "Tree Cover":
                        28.0,

                    "Permanent Water Bodies":
                        18.0,

                    "Cropland":
                        8.0,

                    "Grassland":
                        4.0,

                },

                "dominant_class":
                    "Built-up",

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

                "land_cover_effects": {

                    "Built-up":
                        4.20,

                    "Tree Cover":
                        -1.68,

                    "Permanent Water Bodies":
                        -1.44,

                },

            },

        },

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

    print()
    print("=" * 70)
    print("RESPONSE GUIDE TEST")
    print("=" * 70)

    result = guide.build(
        test_context
    )

    print()
    print("Response guidance added:")
    print()

    print(
        "Scientific caution:",
        result["instructions"][
            "scientific_caution"
        ]
    )

    print(
        "Avoid unsupported claims:",
        result["instructions"][
            "avoid_unsupported_claims"
        ]
    )

    print(
        "Structured response:",
        result["instructions"][
            "structured_response"
        ]
    )

    print()
    print("SCIENTIFIC RULES")
    print("-" * 70)

    for index, rule in enumerate(
        result["instructions"][
            "scientific_rules"
        ],
        start=1
    ):

        print(
            f"{index}. {rule}"
        )

    print()
    print("RESPONSE STRUCTURE")
    print("-" * 70)

    for index, rule in enumerate(
        result["instructions"][
            "response_structure"
        ],
        start=1
    ):

        print(
            f"{index}. {rule}"
        )

    print()
    print("=" * 70)
    print("RESPONSE GUIDE TEST COMPLETED")
    print("=" * 70)