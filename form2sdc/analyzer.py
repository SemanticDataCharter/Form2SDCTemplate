"""Form analyzer protocol and Gemini implementation.

Gemini-first with a thin FormAnalyzer protocol for swappability.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Protocol, runtime_checkable

from form2sdc.prompt_loader import load_system_prompt
from form2sdc.types import FormAnalysis


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
    """Gemini-powered form analyzer using google-genai SDK.

    Uses Form2SDCTemplate.md as system prompt and structured output
    to convert forms into SDC4-compliant template data.
    """

    # MIME type detection
    _MIME_MAP = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
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
            system_prompt: Override for system prompt (default: load Form2SDCTemplate.md).
            temperature: Generation temperature (low for faithful extraction).
        """
        try:
            from google import genai
            from google.genai import types as genai_types
        except ImportError:
            raise ImportError(
                "google-genai package required. Install with: "
                "pip install 'form2sdc[gemini]'"
            )

        self._genai = genai
        self._genai_types = genai_types
        self._model = model
        self._temperature = temperature
        self._system_prompt = system_prompt or load_system_prompt()
        self._client = genai.Client(api_key=api_key)

    def analyze(
        self,
        file_path: Optional[Path] = None,
        file_content: Optional[bytes] = None,
        mime_type: Optional[str] = None,
        additional_instructions: str = "",
    ) -> FormAnalysis:
        """Analyze a form using Gemini.

        Args:
            file_path: Path to form file.
            file_content: Raw file bytes.
            mime_type: MIME type (auto-detected from file_path if not provided).
            additional_instructions: Extra context for analysis.

        Returns:
            FormAnalysis with extracted form structure.
        """
        genai_types = self._genai_types

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
            raise ValueError("Either file_path or file_content must be provided")

        if mime_type is None:
            mime_type = "application/octet-stream"

        # Build prompt parts
        parts = [
            genai_types.Part.from_bytes(data=file_content, mime_type=mime_type),
        ]

        # Include the JSON schema in the prompt so Gemini knows the
        # target structure.  We avoid response_schema= entirely because
        # the google-genai SDK's process_schema recurses too deeply on
        # the nested ClusterDefinition model and hits Python's limit.
        schema_json = json.dumps(
            FormAnalysis.model_json_schema(), indent=2
        )

        user_prompt = (
            "Analyze this form and extract its structure. "
            "Identify all fields, their data types, constraints, and relationships. "
            "Create appropriate clusters and sub-clusters for logical groupings.\n\n"
            "Return your response as a single JSON object conforming to this schema:\n"
            f"```json\n{schema_json}\n```"
        )
        if additional_instructions:
            user_prompt += f"\n\nAdditional instructions: {additional_instructions}"

        parts.append(genai_types.Part.from_text(text=user_prompt))

        # Request JSON output without response_schema to avoid SDK
        # RecursionError on deeply nested Pydantic models
        response = self._client.models.generate_content(
            model=self._model,
            contents=parts,
            config=genai_types.GenerateContentConfig(
                system_instruction=self._system_prompt,
                temperature=self._temperature,
                response_mime_type="application/json",
            ),
        )

        # Parse and validate with Pydantic
        result_text = response.text
        result_data = json.loads(result_text)
        return FormAnalysis.model_validate(result_data)
