"""Tests for form2sdc.validator implementing all 12 spec test cases plus additional coverage.

Test cases 1-12 are from VALIDATOR_SPECIFICATION.md section 7.
Additional tests cover rules not in the spec's test suite.
"""

import pytest

from form2sdc.validator import Form2SDCValidator


@pytest.fixture
def validator():
    return Form2SDCValidator()


# ════════════════════════════════════════════════════════════════════
# Spec Test Cases (section 7)
# ════════════════════════════════════════════════════════════════════


class TestSpecValidTemplates:
    """Tests 1-2: Valid templates should produce valid=True."""

    def test_01_minimal_valid_template(self, validator, valid_minimal_template):
        """Test 1: Minimal valid template."""
        result = validator.validate(valid_minimal_template)
        assert result.valid is True
        assert result.errors == []

    def test_02_complete_template_all_types(self, validator, valid_complete_template):
        """Test 2: Complete template with all types."""
        result = validator.validate(valid_complete_template)
        assert result.valid is True
        assert result.errors == []


class TestSpecCriticalErrors:
    """Tests 3-9: CRITICAL error detection."""

    def test_03_missing_yaml_front_matter(self, validator):
        """Test 3: Missing YAML front matter."""
        content = """## Root

**Type**: Cluster
"""
        result = validator.validate(content)
        assert result.valid is False
        assert any(e.code == "E-DOC-001" for e in result.errors)

    def test_04_missing_required_fields(self, validator):
        """Test 4: Missing source_language and template_version."""
        content = """---
project_name: "Test"
---

## Root

**Type**: Cluster
"""
        result = validator.validate(content)
        assert result.valid is False
        codes = {e.code for e in result.errors}
        assert "E-DOC-004" in codes  # missing source_language
        assert "E-DOC-005" in codes  # missing template_version

    def test_05_invalid_component_type(self, validator):
        """Test 5: Invalid component Type value."""
        content = """---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### Name

**Type**: String
"""
        result = validator.validate(content)
        assert result.valid is False
        assert any(
            e.code == "E-CMP-002" and e.component == "Name"
            for e in result.errors
        )

    def test_06_missing_units_for_quantified(self, validator):
        """Test 6: Missing Units for XdQuantity."""
        content = """---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### Weight

**Type**: XdQuantity
**Description**: Body weight
"""
        result = validator.validate(content)
        assert result.valid is False
        assert any(
            e.code == "E-REQ-001" and e.component == "Weight"
            for e in result.errors
        )

    def test_07_xdstring_pattern_and_enumeration(self, validator):
        """Test 7: XdString with both Pattern and Enumeration."""
        content = """---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### Color

**Type**: XdString
**Pattern**: ^[A-Z]+$
**Enumeration**: Red, Green, Blue
"""
        result = validator.validate(content)
        assert result.valid is False
        assert any(
            e.code == "E-BIZ-003" and e.component == "Color"
            for e in result.errors
        )

    def test_08_xdboolean_with_enumeration(self, validator):
        """Test 8: XdBoolean with Enumeration."""
        content = """---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### Active

**Type**: XdBoolean
**Enumeration**: Yes, No
"""
        result = validator.validate(content)
        assert result.valid is False
        assert any(
            e.code == "E-BIZ-001" and e.component == "Active"
            for e in result.errors
        )

    def test_09_first_component_not_cluster(self, validator):
        """Test 9: First component is not Cluster."""
        content = """---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

### Name

**Type**: XdString
"""
        result = validator.validate(content)
        assert result.valid is False
        assert any(e.code == "E-DOC-007" for e in result.errors)


class TestSpecEdgeCases:
    """Tests 10-12: Edge cases."""

    def test_10_deprecated_values_keyword(self, validator):
        """Test 10: Deprecated 'Values' keyword produces warning."""
        content = """---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### Status

**Type**: XdString
**Values**: Active, Inactive
"""
        result = validator.validate(content)
        assert result.valid is True  # Warnings don't block
        assert any(w.code == "W-DEP-001" for w in result.warnings)

    def test_11_component_reuse(self, validator):
        """Test 11: Valid component reuse syntax."""
        content = """---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### Address

**Type**: @Common:PostalAddress
"""
        result = validator.validate(content)
        assert result.valid is True
        assert result.errors == []

    def test_12_empty_units_value(self, validator):
        """Test 12: Empty Units value."""
        content = """---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### Weight

**Type**: XdQuantity
**Units**:
"""
        result = validator.validate(content)
        assert result.valid is False
        assert any(e.code == "E-REQ-002" for e in result.errors)


# ════════════════════════════════════════════════════════════════════
# Additional coverage for rules not in spec test suite
# ════════════════════════════════════════════════════════════════════


class TestDocumentStructure:
    """Additional E-DOC tests."""

    def test_invalid_yaml_syntax(self, validator):
        """E-DOC-002: Invalid YAML."""
        content = """---
project_name: "Test
source_language: "English"
---

## Root

**Type**: Cluster
"""
        result = validator.validate(content)
        assert result.valid is False
        assert any(e.code == "E-DOC-002" for e in result.errors)

    def test_empty_body(self, validator):
        """E-DOC-006: Empty body after front matter."""
        content = """---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

"""
        result = validator.validate(content)
        assert result.valid is False
        assert any(e.code == "E-DOC-006" for e in result.errors)

    def test_missing_project_name(self, validator):
        """E-DOC-003: Missing project_name."""
        content = """---
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster
"""
        result = validator.validate(content)
        assert result.valid is False
        assert any(e.code == "E-DOC-003" for e in result.errors)


class TestComponentStructure:
    """E-CMP-003, E-CMP-004, E-CMP-005 tests."""

    def test_type_not_first_keyword(self, validator):
        """E-CMP-003: Type must be first keyword."""
        content = """---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### Patient Name

**Description**: Full name of the patient
**Type**: XdString
"""
        result = validator.validate(content)
        assert result.valid is False
        assert any(
            e.code == "E-CMP-003" and e.component == "Patient Name"
            for e in result.errors
        )

    def test_duplicate_component_names(self, validator):
        """E-CMP-005: Duplicate component names."""
        content = """---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### Name

**Type**: XdString
**Description**: First name

### Name

**Type**: XdString
**Description**: Last name
"""
        result = validator.validate(content)
        assert any(e.code == "E-CMP-005" for e in result.errors)

    def test_missing_type_keyword(self, validator):
        """E-CMP-001: Missing Type keyword with name-based suggestion."""
        content = """---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### Patient Name

**Description**: Person's full name
"""
        result = validator.validate(content)
        assert result.valid is False
        assert any(e.code == "E-CMP-001" for e in result.errors)


class TestBusinessLogic:
    """E-BIZ-002 through E-BIZ-007 tests."""

    def test_xdboolean_with_pattern(self, validator):
        """E-BIZ-002: XdBoolean cannot have Pattern."""
        content = """---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### Active

**Type**: XdBoolean
**Pattern**: ^(true|false)$
"""
        result = validator.validate(content)
        assert result.valid is False
        assert any(e.code == "E-BIZ-002" for e in result.errors)

    def test_min_length_exceeds_max_length(self, validator):
        """E-BIZ-004: Min Length > Max Length."""
        content = """---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### Code

**Type**: XdString
**Min Length**: 10
**Max Length**: 5
"""
        result = validator.validate(content)
        assert result.valid is False
        assert any(e.code == "E-BIZ-004" for e in result.errors)

    def test_min_magnitude_exceeds_max(self, validator):
        """E-BIZ-005: Min Magnitude > Max Magnitude."""
        content = """---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### Score

**Type**: XdCount
**Units**: points
**Min Magnitude**: 100
**Max Magnitude**: 50
"""
        result = validator.validate(content)
        assert result.valid is False
        assert any(e.code == "E-BIZ-005" for e in result.errors)

    def test_min_date_exceeds_max_date(self, validator):
        """E-BIZ-006: Min Date > Max Date."""
        content = """---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### Event Date

**Type**: XdTemporal
**Temporal Type**: date
**Min Date**: 2025-01-01
**Max Date**: 2020-01-01
"""
        result = validator.validate(content)
        assert result.valid is False
        assert any(e.code == "E-BIZ-006" for e in result.errors)

    def test_invalid_regex_pattern(self, validator):
        """E-BIZ-007: Invalid regex pattern."""
        content = """---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### Code

**Type**: XdString
**Pattern**: ^[A-Z
"""
        result = validator.validate(content)
        assert result.valid is False
        assert any(e.code == "E-BIZ-007" for e in result.errors)


class TestSyntaxErrors:
    """E-SYN-002, E-SYN-003 tests."""

    def test_invalid_numeric_value(self, validator):
        """E-SYN-002: Non-numeric value for numeric keyword."""
        content = """---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### Weight

**Type**: XdQuantity
**Units**: kg
**Min Magnitude**: abc
"""
        result = validator.validate(content)
        assert result.valid is False
        assert any(e.code == "E-SYN-002" for e in result.errors)

    def test_invalid_component_reference(self, validator):
        """E-SYN-003: Invalid @Project:Label format."""
        content = """---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### Address

**Type**: @Invalid Format
"""
        result = validator.validate(content)
        assert result.valid is False
        assert any(e.code == "E-SYN-003" for e in result.errors)


class TestRequiredFields:
    """E-REQ tests."""

    def test_xdcount_requires_units(self, validator):
        """E-REQ-001: XdCount requires Units."""
        content = """---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### Count

**Type**: XdCount
**Description**: A count
"""
        result = validator.validate(content)
        assert result.valid is False
        assert any(
            e.code == "E-REQ-001" and e.component == "Count"
            for e in result.errors
        )

    def test_xdfloat_requires_units(self, validator):
        """E-REQ-001: XdFloat requires Units."""
        content = """---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### Temp

**Type**: XdFloat
**Description**: Temperature
"""
        result = validator.validate(content)
        assert result.valid is False
        assert any(e.code == "E-REQ-001" for e in result.errors)

    def test_xddouble_requires_units(self, validator):
        """E-REQ-001: XdDouble requires Units."""
        content = """---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### Coordinate

**Type**: XdDouble
**Description**: GPS coordinate
"""
        result = validator.validate(content)
        assert result.valid is False
        assert any(e.code == "E-REQ-001" for e in result.errors)

    def test_xdordinal_requires_enumeration(self, validator):
        """E-REQ-003: XdOrdinal requires Enumeration."""
        content = """---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### Severity

**Type**: XdOrdinal
**Description**: Severity level
"""
        result = validator.validate(content)
        assert result.valid is False
        assert any(e.code == "E-REQ-003" for e in result.errors)


class TestWarnings:
    """Warning rule tests."""

    def test_missing_description_warning(self, validator):
        """W-BP-001: Missing Description."""
        content = """---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### SSN

**Type**: XdString
"""
        result = validator.validate(content)
        assert any(w.code == "W-BP-001" for w in result.warnings)

    def test_short_component_name(self, validator):
        """W-BP-002: Short component name."""
        content = """---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### ID

**Type**: XdString
**Description**: An identifier
"""
        result = validator.validate(content)
        assert any(w.code == "W-BP-002" for w in result.warnings)

    def test_deprecated_unit_keyword(self, validator):
        """W-DEP-002: Deprecated 'Unit' keyword."""
        content = """---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### Weight

**Type**: XdQuantity
**Unit**: kg
"""
        result = validator.validate(content)
        assert result.valid is True
        assert any(w.code == "W-DEP-002" for w in result.warnings)

    def test_temporal_without_temporal_type(self, validator):
        """W-BP-006: XdTemporal without Temporal Type."""
        content = """---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster

### Event Date

**Type**: XdTemporal
**Description**: When the event occurred
"""
        result = validator.validate(content)
        assert any(w.code == "W-BP-006" for w in result.warnings)


class TestFrontMatterCompatibility:
    """Test both YAML front matter formats."""

    def test_form2sdc_template_format(self, validator):
        """Accept Form2SDCTemplate.md format with dataset.name."""
        content = """---
template_version: "4.0.0"
dataset:
  name: "Test Dataset"
  description: "A test"
source_language: "English"
---

## Root

**Type**: Cluster
**Description**: Root cluster
"""
        result = validator.validate(content)
        assert result.valid is True

    def test_validator_spec_format(self, validator):
        """Accept validator spec format with project_name."""
        content = """---
project_name: "Test"
source_language: "English"
template_version: "1.0.0"
---

## Root

**Type**: Cluster
**Description**: Root cluster
"""
        result = validator.validate(content)
        assert result.valid is True


class TestMetadata:
    """Test validation result metadata."""

    def test_metadata_fields(self, validator, valid_minimal_template):
        """Metadata should contain required fields."""
        result = validator.validate(valid_minimal_template, document="test.md")
        assert result.metadata["validator"] == "form2sdc-validator-python"
        assert result.metadata["version"] == "1.0.0"
        assert result.metadata["document"] == "test.md"
        assert "validation_time" in result.metadata
        assert result.metadata["total_components"] >= 2
        assert result.metadata["critical_count"] == 0

    def test_error_counts(self, validator):
        """Metadata counts should match actual lists."""
        content = """---
project_name: "Test"
---

### Name

**Type**: String
"""
        result = validator.validate(content)
        assert result.metadata["critical_count"] == len(result.errors)
        assert result.metadata["warning_count"] == len(result.warnings)
        assert result.metadata["suggestion_count"] == len(result.suggestions)
