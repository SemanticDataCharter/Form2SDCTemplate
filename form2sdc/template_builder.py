"""Template builder: converts FormAnalysis to SDC4 markdown string.

Pure Python, no LLM calls. Generates md2pd-parser-compliant markdown from
structured FormAnalysis data.

The output of this builder is what the production SDCStudio md2pd parser
(``src/md2pd/agents/template_parser_agent.py``) expects: a YAML front matter
block, an optional ``# Dataset Overview`` H1, then named-tree H2 sections
(``## Data:``, ``## Subject:``, ``## Provider:``, ``## Participation:``,
``## Workflow:``, ``## Attestation:``, ``## Audit:``, ``## Links:``) with
``### column_name`` columns inside the cluster sections.
"""

from __future__ import annotations

from form2sdc.types import (
    AttestationDefinition,
    AuditDefinition,
    ClusterDefinition,
    ColumnDefinition,
    ColumnType,
    EnumerationItem,
    FormAnalysis,
    PartyDefinition,
    resolve_sdc4_type,
)


class TemplateBuilder:
    """Builds md2pd-compliant markdown templates from FormAnalysis objects."""

    def build(self, analysis: FormAnalysis) -> str:
        """Convert a FormAnalysis to a complete SDC4 markdown template.

        Renders sections in the order md2pd's parser scans them:

        1. YAML front matter
        2. ``# Dataset Overview`` (H1, optional)
        3. ``## Subject:`` (party, optional)
        4. ``## Provider:`` (party, optional)
        5. ``## Participation:`` (parties, optional, multiple)
        6. ``## Data:`` (required — exactly one)
        7. ``## Workflow:`` (cluster, optional)
        8. ``## Attestation:`` (optional)
        9. ``## Audit:`` (optional, multiple)
        10. ``## Links:`` (optional)

        Args:
            analysis: Structured form analysis result.

        Returns:
            Complete markdown string ready for SDCStudio upload.
        """
        parts: list[str] = []

        parts.append(self._render_front_matter(analysis))
        parts.append(self._render_dataset_overview(analysis))

        # Subject / Provider / Participation (party sections come before Data
        # so that demographic/identity fields are clearly separated from the
        # form payload).
        if analysis.subject:
            parts.append(self._render_party(analysis.subject, "Subject"))
        if analysis.provider:
            parts.append(self._render_party(analysis.provider, "Provider"))
        if analysis.participations:
            for p in analysis.participations:
                parts.append(self._render_party(p, "Participation"))

        # Data section (required) — the form payload
        parts.append(self._render_cluster_section(analysis.data, "Data"))

        # Workflow section (optional). Note: md2pd currently parses but does
        # not store ``## Workflow:`` clusters; we still emit it for forward
        # compatibility and so that the markdown documents intent.
        if analysis.workflow:
            parts.append(self._render_cluster_section(analysis.workflow, "Workflow"))

        # Attestation section
        if analysis.attestation:
            parts.append(self._render_attestation(analysis.attestation))

        # Audit sections
        if analysis.audit:
            for audit in analysis.audit:
                parts.append(self._render_audit(audit))

        # Links section
        if analysis.links:
            parts.append(self._render_links(analysis.links))

        return "\n".join(parts)

    # ── PART 1: YAML Front Matter ────────────────────────────────────

    def _render_front_matter(self, analysis: FormAnalysis) -> str:
        lines = ["---"]
        lines.append('template_version: "4.0.0"')
        lines.append("dataset:")
        lines.append(f'  name: "{self._escape_yaml(analysis.dataset_name)}"')

        if analysis.dataset_description:
            lines.append(
                f'  description: "{self._escape_yaml(analysis.dataset_description)}"'
            )

        if analysis.domain:
            lines.append(f'  domain: "{self._escape_yaml(analysis.domain)}"')
        if analysis.creator:
            lines.append(f'  creator: "{self._escape_yaml(analysis.creator)}"')

        # md2pd reads enrichment.enable_llm; default-true matches the parser default
        # but emitting it explicitly makes the template self-documenting.
        if analysis.enable_llm is not None:
            lines.append("enrichment:")
            lines.append(
                f"  enable_llm: {'true' if analysis.enable_llm else 'false'}"
            )

        lines.append("---")
        return "\n".join(lines)

    # ── PART 2: Dataset Overview ─────────────────────────────────────

    def _render_dataset_overview(self, analysis: FormAnalysis) -> str:
        if not (
            analysis.dataset_description
            or analysis.purpose
            or analysis.business_context
            or analysis.primary_use
            or analysis.secondary_use
            or analysis.stakeholders
        ):
            return ""

        lines = ["", "# Dataset Overview", ""]

        if analysis.dataset_description:
            lines.append(analysis.dataset_description)
            lines.append("")

        if analysis.purpose:
            lines.append(f"**Purpose**: {analysis.purpose}")

        # Build a Business Context value from any of the related fields.
        context_parts: list[str] = []
        if analysis.business_context:
            context_parts.append(analysis.business_context)
        if analysis.primary_use:
            context_parts.append(f"Primary use: {analysis.primary_use}")
        if analysis.secondary_use:
            context_parts.append(f"Secondary use: {analysis.secondary_use}")
        if analysis.stakeholders:
            context_parts.append(f"Stakeholders: {analysis.stakeholders}")
        if context_parts:
            lines.append(f"**Business Context**: {' '.join(context_parts)}")

        return "\n".join(lines)

    # ── Cluster sections (Data, Workflow) ────────────────────────────

    def _render_cluster_section(
        self, cluster: ClusterDefinition, section_type: str
    ) -> str:
        """Render a Data or Workflow section.

        md2pd reads:
        - the first prose paragraph as the cluster description (NOT a
          ``**Description**:`` keyword)
        - ``**Purpose**:`` and ``**Business Context**:`` as keywords
        - ``**Rules**:`` followed by a bulleted list as cross-field rules
        """
        lines = ["", f"## {section_type}: {cluster.name}", ""]

        # Description as prose first paragraph (md2pd's expected form).
        if cluster.description:
            lines.append(cluster.description)
            lines.append("")

        if cluster.purpose:
            lines.append(f"**Purpose**: {cluster.purpose}")
        if cluster.business_context:
            lines.append(f"**Business Context**: {cluster.business_context}")

        if cluster.rules:
            lines.append("**Rules**:")
            for rule in cluster.rules:
                lines.append(f"  - {rule}")

        if cluster.purpose or cluster.business_context or cluster.rules:
            lines.append("")

        for col in cluster.columns:
            lines.append(self._render_column(col))

        return "\n".join(lines)

    # ── Party sections (Subject, Provider, Participation) ────────────

    def _render_party(self, party: PartyDefinition, section_type: str) -> str:
        lines = ["", f"## {section_type}: {party.name}", ""]

        if party.description:
            lines.append(f"**Description**: {party.description}")

        if section_type == "Participation":
            if party.function:
                lines.append(f"**Function**: {party.function}")
            if party.function_description:
                lines.append(
                    f"**Function Description**: {party.function_description}"
                )
            if party.mode:
                lines.append(f"**Mode**: {party.mode}")
            if party.mode_description:
                lines.append(f"**Mode Description**: {party.mode_description}")

        if party.description or party.function or party.mode:
            lines.append("")

        for col in party.columns:
            lines.append(self._render_column(col))

        return "\n".join(lines)

    # ── Attestation section ──────────────────────────────────────────

    def _render_attestation(self, att: AttestationDefinition) -> str:
        """Render an Attestation section.

        md2pd's attestation parser extracts the label that precedes any
        parenthetical specification. Plain-label form is sufficient and
        what we emit here; downstream consumers can extend with parenthetical
        media-type / content-mode specs if needed.
        """
        lines = ["", f"## Attestation: {att.name}", ""]

        if att.view:
            lines.append(f"**View**: {att.view}")
        if att.proof:
            lines.append(f"**Proof**: {att.proof}")
        if att.reason:
            lines.append(f"**Reason**: {att.reason}")

        if att.view or att.proof or att.reason:
            lines.append("")
        return "\n".join(lines)

    # ── Audit section ────────────────────────────────────────────────

    def _render_audit(self, audit: AuditDefinition) -> str:
        lines = ["", f"## Audit: {audit.name}", ""]

        if audit.system_id:
            lines.append(f"**System ID**: {audit.system_id}")
        if audit.system_user:
            lines.append(f"**System User**: {audit.system_user}")
        if audit.location:
            lines.append(f"**Location**: {audit.location}")

        if audit.system_id or audit.system_user or audit.location:
            lines.append("")
        return "\n".join(lines)

    # ── Links section ────────────────────────────────────────────────

    def _render_links(self, links: list[str]) -> str:
        lines = ["", "## Links:", ""]
        for uri in links:
            lines.append(f"  - {uri}")
        lines.append("")
        return "\n".join(lines)

    # ── Column rendering ─────────────────────────────────────────────

    def _render_column(self, col: ColumnDefinition) -> str:
        """Render a single column.

        Output format (column-level keywords md2pd recognizes):
        - ``**Type**:`` (always first)
        - ``**ReuseComponent**:`` if set
        - ``**Description**:``
        - ``**Units**:`` for quantified types
        - ``**Enumeration**:`` (bulleted list)
        - ``**Constraints**:`` (bulleted list of md2pd-supported keys only)
        - ``**Examples**:`` (comma-separated)
        - ``**Business Rules**:``
        - ``**Relationships**:``
        - ``**Semantic Links**:`` (bulleted list, one URI per line)
        """
        lines = [f"### {col.name}", ""]

        sdc4_type = resolve_sdc4_type(col.column_type.value)
        lines.append(f"**Type**: {sdc4_type}")

        if col.reuse_component:
            lines.append(f"**ReuseComponent**: {col.reuse_component}")

        if col.description:
            lines.append(f"**Description**: {col.description}")

        if col.units:
            lines.append(f"**Units**: {col.units}")

        if col.enumeration:
            lines.append(self._render_enumeration(col.enumeration))

        if col.constraints:
            constraint_block = self._render_constraints(col.constraints)
            if constraint_block:
                lines.append(constraint_block)

        if col.examples:
            lines.append(f"**Examples**: {', '.join(col.examples)}")

        if col.business_rules:
            lines.append(f"**Business Rules**: {col.business_rules}")

        if col.relationships:
            lines.append(f"**Relationships**: {col.relationships}")

        if col.semantic_links:
            lines.append("**Semantic Links**:")
            for uri in col.semantic_links:
                lines.append(f"  - {uri}")

        lines.append("")
        return "\n".join(lines)

    # ── Enumerations ─────────────────────────────────────────────────

    def _render_enumeration(self, items: list[EnumerationItem]) -> str:
        lines = ["**Enumeration**:"]
        for item in items:
            if item.description:
                lines.append(f"  - {item.value}: {item.description}")
            elif item.label and item.label != item.value:
                lines.append(f"  - {item.value}: {item.label}")
            else:
                lines.append(f"  - {item.value}")
        return "\n".join(lines)

    # ── Constraints ──────────────────────────────────────────────────

    def _render_constraints(self, c) -> str:
        """Render the ``**Constraints**:`` block.

        md2pd recognizes only ``required``, ``range`` (a two-element list),
        and ``precision``. Other constraint hints are intentionally dropped
        rather than emitted as flat keywords md2pd would silently ignore.

        ``min_value`` / ``max_value`` are folded into a single
        ``range: [min, max]`` line, with ``null`` for the unspecified end
        when only one bound is set.
        """
        items: list[str] = []

        if c.required is not None:
            items.append(
                f"  - required: {'true' if c.required else 'false'}"
            )

        if c.min_value is not None or c.max_value is not None:
            min_part = self._number_or_null(c.min_value)
            max_part = self._number_or_null(c.max_value)
            items.append(f"  - range: [{min_part}, {max_part}]")

        if c.precision is not None:
            items.append(f"  - precision: {c.precision}")

        if not items:
            return ""

        return "**Constraints**:\n" + "\n".join(items)

    # ── Helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _number_or_null(value: float | None) -> str:
        if value is None:
            return "null"
        # Render integer-valued floats without a trailing .0
        if float(value).is_integer():
            return str(int(value))
        return str(value)

    @staticmethod
    def _escape_yaml(value: str) -> str:
        """Escape double quotes and backslashes for double-quoted YAML scalars."""
        return value.replace("\\", "\\\\").replace('"', '\\"')
