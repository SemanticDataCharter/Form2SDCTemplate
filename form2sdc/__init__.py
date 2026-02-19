"""form2sdc - Convert forms to SDC4-compliant templates."""

__version__ = "4.2.0"

from form2sdc.types import (
    ColumnType,
    Constraint,
    EnumerationItem,
    ColumnDefinition,
    ClusterDefinition,
    PartyDefinition,
    FormAnalysis,
)
from form2sdc.validator import Form2SDCValidator, ValidationResult, ValidationIssue
from form2sdc.template_builder import TemplateBuilder

__all__ = [
    "ColumnType",
    "Constraint",
    "EnumerationItem",
    "ColumnDefinition",
    "ClusterDefinition",
    "PartyDefinition",
    "FormAnalysis",
    "Form2SDCValidator",
    "ValidationResult",
    "ValidationIssue",
    "TemplateBuilder",
]
