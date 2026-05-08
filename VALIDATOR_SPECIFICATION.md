# Form2SDC Validator Specification

**Version:** 4.5.0 — md2pd-aligned rewrite
**Implements:** `form2sdc.validator.Form2SDCValidator`
**Source of truth:** the production md2pd parser at `SDCStudio/src/md2pd/agents/template_parser_agent.py`

## Purpose

The validator's contract: **a template that passes this validator will parse cleanly through the SDCStudio md2pd parser without rejection or silent data loss.**

This spec replaces the pre-4.5 validator specification, which validated against a flat-keyword constraint model that md2pd never supported (the old `**Min Length**:`, `**Pattern**:`, `**Min Magnitude**:`, etc. were silently ignored on upload). The 4.5 validator validates against md2pd's actual model.

## Severity levels

- **CRITICAL** (`E-` codes) — the template will fail or silently lose data on upload. `valid` is `False`.
- **WARNING** (`W-` codes) — allowed but inadvisable, or a deprecated form was auto-corrected.
- **SUGGESTION** (`S-` codes) — non-blocking style improvement.

## Validation phases

1. Extract YAML front matter (`---` delimited).
2. Parse YAML.
3. Validate front matter keys.
4. Parse body into sections + columns.
5. Validate section structure (required sections, multiplicity, valid section types).
6. Validate each section's keywords.
7. Validate each column's keywords, type, constraints, and reuse syntax.

## Rule codes

### Document-level (`E-DOC-*`)

| Code | Severity | Trigger | Fix |
|---|---|---|---|
| `E-DOC-001` | CRITICAL | Missing YAML front matter | Add `---`-delimited front matter at the top of the document |
| `E-DOC-002` | CRITICAL | YAML syntax error or non-mapping front matter | Fix YAML (quotes, indentation, colons) |
| `E-DOC-003` | CRITICAL | Missing or non-`4.x` `template_version` | Use `template_version: "4.0.0"` (or any 4.x.x value) |
| `E-DOC-006` | CRITICAL | No content after front matter | Add at least one `## Data: <Name>` section with columns |

### Section-level (`E-SEC-*`)

| Code | Severity | Trigger | Fix |
|---|---|---|---|
| `E-SEC-001` | CRITICAL | H2 heading is not one of the eight named-tree section types | Use `## Data:`, `## Subject:`, `## Provider:`, `## Participation:`, `## Workflow:`, `## Attestation:`, `## Audit:`, or `## Links:` |
| `E-SEC-002` | CRITICAL | No `## Data:` section in template | Add one `## Data: <Name>` section containing the form payload |
| `E-SEC-003` | CRITICAL | More than one `## Data:` section (md2pd discards all but the last) | Consolidate into a single `## Data:` section |
| `E-SEC-004` | CRITICAL | Multiple instances of a single-instance section (`Subject`, `Provider`, `Attestation`, `Links`) | Keep at most one of each |

### Column-level (`E-COL-*`)

| Code | Severity | Trigger | Fix |
|---|---|---|---|
| `E-COL-001` | CRITICAL | Column heading uses `### Column: name` form | Drop the `Column:` prefix; use `### name` |
| `E-COL-002` | CRITICAL | Column heading is empty | Provide a name after `### ` |
| `E-COL-003` | CRITICAL | Deprecated keyword (e.g. `**Values**:`, `**Unit**:`, `**Example**:`) — auto-correctable | Rename to the parser-recognized form (`**Enumeration**:`, `**Units**:`, `**Examples**:`) |
| `E-COL-004` | CRITICAL | Column keyword is not in md2pd's allowlist (e.g. legacy flat-constraint keywords like `**Min Length**:`, `**Pattern**:`, `**Min Magnitude**:`) | Use a recognized keyword or fold the value into `**Description**:` / `**Business Rules**:` |
| `E-COL-005` | CRITICAL | `**Type**:` value is not a recognized SDC4 type or user-friendly type | Use one of the explicit SDC4 types or user-friendly types listed in PART 6 of `Form2SDCTemplate.md` |
| `E-COL-006` | CRITICAL | `**Type**: xdboolean` combined with `**Enumeration**:` (md2pd error) | Drop the Enumeration, or change Type to a categorical type |
| `E-COL-007` | CRITICAL | `**Constraints**:` sub-key is not one of `required` / `range` / `precision` (md2pd silently drops the rest) | Remove the unsupported sub-key; express the intent in `**Description**:` or `**Business Rules**:` |
| `E-COL-008` | CRITICAL | `precision:` value is not an integer | Use a non-negative integer |
| `E-COL-009` | CRITICAL | `required:` value is not `true` / `false` | Use `required: true` or `required: false` |
| `E-COL-010` | CRITICAL | `**ReuseComponent**:` does not match `@Project:Label` syntax | Use `@ProjectName:ComponentLabel` with both parts non-empty |
| `E-COL-011` | CRITICAL | `range:` value is not a two-element list | Use `range: [min, max]` (use `null` for an unbounded end) |

### YAML hygiene (`W-YAML-*`)

| Code | Severity | Trigger | Fix |
|---|---|---|---|
| `W-YAML-001` | WARNING | Unrecognized top-level YAML key (md2pd ignores it) | Remove the key or fold its value into `dataset.description` |
| `W-YAML-002` | WARNING | Unrecognized `dataset.*` key (md2pd ignores it) | Remove or fold into `dataset.description` |
| `W-YAML-003` | WARNING | Unrecognized `enrichment.*` key (md2pd ignores it) | Remove |

### Section keywords (`W-SEC-*`)

| Code | Severity | Trigger | Fix |
|---|---|---|---|
| `W-SEC-001` | WARNING | Section-level keyword that md2pd does not extract for that section type | Remove or use a recognized keyword for the section |
| `W-SEC-002` | WARNING | `**Rules**:` outside a column-bearing section | Move into Data, Workflow, Subject, Provider, or Participation |
| `W-SEC-003` | WARNING | `### name` column inside a non-column-bearing section (Attestation, Audit, Links) | Move to a column-bearing section |

### Deprecated forms (`W-DEP-*`)

| Code | Severity | Trigger | Fix |
|---|---|---|---|
| `W-DEP-001` | WARNING | Section keyword uses a deprecated alias (e.g. `Values` instead of `Enumeration`) | Rename to the canonical form |

### Quality / style suggestions (`S-*`)

| Code | Severity | Trigger | Fix |
|---|---|---|---|
| `S-QL-001` | SUGGESTION | Front matter has no `dataset` block | Add `dataset:\n  name: "..."\n  description: "..."` |
| `S-QL-002` | SUGGESTION | `dataset.name` missing (md2pd defaults to filename) | Add `dataset.name: "..."` |
| `S-QL-003` | SUGGESTION | `dataset.description` missing | Add `dataset.description: "..."` |
| `S-COL-001` | SUGGESTION | Column has no `**Type**:` (md2pd defaults to `text`/XdString) | Add `**Type**:` as the first keyword |
| `S-COL-002` | SUGGESTION | Column has no `**Description**:` | Add a description |
| `S-COL-003` | SUGGESTION | Column has no `**Examples**:` (except for boolean columns) | Add 2-3 sample values |

## What the validator does NOT validate

- Numeric range bounds beyond list shape — md2pd doesn't enforce them either.
- Regex patterns, length limits, format strings, default values, file media types, max sizes, temporal types — md2pd doesn't accept these as validation; the validator rejects flat-keyword forms (E-COL-004) and unsupported constraint sub-keys (E-COL-007) so they cannot be silently lost.
- Cross-component name uniqueness — md2pd does not enforce this; columns with duplicate names will collide on upload, but neither md2pd nor this validator currently flags it.

## Round-trip guarantee

For any `FormAnalysis` instance:

1. `TemplateBuilder().build(analysis)` produces markdown that
2. `Form2SDCValidator().validate(markdown)` accepts (no errors)
3. and that md2pd parses without rejection or data loss.

The test suite in `tests/test_template_builder.py` enforces (1)+(2). End-to-end testing against md2pd itself happens in the SDCStudio repository.
