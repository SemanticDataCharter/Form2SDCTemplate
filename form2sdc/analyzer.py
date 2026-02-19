"""Form analyzer protocol and Gemini implementation.

Gemini-first with a thin FormAnalyzer protocol for swappability.
"""

from __future__ import annotations

import base64
import json
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional, Protocol, runtime_checkable

from form2sdc.prompt_loader import load_system_prompt
from form2sdc.types import FormAnalysis

# Gemini REST API base URL
_GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models"
)


@runtime_checkable
class FormAnalyzer(Protocol):
    """Protocol for form analyzers. Implement this to add new LLM backends."""

    def analyze(
        self,
        file_path: Optional[Path] = None,
        file_content: Optional[bytes] = None,
        mime_type: Optional[str] = None,
        additional_instructions: str = "",
    ) -> FormAnalysis:
        """Analyze a form and return structured data.

        Args:
            file_path: Path to form file (PDF, DOCX, image).
            file_content: Raw file bytes (alternative to file_path).
            mime_type: MIME type of the file content.
            additional_instructions: Extra instructions for the analyzer.

        Returns:
            FormAnalysis with structured form data.
        """
        ...


class GeminiAnalyzer:
    """Gemini-powered form analyzer using the REST API directly.

    Uses Form2SDCTemplate.md as system prompt and structured output
    to convert forms into SDC4-compliant template data.

    Bypasses the google-genai SDK entirely to avoid RecursionError
    from its process_schema on self-referential Pydantic models.
    """

    # MIME type detection
    _MIME_MAP = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument"
                 ".wordprocessingml.document",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".tiff": "image/tiff",
        ".bmp": "image/bmp",
    }

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.5-flash",
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
    ) -> None:
        """Initialize GeminiAnalyzer.

        Args:
            api_key: Google AI API key.
            model: Gemini model name.
            system_prompt: Override for system prompt
                (default: load Form2SDCTemplate.md).
            temperature: Generation temperature
                (low for faithful extraction).
        """
        self._api_key = api_key
        self._model = model
        self._temperature = temperature
        self._system_prompt = system_prompt or load_system_prompt()

    def analyze(
        self,
        file_path: Optional[Path] = None,
        file_content: Optional[bytes] = None,
        mime_type: Optional[str] = None,
        additional_instructions: str = "",
    ) -> FormAnalysis:
        """Analyze a form using the Gemini REST API.

        Args:
            file_path: Path to form file.
            file_content: Raw file bytes.
            mime_type: MIME type (auto-detected from file_path if
                not provided).
            additional_instructions: Extra context for analysis.

        Returns:
            FormAnalysis with extracted form structure.
        """
        # Prepare file content
        if file_path is not None:
            file_path = Path(file_path)
            if file_content is None:
                file_content = file_path.read_bytes()
            if mime_type is None:
                mime_type = self._MIME_MAP.get(
                    file_path.suffix.lower(), "application/octet-stream"
                )

        if file_content is None:
            raise ValueError(
                "Either file_path or file_content must be provided"
            )

        if mime_type is None:
            mime_type = "application/octet-stream"

        # Build the JSON schema for the prompt
        schema_json = json.dumps(
            FormAnalysis.model_json_schema(), indent=2
        )

        user_prompt = (
            "Analyze this form and extract its structure. "
            "Identify all fields, their data types, constraints, "
            "and relationships. "
            "Create appropriate clusters and sub-clusters for "
            "logical groupings.\n\n"
            "Return ONLY a JSON object (no markdown fences, "
            "no commentary) conforming to this schema:\n"
            f"{schema_json}"
        )
        if additional_instructions:
            user_prompt += (
                f"\n\nAdditional instructions: "
                f"{additional_instructions}"
            )

        # Build REST API request body
        file_b64 = base64.standard_b64encode(file_content).decode("ascii")

        request_body = {
            "systemInstruction": {
                "parts": [{"text": self._system_prompt}],
            },
            "contents": [
                {
                    "parts": [
                        {
                            "inlineData": {
                                "mimeType": mime_type,
                                "data": file_b64,
                            },
                        },
                        {"text": user_prompt},
                    ],
                },
            ],
            "generationConfig": {
                "temperature": self._temperature,
                "responseMimeType": "application/json",
            },
        }

        # Call the Gemini REST API directly (no SDK)
        url = (
            f"{_GEMINI_API_URL}/{self._model}:generateContent"
            f"?key={self._api_key}"
        )
        req = urllib.request.Request(
            url,
            data=json.dumps(request_body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                response_data = json.loads(
                    resp.read().decode("utf-8")
                )
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Gemini API error {e.code}: {body}"
            ) from e

        # Extract text from response
        try:
            result_text = (
                response_data["candidates"][0]["content"]
                ["parts"][0]["text"]
            )
        except (KeyError, IndexError) as e:
            raise RuntimeError(
                f"Unexpected Gemini response format: "
                f"{json.dumps(response_data, indent=2)[:500]}"
            ) from e

        # Strip markdown fences if present
        result_text = result_text.strip()
        fence_match = re.search(
            r"```(?:json)?\s*\n(.*?)\n\s*```",
            result_text,
            re.DOTALL,
        )
        if fence_match:
            result_text = fence_match.group(1)

        # Parse and validate with Pydantic
        result_data = json.loads(result_text)
        return FormAnalysis.model_validate(result_data)
