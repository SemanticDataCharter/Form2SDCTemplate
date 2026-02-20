"""Shared test fixtures for form2sdc tests."""

import pytest


@pytest.fixture
def valid_front_matter():
    """Minimal valid YAML front matter block."""
    return 'template_version: "1.0.0"\ndataset:\n  name: "Test"\nsource_language: "English"'


@pytest.fixture
def valid_minimal_template():
    """Minimal valid template with Data section and one component."""
    return """---
template_version: "1.0.0"
dataset:
  name: "Minimal"
source_language: "English"
---

## Data: Root

**Type**: Cluster
**Description**: Root cluster

### Name

**Type**: XdString
**Description**: Person's name
"""


@pytest.fixture
def valid_complete_template():
    """Complete template with all types from spec Test 2."""
    return """---
template_version: "1.0.0"
dataset:
  name: "Complete Example"
  description: "Comprehensive test template"
  creator: "Test Suite"
source_language: "English"
---

## Data: Patient Record

**Type**: Cluster
**Description**: Complete patient information
**Cardinality**: 1..1

### Patient Name

**Type**: XdString
**Description**: Full legal name
**Pattern**: ^[A-Za-z\\s'-]+$
**Min Length**: 2
**Max Length**: 100
**Examples**: John Doe, Mary O'Brien

### Age

**Type**: XdCount
**Description**: Age in years
**Units**: years
**Min Magnitude**: 0
**Max Magnitude**: 120

### Weight

**Type**: XdQuantity
**Description**: Body weight
**Units**: kg, lb
**Min Magnitude**: 0.0
**Max Magnitude**: 500.0
**Precision**: 5
**Fraction Digits**: 1

### Temperature

**Type**: XdFloat
**Description**: Body temperature
**Units**: °C, °F
**Min Magnitude**: 35.0
**Max Magnitude**: 42.0

### Birth Date

**Type**: XdTemporal
**Description**: Date of birth
**Temporal Type**: date
**Min Date**: 1900-01-01
**Max Date**: 2025-12-31

### Consent Given

**Type**: XdBoolean
**Description**: Patient consent for treatment
**Default Value**: false

### Pain Level

**Type**: XdOrdinal
**Description**: Self-reported pain intensity
**Enumeration**:
1. None
2. Mild
3. Moderate
4. Severe

### Medical Report

**Type**: XdFile
**Description**: Diagnostic report file
**Media Types**: application/pdf, image/jpeg
**Max Size**: 10MB
"""
