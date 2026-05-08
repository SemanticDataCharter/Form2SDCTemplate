"""Tests for ``form2sdc.validator`` (md2pd-aligned, 4.2.0+).

Each test exercises one validation rule. Rule codes are stable contracts
documented in ``VALIDATOR_SPECIFICATION.md``.
"""

from __future__ import annotations

from form2sdc.validator import Form2SDCValidator


def _validate(content: str):
    return Form2SDCValidator().validate(content)


def _has_error(result, code: str) -> bool:
    return any(e.code == code for e in result.errors)


def _has_warning(result, code: str) -> bool:
    return any(w.code == code for w in result.warnings)


def _has_suggestion(result, code: str) -> bool:
    return any(s.code == code for s in result.suggestions)


# ── Front matter (E-DOC-*) ──────────────────────────────────────────


def test_missing_front_matter_emits_e_doc_001() -> None:
    result = _validate("# Just markdown, no YAML\n")
    assert not result.valid
    assert _has_error(result, "E-DOC-001")


def test_invalid_yaml_emits_e_doc_002() -> None:
    content = """---
template_version: "4.0.0
dataset:
  name: "Test"
---

## Data: X
"""
    result = _validate(content)
    assert not result.valid
    assert _has_error(result, "E-DOC-002")


def test_missing_template_version_emits_e_doc_003() -> None:
    content = """---
dataset:
  name: "Test"
---

## Data: X

### foo
**Type**: text
**Description**: A field
**Examples**: a
"""
    result = _validate(content)
    assert not result.valid
    assert _has_error(result, "E-DOC-003")


def test_template_version_3_emits_e_doc_003() -> None:
    content = """---
template_version: "3.0.0"
dataset:
  name: "Test"
---

## Data: X

### foo
**Type**: text
**Description**: A field
**Examples**: a
"""
    result = _validate(content)
    assert not result.valid
    assert _has_error(result, "E-DOC-003")


def test_template_version_4_2_1_is_accepted() -> None:
    content = """---
template_version: "4.2.1"
dataset:
  name: "Test"
---

## Data: X

### foo
**Type**: text
**Description**: A field
**Examples**: a
"""
    result = _validate(content)
    assert not _has_error(result, "E-DOC-003")


# ── Section structure (E-SEC-*) ─────────────────────────────────────


def test_unknown_section_heading_emits_e_sec_001() -> None:
    content = """---
template_version: "4.0.0"
dataset:
  name: "Test"
---

## Cluster: Patient

### foo
**Type**: text
**Description**: A field
**Examples**: a
"""
    result = _validate(content)
    assert _has_error(result, "E-SEC-001")


def test_root_cluster_heading_emits_e_sec_001() -> None:
    content = """---
template_version: "4.0.0"
dataset:
  name: "Test"
---

## Root Cluster: Patient

### foo
**Type**: text
**Description**: A field
**Examples**: a
"""
    result = _validate(content)
    assert _has_error(result, "E-SEC-001")


def test_missing_data_section_emits_e_sec_002() -> None:
    content = """---
template_version: "4.0.0"
dataset:
  name: "Test"
---

## Subject: Patient
**Description**: The patient
"""
    result = _validate(content)
    assert _has_error(result, "E-SEC-002")


def test_multiple_data_sections_emit_e_sec_003() -> None:
    content = """---
template_version: "4.0.0"
dataset:
  name: "Test"
---

## Data: First

### a
**Type**: text
**Description**: A
**Examples**: x

## Data: Second

### b
**Type**: text
**Description**: B
**Examples**: y
"""
    result = _validate(content)
    assert _has_error(result, "E-SEC-003")


def test_multiple_subject_sections_emit_e_sec_004() -> None:
    content = """---
template_version: "4.0.0"
dataset:
  name: "Test"
---

## Subject: First
**Description**: First subject

## Subject: Second
**Description**: Second subject

## Data: Root

### a
**Type**: text
**Description**: A
**Examples**: x
"""
    result = _validate(content)
    assert _has_error(result, "E-SEC-004")


# ── Column heading (E-COL-001, E-COL-002) ───────────────────────────


def test_column_with_column_prefix_emits_e_col_001() -> None:
    content = """---
template_version: "4.0.0"
dataset:
  name: "Test"
---

## Data: Root

### Column: foo
**Type**: text
**Description**: A field
**Examples**: a
"""
    result = _validate(content)
    assert _has_error(result, "E-COL-001")


# ── Column keywords (E-COL-003, E-COL-004) ──────────────────────────


def test_deprecated_keyword_values_emits_e_col_003() -> None:
    content = """---
template_version: "4.0.0"
dataset:
  name: "Test"
---

## Data: Root

### foo
**Type**: text
**Description**: A field
**Values**:
  - a: A value
  - b: B value
**Examples**: a
"""
    result = _validate(content)
    assert _has_error(result, "E-COL-003")


def test_legacy_min_length_keyword_emits_e_col_004() -> None:
    content = """---
template_version: "4.0.0"
dataset:
  name: "Test"
---

## Data: Root

### foo
**Type**: text
**Description**: A field
**Min Length**: 2
**Max Length**: 100
**Examples**: abc
"""
    result = _validate(content)
    assert _has_error(result, "E-COL-004")


def test_legacy_pattern_keyword_emits_e_col_004() -> None:
    content = """---
template_version: "4.0.0"
dataset:
  name: "Test"
---

## Data: Root

### foo
**Type**: text
**Description**: A field
**Pattern**: ^[A-Z]+$
**Examples**: ABC
"""
    result = _validate(content)
    assert _has_error(result, "E-COL-004")


# ── Type validation (E-COL-005, E-COL-006) ──────────────────────────


def test_invalid_type_emits_e_col_005() -> None:
    content = """---
template_version: "4.0.0"
dataset:
  name: "Test"
---

## Data: Root

### foo
**Type**: XdRatio
**Description**: A field
**Examples**: a
"""
    result = _validate(content)
    assert _has_error(result, "E-COL-005")


def test_xdboolean_with_enumeration_emits_e_col_006() -> None:
    content = """---
template_version: "4.0.0"
dataset:
  name: "Test"
---

## Data: Root

### consent
**Type**: xdboolean
**Description**: Consent given
**Enumeration**:
  - yes: Yes
  - no: No
"""
    result = _validate(content)
    assert _has_error(result, "E-COL-006")


# ── Constraints (E-COL-007, E-COL-008, E-COL-009, E-COL-011) ────────


def test_unknown_constraint_subkey_emits_e_col_007() -> None:
    content = """---
template_version: "4.0.0"
dataset:
  name: "Test"
---

## Data: Root

### foo
**Type**: text
**Description**: A field
**Constraints**:
  - format: "UUID v4"
**Examples**: a
"""
    result = _validate(content)
    assert _has_error(result, "E-COL-007")


def test_unique_constraint_subkey_emits_e_col_007() -> None:
    content = """---
template_version: "4.0.0"
dataset:
  name: "Test"
---

## Data: Root

### foo
**Type**: text
**Description**: A field
**Constraints**:
  - unique: true
**Examples**: a
"""
    result = _validate(content)
    assert _has_error(result, "E-COL-007")


def test_non_integer_precision_emits_e_col_008() -> None:
    content = """---
template_version: "4.0.0"
dataset:
  name: "Test"
---

## Data: Root

### foo
**Type**: decimal
**Description**: A field
**Units**: USD
**Constraints**:
  - precision: two
**Examples**: 1.0
"""
    result = _validate(content)
    assert _has_error(result, "E-COL-008")


def test_non_boolean_required_emits_e_col_009() -> None:
    content = """---
template_version: "4.0.0"
dataset:
  name: "Test"
---

## Data: Root

### foo
**Type**: text
**Description**: A field
**Constraints**:
  - required: yes
**Examples**: a
"""
    result = _validate(content)
    assert _has_error(result, "E-COL-009")


def test_range_must_be_two_element_list_emits_e_col_011() -> None:
    content = """---
template_version: "4.0.0"
dataset:
  name: "Test"
---

## Data: Root

### foo
**Type**: integer
**Description**: A field
**Units**: years
**Constraints**:
  - range: [0, 50, 100]
**Examples**: 25
"""
    result = _validate(content)
    assert _has_error(result, "E-COL-011")


def test_range_string_value_emits_e_col_011() -> None:
    content = """---
template_version: "4.0.0"
dataset:
  name: "Test"
---

## Data: Root

### foo
**Type**: integer
**Description**: A field
**Units**: years
**Constraints**:
  - range: 0 to 100
**Examples**: 25
"""
    result = _validate(content)
    assert _has_error(result, "E-COL-011")


def test_valid_range_with_null_does_not_emit_error() -> None:
    content = """---
template_version: "4.0.0"
dataset:
  name: "Test"
---

## Data: Root

### foo
**Type**: integer
**Description**: A field
**Units**: years
**Constraints**:
  - range: [0, null]
**Examples**: 25
"""
    result = _validate(content)
    assert not _has_error(result, "E-COL-011")


# ── ReuseComponent (E-COL-010) ──────────────────────────────────────


def test_reuse_component_without_at_emits_e_col_010() -> None:
    content = """---
template_version: "4.0.0"
dataset:
  name: "Test"
---

## Data: Root

### state
**Type**: text
**ReuseComponent**: NIEM:StateCode
**Description**: State code
**Examples**: CA
"""
    result = _validate(content)
    assert _has_error(result, "E-COL-010")


def test_reuse_component_without_colon_emits_e_col_010() -> None:
    content = """---
template_version: "4.0.0"
dataset:
  name: "Test"
---

## Data: Root

### state
**Type**: text
**ReuseComponent**: @NIEMStateCode
**Description**: State code
**Examples**: CA
"""
    result = _validate(content)
    assert _has_error(result, "E-COL-010")


def test_valid_reuse_component_does_not_emit_error() -> None:
    content = """---
template_version: "4.0.0"
dataset:
  name: "Test"
---

## Data: Root

### state
**Type**: text
**ReuseComponent**: @NIEM:StateUSPostalServiceCode
**Description**: US state postal abbreviation
**Examples**: CA, NY, TX
"""
    result = _validate(content)
    assert not _has_error(result, "E-COL-010")


# ── YAML hygiene warnings ───────────────────────────────────────────


def test_unknown_yaml_top_level_key_emits_w_yaml_001() -> None:
    content = """---
template_version: "4.0.0"
dataset:
  name: "Test"
source_language: "English"
---

## Data: Root

### foo
**Type**: text
**Description**: A field
**Examples**: a
"""
    result = _validate(content)
    assert _has_warning(result, "W-YAML-001")


def test_unknown_dataset_subkey_emits_w_yaml_002() -> None:
    content = """---
template_version: "4.0.0"
dataset:
  name: "Test"
  domain: "Healthcare"
---

## Data: Root

### foo
**Type**: text
**Description**: A field
**Examples**: a
"""
    result = _validate(content)
    assert _has_warning(result, "W-YAML-002")


# ── Section-level keyword warnings ──────────────────────────────────


def test_unknown_section_keyword_emits_w_sec_001() -> None:
    content = """---
template_version: "4.0.0"
dataset:
  name: "Test"
---

## Data: Root

**SomeUnknownSectionKeyword**: ignored

### foo
**Type**: text
**Description**: A field
**Examples**: a
"""
    result = _validate(content)
    assert _has_warning(result, "W-SEC-001")


# ── Suggestions ─────────────────────────────────────────────────────


def test_missing_dataset_description_emits_s_ql_003() -> None:
    content = """---
template_version: "4.0.0"
dataset:
  name: "Test"
---

## Data: Root

### foo
**Type**: text
**Description**: A field
**Examples**: a
"""
    result = _validate(content)
    assert _has_suggestion(result, "S-QL-003")


def test_missing_column_description_emits_s_col_002() -> None:
    content = """---
template_version: "4.0.0"
dataset:
  name: "Test"
---

## Data: Root

### foo
**Type**: text
**Examples**: a
"""
    result = _validate(content)
    assert _has_suggestion(result, "S-COL-002")


# ── Happy path: valid template passes ───────────────────────────────


def test_minimal_valid_template_passes(valid_minimal_template: str) -> None:
    result = _validate(valid_minimal_template)
    assert result.valid, (
        "Minimal valid template should pass:\n"
        + "\n".join(f"  [{e.code}] {e.message}" for e in result.errors)
    )


def test_complete_valid_template_passes(valid_complete_template: str) -> None:
    result = _validate(valid_complete_template)
    assert result.valid, (
        "Complete valid template should pass:\n"
        + "\n".join(f"  [{e.code}] {e.message}" for e in result.errors)
    )
