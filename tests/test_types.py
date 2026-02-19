"""Tests for form2sdc.types Pydantic models."""

import pytest
from pydantic import ValidationError

from form2sdc.types import (
    ColumnDefinition,
    ColumnType,
    ClusterDefinition,
    Constraint,
    EnumerationItem,
    FormAnalysis,
    PartyDefinition,
    resolve_sdc4_type,
    FRIENDLY_TO_SDC4,
)


class TestColumnType:
    """Test ColumnType enum."""

    def test_user_friendly_types(self):
        assert ColumnType.TEXT == "text"
        assert ColumnType.INTEGER == "integer"
        assert ColumnType.DECIMAL == "decimal"
        assert ColumnType.BOOLEAN == "boolean"
        assert ColumnType.DATE == "date"
        assert ColumnType.DATETIME == "datetime"
        assert ColumnType.TIME == "time"
        assert ColumnType.IDENTIFIER == "identifier"
        assert ColumnType.EMAIL == "email"
        assert ColumnType.URL == "url"

    def test_sdc4_explicit_types(self):
        assert ColumnType.XDSTRING == "XdString"
        assert ColumnType.XDCOUNT == "XdCount"
        assert ColumnType.XDQUANTITY == "XdQuantity"
        assert ColumnType.CLUSTER == "Cluster"

    def test_from_string(self):
        assert ColumnType("text") == ColumnType.TEXT
        assert ColumnType("XdString") == ColumnType.XDSTRING


class TestResolveSdc4Type:
    """Test type resolution from friendly to SDC4."""

    def test_friendly_mappings(self):
        assert resolve_sdc4_type("text") == "XdString"
        assert resolve_sdc4_type("integer") == "XdCount"
        assert resolve_sdc4_type("decimal") == "XdQuantity"
        assert resolve_sdc4_type("boolean") == "XdBoolean"
        assert resolve_sdc4_type("date") == "XdTemporal"
        assert resolve_sdc4_type("url") == "XdLink"

    def test_explicit_types_pass_through(self):
        assert resolve_sdc4_type("XdString") == "XdString"
        assert resolve_sdc4_type("Cluster") == "Cluster"
        assert resolve_sdc4_type("XdOrdinal") == "XdOrdinal"


class TestConstraint:
    """Test Constraint model."""

    def test_empty_constraint(self):
        c = Constraint()
        assert c.required is None
        assert c.min_value is None

    def test_full_constraint(self):
        c = Constraint(
            required=True,
            unique=True,
            min_value=0,
            max_value=100,
            precision=5,
            fraction_digits=2,
            pattern=r"^\d+$",
        )
        assert c.required is True
        assert c.max_value == 100
        assert c.precision == 5


class TestEnumerationItem:
    """Test EnumerationItem model."""

    def test_value_only(self):
        item = EnumerationItem(value="active")
        assert item.value == "active"
        assert item.label is None

    def test_with_description(self):
        item = EnumerationItem(
            value="1", label="Active", description="Account in good standing"
        )
        assert item.label == "Active"


class TestColumnDefinition:
    """Test ColumnDefinition model."""

    def test_minimal_column(self):
        col = ColumnDefinition(name="age", column_type=ColumnType.INTEGER)
        assert col.name == "age"
        assert col.column_type == ColumnType.INTEGER
        assert col.description == ""

    def test_full_column(self):
        col = ColumnDefinition(
            name="weight",
            column_type=ColumnType.DECIMAL,
            description="Patient body weight",
            examples=["72.5", "85.0"],
            units="kg",
            constraints=Constraint(min_value=0, max_value=500),
        )
        assert col.units == "kg"
        assert len(col.examples) == 2

    def test_column_with_enumeration(self):
        col = ColumnDefinition(
            name="status",
            column_type=ColumnType.TEXT,
            enumeration=[
                EnumerationItem(value="active", description="Active account"),
                EnumerationItem(value="inactive", description="Closed"),
            ],
        )
        assert len(col.enumeration) == 2

    def test_missing_required_field(self):
        with pytest.raises(ValidationError):
            ColumnDefinition(column_type=ColumnType.TEXT)  # missing name


class TestClusterDefinition:
    """Test ClusterDefinition model."""

    def test_minimal_cluster(self):
        cluster = ClusterDefinition(name="Root")
        assert cluster.name == "Root"
        assert cluster.columns == []
        assert cluster.sub_clusters == []

    def test_nested_cluster(self):
        cluster = ClusterDefinition(
            name="Patient Record",
            description="All patient data",
            columns=[
                ColumnDefinition(
                    name="name", column_type=ColumnType.TEXT
                )
            ],
            sub_clusters=[
                ClusterDefinition(
                    name="Contact Info",
                    parent="Patient Record",
                    columns=[
                        ColumnDefinition(
                            name="email", column_type=ColumnType.EMAIL
                        )
                    ],
                )
            ],
        )
        assert len(cluster.columns) == 1
        assert len(cluster.sub_clusters) == 1
        assert cluster.sub_clusters[0].parent == "Patient Record"


class TestPartyDefinition:
    """Test PartyDefinition model."""

    def test_subject(self):
        party = PartyDefinition(
            name="Patient",
            description="The patient being recorded",
            party_type="subject",
        )
        assert party.party_type == "subject"

    def test_participation_with_function(self):
        party = PartyDefinition(
            name="Attending Physician",
            description="Doctor overseeing care",
            party_type="participation",
            function="Physician",
            function_description="Medical doctor providing care",
            mode="In-Person",
            mode_description="Physical presence",
        )
        assert party.function == "Physician"
        assert party.mode == "In-Person"


class TestFormAnalysis:
    """Test FormAnalysis model."""

    def test_minimal_analysis(self):
        analysis = FormAnalysis(
            dataset_name="Test",
            root_cluster=ClusterDefinition(name="Root"),
        )
        assert analysis.dataset_name == "Test"
        assert analysis.source_language == "English"

    def test_full_analysis(self):
        analysis = FormAnalysis(
            dataset_name="Patient Demographics",
            dataset_description="Patient demographic information",
            domain="Healthcare",
            creator="Clinical Team",
            source_language="English",
            purpose="Record patient demographics",
            root_cluster=ClusterDefinition(
                name="Patient Record",
                description="Root cluster",
                columns=[
                    ColumnDefinition(
                        name="Full Name",
                        column_type=ColumnType.TEXT,
                        description="Patient legal name",
                    )
                ],
            ),
            subject=PartyDefinition(
                name="Patient",
                description="The patient",
                party_type="subject",
            ),
        )
        assert analysis.domain == "Healthcare"
        assert analysis.subject.name == "Patient"
        assert len(analysis.root_cluster.columns) == 1
