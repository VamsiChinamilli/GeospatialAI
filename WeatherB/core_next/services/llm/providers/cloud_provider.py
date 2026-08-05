"""
cloud_provider.py

OpenRouter cloud LLM provider.

Responsibilities
----------------
- Communicate with OpenRouter.
- Send prepared prompts to the configured cloud model.
- Support normal and streaming generation.
- Return generated text/chunks.

This provider does NOT:
- Build application prompts.
- Analyze satellite data.
- Calculate LST.
- Manage conversation sessions.
- Decide request type.
"""

import json
from typing import Iterator

import requests

from django.conf import settings


class CloudProvider:
    """
    Provider for cloud-based LLM inference through OpenRouter.
    """

    DEFAULT_URL = (
        "https://openrouter.ai/api/v1/chat/completions"
    )

    DEFAULT_MODEL = (
        "qwen/qwen-2.5-7b-instruct"
    )

    def __init__(
        self,
        model: str | None = None,
        url: str | None = None,
        timeout: int = 120,
    ):
        """
        Initialize the OpenRouter provider.

        Configuration is read from Django settings,
        which loads values from .env.
        """

        self.api_key = getattr(
            settings,
            "OPENROUTER_API_KEY",
            None,
        )

        self.model = (
            model
            or getattr(
                settings,
                "OPENROUTER_MODEL",
                self.DEFAULT_MODEL,
            )
        )

        self.url = (
            url
            or getattr(
                settings,
                "OPENROUTER_URL",
                self.DEFAULT_URL,
            )
        )

        self.timeout = timeout

        if not self.api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is not configured."
            )

    # ============================================================
    # Provider name
    # ============================================================

    def name(self) -> str:
        return "openrouter"

    # ============================================================
    # Headers
    # ============================================================

    def _headers(self) -> dict:
        """
        Build HTTP headers required by OpenRouter.
        """

        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    # ============================================================
    # Normal generation
    # ============================================================

    def generate(
        self,
        prompt: str,
    ) -> str:
        """
        Generate a complete response.

        Waits until the cloud model finishes.
        """

        if not isinstance(prompt, str):
            raise TypeError(
                "Cloud LLM prompt must be a string."
            )

        prompt = prompt.strip()

        if not prompt:
            raise ValueError(
                "Cloud LLM prompt cannot be empty."
            )

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "stream": False,
        }

        try:
            response = requests.post(
                self.url,
                headers=self._headers(),
                json=payload,
                timeout=self.timeout,
            )

            response.raise_for_status()

        except requests.RequestException as exc:
            raise RuntimeError(
                "Unable to communicate with OpenRouter."
            ) from exc

        try:
            data = response.json()

        except ValueError as exc:
            raise RuntimeError(
                "OpenRouter returned invalid JSON."
            ) from exc

        try:
            generated_text = (
                data["choices"][0]["message"]["content"]
            )

        except (
            KeyError,
            IndexError,
            TypeError,
        ) as exc:
            raise RuntimeError(
                "OpenRouter returned an unexpected response format."
            ) from exc

        if not isinstance(
            generated_text,
            str,
        ):
            raise RuntimeError(
                "OpenRouter returned invalid generated text."
            )

        generated_text = generated_text.strip()

        if not generated_text:
            raise RuntimeError(
                "OpenRouter returned an empty response."
            )

        return generated_text

    # ============================================================
    # Streaming generation
    # ============================================================

    def generate_stream(self, prompt: str):
        """
    Generate a streaming response from OpenRouter.

    OpenRouter uses Server-Sent Events (SSE).

    Relevant stream lines look like:

        data: {"choices":[...]}

    The stream ends with:

        data: [DONE]

    Non-data SSE lines are ignored.
    """

    # --------------------------------------------------------
    # Validate prompt
    # --------------------------------------------------------

        if not isinstance(prompt, str):
            raise TypeError(
            "OpenRouter prompt must be a string."
        )

        prompt = prompt.strip()

        if not prompt:
            raise ValueError(
            "OpenRouter prompt cannot be empty."
        )

    # --------------------------------------------------------
    # Request payload
    # --------------------------------------------------------

        payload = {
        "model": self.model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "stream": True,
    }

    # --------------------------------------------------------
    # Request
    # --------------------------------------------------------

        try:

            response = requests.post(
            self.url,
            headers=self._headers(),
            json=payload,
            timeout=self.timeout,
            stream=True,
        )

            response.raise_for_status()

        except requests.RequestException as exc:

            raise RuntimeError(
            "Unable to communicate with OpenRouter "
            "during streaming."
        ) from exc

    # --------------------------------------------------------
    # Read SSE stream
    # --------------------------------------------------------

        try:

            for raw_line in response.iter_lines(
            decode_unicode=True
        ):

            # Ignore empty lines
                if not raw_line:
                    continue

                line = raw_line.strip()

            # ------------------------------------------------
            # DEBUG
            # ------------------------------------------------
            # Keep this temporarily while testing.
            # It lets us see exactly what OpenRouter sends.
            #    print("OPENROUTER STREAM:",repr(line))

            # ------------------------------------------------
            # Ignore non-SSE-data lines
            # ------------------------------------------------

                if not line.startswith("data:"):
                    continue

            # Remove "data:" prefix

                data_string = line[len("data:"):
                                   ].strip()

            # ------------------------------------------------
            # Stream finished
            # ------------------------------------------------

                if data_string == "[DONE]":
                    break

            # ------------------------------------------------
            # Parse JSON
            # ------------------------------------------------

                try:

                    data = json.loads(
                    data_string
                )

                except json.JSONDecodeError as exc:

                    raise RuntimeError(
                    "OpenRouter returned invalid JSON "
                    "during streaming."
                ) from exc

            # ------------------------------------------------
            # Extract choices
            # ------------------------------------------------

                choices = data.get(
                "choices",
                []
            )

                if not choices:
                    continue

            # ------------------------------------------------
            # Extract delta
            # ------------------------------------------------

                delta = choices[0].get(
                "delta",
                {}
            )

            # ------------------------------------------------
            # Extract token
            # ------------------------------------------------

                chunk = delta.get(
                "content",
                ""
            )

                if chunk:
                    yield chunk

        except requests.RequestException as exc:

            raise RuntimeError(
            "Error while reading the "
            "OpenRouter stream."
        ) from exc

        finally:

            response.close()