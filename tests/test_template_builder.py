"""Tests for form2sdc.template_builder including round-trip validation."""

import pytest

from form2sdc.template_builder import TemplateBuilder
from form2sdc.validator import Form2SDCValidator
from form2sdc.types import (
    ClusterDefinition,
    ColumnDefinition,
    ColumnType,
    Constraint,
    EnumerationItem,
    FormAnalysis,
    PartyDefinition,
)


@pytest.fixture
def builder():
    return TemplateBuilder()


@pytest.fixture
def validator():
    return Form2SDCValidator()


class TestFrontMatter:
    """Test YAML front matter generation."""

    def test_minimal_front_matter(self, builder):
        analysis = FormAnalysis(
            dataset_name="Test",
            root_cluster=ClusterDefinition(name="Root"),
        )
        result = builder.build(analysis)
        assert '---' in result
        assert 'project_name: "Test"' in result
        assert 'source_language: "English"' in result
        assert 'template_version: "4.0.0"' in result

    def test_front_matter_with_metadata(self, builder):
        analysis = FormAnalysis(
            dataset_name="Test",
            dataset_description="A description",
            domain="Healthcare",
            creator="Test Author",
            root_cluster=ClusterDefinition(name="Root"),
        )
        result = builder.build(analysis)
        assert 'description: "A description"' in result
        assert 'author: "Test Author"' in result
        assert 'domain: "Healthcare"' in result


class TestRootCluster:
    """Test root cluster rendering."""

    def test_basic_cluster(self, builder):
        analysis = FormAnalysis(
            dataset_name="Test",
            root_cluster=ClusterDefinition(
                name="Patient Record",
                description="All patient data",
            ),
        )
        result = builder.build(analysis)
        assert "## Patient Record" in result
        assert "**Type**: Cluster" in result
        assert "**Description**: All patient data" in result


class TestColumnRendering:
    """Test column/field rendering."""

    def test_string_column(self, builder):
        analysis = FormAnalysis(
            dataset_name="Test",
            root_cluster=ClusterDefinition(
                name="Root",
                columns=[
                    ColumnDefinition(
                        name="Full Name",
                        column_type=ColumnType.TEXT,
                        description="Person's name",
                        examples=["John Doe", "Jane Smith"],
                    )
                ],
            ),
        )
        result = builder.build(analysis)
        assert "### Full Name" in result
        assert "**Type**: XdString" in result
        assert "**Description**: Person's name" in result
        assert "**Examples**: John Doe, Jane Smith" in result

    def test_quantified_column_with_units(self, builder):
        analysis = FormAnalysis(
            dataset_name="Test",
            root_cluster=ClusterDefinition(
                name="Root",
                columns=[
                    ColumnDefinition(
                        name="Weight",
                        column_type=ColumnType.DECIMAL,
                        description="Body weight",
                        units="kg, lb",
                        constraints=Constraint(min_value=0, max_value=500),
                    )
                ],
            ),
        )
        result = builder.build(analysis)
        assert "**Type**: XdQuantity" in result
        assert "**Units**: kg, lb" in result
        assert "**Min Magnitude**: 0" in result
        assert "**Max Magnitude**: 500" in result

    def test_boolean_column(self, builder):
        analysis = FormAnalysis(
            dataset_name="Test",
            root_cluster=ClusterDefinition(
                name="Root",
                columns=[
                    ColumnDefinition(
                        name="Active",
                        column_type=ColumnType.BOOLEAN,
                        description="Is active",
                        constraints=Constraint(default_value="false"),
                    )
                ],
            ),
        )
        result = builder.build(analysis)
        assert "**Type**: XdBoolean" in result
        assert "**Default Value**: false" in result

    def test_enumeration_rendering(self, builder):
        analysis = FormAnalysis(
            dataset_name="Test",
            root_cluster=ClusterDefinition(
                name="Root",
                columns=[
                    ColumnDefinition(
                        name="Status",
                        column_type=ColumnType.TEXT,
                        description="Account status",
                        enumeration=[
                            EnumerationItem(
                                value="active",
                                description="Account in good standing",
                            ),
                            EnumerationItem(value="inactive", description="Closed"),
                        ],
                    )
                ],
            ),
        )
        result = builder.build(analysis)
        assert "**Enumeration**:" in result
        assert "  - active: Account in good standing" in result
        assert "  - inactive: Closed" in result

    def test_temporal_column(self, builder):
        analysis = FormAnalysis(
            dataset_name="Test",
            root_cluster=ClusterDefinition(
                name="Root",
                columns=[
                    ColumnDefinition(
                        name="Birth Date",
                        column_type=ColumnType.DATE,
                        description="Date of birth",
                        constraints=Constraint(
                            temporal_type="date",
                            min_date="1900-01-01",
                            max_date="2025-12-31",
                        ),
                    )
                ],
            ),
        )
        result = builder.build(analysis)
        assert "**Type**: XdTemporal" in result
        assert "**Temporal Type**: date" in result
        assert "**Min Date**: 1900-01-01" in result

    def test_reuse_component(self, builder):
        analysis = FormAnalysis(
            dataset_name="Test",
            root_cluster=ClusterDefinition(
                name="Root",
                columns=[
                    ColumnDefinition(
                        name="State Code",
                        column_type=ColumnType.TEXT,
                        description="US state code",
                        reuse_component="@NIEM:StateUSPostalServiceCode",
                    )
                ],
            ),
        )
        result = builder.build(analysis)
        assert "**ReuseComponent**: @NIEM:StateUSPostalServiceCode" in result


class TestPartyRendering:
    """Test Subject/Provider/Participation rendering."""

    def test_subject_section(self, builder):
        analysis = FormAnalysis(
            dataset_name="Test",
            root_cluster=ClusterDefinition(name="Root"),
            subject=PartyDefinition(
                name="Patient",
                description="The patient being recorded",
                party_type="subject",
                columns=[
                    ColumnDefinition(
                        name="MRN",
                        column_type=ColumnType.IDENTIFIER,
                        description="Medical record number",
                    )
                ],
            ),
        )
        result = builder.build(analysis)
        assert "## Subject: Patient" in result
        assert "**Description**: The patient being recorded" in result
        assert "### MRN" in result

    def test_participation_with_function(self, builder):
        analysis = FormAnalysis(
            dataset_name="Test",
            root_cluster=ClusterDefinition(name="Root"),
            participations=[
                PartyDefinition(
                    name="Physician",
                    description="Attending doctor",
                    party_type="participation",
                    function="Clinician",
                    function_description="Provides medical care",
                    mode="In-Person",
                    mode_description="Physical presence",
                )
            ],
        )
        result = builder.build(analysis)
        assert "## Participation: Physician" in result
        assert "**Function**: Clinician" in result
        assert "**Mode**: In-Person" in result


class TestSubClusters:
    """Test sub-cluster rendering."""

    def test_sub_cluster(self, builder):
        analysis = FormAnalysis(
            dataset_name="Test",
            root_cluster=ClusterDefinition(
                name="Patient Record",
                description="Root",
                sub_clusters=[
                    ClusterDefinition(
                        name="Contact Info",
                        description="Contact details",
                        purpose="Store contact information",
                        parent="Patient Record",
                        columns=[
                            ColumnDefinition(
                                name="Email",
                                column_type=ColumnType.EMAIL,
                                description="Email address",
                            )
                        ],
                    )
                ],
            ),
        )
        result = builder.build(analysis)
        assert "## Sub-Cluster: Contact Info" in result
        assert "**Purpose**: Store contact information" in result
        assert "**Parent**: Patient Record" in result
        assert "### Email" in result


class TestRoundTrip:
    """Build a template then validate it - must pass validation."""

    def test_round_trip_minimal(self, builder, validator):
        """Build minimal template, validate it."""
        analysis = FormAnalysis(
            dataset_name="Round Trip Test",
            source_language="English",
            root_cluster=ClusterDefinition(
                name="Root",
                description="Root cluster",
                columns=[
                    ColumnDefinition(
                        name="Patient Name",
                        column_type=ColumnType.TEXT,
                        description="Full legal name",
                        examples=["John Doe"],
                    )
                ],
            ),
        )
        template = builder.build(analysis)
        result = validator.validate(template)
        assert result.valid is True, (
            f"Round-trip validation failed with errors: "
            f"{[e.message for e in result.errors]}"
        )

    def test_round_trip_complex(self, builder, validator):
        """Build complex template with multiple types, validate it."""
        analysis = FormAnalysis(
            dataset_name="Complex Test",
            dataset_description="A comprehensive test",
            source_language="English",
            creator="Test Suite",
            domain="Healthcare",
            root_cluster=ClusterDefinition(
                name="Patient Record",
                description="Complete patient information",
                columns=[
                    ColumnDefinition(
                        name="Full Name",
                        column_type=ColumnType.TEXT,
                        description="Legal name",
                        examples=["John Doe"],
                        constraints=Constraint(
                            min_length=2, max_length=100
                        ),
                    ),
                    ColumnDefinition(
                        name="Age",
                        column_type=ColumnType.INTEGER,
                        description="Age in years",
                        units="years",
                        examples=["25", "60"],
                        constraints=Constraint(min_value=0, max_value=120),
                    ),
                    ColumnDefinition(
                        name="Is Active",
                        column_type=ColumnType.BOOLEAN,
                        description="Whether record is active",
                    ),
                    ColumnDefinition(
                        name="Birth Date",
                        column_type=ColumnType.DATE,
                        description="Date of birth",
                        examples=["1990-01-15"],
                        constraints=Constraint(
                            temporal_type="date",
                            min_date="1900-01-01",
                            max_date="2025-12-31",
                        ),
                    ),
                ],
            ),
        )
        template = builder.build(analysis)
        result = validator.validate(template)
        assert result.valid is True, (
            f"Round-trip validation failed with errors: "
            f"{[e.message for e in result.errors]}"
        )
