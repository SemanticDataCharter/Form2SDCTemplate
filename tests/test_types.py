"""Tests for the Pydantic models in ``form2sdc.types``.

The 4.5.0 cleanup slimmed the Constraint model down to only the fields md2pd
acts on. These tests pin down the new shape.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

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
    resolve_sdc4_type,
)


# ── resolve_sdc4_type ───────────────────────────────────────────────


def test_resolve_user_friendly_text_to_xdstring() -> None:
    assert resolve_sdc4_type("text") == "XdString"


def test_resolve_user_friendly_integer_to_xdcount() -> None:
    assert resolve_sdc4_type("integer") == "XdCount"


def test_resolve_user_friendly_decimal_to_xdquantity() -> None:
    assert resolve_sdc4_type("decimal") == "XdQuantity"


def test_resolve_user_friendly_date_to_xdtemporal() -> None:
    assert resolve_sdc4_type("date") == "XdTemporal"


def test_resolve_explicit_sdc4_type_passthrough() -> None:
    assert resolve_sdc4_type("XdOrdinal") == "XdOrdinal"


# ── Constraint model ─────────────────────────────────────────────────


def test_constraint_accepts_required() -> None:
    c = Constraint(required=True)
    assert c.required is True


def test_constraint_accepts_min_max_value() -> None:
    c = Constraint(min_value=0, max_value=100)
    assert c.min_value == 0
    assert c.max_value == 100


def test_constraint_accepts_precision() -> None:
    c = Constraint(precision=2)
    assert c.precision == 2


# ── EnumerationItem / ColumnDefinition ───────────────────────────────


def test_enumeration_item_minimal() -> None:
    item = EnumerationItem(value="active")
    assert item.value == "active"
    assert item.label is None


def test_column_definition_minimal() -> None:
    col = ColumnDefinition(
        name="age",
        column_type=ColumnType.INTEGER,
        description="Age in years",
    )
    assert col.name == "age"
    assert col.column_type == ColumnType.INTEGER


def test_column_definition_with_reuse_component() -> None:
    col = ColumnDefinition(
        name="state",
        column_type=ColumnType.TEXT,
        description="US state code",
        reuse_component="@NIEM:StateUSPostalServiceCode",
    )
    assert col.reuse_component == "@NIEM:StateUSPostalServiceCode"


# ── ClusterDefinition ───────────────────────────────────────────────


def test_cluster_definition_with_rules() -> None:
    cluster = ClusterDefinition(
        name="Patient Record",
        description="Patient data",
        rules=["start_date must be before end_date"],
    )
    assert cluster.rules == ["start_date must be before end_date"]


# ── PartyDefinition / AttestationDefinition / AuditDefinition ────────


def test_party_definition_subject() -> None:
    party = PartyDefinition(
        name="Patient",
        description="The patient",
        party_type="subject",
    )
    assert party.party_type == "subject"


def test_attestation_definition_minimal() -> None:
    att = AttestationDefinition(
        name="Encounter Sign-off",
        view="Clinical Summary",
        proof="Clinician Signature",
        reason="Attestation Reason",
    )
    assert att.view == "Clinical Summary"


def test_audit_definition_minimal() -> None:
    audit = AuditDefinition(name="Provenance")
    assert audit.name == "Provenance"


# ── FormAnalysis ────────────────────────────────────────────────────


def _minimal_data() -> ClusterDefinition:
    return ClusterDefinition(
        name="Root",
        description="Root cluster",
        columns=[
            ColumnDefinition(
                name="x",
                column_type=ColumnType.TEXT,
                description="A field",
            )
        ],
    )


def test_form_analysis_minimal() -> None:
    analysis = FormAnalysis(
        dataset_name="Test",
        data=_minimal_data(),
    )
    assert analysis.dataset_name == "Test"
    assert analysis.enable_llm is True
