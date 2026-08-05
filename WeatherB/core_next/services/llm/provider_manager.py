"""
provider_manager.py

LLM provider selection and fallback manager.

Priority:
    1. Local Ollama / Qwen
    2. OpenRouter / CloudProvider

If Ollama is available with the configured model,
local inference is preferred.

If Ollama is unavailable, the manager falls back
to OpenRouter automatically.
"""

from core_next.services.llm.providers.ollama_provider import (
    OllamaProvider,
)

from core_next.services.llm.providers.cloud_provider import (
    CloudProvider,
)


class ProviderManager:
    """
    Selects the best available LLM provider.

    Priority:
        Ollama → OpenRouter
    """

    def __init__(
        self,
        ollama_provider=None,
        cloud_provider=None,
    ):
        """
        Initialize provider manager.

        Providers may be injected for testing,
        but sensible defaults are created automatically.
        """

        self.ollama_provider = (
            ollama_provider
            or OllamaProvider(
                model="qwen2.5:7b"
            )
        )

        self.cloud_provider = (
            cloud_provider
            or CloudProvider()
        )

        self.active_provider = None

        self._select_provider()

    # ============================================================
    # Provider Selection
    # ============================================================

    def _select_provider(self):
        """
        Select the first available provider.

        Priority:

            1. Local Ollama
            2. OpenRouter
        """

        # --------------------------------------------------------
        # Try local Ollama first
        # --------------------------------------------------------

        try:

            if self.ollama_provider.is_available():

                self.active_provider = (
                    self.ollama_provider
                )

                return

        except Exception:
            # Local provider unavailable.
            # Continue to cloud fallback.
            pass

        # --------------------------------------------------------
        # Fallback to OpenRouter
        # --------------------------------------------------------

        self.active_provider = (
            self.cloud_provider
        )

    # ============================================================
    # Provider Name
    # ============================================================

    def name(self) -> str:
        """
        Return the active provider name.
        """

        return self.active_provider.name()

    # ============================================================
    # Normal Generation
    # ============================================================

    def generate(
        self,
        prompt: str,
    ) -> str:
        """
        Generate using the selected provider.
        """

        return self.active_provider.generate(
            prompt
        )

    # ============================================================
    # Streaming Generation
    # ============================================================

    def generate_stream(
        self,
        prompt: str,
    ):
        """
        Stream using the selected provider.
        """

        yield from self.active_provider.generate_stream(
            prompt
        )

    # ============================================================
    # Active Provider
    # ============================================================

    def get_provider(self):
        """
        Return the currently selected provider.
        """

        return self.active_provider