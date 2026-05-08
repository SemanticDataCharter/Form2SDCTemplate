"""md2pd-compliance validator for Form2SDCTemplate markdown documents.

Validates against the production SDCStudio md2pd parser
(``src/md2pd/agents/template_parser_agent.py``). The contract is:
*if a template passes this validator with no errors, md2pd will parse it
without rejecting it or silently dropping data.*

The validator is structurally aware of the eight named-tree sections
(``## Data:``, ``## Subject:``, ``## Provider:``, ``## Participation:``,
``## Workflow:``, ``## Attestation:``, ``## Audit:``, ``## Links:``) and
treats each ``### name`` inside a section as a column.

Severity:

- **CRITICAL** (E-codes): the template will fail or silently lose data on
  upload. ``valid`` is set to ``False``.
- **WARNING** (W-codes): something is allowed but inadvisable, or a
  deprecated form was auto-corrected.
- **SUGGESTION** (S-codes): non-blocking style improvement.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from typing import Optional

import yaml


# ── Result types ─────────────────────────────────────────────────────


@dataclass
class ValidationIssue:
    """A single validation finding."""

    code: str
    severity: str  # "CRITICAL", "WARNING", "SUGGESTION"
    message: str
    line: int
    column: Optional[int] = None
    context: str = ""
    fix: str = ""
    component: Optional[str] = None
    keyword: Optional[str] = None


@dataclass
class ValidationResult:
    """Complete validation output."""

    valid: bool
    errors: list[ValidationIssue]
    warnings: list[ValidationIssue]
    suggestions: list[ValidationIssue]
    metadata: dict


# ── Allowlists (mirror md2pd's parser exactly) ───────────────────────


# md2pd's eight named-tree section types
SECTION_TYPES = (
    "Data",
    "Subject",
    "Provider",
    "Participation",
    "Workflow",
    "Attestation",
    "Audit",
    "Links",
)

# Sections that may appear at most once
SINGLE_INSTANCE_SECTIONS = ("Data", "Subject", "Provider", "Attestation", "Links")
# Sections that may appear multiple times
MULTI_INSTANCE_SECTIONS = ("Participation", "Workflow", "Audit")
# Sections that contain ### columns
COLUMN_BEARING_SECTIONS = (
    "Data",
    "Subject",
    "Provider",
    "Participation",
    "Workflow",
)

# Explicit SDC4 types md2pd understands (lowercase user input)
EXPLICIT_SDC4_TYPES = {
    "xdstring",
    "xdtoken",
    "xdcount",
    "xdordinal",
    "xdquantity",
    "xdfloat",
    "xddouble",
    "xdboolean",
    "xdtemporal",
    "xdlink",
    "xdfile",
    "xdinterval",
}

# User-friendly types md2pd maps to SDC4 types
USER_FRIENDLY_TYPES = {
    "text",
    "string",
    "varchar",
    "char",
    "integer",
    "int",
    "whole number",
    "count",
    "decimal",
    "float",
    "number",
    "numeric",
    "double",
    "boolean",
    "bool",
    "flag",
    "date",
    "datetime",
    "timestamp",
    "time",
    "identifier",
    "id",
    "uuid",
    "guid",
    "email",
    "url",
    "uri",
    "link",
}

VALID_TYPE_VALUES = EXPLICIT_SDC4_TYPES | USER_FRIENDLY_TYPES

# Column-level keywords md2pd actively parses
PARSED_COLUMN_KEYWORDS = {
    "Type",
    "Description",
    "Units",
    "Constraints",
    "Enumeration",
    "Examples",
    "Relationships",
    "Business Rules",
    "Semantic Links",
    "Reuse",
    "ReuseComponent",
}

# Column-level keywords md2pd accepts as documentation (no field extraction)
DOCUMENTATION_COLUMN_KEYWORDS = {
    "Ontology Mappings",
    "Standard",
    "NIH CDE Source",
    "PHI Status",
    "Clinical Significance",
    "HL7 Security Classification",
    "Access Control Requirements",
    "De-identification Considerations",
    "Calculation Method",
    "Important Distinctions",
    "Important Notes",
}

VALID_COLUMN_KEYWORDS = PARSED_COLUMN_KEYWORDS | DOCUMENTATION_COLUMN_KEYWORDS

# Constraint sub-keys md2pd actively uses
RECOGNIZED_CONSTRAINT_KEYS = {"required", "range", "precision"}

# Common typos / deprecated keywords with auto-correction suggestions
KEYWORD_CORRECTIONS = {
    "Values": "Enumeration",
    "Value": "Enumeration",
    "Enumerations": "Enumeration",
    "Allowed Values": "Enumeration",
    "Options": "Enumeration",
    "Unit": "Units",
    "DataType": "Type",
    "Data Type": "Type",
    "Example": "Examples",
    "Constraint": "Constraints",
    "Business Rule": "Business Rules",
    "Relationship": "Relationships",
}

# Section-level keywords by section type
SECTION_KEYWORDS = {
    "Data": {"Purpose", "Business Context", "Rules"},
    "Workflow": {"Description", "Purpose", "Business Context", "Rules"},
    "Subject": {"Description"},
    "Provider": {"Description"},
    "Participation": {
        "Description",
        "Function",
        "Function Description",
        "Mode",
        "Mode Description",
    },
    "Attestation": {"View", "Proof", "Reason"},
    "Audit": {"System ID", "System User", "Location"},
    "Links": set(),
}

# md2pd-recognized YAML front matter keys
RECOGNIZED_YAML_KEYS = {"template_version", "dataset", "enrichment"}
RECOGNIZED_DATASET_KEYS = {"name", "description", "creator", "project"}
RECOGNIZED_ENRICHMENT_KEYS = {"enable_llm"}


# ── Internal parsing model ───────────────────────────────────────────


@dataclass
class _Column:
    name: str
    line: int
    keywords: dict[str, "_KeywordValue"] = field(default_factory=dict)
    keyword_order: list[str] = field(default_factory=list)
    constraint_subkeys: dict[str, "_KeywordValue"] = field(default_factory=dict)


@dataclass
class _Section:
    section_type: str  # one of SECTION_TYPES, or "Unknown" for invalid headings
    name: str
    raw_heading: str  # for error reporting on unknown headings
    line: int
    keywords: dict[str, "_KeywordValue"] = field(default_factory=dict)
    rules: list[str] = field(default_factory=list)
    columns: list[_Column] = field(default_factory=list)


@dataclass
class _KeywordValue:
    value: str
    line: int


# ── Validator ────────────────────────────────────────────────────────


class Form2SDCValidator:
    """Validates a Form2SDCTemplate markdown document against md2pd."""

    def __init__(self) -> None:
        self._errors: list[ValidationIssue] = []
        self._warnings: list[ValidationIssue] = []
        self._suggestions: list[ValidationIssue] = []
        self._yaml_end_line: int = 0

    def validate(
        self, markdown_content: str, document: str = ""
    ) -> ValidationResult:
        """Validate a markdown document and return a structured result."""
        self._errors = []
        self._warnings = []
        self._suggestions = []
        self._yaml_end_line = 0

        # Phase 1: extract YAML front matter
        yaml_block, body = self._extract_yaml_and_body(markdown_content)
        if yaml_block is None:
            self._error(
                "E-DOC-001",
                1,
                "Missing YAML front matter",
                "Add YAML front matter between '---' delimiters at the start of the document.",
            )
            return self._build_result(document)

        front_matter = self._parse_yaml(yaml_block)
        if front_matter is None:
            return self._build_result(document)

        self._validate_front_matter(front_matter)

        # Phase 2: parse body into sections + columns
        sections = self._parse_sections(body)

        if not body or not body.strip():
            self._error(
                "E-DOC-006",
                self._yaml_end_line + 1,
                "No content found after YAML front matter",
                "Add at least a '## Data: <Name>' section with column definitions.",
            )
            return self._build_result(document)

        # Phase 3: validate structure
        self._validate_section_structure(sections)

        # Phase 4: validate each section's keywords + columns
        for section in sections:
            self._validate_section(section)

        return self._build_result(document)

    # ── YAML extraction ──────────────────────────────────────────────

    def _extract_yaml_and_body(
        self, content: str
    ) -> tuple[Optional[str], str]:
        content = content.lstrip("﻿")  # strip BOM
        lines = content.split("\n")

        if not lines or lines[0].strip() != "---":
            return None, content

        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                self._yaml_end_line = i + 1  # 1-indexed
                yaml_block = "\n".join(lines[1:i])
                body = "\n".join(lines[i + 1 :])
                return yaml_block, body

        return None, content

    def _parse_yaml(self, yaml_block: str) -> Optional[dict]:
        try:
            result = yaml.safe_load(yaml_block)
        except yaml.YAMLError as exc:
            line = 2
            if hasattr(exc, "problem_mark") and exc.problem_mark is not None:
                line = exc.problem_mark.line + 2
            self._error(
                "E-DOC-002",
                line,
                f"Invalid YAML syntax: {exc}",
                "Fix YAML syntax (check quotes, indentation, colons).",
            )
            return None

        if not isinstance(result, dict):
            self._error(
                "E-DOC-002",
                2,
                "YAML front matter must be a mapping (key: value pairs)",
                "Wrap front matter content in 'key: value' lines.",
            )
            return None

        return result

    # ── Front matter validation ──────────────────────────────────────

    def _validate_front_matter(self, fm: dict) -> None:
        # E-DOC-003: template_version must be present and 4.x
        version = fm.get("template_version")
        if not version:
            self._error(
                "E-DOC-003",
                2,
                "Missing required field 'template_version' in YAML front matter",
                'Add `template_version: "4.0.0"` to front matter.',
            )
        else:
            try:
                major = int(str(version).split(".")[0])
                if major != 4:
                    self._error(
                        "E-DOC-003",
                        2,
                        f"template_version '{version}' does not start with major version 4",
                        'Use `template_version: "4.0.0"` (or any 4.x.x value).',
                    )
            except (ValueError, IndexError):
                self._error(
                    "E-DOC-003",
                    2,
                    f"template_version '{version}' is not in semantic-version form",
                    'Use `template_version: "4.0.0"` (semantic version with major 4).',
                )

        # dataset block: name and description are recommended (not required by md2pd)
        dataset = fm.get("dataset")
        if not isinstance(dataset, dict):
            self._suggestion(
                "S-QL-001",
                2,
                "Add a 'dataset' block to front matter for clearer metadata",
                'Add `dataset:\\n  name: "..."\\n  description: "..."`.',
            )
            dataset = {}

        if not dataset.get("name"):
            self._suggestion(
                "S-QL-002",
                2,
                "Consider adding 'dataset.name' to front matter (md2pd defaults to filename)",
                'Add `dataset.name: "Your Dataset Name"`.',
            )
        if not dataset.get("description"):
            self._suggestion(
                "S-QL-003",
                2,
                "Consider adding 'dataset.description' for richer metadata",
                'Add `dataset.description: "Brief description"`.',
            )

        # Warn on YAML keys md2pd does not read (silently ignored).
        for key in fm:
            if key not in RECOGNIZED_YAML_KEYS:
                self._warning(
                    "W-YAML-001",
                    2,
                    f"YAML key '{key}' is not parsed by md2pd and will be ignored",
                    f"Remove '{key}' or move the value into 'dataset.description'.",
                )

        if isinstance(dataset, dict):
            for key in dataset:
                if key not in RECOGNIZED_DATASET_KEYS:
                    self._warning(
                        "W-YAML-002",
                        2,
                        f"YAML key 'dataset.{key}' is not parsed by md2pd and will be ignored",
                        f"Remove 'dataset.{key}' or fold its value into 'dataset.description'.",
                    )

        enrichment = fm.get("enrichment")
        if isinstance(enrichment, dict):
            for key in enrichment:
                if key not in RECOGNIZED_ENRICHMENT_KEYS:
                    self._warning(
                        "W-YAML-003",
                        2,
                        f"YAML key 'enrichment.{key}' is not parsed by md2pd and will be ignored",
                        f"Remove 'enrichment.{key}'.",
                    )

    # ── Body parsing ─────────────────────────────────────────────────

    _SECTION_HEADING_RE = re.compile(r"^##\s+(\S[^:]*):\s*(.*)$")
    _COLUMN_HEADING_RE = re.compile(r"^###\s+(.+?)\s*$")
    _KEYWORD_RE = re.compile(r"^\*\*([^*]+?)\*\*:\s*(.*)$")
    _RULES_HEADER_RE = re.compile(r"^\*\*Rules\*\*:\s*$")
    _BULLET_RE = re.compile(r"^\s*-\s+(.*)$")

    def _parse_sections(self, body: str) -> list[_Section]:
        """Parse the markdown body into a list of sections with columns."""
        sections: list[_Section] = []
        current_section: Optional[_Section] = None
        current_column: Optional[_Column] = None
        in_constraints_block = False
        in_rules_block = False

        lines = body.split("\n")

        for i, raw_line in enumerate(lines):
            line_num = self._yaml_end_line + i + 1
            line = raw_line.rstrip("\r")

            # Heading detection
            if line.startswith("##"):
                # End any open rules/constraints blocks
                in_constraints_block = False
                in_rules_block = False

                # H1 (# Dataset Overview) — currently informational; we don't
                # parse its keywords here, md2pd extracts Purpose/Business
                # Context but we treat the H1 block as a comment.
                if line.startswith("# ") and not line.startswith("## "):
                    current_column = None
                    continue

                if line.startswith("## "):
                    # Section heading
                    section_match = self._SECTION_HEADING_RE.match(line)
                    if section_match:
                        type_token = section_match.group(1).strip()
                        name_token = section_match.group(2).strip()
                    else:
                        # `## SomethingWithoutColon`
                        type_token = line[3:].strip()
                        name_token = ""

                    if type_token in SECTION_TYPES:
                        section = _Section(
                            section_type=type_token,
                            name=name_token,
                            raw_heading=line,
                            line=line_num,
                        )
                    else:
                        # Invalid section heading (e.g. ## Cluster:, ## Root Cluster:)
                        section = _Section(
                            section_type="Unknown",
                            name=type_token + (": " + name_token if name_token else ""),
                            raw_heading=line,
                            line=line_num,
                        )
                    sections.append(section)
                    current_section = section
                    current_column = None
                    continue

                if line.startswith("### "):
                    # Column heading inside the current section
                    col_match = self._COLUMN_HEADING_RE.match(line)
                    if col_match and current_section is not None:
                        col = _Column(
                            name=col_match.group(1).strip(),
                            line=line_num,
                        )
                        current_section.columns.append(col)
                        current_column = col
                    continue

            # Bold-keyword line
            kw_match = self._KEYWORD_RE.match(line)
            if kw_match:
                in_constraints_block = False
                in_rules_block = False

                keyword = kw_match.group(1).strip()
                value = kw_match.group(2).strip()

                if keyword == "Constraints":
                    in_constraints_block = True
                if keyword == "Rules":
                    in_rules_block = True

                # Apply known typo corrections (we still record the original
                # keyword in the typo map for warning emission later)
                target = current_column if current_column is not None else current_section

                if target is None:
                    # Stray keyword before any section — md2pd ignores it.
                    continue

                if isinstance(target, _Column):
                    target.keywords[keyword] = _KeywordValue(value=value, line=line_num)
                    target.keyword_order.append(keyword)
                else:
                    target.keywords[keyword] = _KeywordValue(value=value, line=line_num)
                continue

            # Bulleted lines under Constraints or Rules blocks
            bullet_match = self._BULLET_RE.match(line)
            if bullet_match:
                bullet_text = bullet_match.group(1).strip()
                if in_constraints_block and current_column is not None:
                    if ":" in bullet_text:
                        sub_key, sub_val = bullet_text.split(":", 1)
                        current_column.constraint_subkeys[sub_key.strip()] = (
                            _KeywordValue(value=sub_val.strip(), line=line_num)
                        )
                    continue
                if in_rules_block and current_section is not None:
                    current_section.rules.append(bullet_text)
                    continue
                # Bullet outside a block — just plain markdown content; ignore.
                continue

            # Blank line: stays inside current blocks until a non-blank
            # non-bullet line breaks them.
            if not line.strip():
                continue

            # Any other prose breaks Constraints / Rules blocks.
            in_constraints_block = False
            in_rules_block = False

        return sections

    # ── Section / structure validation ───────────────────────────────

    def _validate_section_structure(self, sections: list[_Section]) -> None:
        # Count sections by type
        type_counts: dict[str, int] = {}
        for sec in sections:
            type_counts[sec.section_type] = type_counts.get(sec.section_type, 0) + 1

            # Reject unknown section types entirely
            if sec.section_type == "Unknown":
                self._error(
                    "E-SEC-001",
                    sec.line,
                    f"Heading '{sec.raw_heading.strip()}' is not a recognized named-tree section",
                    f"Use one of: {', '.join(SECTION_TYPES)}. md2pd will silently discard sections with other prefixes.",
                )

        # Data: required, exactly one
        data_count = type_counts.get("Data", 0)
        if data_count == 0:
            self._error(
                "E-SEC-002",
                self._yaml_end_line + 1,
                "Missing required '## Data:' section",
                "Add a '## Data: <Name>' section containing the form payload columns.",
            )
        elif data_count > 1:
            self._error(
                "E-SEC-003",
                next(s.line for s in sections if s.section_type == "Data"),
                f"Found {data_count} '## Data:' sections; md2pd keeps only the last and discards the rest",
                "Consolidate all form-payload columns into a single '## Data:' section.",
            )

        # Single-instance sections
        for sec_type in SINGLE_INSTANCE_SECTIONS:
            if sec_type == "Data":
                continue  # handled above
            count = type_counts.get(sec_type, 0)
            if count > 1:
                self._error(
                    "E-SEC-004",
                    next(s.line for s in sections if s.section_type == sec_type),
                    f"Found {count} '## {sec_type}:' sections; only one is allowed",
                    f"Keep at most one '## {sec_type}:' section per template.",
                )

    # ── Per-section validation ───────────────────────────────────────

    def _validate_section(self, section: _Section) -> None:
        if section.section_type == "Unknown":
            return  # already reported as E-SEC-001

        # Validate section-level keywords against the per-section allowlist.
        allowed_keywords = SECTION_KEYWORDS.get(section.section_type, set())
        for keyword in section.keywords:
            if keyword == "Rules":
                # Rules are extracted into section.rules during parsing.
                continue
            if keyword in KEYWORD_CORRECTIONS:
                self._warning(
                    "W-DEP-001",
                    section.keywords[keyword].line,
                    f"Section keyword '**{keyword}**' is deprecated — use '**{KEYWORD_CORRECTIONS[keyword]}**'",
                    f"Rename to '**{KEYWORD_CORRECTIONS[keyword]}**'.",
                    keyword=keyword,
                )
                continue
            if keyword not in allowed_keywords:
                self._warning(
                    "W-SEC-001",
                    section.keywords[keyword].line,
                    f"Keyword '**{keyword}**' is not parsed at the '## {section.section_type}:' level and will be ignored",
                    f"Allowed section keywords for {section.section_type}: "
                    + (", ".join(sorted(allowed_keywords)) or "(none)"),
                    keyword=keyword,
                )

        # Validate Rules bullets (cluster sections only)
        if section.rules and section.section_type not in (
            "Data",
            "Workflow",
            "Subject",
            "Provider",
            "Participation",
        ):
            self._warning(
                "W-SEC-002",
                section.line,
                f"'**Rules**:' is only meaningful in column-bearing sections; ignored in '## {section.section_type}:'",
                "Move Rules into a Data, Workflow, Subject, Provider, or Participation section.",
            )

        # Columns appear only in column-bearing sections.
        if section.columns and section.section_type not in COLUMN_BEARING_SECTIONS:
            for col in section.columns:
                self._warning(
                    "W-SEC-003",
                    col.line,
                    f"Column '### {col.name}' inside '## {section.section_type}:' will be ignored by md2pd",
                    f"Move the column into a column-bearing section "
                    f"({', '.join(COLUMN_BEARING_SECTIONS)}).",
                    component=col.name,
                )

        # Per-column validation
        for col in section.columns:
            self._validate_column(col, section)

    # ── Per-column validation ────────────────────────────────────────

    def _validate_column(self, col: _Column, section: _Section) -> None:
        # E-COL-001: column heading must not start with 'Column:'
        if col.name.lower().startswith("column:"):
            self._error(
                "E-COL-001",
                col.line,
                f"Column heading '### {col.name}' includes a 'Column:' prefix",
                "Drop the 'Column:' prefix — md2pd takes the literal text after '###' as the column name. Use '### "
                + col.name.split(":", 1)[1].strip()
                + "' instead.",
                component=col.name,
            )

        # E-COL-002: empty name
        if not col.name.strip():
            self._error(
                "E-COL-002",
                col.line,
                "Column heading is empty",
                "Provide a column name after '### '.",
                component=col.name,
            )
            return

        # Validate keywords
        for keyword in col.keyword_order:
            if keyword in KEYWORD_CORRECTIONS:
                target = KEYWORD_CORRECTIONS[keyword]
                self._error(
                    "E-COL-003",
                    col.keywords[keyword].line,
                    f"Column keyword '**{keyword}**' is invalid; md2pd expects '**{target}**'",
                    f"Rename to '**{target}**'.",
                    component=col.name,
                    keyword=keyword,
                )
                continue
            if keyword not in VALID_COLUMN_KEYWORDS:
                self._error(
                    "E-COL-004",
                    col.keywords[keyword].line,
                    f"Column keyword '**{keyword}**' is not in md2pd's allowlist and will be silently dropped",
                    "Use one of: "
                    + ", ".join(sorted(PARSED_COLUMN_KEYWORDS))
                    + ". For free-form documentation, fold the value into '**Description**:' or '**Business Rules**:'.",
                    component=col.name,
                    keyword=keyword,
                )

        # Type validation
        if "Type" not in col.keywords:
            self._suggestion(
                "S-COL-001",
                col.line,
                f"Column '### {col.name}' has no '**Type**:'; md2pd will default to 'text' (XdString)",
                "Add '**Type**: <type>' as the first keyword for clarity.",
                component=col.name,
            )
        else:
            type_value_raw = col.keywords["Type"].value.strip()
            type_value_lc = type_value_raw.lower()
            if type_value_lc not in VALID_TYPE_VALUES:
                self._error(
                    "E-COL-005",
                    col.keywords["Type"].line,
                    f"Type '{type_value_raw}' is not recognized by md2pd",
                    "Valid explicit SDC4 types: "
                    + ", ".join(sorted(EXPLICIT_SDC4_TYPES))
                    + ". Or use a user-friendly type: text, integer, decimal, boolean, date, datetime, time, identifier, email, url.",
                    component=col.name,
                    keyword="Type",
                )

            # XdBoolean cannot have an Enumeration
            if type_value_lc == "xdboolean" and "Enumeration" in col.keywords:
                self._error(
                    "E-COL-006",
                    col.keywords["Enumeration"].line,
                    f"Column '### {col.name}' is XdBoolean and cannot have '**Enumeration**:'",
                    "Either remove the Enumeration block or change Type to a categorical type (e.g., 'text' with Enumeration → XdToken).",
                    component=col.name,
                    keyword="Enumeration",
                )

        # Constraints validation
        if "Constraints" in col.keywords:
            for sub_key, sub_val in col.constraint_subkeys.items():
                if sub_key not in RECOGNIZED_CONSTRAINT_KEYS:
                    self._error(
                        "E-COL-007",
                        sub_val.line,
                        f"Constraint sub-key '{sub_key}' is not parsed by md2pd and will be silently dropped",
                        "Allowed sub-keys: required, range, precision. Express other validation hints in '**Description**:' or '**Business Rules**:'.",
                        component=col.name,
                        keyword="Constraints",
                    )
                elif sub_key == "range":
                    self._validate_range_value(col, sub_val)
                elif sub_key == "precision":
                    if not self._is_int(sub_val.value):
                        self._error(
                            "E-COL-008",
                            sub_val.line,
                            f"Constraint 'precision: {sub_val.value}' must be an integer",
                            "Set precision to a non-negative integer (e.g. `precision: 2`).",
                            component=col.name,
                            keyword="Constraints",
                        )
                elif sub_key == "required":
                    if sub_val.value.strip().lower() not in {"true", "false"}:
                        self._error(
                            "E-COL-009",
                            sub_val.line,
                            f"Constraint 'required: {sub_val.value}' must be 'true' or 'false'",
                            "Use `required: true` or `required: false`.",
                            component=col.name,
                            keyword="Constraints",
                        )

        # ReuseComponent format check
        if "ReuseComponent" in col.keywords:
            value = col.keywords["ReuseComponent"].value.strip()
            if not value.startswith("@"):
                self._error(
                    "E-COL-010",
                    col.keywords["ReuseComponent"].line,
                    f"ReuseComponent '{value}' must start with '@'",
                    "Use '@ProjectName:ComponentLabel'.",
                    component=col.name,
                    keyword="ReuseComponent",
                )
            elif ":" not in value[1:]:
                self._error(
                    "E-COL-010",
                    col.keywords["ReuseComponent"].line,
                    f"ReuseComponent '{value}' is missing the ':' separator",
                    "Use '@ProjectName:ComponentLabel'.",
                    component=col.name,
                    keyword="ReuseComponent",
                )
            else:
                project_part, label_part = value[1:].split(":", 1)
                if not project_part.strip() or not label_part.strip():
                    self._error(
                        "E-COL-010",
                        col.keywords["ReuseComponent"].line,
                        f"ReuseComponent '{value}' has an empty project or label",
                        "Use '@ProjectName:ComponentLabel' with both parts non-empty.",
                        component=col.name,
                        keyword="ReuseComponent",
                    )

        # Suggestions
        if "Description" not in col.keywords:
            self._suggestion(
                "S-COL-002",
                col.line,
                f"Column '### {col.name}' has no '**Description**:'",
                "Add a '**Description**:' so the LLM and downstream consumers understand the field.",
                component=col.name,
            )
        if (
            "Examples" not in col.keywords
            and "Type" in col.keywords
            and "Enumeration" not in col.keywords
        ):
            # Booleans and enumerated columns already document their value set:
            # boolean is implicitly true/false, and **Enumeration**: lists every
            # allowed value. **Examples**: would be a redundant subset.
            type_lc = col.keywords["Type"].value.strip().lower()
            if type_lc not in {"xdboolean", "boolean", "bool", "flag"}:
                self._suggestion(
                    "S-COL-003",
                    col.line,
                    f"Column '### {col.name}' has no '**Examples**:'",
                    "Add 2-3 sample values to '**Examples**:' for clarity.",
                    component=col.name,
                )

    # ── Helpers ──────────────────────────────────────────────────────

    def _validate_range_value(self, col: _Column, sub_val: _KeywordValue) -> None:
        raw = sub_val.value.strip()
        if not (raw.startswith("[") and raw.endswith("]")):
            self._error(
                "E-COL-011",
                sub_val.line,
                f"Constraint 'range: {raw}' must be a two-element list like '[min, max]'",
                "Use 'range: [min, max]' (use 'null' for an unbounded end).",
                component=col.name,
                keyword="Constraints",
            )
            return
        # Accept YAML's `null` and Python's `None` as the unbounded marker;
        # ast.literal_eval recognizes only `None`, so translate before parsing.
        normalized = re.sub(r"\bnull\b", "None", raw, flags=re.IGNORECASE)
        try:
            parsed = ast.literal_eval(normalized)
        except (ValueError, SyntaxError):
            self._error(
                "E-COL-011",
                sub_val.line,
                f"Constraint 'range: {raw}' is not parseable as a list",
                "Use 'range: [min, max]' with numeric values or null.",
                component=col.name,
                keyword="Constraints",
            )
            return
        if not isinstance(parsed, list) or len(parsed) != 2:
            self._error(
                "E-COL-011",
                sub_val.line,
                f"Constraint 'range: {raw}' must have exactly two elements",
                "Use 'range: [min, max]'.",
                component=col.name,
                keyword="Constraints",
            )

    @staticmethod
    def _is_int(s: str) -> bool:
        try:
            int(s.strip())
            return True
        except (ValueError, TypeError):
            return False

    def _error(
        self,
        code: str,
        line: int,
        message: str,
        fix: str = "",
        component: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> None:
        self._errors.append(
            ValidationIssue(
                code=code,
                severity="CRITICAL",
                message=message,
                line=line,
                fix=fix,
                component=component,
                keyword=keyword,
            )
        )

    def _warning(
        self,
        code: str,
        line: int,
        message: str,
        fix: str = "",
        component: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> None:
        self._warnings.append(
            ValidationIssue(
                code=code,
                severity="WARNING",
                message=message,
                line=line,
                fix=fix,
                component=component,
                keyword=keyword,
            )
        )

    def _suggestion(
        self,
        code: str,
        line: int,
        message: str,
        fix: str = "",
        component: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> None:
        self._suggestions.append(
            ValidationIssue(
                code=code,
                severity="SUGGESTION",
                message=message,
                line=line,
                fix=fix,
                component=component,
                keyword=keyword,
            )
        )

    def _build_result(self, document: str) -> ValidationResult:
        valid = len(self._errors) == 0
        return ValidationResult(
            valid=valid,
            errors=self._errors,
            warnings=self._warnings,
            suggestions=self._suggestions,
            metadata={
                "document": document,
                "error_count": len(self._errors),
                "warning_count": len(self._warnings),
                "suggestion_count": len(self._suggestions),
            },
        )
