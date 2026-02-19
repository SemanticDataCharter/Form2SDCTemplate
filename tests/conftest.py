"""Shared test fixtures for form2sdc tests."""

import pytest


@pytest.fixture
def valid_front_matter():
    """Minimal valid YAML front matter block."""
    return 'project_name: "Test"\nsource_language: "English"\ntemplate_version: "1.0.0"'


@pytest.fixture
def valid_minimal_template():
    """Minimal valid template with root cluster and one component."""
    return """---
project_name: "Minimal"
source_language: "English"
template_version: "1.0.0"
---

## Root

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
project_name: "Complete Example"
source_language: "English"
template_version: "1.0.0"
description: "Comprehensive test template"
author: "Test Suite"
---

## Patient Record

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
