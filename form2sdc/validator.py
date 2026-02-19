"""Form2SDCTemplate validator implementing all rules from VALIDATOR_SPECIFICATION.md.

Supports both Form2SDCTemplate.md v4.1.0 YAML format (dataset.name) and
validator spec format (project_name). Normalizes internally.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import yaml


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


VALID_TYPES = frozenset(
    {
        "Cluster",
        "XdString",
        "XdBoolean",
        "XdCount",
        "XdQuantity",
        "XdFloat",
        "XdDouble",
        "XdTemporal",
        "XdOrdinal",
        "XdRatio",
        "XdInterval",
        "XdFile",
        "XdLink",
        "XdToken",
    }
)

QUANTIFIED_TYPES = frozenset({"XdCount", "XdQuantity", "XdFloat", "XdDouble"})

# Deprecated keyword aliases
KEYWORD_ALIASES = {
    "Values": "Enumeration",
    "Unit": "Units",
}

# Type suggestions based on component name patterns
TYPE_SUGGESTIONS = [
    (re.compile(r"(?i)(name|address|description|comment|note)"), "XdString"),
    (re.compile(r"(?i)(count|number|age|quantity)"), "XdCount"),
    (re.compile(r"(?i)(weight|height|temperature|pressure|dose)"), "XdQuantity"),
    (re.compile(r"(?i)(date|time|created|updated|birth)"), "XdTemporal"),
    (re.compile(r"(?i)(status|level|grade|severity|priority)"), "XdOrdinal"),
    (re.compile(r"(?i)(^is_|^has_|enabled|active|flag)"), "XdBoolean"),
    (re.compile(r"(?i)(_id$|_code$|_key$|identifier)"), "XdIdentifier"),
    (re.compile(r"(?i)(_url$|_link$|website|homepage)"), "XdLink"),
]


@dataclass
class _Component:
    """Internal representation of a parsed component."""

    name: str
    start_line: int
    keywords: dict[str, _KeywordValue] = field(default_factory=dict)
    keyword_order: list[str] = field(default_factory=list)


@dataclass
class _KeywordValue:
    value: str
    line: int


class Form2SDCValidator:
    """Validates Form2SDCTemplate markdown documents.

    Implements all rules from VALIDATOR_SPECIFICATION.md:
    - 24 CRITICAL (E-) rules
    - 15 WARNING (W-) rules
    - 12 SUGGESTION (S-) rules
    """

    def __init__(self) -> None:
        self._errors: list[ValidationIssue] = []
        self._warnings: list[ValidationIssue] = []
        self._suggestions: list[ValidationIssue] = []
        self._components: list[_Component] = []
        self._yaml_end_line: int = 0

    def validate(
        self, markdown_content: str, document: str = ""
    ) -> ValidationResult:
        """Validate a Form2SDCTemplate markdown document.

        Args:
            markdown_content: Full markdown content including YAML front matter.
            document: Optional filename for metadata.

        Returns:
            ValidationResult with errors, warnings, and suggestions.
        """
        self._errors = []
        self._warnings = []
        self._suggestions = []
        self._components = []
        self._yaml_end_line = 0

        # Phase 1: Extract and validate YAML front matter
        yaml_block, markdown_body = self._extract_yaml_and_body(markdown_content)

        if yaml_block is None:
            self._add_error(
                "E-DOC-001",
                1,
                "Missing YAML front matter",
                fix="Add YAML front matter between '---' delimiters at the start of the document",
            )
            return self._build_result(document)

        # Parse YAML
        front_matter = self._parse_yaml(yaml_block)
        if front_matter is None:
            return self._build_result(document)

        self._validate_front_matter(front_matter)

        if self._has_critical_errors():
            return self._build_result(document)

        # Phase 2: Check markdown body exists
        if not markdown_body or not markdown_body.strip():
            self._add_error(
                "E-DOC-006",
                self._yaml_end_line + 1,
                "No content found after YAML front matter",
                fix="Add markdown content with at least one Cluster component after the front matter",
            )
            return self._build_result(document)

        # Phase 3: Parse components
        self._components = self._parse_components(markdown_body)

        if not self._components:
            self._add_error(
                "E-DOC-006",
                self._yaml_end_line + 1,
                "No components found in markdown body",
                fix="Add at least one component with a heading and **Type** keyword",
            )
            return self._build_result(document)

        # Phase 4: Validate each component
        for comp in self._components:
            self._validate_component(comp)

        # Phase 5: Cross-component validation
        self._validate_root_cluster(self._components[0])
        self._validate_component_names(self._components)

        # Phase 6: Context-aware suggestions
        self._add_context_suggestions(self._components)

        return self._build_result(document)

    # ── YAML extraction ──────────────────────────────────────────────

    def _extract_yaml_and_body(
        self, content: str
    ) -> tuple[Optional[str], str]:
        """Extract YAML front matter and markdown body from content."""
        content = content.lstrip("\ufeff")  # Strip BOM
        lines = content.split("\n")

        if not lines or lines[0].strip() != "---":
            return None, content

        # Find closing ---
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                self._yaml_end_line = i + 1  # 1-indexed
                yaml_block = "\n".join(lines[1:i])
                body = "\n".join(lines[i + 1 :])
                return yaml_block, body

        return None, content

    def _parse_yaml(self, yaml_block: str) -> Optional[dict]:
        """Parse YAML and report errors."""
        try:
            result = yaml.safe_load(yaml_block)
            if not isinstance(result, dict):
                self._add_error(
                    "E-DOC-002",
                    2,
                    "YAML front matter must be a mapping (key: value pairs)",
                    fix="Ensure front matter contains key-value pairs like 'project_name: \"My Project\"'",
                )
                return None
            return result
        except yaml.YAMLError as e:
            line = 2
            if hasattr(e, "problem_mark") and e.problem_mark is not None:
                line = e.problem_mark.line + 2  # Adjust for --- line
            self._add_error(
                "E-DOC-002",
                line,
                f"Invalid YAML syntax: {e}",
                fix="Fix YAML syntax errors (check quotes, indentation, colons)",
            )
            return None

    # ── Front matter validation ──────────────────────────────────────

    def _validate_front_matter(self, fm: dict) -> None:
        """Validate YAML front matter fields.

        Supports both validator spec format (project_name, source_language)
        and Form2SDCTemplate.md format (dataset.name, dataset.description).
        """
        # Normalize: support both formats
        normalized = self._normalize_front_matter(fm)

        # E-DOC-003: project_name required
        if not normalized.get("project_name"):
            self._add_error(
                "E-DOC-003",
                2,
                "Missing required field 'project_name' in YAML front matter",
                fix="Add 'project_name: \"Your Project Name\"' to front matter",
            )

        # E-DOC-004: source_language required
        if not normalized.get("source_language"):
            self._add_error(
                "E-DOC-004",
                2,
                "Missing required field 'source_language' in YAML front matter",
                fix="Add 'source_language: \"English\"' (or appropriate language) to front matter",
            )

        # E-DOC-005: template_version required
        if not normalized.get("template_version"):
            self._add_error(
                "E-DOC-005",
                2,
                "Missing required field 'template_version' in YAML front matter",
                fix="Add 'template_version: \"4.0.0\"' to front matter",
            )

        # S-QL-005: Metadata suggestions
        if "description" not in fm and not (
            isinstance(fm.get("dataset"), dict)
            and "description" in fm["dataset"]
        ):
            self._add_suggestion(
                "S-QL-005",
                2,
                "Consider adding a 'description' field to front matter",
                fix="Add 'description: \"Brief description of the template\"'",
            )
        if "author" not in fm and "creator" not in fm and not (
            isinstance(fm.get("dataset"), dict)
            and "creator" in fm["dataset"]
        ):
            self._add_suggestion(
                "S-QL-005",
                2,
                "Consider adding an 'author' field to front matter for traceability",
                fix="Add 'author: \"Your Name or Organization\"'",
            )

    def _normalize_front_matter(self, fm: dict) -> dict:
        """Normalize front matter to canonical field names.

        Handles both:
        - Validator spec format: project_name, source_language, template_version
        - Form2SDCTemplate.md format: dataset.name, dataset.description, template_version
        """
        normalized: dict = {}

        # project_name: direct or dataset.name
        if "project_name" in fm:
            normalized["project_name"] = fm["project_name"]
        elif isinstance(fm.get("dataset"), dict) and fm["dataset"].get("name"):
            normalized["project_name"] = fm["dataset"]["name"]

        # source_language: direct
        if "source_language" in fm:
            normalized["source_language"] = fm["source_language"]

        # template_version: direct
        if "template_version" in fm:
            normalized["template_version"] = fm["template_version"]

        return normalized

    # ── Component parsing ────────────────────────────────────────────

    def _parse_components(self, markdown_body: str) -> list[_Component]:
        """Parse component blocks from markdown body."""
        components: list[_Component] = []
        current: Optional[_Component] = None

        heading_re = re.compile(r"^(#{1,6})\s+(.+)")
        bold_re = re.compile(r"^\*\*(.+?)\*\*\s*$")
        keyword_re = re.compile(r"^\*\*(.+?)\*\*:\s*(.*)")

        lines = markdown_body.split("\n")
        for i, line in enumerate(lines):
            line_num = self._yaml_end_line + i + 1

            # Detect component heading
            heading_match = heading_re.match(line)
            bold_match = bold_re.match(line) if not heading_match else None

            if heading_match or bold_match:
                # Check if this is actually a keyword line (bold with colon)
                if bold_match and keyword_re.match(line):
                    # This is a keyword, not a component name
                    if current is not None:
                        kw_match = keyword_re.match(line)
                        if kw_match:
                            keyword = kw_match.group(1)
                            value = kw_match.group(2).strip()
                            self._process_keyword(current, keyword, value, line_num)
                    continue

                if current is not None:
                    components.append(current)

                name = (
                    heading_match.group(2).strip()
                    if heading_match
                    else bold_match.group(1).strip()
                )
                current = _Component(name=name, start_line=line_num)

            elif keyword_re.match(line):
                if current is not None:
                    kw_match = keyword_re.match(line)
                    if kw_match:
                        keyword = kw_match.group(1)
                        value = kw_match.group(2).strip()
                        self._process_keyword(current, keyword, value, line_num)

        if current is not None:
            components.append(current)

        return components

    def _process_keyword(
        self,
        component: _Component,
        keyword: str,
        value: str,
        line_num: int,
    ) -> None:
        """Process a keyword, applying alias normalization and deprecation warnings."""
        # Check for deprecated keywords
        if keyword in KEYWORD_ALIASES:
            new_keyword = KEYWORD_ALIASES[keyword]
            if keyword == "Values":
                self._add_warning(
                    "W-DEP-001",
                    line_num,
                    f"Keyword '**{keyword}**' is deprecated - use '**{new_keyword}**' instead",
                    fix=f"Change '**{keyword}**' to '**{new_keyword}**'",
                    component=component.name,
                    keyword=keyword,
                )
            elif keyword == "Unit":
                self._add_warning(
                    "W-DEP-002",
                    line_num,
                    f"Keyword '**{keyword}**' is deprecated - use '**{new_keyword}**' instead",
                    fix=f"Change '**{keyword}**' to '**{new_keyword}**'",
                    component=component.name,
                    keyword=keyword,
                )
            keyword = new_keyword

        component.keywords[keyword] = _KeywordValue(value=value, line=line_num)
        component.keyword_order.append(keyword)

    # ── Component validation ─────────────────────────────────────────

    def _validate_component(self, comp: _Component) -> None:
        """Validate a single component."""
        # E-CMP-004: Component name must be non-empty
        if not comp.name.strip():
            self._add_error(
                "E-CMP-004",
                comp.start_line,
                "Component name must be non-empty",
                fix="Add a descriptive name to the component heading",
                component=comp.name,
            )
            return

        # E-CMP-001: Type is required
        if "Type" not in comp.keywords:
            suggestion = self._suggest_type_from_name(comp.name)
            fix = "Add '**Type**: <type>' as the first keyword"
            if suggestion:
                fix += f" (suggestion: {suggestion})"
            self._add_error(
                "E-CMP-001",
                comp.start_line,
                "Missing **Type** keyword",
                fix=fix,
                component=comp.name,
            )
            return

        type_value = comp.keywords["Type"].value.strip()

        # Check for component reuse syntax (@Project:Label)
        if type_value.startswith("@"):
            self._validate_component_reference(comp, type_value)
            return

        # E-CMP-002: Type must be valid
        if type_value not in VALID_TYPES:
            self._add_error(
                "E-CMP-002",
                comp.keywords["Type"].line,
                f"Invalid Type '{type_value}' - must be one of: {', '.join(sorted(VALID_TYPES))}",
                fix=f"Change to a valid SDC4 type",
                component=comp.name,
                keyword="Type",
            )
            return

        # E-CMP-003: Type must be the first keyword
        if comp.keyword_order and comp.keyword_order[0] != "Type":
            self._add_error(
                "E-CMP-003",
                comp.start_line,
                "**Type** must be the first keyword in component",
                fix="Move '**Type**' to be the first keyword after the component heading",
                component=comp.name,
                keyword="Type",
            )

        # Type-specific validation
        if type_value in QUANTIFIED_TYPES:
            self._validate_quantified_type(comp, type_value)
        elif type_value == "XdString":
            self._validate_string_type(comp)
        elif type_value == "XdToken":
            self._validate_token_type(comp)
        elif type_value == "XdBoolean":
            self._validate_boolean_type(comp)
        elif type_value == "XdTemporal":
            self._validate_temporal_type(comp)
        elif type_value == "XdOrdinal":
            self._validate_ordinal_type(comp)
        elif type_value == "Cluster":
            self._validate_cluster_type(comp)

        # W-BP-001: Description recommended
        if "Description" not in comp.keywords and type_value != "Cluster":
            self._add_warning(
                "W-BP-001",
                comp.start_line,
                "Missing **Description** keyword - LLM may misinterpret component purpose",
                fix=f"Add '**Description**: <description of {comp.name}>'",
                component=comp.name,
            )

        # W-BP-002: Name should be descriptive
        if len(comp.name.strip()) < 3 and type_value != "Cluster":
            self._add_warning(
                "W-BP-002",
                comp.start_line,
                f"Component name '{comp.name}' is too short - use descriptive names (>3 characters)",
                fix="Use a more descriptive component name",
                component=comp.name,
            )

        # W-BP-003: Examples improve understanding
        if "Examples" not in comp.keywords and type_value not in ("Cluster", "XdBoolean", "XdFile"):
            self._add_warning(
                "W-BP-003",
                comp.start_line,
                "Missing **Examples** keyword - examples improve LLM understanding",
                fix=f"Add '**Examples**: <2-3 sample values>'",
                component=comp.name,
            )

    def _validate_component_reference(
        self, comp: _Component, ref: str
    ) -> None:
        """Validate @Project:Label component reuse syntax (E-SYN-003)."""
        pattern = re.compile(r"^@([A-Za-z0-9_-]+):([A-Za-z0-9_-]+)$")
        match = pattern.match(ref)
        if not match:
            self._add_error(
                "E-SYN-003",
                comp.keywords["Type"].line,
                f"Invalid component reference '{ref}' - must follow @ProjectName:ComponentLabel format",
                fix="Use format '@ProjectName:ComponentLabel' with no spaces",
                component=comp.name,
                keyword="Type",
            )

    def _validate_quantified_type(
        self, comp: _Component, type_value: str
    ) -> None:
        """Validate XdCount, XdQuantity, XdFloat, XdDouble."""
        # E-REQ-001: Units required
        if "Units" not in comp.keywords:
            self._add_error(
                "E-REQ-001",
                comp.start_line,
                f"{type_value} requires **Units** keyword",
                fix=f"Add '**Units**: <unit>' (e.g., kg, years, USD)",
                component=comp.name,
            )
            return

        # E-REQ-002: Units must be non-empty
        units_value = comp.keywords["Units"].value.strip()
        if not units_value:
            self._add_error(
                "E-REQ-002",
                comp.keywords["Units"].line,
                "**Units** value cannot be empty",
                fix="Specify at least one unit (e.g., 'kg', 'years', 'USD')",
                component=comp.name,
                keyword="Units",
            )

        # W-AMB-003: Units without definitions
        if units_value and "(" not in units_value:
            self._add_warning(
                "W-AMB-003",
                comp.keywords["Units"].line,
                "Units list lacks definitions - LLM may misinterpret symbols",
                fix="Add definitions: e.g., 'kg (kilograms), lb (pounds)'",
                component=comp.name,
                keyword="Units",
            )

        # E-BIZ-005: Min Magnitude <= Max Magnitude
        self._validate_numeric_range(
            comp,
            "Min Magnitude",
            "Max Magnitude",
            "E-BIZ-005",
        )

        # E-SYN-002: Numeric values must be valid
        for kw in ("Min Magnitude", "Max Magnitude", "Precision", "Fraction Digits"):
            if kw in comp.keywords:
                val = comp.keywords[kw].value.strip()
                if val:
                    try:
                        float(val)
                    except ValueError:
                        self._add_error(
                            "E-SYN-002",
                            comp.keywords[kw].line,
                            f"Invalid numeric value '{val}' for **{kw}**",
                            fix=f"Provide a valid number for **{kw}**",
                            component=comp.name,
                            keyword=kw,
                        )

        # W-BP-004: Magnitude constraints recommended
        if (
            "Min Magnitude" not in comp.keywords
            and "Max Magnitude" not in comp.keywords
        ):
            self._add_warning(
                "W-BP-004",
                comp.start_line,
                "Consider specifying Min/Max Magnitude constraints for bounded data",
                fix="Add '**Min Magnitude**: <min>' and '**Max Magnitude**: <max>'",
                component=comp.name,
            )

    def _validate_string_type(self, comp: _Component) -> None:
        """Validate XdString components."""
        has_pattern = "Pattern" in comp.keywords
        has_enum = "Enumeration" in comp.keywords

        # E-BIZ-003: Cannot have both
        if has_pattern and has_enum:
            self._add_error(
                "E-BIZ-003",
                comp.keywords["Enumeration"].line,
                "XdString cannot have both **Pattern** and **Enumeration** - choose one",
                fix="Remove either Pattern (for free text) or Enumeration (for fixed choices)",
                component=comp.name,
            )

        # E-BIZ-007: Pattern must be valid regex
        if has_pattern:
            self._validate_regex_pattern(comp)

        # E-BIZ-004: Min Length <= Max Length
        self._validate_numeric_range(
            comp, "Min Length", "Max Length", "E-BIZ-004"
        )

        # E-SYN-002: Length values must be numeric
        for kw in ("Min Length", "Max Length"):
            if kw in comp.keywords:
                val = comp.keywords[kw].value.strip()
                if val:
                    try:
                        int(val)
                    except ValueError:
                        self._add_error(
                            "E-SYN-002",
                            comp.keywords[kw].line,
                            f"Invalid numeric value '{val}' for **{kw}**",
                            fix=f"Provide a valid integer for **{kw}**",
                            component=comp.name,
                            keyword=kw,
                        )

        # W-BP-005: Max Length recommended
        if "Max Length" not in comp.keywords and not has_enum:
            self._add_warning(
                "W-BP-005",
                comp.start_line,
                "Consider specifying **Max Length** to prevent unbounded strings",
                fix="Add '**Max Length**: 255' (or appropriate limit)",
                component=comp.name,
            )

        # S-OPT-004: Suggest XdToken for enumerated strings
        if has_enum and not has_pattern:
            self._add_suggestion(
                "S-OPT-004",
                comp.start_line,
                "Consider using XdToken instead of XdString for categorical data with fixed values",
                fix="Change '**Type**: XdString' to '**Type**: XdToken'",
                component=comp.name,
            )

    def _validate_token_type(self, comp: _Component) -> None:
        """Validate XdToken components."""
        # XdToken should have Enumeration
        if "Enumeration" not in comp.keywords:
            self._add_warning(
                "W-BP-001",
                comp.start_line,
                "XdToken typically has an **Enumeration** of allowed values",
                fix="Add '**Enumeration**:' with the list of valid values",
                component=comp.name,
            )

    def _validate_boolean_type(self, comp: _Component) -> None:
        """Validate XdBoolean components."""
        # E-BIZ-001: No Enumeration
        if "Enumeration" in comp.keywords:
            self._add_error(
                "E-BIZ-001",
                comp.keywords["Enumeration"].line,
                "XdBoolean cannot have **Enumeration** keyword",
                fix="Remove **Enumeration** - XdBoolean only supports true/false values",
                component=comp.name,
                keyword="Enumeration",
            )

        # E-BIZ-002: No Pattern
        if "Pattern" in comp.keywords:
            self._add_error(
                "E-BIZ-002",
                comp.keywords["Pattern"].line,
                "XdBoolean cannot have **Pattern** keyword",
                fix="Remove **Pattern** - XdBoolean only supports true/false values",
                component=comp.name,
                keyword="Pattern",
            )

    def _validate_temporal_type(self, comp: _Component) -> None:
        """Validate XdTemporal components."""
        # W-BP-006: Temporal Type recommended
        if "Temporal Type" not in comp.keywords:
            self._add_warning(
                "W-BP-006",
                comp.start_line,
                "XdTemporal should specify **Temporal Type** (date, time, datetime, or duration)",
                fix="Add '**Temporal Type**: date' (or time, datetime, duration)",
                component=comp.name,
            )

        # E-BIZ-006: Min Date <= Max Date
        if "Min Date" in comp.keywords and "Max Date" in comp.keywords:
            min_date_str = comp.keywords["Min Date"].value.strip()
            max_date_str = comp.keywords["Max Date"].value.strip()
            try:
                from datetime import date as date_type

                min_date = date_type.fromisoformat(min_date_str)
                max_date = date_type.fromisoformat(max_date_str)
                if min_date > max_date:
                    self._add_error(
                        "E-BIZ-006",
                        comp.keywords["Max Date"].line,
                        f"Min Date ({min_date_str}) exceeds Max Date ({max_date_str})",
                        fix="Ensure Min Date is earlier than or equal to Max Date",
                        component=comp.name,
                        keyword="Max Date",
                    )
            except ValueError:
                pass  # Invalid date format caught by E-SYN-002

    def _validate_ordinal_type(self, comp: _Component) -> None:
        """Validate XdOrdinal components."""
        # E-REQ-003: Enumeration required
        if "Enumeration" not in comp.keywords:
            self._add_error(
                "E-REQ-003",
                comp.start_line,
                "XdOrdinal requires **Enumeration** keyword with ordered values",
                fix="Add '**Enumeration**:' with an ordered list of values",
                component=comp.name,
            )
        else:
            # W-AMB-004: Check enumeration ordering
            enum_val = comp.keywords["Enumeration"].value.strip()
            if enum_val and not re.match(r"^\d+\.", enum_val):
                self._add_warning(
                    "W-AMB-004",
                    comp.keywords["Enumeration"].line,
                    "XdOrdinal enumeration should use numbered ordering for clarity",
                    fix="Use numbered list format: '1. First, 2. Second, ...'",
                    component=comp.name,
                    keyword="Enumeration",
                )

    def _validate_cluster_type(self, comp: _Component) -> None:
        """Validate Cluster components."""
        # Description recommended for Cluster too
        if "Description" not in comp.keywords:
            self._add_warning(
                "W-BP-001",
                comp.start_line,
                "Missing **Description** keyword - LLM may misinterpret cluster purpose",
                fix=f"Add '**Description**: <description of {comp.name}>'",
                component=comp.name,
            )

    def _validate_regex_pattern(self, comp: _Component) -> None:
        """Validate regex pattern syntax (E-BIZ-007)."""
        pattern_val = comp.keywords["Pattern"].value.strip()
        if pattern_val:
            try:
                re.compile(pattern_val)
            except re.error as e:
                self._add_error(
                    "E-BIZ-007",
                    comp.keywords["Pattern"].line,
                    f"Invalid regex pattern: {e}",
                    fix="Fix the regular expression syntax",
                    component=comp.name,
                    keyword="Pattern",
                )

    def _validate_numeric_range(
        self,
        comp: _Component,
        min_kw: str,
        max_kw: str,
        error_code: str,
    ) -> None:
        """Validate that min <= max for a pair of numeric keywords."""
        if min_kw in comp.keywords and max_kw in comp.keywords:
            min_val_str = comp.keywords[min_kw].value.strip()
            max_val_str = comp.keywords[max_kw].value.strip()
            try:
                min_val = float(min_val_str)
                max_val = float(max_val_str)
                if min_val > max_val:
                    self._add_error(
                        error_code,
                        comp.keywords[max_kw].line,
                        f"{min_kw} ({min_val_str}) exceeds {max_kw} ({max_val_str})",
                        fix=f"Ensure {min_kw} is less than or equal to {max_kw}",
                        component=comp.name,
                        keyword=max_kw,
                    )
            except ValueError:
                pass  # Caught by E-SYN-002

    # ── Cross-component validation ───────────────────────────────────

    def _validate_root_cluster(self, first: _Component) -> None:
        """E-DOC-007 / E-REQ-004: First component must be Cluster."""
        if "Type" not in first.keywords:
            return  # Already reported as E-CMP-001
        type_val = first.keywords["Type"].value.strip()
        if type_val != "Cluster" and not type_val.startswith("@"):
            self._add_error(
                "E-DOC-007",
                first.start_line,
                "First component must be Type: Cluster (root cluster required)",
                fix="Change the first component's Type to 'Cluster' or add a root Cluster before it",
                component=first.name,
            )

    def _validate_component_names(self, components: list[_Component]) -> None:
        """E-CMP-005: Component names must be unique."""
        seen: dict[str, int] = {}
        for comp in components:
            name_lower = comp.name.strip().lower()
            if name_lower in seen:
                self._add_error(
                    "E-CMP-005",
                    comp.start_line,
                    f"Duplicate component name '{comp.name}' (first defined at line {seen[name_lower]})",
                    fix="Give each component a unique name",
                    component=comp.name,
                )
            else:
                seen[name_lower] = comp.start_line

    # ── Context-aware suggestions ────────────────────────────────────

    def _add_context_suggestions(self, components: list[_Component]) -> None:
        """Add optimization and quality suggestions."""
        for comp in components:
            if "Type" not in comp.keywords:
                continue
            type_val = comp.keywords["Type"].value.strip()

            # S-QL-001: Semantic context for RDF
            if type_val != "Cluster" and "Semantic Links" not in comp.keywords:
                self._add_suggestion(
                    "S-QL-001",
                    comp.start_line,
                    "Consider adding semantic links to improve RDF generation",
                    fix="Add '**Semantic Links**: <ontology URI>'",
                    component=comp.name,
                )

            # S-OPT-001: Examples for complex patterns
            if (
                "Pattern" in comp.keywords
                and "Examples" not in comp.keywords
            ):
                self._add_suggestion(
                    "S-OPT-001",
                    comp.start_line,
                    "Consider adding **Examples** for complex patterns to improve LLM accuracy",
                    fix="Add '**Examples**: <2-3 sample values matching the pattern>'",
                    component=comp.name,
                )

        # S-QL-004: Consistent naming conventions
        names = [c.name for c in components]
        has_snake = any("_" in n for n in names)
        has_camel = any(
            re.search(r"[a-z][A-Z]", n) for n in names
        )
        has_spaces = any(" " in n for n in names)
        style_count = sum([has_snake, has_camel, has_spaces])
        if style_count > 1:
            self._add_suggestion(
                "S-QL-004",
                components[0].start_line,
                "Inconsistent naming conventions detected - use consistent style for maintainability",
                fix="Choose one naming style: 'snake_case', 'camelCase', or 'Title Case'",
            )

    # ── Helpers ──────────────────────────────────────────────────────

    def _suggest_type_from_name(self, name: str) -> Optional[str]:
        """Suggest a type based on component name patterns."""
        for pattern, suggested_type in TYPE_SUGGESTIONS:
            if pattern.search(name):
                return suggested_type
        return None

    def _has_critical_errors(self) -> bool:
        return len(self._errors) > 0

    def _add_error(
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
                context="",
                fix=fix,
                component=component,
                keyword=keyword,
            )
        )

    def _add_warning(
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
                context="",
                fix=fix,
                component=component,
                keyword=keyword,
            )
        )

    def _add_suggestion(
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
                context="",
                fix=fix,
                component=component,
                keyword=keyword,
            )
        )

    def _build_result(self, document: str = "") -> ValidationResult:
        return ValidationResult(
            valid=len(self._errors) == 0,
            errors=list(self._errors),
            warnings=list(self._warnings),
            suggestions=list(self._suggestions),
            metadata={
                "validator": "form2sdc-validator-python",
                "version": "1.0.0",
                "validation_time": datetime.now(tz=__import__('datetime').timezone.utc).isoformat(),
                "document": document,
                "total_components": len(self._components),
                "critical_count": len(self._errors),
                "warning_count": len(self._warnings),
                "suggestion_count": len(self._suggestions),
            },
        )
