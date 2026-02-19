"""FormToTemplatePipeline: orchestrates file -> analyze -> build -> validate -> result."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from form2sdc.analyzer import FormAnalyzer
from form2sdc.template_builder import TemplateBuilder
from form2sdc.types import FormAnalysis
from form2sdc.validator import Form2SDCValidator, ValidationResult


@dataclass
class PipelineResult:
    """Result of the full pipeline."""

    analysis: FormAnalysis
    template: str
    validation: ValidationResult

    @property
    def valid(self) -> bool:
        """Whether the generated template passes validation."""
        return self.validation.valid


class FormToTemplatePipeline:
    """Orchestrates form-to-template conversion.

    Steps:
    1. Analyze form using FormAnalyzer (Gemini or other)
    2. Build SDC4 markdown template
    3. Validate the generated template
    4. Return complete result
    """

    def __init__(
        self,
        analyzer: FormAnalyzer,
        builder: Optional[TemplateBuilder] = None,
        validator: Optional[Form2SDCValidator] = None,
    ) -> None:
        self.analyzer = analyzer
        self.builder = builder or TemplateBuilder()
        self.validator = validator or Form2SDCValidator()

    def process(
        self,
        file_path: Optional[Path] = None,
        file_content: Optional[bytes] = None,
        mime_type: Optional[str] = None,
        additional_instructions: str = "",
    ) -> PipelineResult:
        """Run the full pipeline.

        Args:
            file_path: Path to form file (PDF, DOCX, image).
            file_content: Raw file bytes (alternative to file_path).
            mime_type: MIME type of the file.
            additional_instructions: Extra context for the analyzer.

        Returns:
            PipelineResult with analysis, template, and validation.
        """
        # Step 1: Analyze
        analysis = self.analyzer.analyze(
            file_path=file_path,
            file_content=file_content,
            mime_type=mime_type,
            additional_instructions=additional_instructions,
        )

        # Step 2: Build template
        template = self.builder.build(analysis)

        # Step 3: Validate
        document_name = str(file_path) if file_path else "generated"
        validation = self.validator.validate(template, document=document_name)

        return PipelineResult(
            analysis=analysis,
            template=template,
            validation=validation,
        )

    def process_analysis(self, analysis: FormAnalysis) -> PipelineResult:
        """Build and validate from an existing FormAnalysis (no LLM call).

        Useful for testing or when analysis was done separately.
        """
        template = self.builder.build(analysis)
        validation = self.validator.validate(template, document="from-analysis")
        return PipelineResult(
            analysis=analysis,
            template=template,
            validation=validation,
        )
