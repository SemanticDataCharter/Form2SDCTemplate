"""form2sdc - Convert forms to SDC4-compliant templates."""

__version__ = "4.6.0"

from form2sdc.types import (
    ColumnType,
    Constraint,
    EnumerationItem,
    ColumnDefinition,
    ClusterDefinition,
    PartyDefinition,
    AttestationDefinition,
    AuditDefinition,
    FormAnalysis,
)
from form2sdc.validator import Form2SDCValidator, ValidationResult, ValidationIssue
from form2sdc.template_builder import TemplateBuilder
from form2sdc.catalog import (
    CatalogClient,
    CatalogMatch,
    ReuseReport,
    apply_catalog_reuse,
)

__all__ = [
    "ColumnType",
    "Constraint",
    "EnumerationItem",
    "ColumnDefinition",
    "ClusterDefinition",
    "PartyDefinition",
    "AttestationDefinition",
    "AuditDefinition",
    "FormAnalysis",
    "Form2SDCValidator",
    "ValidationResult",
    "ValidationIssue",
    "TemplateBuilder",
    "CatalogClient",
    "CatalogMatch",
    "ReuseReport",
    "apply_catalog_reuse",
]
