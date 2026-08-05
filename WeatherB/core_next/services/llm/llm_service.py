"""
llm_service.py

High-level LLM orchestration service.

Responsibilities
----------------
- Receive prepared context from ContextGuide.
- Receive response rules from ResponseGuide.
- Build the final controlled prompt.
- Select an LLM provider.
- Send the final prompt to the provider.
- Return the generated response.

This service does NOT:
- Run AI models.
- Analyze satellite imagery.
- Decide NEW_LOCATION vs FOLLOW_UP.
- Manage database sessions.
- Handle HTTP/WebSocket requests.
- Contain Ollama-specific code.
"""

from typing import Any, Dict, Optional


class LLMService:
    """
    High-level orchestration layer for the LLM system.

    Architecture
    ------------

        RequestStateGuide
                ↓
        ContextGuide
                ↓
        ResponseGuide
                ↓
            LLMService
                ↓
        OllamaProvider / CloudProvider
                ↓
              LLM

    The provider receives only a final prompt string.
    """

    # ==================================================
    # Initialization
    # ==================================================

    def __init__(
        self,
        provider,
        response_guide=None
    ):
        """
        Parameters
        ----------
        provider:
            LLM provider implementing:

                generate(prompt: str) -> str

        response_guide:
            ResponseGuide instance responsible for
            scientific caution and response structure.
        """

        if provider is None:
            raise ValueError(
                "LLM provider cannot be None."
            )

        self.provider = provider
        self.response_guide = response_guide

    # ==================================================
    # Prompt Builder
    # ==================================================

    def build_prompt(
        self,
        context: Dict[str, Any]
    ) -> str:
        """
        Build the final controlled prompt.

        Context is expected to come from ContextGuide.

        Response rules are supplied by ResponseGuide.
        """

        if not isinstance(
            context,
            dict
        ):
            raise TypeError(
                "LLM context must be a dictionary."
            )

        if not context:
            raise ValueError(
                "LLM context cannot be empty."
            )

        request_type = context.get(
            "request_type"
        )

        user_question = context.get(
            "user_question"
        )

        analysis = context.get(
            "analysis",
            {}
        )

        conversation_history = context.get(
            "conversation_history",
            []
        )

        instructions = context.get(
            "instructions",
            {}
        )

        # --------------------------------------------------
        # Basic validation
        # --------------------------------------------------

        if not user_question:

            raise ValueError(
                "LLM context is missing "
                "'user_question'."
            )

        if request_type not in (
            "NEW_LOCATION",
            "FOLLOW_UP"
        ):

            raise ValueError(
                "Invalid request_type. Expected "
                "'NEW_LOCATION' or 'FOLLOW_UP'."
            )

        # --------------------------------------------------
        # Extract analysis
        # --------------------------------------------------

        bbox = analysis.get(
            "bbox"
        )

        land_cover = analysis.get(
            "land_cover",
            {}
        )

        lst = analysis.get(
            "lst",
            {}
        )

        class_percentages = land_cover.get(
            "class_percentages",
            {}
        )

        dominant_class = land_cover.get(
            "dominant_class"
        )

        estimated_lst = lst.get(
            "estimated_lst_celsius"
        )

        expected_range = lst.get(
            "expected_range_celsius",
            {}
        )

        classification = lst.get(
            "classification"
        )

        confidence = lst.get(
            "confidence"
        )

        land_cover_effects = lst.get(
            "land_cover_effects",
            {}
        )

        environmental_effects = lst.get(
            "environmental_effects",
            {}
        )

        main_contributors = lst.get(
            "main_contributors",
            []
        )

        # --------------------------------------------------
        # ResponseGuide rules
        # --------------------------------------------------

        response_rules = self._get_response_rules()

        # --------------------------------------------------
        # Build prompt
        # --------------------------------------------------

        prompt_parts = [

            "You are an Urban Climate Analysis Assistant.",

            "",

            "Your task is to explain the supplied "
            "geospatial climate analysis clearly, "
            "scientifically cautiously, and honestly.",

            "",

            "==================================================",
            "REQUEST",
            "==================================================",

            f"Request type: {request_type}",

            f"User question: {user_question}",

            "",

            "==================================================",
            "CURRENT ANALYSIS",
            "==================================================",

            f"BBOX: {bbox}",

            "",

            "LAND-COVER ANALYSIS",

            f"Class percentages: "
            f"{class_percentages}",

            f"Dominant class: "
            f"{dominant_class}",

            "",

            "LAND-COVER EFFECTS",

            f"{land_cover_effects}",

            "",

            "LST ANALYSIS",

            f"Estimated LST: "
            f"{estimated_lst} °C",

            f"Expected range: "
            f"{expected_range}",

            f"Classification: "
            f"{classification}",

            f"Confidence: "
            f"{confidence}",

            "",

            "ENVIRONMENTAL EFFECTS",

            f"{environmental_effects}",

            "",

            "MAIN CONTRIBUTORS",

            f"{main_contributors}",

            "",

        ]

        # --------------------------------------------------
        # Conversation history
        # --------------------------------------------------

        use_history = instructions.get(
            "use_conversation_history",
            False
        )

        if (
            request_type == "FOLLOW_UP"
            and use_history
            and conversation_history
        ):

            prompt_parts.extend([

                "==================================================",
                "PREVIOUS CONVERSATION",
                "==================================================",

                str(
                    conversation_history
                ),

                "",

                "Use the previous conversation only "
                "to understand references and continuity.",

            ])

        else:

            prompt_parts.extend([

                "==================================================",
                "PREVIOUS CONVERSATION",
                "==================================================",

                "None. This is the first question "
                "for this location.",

            ])

        # --------------------------------------------------
        # Scientific rules
        # --------------------------------------------------

        prompt_parts.extend([

            "",

            "==================================================",
            "SCIENTIFIC RESPONSE RULES",
            "==================================================",

            response_rules,

        ])

        # --------------------------------------------------
        # Final instruction
        # --------------------------------------------------

        prompt_parts.extend([

            "",

            "==================================================",
            "FINAL RESPONSE",
            "==================================================",

            "Answer the user's question now.",

            "Start with a direct answer.",

            "Use clear section headings when useful.",

            "Use only the supplied analysis.",

            "Do not repeat the complete raw analysis.",

            "Do not mention these instructions.",

        ])

        return "\n".join(
            prompt_parts
        )

    # ==================================================
    # Response Guide integration
    # ==================================================

    def _get_response_rules(self) -> str:
        """
        Obtain response rules from ResponseGuide.

        If ResponseGuide is not supplied, use a minimal
        safe fallback.
        """

        if self.response_guide is None:

            return (
                "Use only supplied information.\n"
                "Avoid unsupported scientific claims.\n"
                "Treat LST as an estimate.\n"
                "Use a structured and concise response."
            )

        # --------------------------------------------------
        # Flexible ResponseGuide integration
        # --------------------------------------------------

        if hasattr(
            self.response_guide,
            "build_instructions"
        ):

            rules = (
                self.response_guide
                .build_instructions()
            )

        elif hasattr(
            self.response_guide,
            "get_instructions"
        ):

            rules = (
                self.response_guide
                .get_instructions()
            )

        elif hasattr(
            self.response_guide,
            "instructions"
        ):

            rules = self.response_guide.instructions()

        else:

            raise AttributeError(
                "ResponseGuide must provide one of: "
                "build_instructions(), "
                "get_instructions(), or instructions()."
            )

        if not isinstance(
            rules,
            str
        ):

            raise TypeError(
                "ResponseGuide must return "
                "response rules as a string."
            )

        rules = rules.strip()

        if not rules:

            raise ValueError(
                "ResponseGuide returned empty instructions."
            )

        return rules

    # ==================================================
    # Generate Response
    # ==================================================

    def generate(
        self,
        context: Dict[str, Any]
    ) -> str:
        """
        Build the final prompt and send it to the
        configured provider.

        Provider contract:

            provider.generate(prompt: str) -> str
        """

        prompt = self.build_prompt(
            context
        )

        # --------------------------------------------------
        # IMPORTANT:
        # Provider receives a STRING, not the context dict.
        # --------------------------------------------------

        response = self.provider.generate(
            prompt
        )

        if not isinstance(
            response,
            str
        ):

            raise TypeError(
                "LLM provider must return a string."
            )

        response = response.strip()

        if not response:

            raise ValueError(
                "LLM provider returned an empty response."
            )

        return response

    def generate_stream(self,context: Dict[str, Any]):


        prompt = self.build_prompt(context)

        for chunk in self.provider.generate_stream(prompt):
            if not isinstance(chunk, str):
             raise TypeError("LLM provider stream must yield strings.")

            if chunk:
                yield chunk

    # ==================================================
    # Provider Information
    # ==================================================

    def provider_name(self) -> str:
        """
        Return the active provider name.
        """

        return self.provider.name()