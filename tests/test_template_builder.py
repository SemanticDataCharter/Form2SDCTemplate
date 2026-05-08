"""Tests for ``form2sdc.template_builder`` including round-trip validation.

The round-trip contract: building a template from a FormAnalysis produces
markdown that the Form2SDCValidator accepts (no errors), and that md2pd
will parse without rejection or silent data loss.
"""

from __future__ import annotations

import pytest

from form2sdc.template_builder import TemplateBuilder
from form2sdc.validator import Form2SDCValidator
from form2sdc.types import (
    AttestationDefinition,
    AuditDefinition,
    ClusterDefinition,
    ColumnDefinition,
    ColumnType,
    Constraint,
    EnumerationItem,
    FormAnalysis,
    PartyDefinition,
)


# ── Helpers ─────────────────────────────────────────────────────────


def _minimal_column(name: str = "x", col_type: ColumnType = ColumnType.TEXT) -> ColumnDefinition:
    return ColumnDefinition(
        name=name,
        column_type=col_type,
        description=f"Description for {name}",
        examples=["example1", "example2"],
    )


def _minimal_data(name: str = "Root") -> ClusterDefinition:
    return ClusterDefinition(
        name=name,
        description="Test data section.",
        columns=[_minimal_column("field_a"), _minimal_column("field_b", ColumnType.INTEGER)],
    )


def _minimal_analysis() -> FormAnalysis:
    return FormAnalysis(
        dataset_name="Test Dataset",
        dataset_description="A test dataset.",
        data=_minimal_data(),
    )


# ── Front matter ────────────────────────────────────────────────────


def test_front_matter_has_template_version_4() -> None:
    md = TemplateBuilder().build(_minimal_analysis())
    assert 'template_version: "4.0.0"' in md


def test_front_matter_has_dataset_name() -> None:
    md = TemplateBuilder().build(_minimal_analysis())
    assert 'name: "Test Dataset"' in md


def test_front_matter_has_enrichment_block() -> None:
    md = TemplateBuilder().build(_minimal_analysis())
    assert "enrichment:" in md
    assert "enable_llm: true" in md


def test_front_matter_disable_enrichment() -> None:
    analysis = _minimal_analysis()
    analysis.enable_llm = False
    md = TemplateBuilder().build(analysis)
    assert "enable_llm: false" in md


def test_front_matter_does_not_emit_source_language() -> None:
    md = TemplateBuilder().build(_minimal_analysis())
    assert "source_language" not in md


# ── Dataset overview ────────────────────────────────────────────────


def test_dataset_overview_uses_h1_not_html_comment() -> None:
    md = TemplateBuilder().build(_minimal_analysis())
    assert "# Dataset Overview" in md
    assert "<!-- Dataset:" not in md  # the old HTML-comment form must not appear


def test_dataset_overview_renders_purpose_and_business_context() -> None:
    analysis = _minimal_analysis()
    analysis.purpose = "Why this dataset exists"
    analysis.business_context = "How it is used"
    md = TemplateBuilder().build(analysis)
    assert "**Purpose**: Why this dataset exists" in md
    assert "**Business Context**: How it is used" in md


# ── Data section ────────────────────────────────────────────────────


def test_data_section_uses_data_prefix_not_cluster() -> None:
    md = TemplateBuilder().build(_minimal_analysis())
    assert "## Data: Root" in md
    assert "## Cluster:" not in md
    assert "## Root Cluster:" not in md


def test_data_section_emits_description_as_prose_not_keyword() -> None:
    md = TemplateBuilder().build(_minimal_analysis())
    # The cluster description should appear as prose, NOT as **Description**:
    assert "Test data section." in md
    # Check that there's no **Description**: line within the Data section's keywords
    data_section = md.split("## Data: Root")[1].split("###")[0]
    assert "**Description**:" not in data_section


def test_data_section_does_not_emit_type_cluster_keyword() -> None:
    md = TemplateBuilder().build(_minimal_analysis())
    # The old builder emitted **Type**: Cluster at the section level — must be gone.
    assert "**Type**: Cluster" not in md


def test_data_section_emits_rules() -> None:
    analysis = _minimal_analysis()
    analysis.data.rules = [
        "field_a must be before field_b",
        "At least one of x or y must be provided",
    ]
    md = TemplateBuilder().build(analysis)
    assert "**Rules**:" in md
    assert "field_a must be before field_b" in md


# ── Column rendering ────────────────────────────────────────────────


def test_columns_use_simple_h3_no_column_prefix() -> None:
    md = TemplateBuilder().build(_minimal_analysis())
    assert "### field_a" in md
    assert "### field_b" in md
    assert "### Column:" not in md


def test_column_emits_type_first() -> None:
    md = TemplateBuilder().build(_minimal_analysis())
    section = md.split("### field_a")[1].split("###")[0]
    lines = [line for line in section.split("\n") if line.strip().startswith("**")]
    assert lines[0].startswith("**Type**:")


def test_column_emits_examples_comma_separated() -> None:
    md = TemplateBuilder().build(_minimal_analysis())
    assert "**Examples**: example1, example2" in md


# ── Constraints ─────────────────────────────────────────────────────


def test_constraints_required_only() -> None:
    analysis = _minimal_analysis()
    analysis.data.columns[0].constraints = Constraint(required=True)
    md = TemplateBuilder().build(analysis)
    assert "**Constraints**:" in md
    assert "  - required: true" in md


def test_constraints_range_from_min_max_values() -> None:
    analysis = _minimal_analysis()
    analysis.data.columns[0].constraints = Constraint(min_value=0, max_value=120)
    md = TemplateBuilder().build(analysis)
    assert "  - range: [0, 120]" in md


def test_constraints_range_with_only_min_uses_null_for_max() -> None:
    analysis = _minimal_analysis()
    analysis.data.columns[0].constraints = Constraint(min_value=0)
    md = TemplateBuilder().build(analysis)
    assert "  - range: [0, null]" in md


def test_constraints_range_with_only_max_uses_null_for_min() -> None:
    analysis = _minimal_analysis()
    analysis.data.columns[0].constraints = Constraint(max_value=999.99)
    md = TemplateBuilder().build(analysis)
    assert "  - range: [null, 999.99]" in md


def test_constraints_precision() -> None:
    analysis = _minimal_analysis()
    analysis.data.columns[0].constraints = Constraint(precision=2)
    md = TemplateBuilder().build(analysis)
    assert "  - precision: 2" in md


def test_constraints_does_not_emit_flat_keywords() -> None:
    """Ensure none of the legacy flat-constraint keywords leak into output."""
    analysis = _minimal_analysis()
    analysis.data.columns[0].constraints = Constraint(
        required=True, min_value=0, max_value=10, precision=2
    )
    md = TemplateBuilder().build(analysis)
    for legacy in (
        "**Pattern**:",
        "**Min Length**:",
        "**Max Length**:",
        "**Min Magnitude**:",
        "**Max Magnitude**:",
        "**Precision**:",
        "**Fraction Digits**:",
        "**Temporal Type**:",
        "**Min Date**:",
        "**Max Date**:",
        "**Default Value**:",
        "**Media Types**:",
        "**Max Size**:",
    ):
        assert legacy not in md, f"Legacy flat keyword leaked into output: {legacy}"


# ── Enumeration ─────────────────────────────────────────────────────


def test_enumeration_renders_as_bulleted_list() -> None:
    analysis = _minimal_analysis()
    analysis.data.columns[0].enumeration = [
        EnumerationItem(value="active", description="Account in good standing"),
        EnumerationItem(value="closed", description="Permanently closed"),
    ]
    md = TemplateBuilder().build(analysis)
    assert "**Enumeration**:" in md
    assert "  - active: Account in good standing" in md
    assert "  - closed: Permanently closed" in md


# ── Semantic links ──────────────────────────────────────────────────


def test_semantic_links_render_as_bulleted_list_not_comma_separated() -> None:
    analysis = _minimal_analysis()
    analysis.data.columns[0].semantic_links = [
        "https://loinc.org/21112-8/",
        "http://snomed.info/id/248153007",
    ]
    md = TemplateBuilder().build(analysis)
    assert "**Semantic Links**:" in md
    # The new form is one URI per bullet line, not comma-joined.
    assert "  - https://loinc.org/21112-8/" in md
    assert "  - http://snomed.info/id/248153007" in md
    assert "https://loinc.org/21112-8/, http://snomed.info" not in md


# ── ReuseComponent ──────────────────────────────────────────────────


def test_reuse_component_renders_at_column_level() -> None:
    analysis = _minimal_analysis()
    analysis.data.columns[0].reuse_component = "@NIEM:StateUSPostalServiceCode"
    md = TemplateBuilder().build(analysis)
    assert "**ReuseComponent**: @NIEM:StateUSPostalServiceCode" in md


# ── Subject / Provider / Participation ──────────────────────────────


def test_subject_section() -> None:
    analysis = _minimal_analysis()
    analysis.subject = PartyDefinition(
        name="Patient",
        description="The patient",
        party_type="subject",
        columns=[_minimal_column("patient_id")],
    )
    md = TemplateBuilder().build(analysis)
    assert "## Subject: Patient" in md
    assert "**Description**: The patient" in md


def test_participation_section_emits_function_and_mode() -> None:
    analysis = _minimal_analysis()
    analysis.participations = [
        PartyDefinition(
            name="Examining Clinician",
            description="Performs examination",
            party_type="participation",
            function="Examiner",
            function_description="Documents the examination",
            mode="present",
            mode_description="In person",
            columns=[_minimal_column("clinician_id")],
        )
    ]
    md = TemplateBuilder().build(analysis)
    assert "## Participation: Examining Clinician" in md
    assert "**Function**: Examiner" in md
    assert "**Mode**: present" in md


# ── Attestation / Audit / Links ─────────────────────────────────────


def test_attestation_does_not_emit_committer() -> None:
    analysis = _minimal_analysis()
    analysis.attestation = AttestationDefinition(
        name="Sign-off",
        view="Clinical Summary",
        proof="Clinician Signature",
        reason="Attestation Reason",
    )
    md = TemplateBuilder().build(analysis)
    assert "## Attestation: Sign-off" in md
    assert "**View**: Clinical Summary" in md
    assert "**Committer**:" not in md


def test_audit_section() -> None:
    analysis = _minimal_analysis()
    analysis.audit = [
        AuditDefinition(
            name="Provenance",
            system_id="ehr-prod-01",
            system_user="clinician_jdoe",
            location="Hospital",
        )
    ]
    md = TemplateBuilder().build(analysis)
    assert "## Audit: Provenance" in md
    assert "**System ID**: ehr-prod-01" in md


def test_links_section() -> None:
    analysis = _minimal_analysis()
    analysis.links = [
        "https://www.w3.org/TR/prov-o/",
        "urn:oid:2.16.840.1.113883.4.1",
    ]
    md = TemplateBuilder().build(analysis)
    assert "## Links:" in md
    assert "  - https://www.w3.org/TR/prov-o/" in md
    assert "  - urn:oid:2.16.840.1.113883.4.1" in md


# ── Round-trip: build → validate ────────────────────────────────────


def test_round_trip_minimal_template_validates() -> None:
    md = TemplateBuilder().build(_minimal_analysis())
    result = Form2SDCValidator().validate(md)
    assert result.valid, (
        f"Round-trip validation failed:\n"
        + "\n".join(f"  [{e.code}] {e.message}" for e in result.errors)
        + f"\n\nGenerated markdown:\n{md}"
    )


def test_round_trip_with_constraints_validates() -> None:
    analysis = _minimal_analysis()
    analysis.data.columns[0].constraints = Constraint(
        required=True, min_value=0, max_value=100
    )
    md = TemplateBuilder().build(analysis)
    result = Form2SDCValidator().validate(md)
    assert result.valid, (
        f"Round-trip with constraints failed:\n"
        + "\n".join(f"  [{e.code}] {e.message}" for e in result.errors)
    )


def test_round_trip_complete_template_validates() -> None:
    analysis = FormAnalysis(
        dataset_name="Patient Registration",
        dataset_description="Patient demographic data.",
        creator="Clinical Systems Team",
        purpose="Capture patient demographics for clinical care.",
        business_context="Used by clinical staff and billing.",
        data=ClusterDefinition(
            name="Patient Demographics",
            description="Patient identification and demographic information.",
            purpose="Unique patient identification.",
            columns=[
                ColumnDefinition(
                    name="patient_id",
                    column_type=ColumnType.IDENTIFIER,
                    description="Unique patient identifier.",
                    constraints=Constraint(required=True),
                    examples=["PAT-12345"],
                ),
                ColumnDefinition(
                    name="age",
                    column_type=ColumnType.INTEGER,
                    description="Age in completed years.",
                    units="years",
                    constraints=Constraint(required=True, min_value=0, max_value=120),
                    examples=["25", "42"],
                ),
                ColumnDefinition(
                    name="account_status",
                    column_type=ColumnType.TEXT,
                    description="Patient account status.",
                    enumeration=[
                        EnumerationItem(value="active", description="Active"),
                        EnumerationItem(value="closed", description="Closed"),
                    ],
                    examples=["active"],
                ),
            ],
        ),
        subject=PartyDefinition(
            name="Patient",
            description="The patient.",
            party_type="subject",
            columns=[
                ColumnDefinition(
                    name="full_name",
                    column_type=ColumnType.TEXT,
                    description="Patient's full name.",
                    examples=["Jane Doe"],
                )
            ],
        ),
    )
    md = TemplateBuilder().build(analysis)
    result = Form2SDCValidator().validate(md)
    assert result.valid, (
        f"Round-trip with complete template failed:\n"
        + "\n".join(f"  [{e.code}] {e.message}" for e in result.errors)
    )
