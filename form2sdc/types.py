"""Pydantic models for structured data exchange between Gemini and the template builder.

Uses user-friendly type names (matching Form2SDCTemplate.md PART 6).
The template builder handles mapping to SDC4 internal types.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ColumnType(str, Enum):
    """User-friendly column type names from Form2SDCTemplate.md PART 6."""

    TEXT = "text"
    INTEGER = "integer"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    TIME = "time"
    IDENTIFIER = "identifier"
    EMAIL = "email"
    URL = "url"
    # Explicit SDC4 types (advanced users)
    XDSTRING = "XdString"
    XDTOKEN = "XdToken"
    XDCOUNT = "XdCount"
    XDORDINAL = "XdOrdinal"
    XDQUANTITY = "XdQuantity"
    XDFLOAT = "XdFloat"
    XDDOUBLE = "XdDouble"
    XDBOOLEAN = "XdBoolean"
    XDTEMPORAL = "XdTemporal"
    XDLINK = "XdLink"
    XDFILE = "XdFile"
    CLUSTER = "Cluster"


# Mapping from user-friendly types to SDC4 internal types
FRIENDLY_TO_SDC4: dict[str, str] = {
    "text": "XdString",
    "integer": "XdCount",
    "decimal": "XdQuantity",
    "boolean": "XdBoolean",
    "date": "XdTemporal",
    "datetime": "XdTemporal",
    "time": "XdTemporal",
    "identifier": "XdString",
    "email": "XdString",
    "url": "XdLink",
}


def resolve_sdc4_type(column_type: str) -> str:
    """Resolve a user-friendly or explicit type name to its SDC4 type."""
    return FRIENDLY_TO_SDC4.get(column_type, column_type)


class Constraint(BaseModel):
    """Validation constraints for a column.

    Only the constraints that the production md2pd parser acts on are modeled here:

    - ``required`` → sets column nullability (required vs optional).
    - ``min_value`` / ``max_value`` → rendered as ``range: [min, max]``, used by
      md2pd to populate the column's ``range_values`` field.
    - ``precision`` → drives type inference for decimal user types
      (``precision == 2`` → XdQuantity; ``precision >= 10`` → XdDouble).

    Other validation hints (length limits, regex patterns, format strings,
    media-type filters, default values, etc.) are intentionally not modeled:
    md2pd silently drops them, so capturing them here would create false
    expectations. Express such hints in ``description`` or ``business_rules``
    as free text instead.
    """

    required: Optional[bool] = None
    min_value: Optional[float] = Field(None, description="Min magnitude/length")
    max_value: Optional[float] = Field(None, description="Max magnitude/length")
    precision: Optional[int] = Field(
        None,
        description="Total significant digits; affects md2pd type inference for decimals",
    )


class EnumerationItem(BaseModel):
    """A single enumeration value with optional label and description."""

    value: str
    label: Optional[str] = None
    description: Optional[str] = None


class ColumnDefinition(BaseModel):
    """A single column/field definition within a cluster."""

    name: str = Field(..., description="Column name")
    column_type: ColumnType = Field(..., description="Data type")
    description: str = Field("", description="Human-readable description")
    examples: Optional[list[str]] = Field(None, description="2-3 sample values")
    units: Optional[str] = Field(None, description="Units for quantified types")
    enumeration: Optional[list[EnumerationItem]] = None
    constraints: Optional[Constraint] = None
    business_rules: Optional[str] = None
    relationships: Optional[str] = None
    semantic_links: Optional[list[str]] = Field(
        None, description="URIs to ontology terms"
    )
    reuse_component: Optional[str] = Field(
        None, description="@ProjectName:ComponentLabel"
    )


class ClusterDefinition(BaseModel):
    """A flat grouping of columns within a named-tree section.

    md2pd treats each ``## Data:`` (or ``## Workflow:``) section as a flat
    cluster of columns. Cluster-level validation constraints are not supported
    by md2pd and are intentionally not modeled here.
    """

    name: str = Field(..., description="Cluster name")
    description: str = Field("", description="What this cluster represents")
    purpose: Optional[str] = None
    business_context: Optional[str] = None
    rules: Optional[list[str]] = Field(
        None,
        description="Cross-field validation rules (rendered as **Rules**: bulleted list)",
    )
    columns: list[ColumnDefinition] = Field(default_factory=list)


class PartyDefinition(BaseModel):
    """A participation party (Subject, Provider, or Participation)."""

    name: str = Field(..., description="Party name")
    description: str = Field("", description="Role description")
    party_type: str = Field(
        ..., description="'subject', 'provider', or 'participation'"
    )
    function: Optional[str] = Field(
        None, description="Function label (Participation only)"
    )
    function_description: Optional[str] = None
    mode: Optional[str] = Field(
        None, description="Interaction mode (Participation only)"
    )
    mode_description: Optional[str] = None
    columns: list[ColumnDefinition] = Field(default_factory=list)


class AttestationDefinition(BaseModel):
    """Attestation section — fixed fields from SDC4 model.

    md2pd's attestation parser reads ``**View**:``, ``**Proof**:``, and
    ``**Reason**:`` fields. The committer is modeled separately in the SDC4
    reference model as a Party and is not parsed from the Attestation section
    by md2pd, so it is intentionally omitted here.
    """

    name: str
    view: Optional[str] = Field(None, description="View label (e.g. 'Clinical Summary')")
    proof: Optional[str] = Field(None, description="Proof label (e.g. 'Clinician Signature')")
    reason: Optional[str] = Field(None, description="Reason label (e.g. 'Attestation Reason')")


class AuditDefinition(BaseModel):
    """Audit section — fixed fields from SDC4 model."""

    name: str
    system_id: Optional[str] = Field(None, description="System identifier")
    system_user: Optional[str] = Field(None, description="User description")
    location: Optional[str] = Field(None, description="Location description")


class FormAnalysis(BaseModel):
    """Top-level analysis result from a form analyzer.

    This is the structured output contract between Gemini and the template builder.
    The 8 named trees match the SDC4 data model.
    """

    dataset_name: str = Field(..., description="Name of the dataset/project")
    dataset_description: str = Field("", description="2-4 sentence overview")
    domain: Optional[str] = Field(
        None, description="Healthcare, Finance, Government, etc."
    )
    creator: Optional[str] = None
    purpose: Optional[str] = None
    business_context: Optional[str] = None
    primary_use: Optional[str] = None
    secondary_use: Optional[str] = None
    stakeholders: Optional[str] = None
    enable_llm: Optional[bool] = Field(
        True, description="Whether to enable LLM enrichment"
    )

    # 8 Named Trees (SDC4 data model)
    data: ClusterDefinition = Field(
        ..., description="Data section — required, flat columns"
    )
    subject: Optional[PartyDefinition] = None
    provider: Optional[PartyDefinition] = None
    participations: Optional[list[PartyDefinition]] = None
    workflow: Optional[ClusterDefinition] = Field(
        None, description="Workflow section — flat columns"
    )
    attestation: Optional[AttestationDefinition] = None
    audit: Optional[list[AuditDefinition]] = Field(
        None, description="Audit sections — multiple allowed"
    )
    links: Optional[list[str]] = Field(
        None, description="URI list for linked resources"
    )
