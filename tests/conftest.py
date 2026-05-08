"""Shared test fixtures for form2sdc tests.

Fixtures match the post-4.5.0 md2pd-aligned model:
- template_version is 4.x
- single ## Data: section per template
- ### name (no `Column:` prefix)
- bullet-list **Constraints** with only required/range/precision sub-keys
- no flat-keyword constraints (Pattern, Min Length, Min Magnitude, etc.)
"""

import pytest


@pytest.fixture
def valid_minimal_template() -> str:
    """Smallest template that md2pd will parse: front matter + Data section + one column."""
    return """---
template_version: "4.0.0"
dataset:
  name: "Minimal"
---

## Data: Root

Minimal template with a single column.

### name
**Type**: text
**Description**: Person's name
**Examples**: Jane, John
"""


@pytest.fixture
def valid_complete_template() -> str:
    """Comprehensive template covering type system, constraints, enum, and reuse."""
    return """---
template_version: "4.0.0"
dataset:
  name: "Complete Example"
  description: "Comprehensive md2pd-compliant test template"
  creator: "Test Suite"
enrichment:
  enable_llm: true
---

# Dataset Overview

Comprehensive patient record template exercising the full md2pd surface area.

**Purpose**: Validate type inference, constraints, enumeration, and component reuse.
**Business Context**: Used in the Form2SDC validator regression suite.

## Data: Patient Record

Complete patient information collected at registration.

**Purpose**: Single source of truth for patient identity and vitals.
**Business Context**: Required for billing and clinical workflows.

### patient_name
**Type**: text
**Description**: Full legal name.
**Constraints**:
  - required: true
**Examples**: John Doe, Mary O'Brien

### age
**Type**: integer
**Description**: Age in completed years.
**Units**: years
**Constraints**:
  - required: true
  - range: [0, 120]
**Examples**: 25, 42, 67

### weight
**Type**: decimal
**Description**: Body weight.
**Units**: kg
**Constraints**:
  - precision: 1
  - range: [0, 500]
**Examples**: 65.5, 72.0

### birth_date
**Type**: date
**Description**: Date of birth.
**Constraints**:
  - required: true
**Examples**: 1985-03-15, 1970-12-01

### consent_given
**Type**: boolean
**Description**: Patient consent for treatment.
**Examples**: true, false

### pain_level
**Type**: xdordinal
**Description**: Self-reported pain intensity.
**Enumeration**:
  - 0: None
  - 1: Mild
  - 2: Moderate
  - 3: Severe

### account_status
**Type**: text
**Description**: Patient account status.
**Enumeration**:
  - active: Account in good standing
  - suspended: Temporarily suspended
  - closed: Permanently closed

### state
**Type**: text
**ReuseComponent**: @NIEM:StateUSPostalServiceCode
**Description**: US state postal abbreviation
**Examples**: CA, NY, TX
"""
