
"""
ollama_provider.py

Ollama LLM provider.

Current local model
-------------------
qwen2.5:7b

Responsibilities
----------------
- Communicate with local Ollama.
- Send prepared prompts to Qwen.
- Support normal and streaming generation.
- Return generated text/chunks.

This provider does NOT:
- Analyze satellite data.
- Calculate LST.
- Manage sessions.
- Decide request type.
- Build application-level analysis context.
"""

import json
from typing import Iterator

import requests


class OllamaProvider:
    """
    Provider for locally running Ollama models.
    """

    DEFAULT_URL = "http://localhost:11434/api/generate"

    def __init__(
        self,
        model: str = "qwen2.5:7b",
        url: str = DEFAULT_URL,
        timeout: int = 120
    ):

        self.model = model
        self.url = url
        self.timeout = timeout

    # ==================================================
    # Provider name
    # ==================================================

    def name(self) -> str:
        return "ollama"

    # ==================================================
    # Normal generation
    # ==================================================

    def is_available(self) -> bool:
        """
        Check whether Ollama is running and the configured
        model is available locally.

        This does NOT generate any text.
        """

        try:
            base_url = self.url.replace(
                "/api/generate",
                ""
            )

            response = requests.get(
                f"{base_url}/api/tags",
                timeout=3
            )

            if response.status_code != 200:
                return False

            data = response.json()

            models = data.get(
                "models",
                []
            )

            for model in models:

                if model.get("name") == self.model:
                    return True

            return False

        except (
            requests.RequestException,
            ValueError,
            TypeError,
        ):

            return False    

    def generate(
        self,
        prompt: str
    ) -> str:
        """
        Generate a complete response from Ollama.

        This method waits until Qwen finishes and then
        returns the complete generated response.
        """

        if not isinstance(prompt, str):
            raise TypeError(
                "Ollama prompt must be a string."
            )

        prompt = prompt.strip()

        if not prompt:
            raise ValueError(
                "Ollama prompt cannot be empty."
            )

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        try:

            response = requests.post(
                self.url,
                json=payload,
                timeout=self.timeout
            )

            response.raise_for_status()

        except requests.RequestException as exc:

            raise RuntimeError(
                "Unable to communicate with Ollama. "
                "Make sure Ollama is running and the "
                f"model '{self.model}' is available."
            ) from exc

        try:

            data = response.json()

        except ValueError as exc:

            raise RuntimeError(
                "Ollama returned invalid JSON."
            ) from exc

        generated_text = data.get(
            "response",
            ""
        )

        if not isinstance(
            generated_text,
            str
        ):

            raise RuntimeError(
                "Ollama returned an invalid response."
            )

        generated_text = generated_text.strip()

        if not generated_text:

            raise RuntimeError(
                "Ollama returned no generated response."
            )

        return generated_text

    # ==================================================
    # Streaming generation
    # ==================================================

    def generate_stream(self,prompt: str):
        if not isinstance(prompt,str):
            raise TypeError(
            "Ollama prompt must be a string."
        )

        prompt = prompt.strip()

        if not prompt:
            raise ValueError(
            "Ollama prompt cannot be empty."
        )

        payload = {
        "model": self.model,
        "prompt": prompt,
        "stream": True,
    }

        try:

            response = requests.post(
            self.url,
            json=payload,
            timeout=self.timeout,
            stream=True,
        )

            response.raise_for_status()

        except requests.RequestException as exc:

            raise RuntimeError(
            "Unable to communicate with Ollama. "
            "Make sure Ollama is running and the "
            f"model '{self.model}' is available."
        ) from exc

        try:

            for line in response.iter_lines(decode_unicode=True):

                if not line:
                    continue

                try:

                    data = json.loads(line)

                except json.JSONDecodeError as exc:

                    raise RuntimeError("Ollama returned invalid JSON ""during streaming.") from exc

                chunk = data.get("response","")

                if chunk:

                    yield chunk

                if data.get("done",False):


                    break

        except requests.RequestException as exc:

            raise RuntimeError(
            "Error while reading the Ollama stream."
        ) from exc


