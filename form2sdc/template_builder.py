"""Template builder: converts FormAnalysis to SDC4 markdown string.

Pure Python, no LLM calls. Generates Form2SDCTemplate-compliant markdown
from structured FormAnalysis data.
"""

from __future__ import annotations

from form2sdc.types import (
    ClusterDefinition,
    ColumnDefinition,
    ColumnType,
    EnumerationItem,
    FormAnalysis,
    PartyDefinition,
    resolve_sdc4_type,
)


class TemplateBuilder:
    """Builds SDC4-compliant markdown templates from FormAnalysis objects."""

    def build(self, analysis: FormAnalysis) -> str:
        """Convert a FormAnalysis to a complete SDC4 markdown template.

        Args:
            analysis: Structured form analysis result.

        Returns:
            Complete markdown string ready for SDCStudio upload.
        """
        parts: list[str] = []

        parts.append(self._render_front_matter(analysis))
        parts.append(self._render_dataset_overview(analysis))

        # Subject / Provider / Participation (PART 3)
        if analysis.subject:
            parts.append(self._render_party(analysis.subject, "Subject"))
        if analysis.provider:
            parts.append(self._render_party(analysis.provider, "Provider"))
        if analysis.participations:
            for p in analysis.participations:
                parts.append(self._render_party(p, "Participation"))

        # Root cluster and columns (PARTs 4-5)
        parts.append(self._render_cluster(analysis.root_cluster, level=2))

        # Sub-clusters (PART 9)
        for sub in analysis.root_cluster.sub_clusters:
            parts.append(self._render_sub_cluster(sub))

        return "\n".join(parts)

    # ── PART 1: YAML Front Matter ────────────────────────────────────

    def _render_front_matter(self, analysis: FormAnalysis) -> str:
        lines = ["---"]
        lines.append(f'project_name: "{analysis.dataset_name}"')
        lines.append(f'source_language: "{analysis.source_language}"')
        lines.append('template_version: "4.0.0"')

        if analysis.dataset_description:
            # Escape quotes in description
            desc = analysis.dataset_description.replace('"', '\\"')
            lines.append(f'description: "{desc}"')
        if analysis.creator:
            lines.append(f'author: "{analysis.creator}"')
        if analysis.domain:
            lines.append(f'domain: "{analysis.domain}"')

        lines.append("---")
        return "\n".join(lines)

    # ── PART 2: Dataset Overview ─────────────────────────────────────

    def _render_dataset_overview(self, analysis: FormAnalysis) -> str:
        lines = [""]

        if analysis.dataset_description:
            lines.append(f"<!-- Dataset: {analysis.dataset_name} -->")
            lines.append("")
            lines.append(analysis.dataset_description)
            lines.append("")

        if analysis.purpose:
            lines.append(f"<!-- Purpose: {analysis.purpose} -->")
            lines.append("")

        if analysis.business_context or analysis.primary_use:
            lines.append("<!-- Business Context:")
            if analysis.primary_use:
                lines.append(f"  Primary use: {analysis.primary_use}")
            if analysis.secondary_use:
                lines.append(f"  Secondary use: {analysis.secondary_use}")
            if analysis.stakeholders:
                lines.append(f"  Stakeholders: {analysis.stakeholders}")
            lines.append("-->")
            lines.append("")

        return "\n".join(lines)

    # ── PART 3: Party sections ───────────────────────────────────────

    def _render_party(self, party: PartyDefinition, section_type: str) -> str:
        lines = [f"## {section_type}: {party.name}", ""]

        if party.description:
            lines.append(f"**Description**: {party.description}")
            lines.append("")

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
            if party.function or party.mode:
                lines.append("")

        for col in party.columns:
            lines.append(self._render_column(col, level=3))

        return "\n".join(lines)

    # ── PARTs 4-5: Root Cluster + Columns ────────────────────────────

    def _render_cluster(
        self, cluster: ClusterDefinition, level: int = 2
    ) -> str:
        hashes = "#" * level
        lines = [f"{hashes} {cluster.name}", ""]
        lines.append("**Type**: Cluster")

        if cluster.description:
            lines.append(f"**Description**: {cluster.description}")

        if cluster.purpose:
            lines.append(f"**Purpose**: {cluster.purpose}")

        if cluster.business_context:
            lines.append(f"**Business Context**: {cluster.business_context}")

        if cluster.constraints and cluster.constraints.cardinality:
            lines.append(f"**Cardinality**: {cluster.constraints.cardinality}")

        lines.append("")

        for col in cluster.columns:
            lines.append(self._render_column(col, level=level + 1))

        return "\n".join(lines)

    def _render_column(self, col: ColumnDefinition, level: int = 3) -> str:
        hashes = "#" * level
        lines = [f"{hashes} {col.name}", ""]

        # Type (mapped to SDC4) — always first
        sdc4_type = resolve_sdc4_type(col.column_type.value)
        lines.append(f"**Type**: {sdc4_type}")

        # Reuse component reference (after Type)
        if col.reuse_component:
            lines.append(f"**ReuseComponent**: {col.reuse_component}")

        # Description
        if col.description:
            lines.append(f"**Description**: {col.description}")

        # Units (for quantified types)
        if col.units:
            lines.append(f"**Units**: {col.units}")

        # Enumeration (PART 7)
        if col.enumeration:
            lines.append(self._render_enumeration(col.enumeration))

        # Constraints (PART 8)
        if col.constraints:
            lines.extend(self._render_constraints(col.constraints, sdc4_type))

        # Examples
        if col.examples:
            lines.append(f"**Examples**: {', '.join(col.examples)}")

        # Business Rules
        if col.business_rules:
            lines.append(f"**Business Rules**: {col.business_rules}")

        # Relationships
        if col.relationships:
            lines.append(f"**Relationships**: {col.relationships}")

        # Semantic Links
        if col.semantic_links:
            lines.append(
                f"**Semantic Links**: {', '.join(col.semantic_links)}"
            )

        lines.append("")
        return "\n".join(lines)

    # ── PART 7: Enumerations ─────────────────────────────────────────

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

    # ── PART 8: Constraints ──────────────────────────────────────────

    def _render_constraints(
        self, c, sdc4_type: str
    ) -> list[str]:
        lines: list[str] = []

        if c.pattern:
            lines.append(f"**Pattern**: {c.pattern}")
        if c.min_length is not None:
            lines.append(f"**Min Length**: {c.min_length}")
        if c.max_length is not None:
            lines.append(f"**Max Length**: {c.max_length}")
        if c.min_value is not None:
            lines.append(f"**Min Magnitude**: {c.min_value}")
        if c.max_value is not None:
            lines.append(f"**Max Magnitude**: {c.max_value}")
        if c.precision is not None:
            lines.append(f"**Precision**: {c.precision}")
        if c.fraction_digits is not None:
            lines.append(f"**Fraction Digits**: {c.fraction_digits}")
        if c.temporal_type:
            lines.append(f"**Temporal Type**: {c.temporal_type}")
        if c.min_date:
            lines.append(f"**Min Date**: {c.min_date}")
        if c.max_date:
            lines.append(f"**Max Date**: {c.max_date}")
        if c.default_value is not None:
            lines.append(f"**Default Value**: {c.default_value}")
        if c.media_types:
            lines.append(f"**Media Types**: {', '.join(c.media_types)}")
        if c.max_size:
            lines.append(f"**Max Size**: {c.max_size}")

        # Render general constraints block if needed
        constraint_items: list[str] = []
        if c.required is not None:
            constraint_items.append(
                f"  - required: {'true' if c.required else 'false'}"
            )
        if c.unique is not None and c.unique:
            constraint_items.append("  - unique: true")
        if c.format:
            constraint_items.append(f'  - format: "{c.format}"')

        if constraint_items:
            lines.append("**Constraints**:")
            lines.extend(constraint_items)

        return lines

    # ── PART 9: Sub-Clusters ─────────────────────────────────────────

    def _render_sub_cluster(self, cluster: ClusterDefinition) -> str:
        lines = [f"## Sub-Cluster: {cluster.name}", ""]

        if cluster.description:
            lines.append(cluster.description)
            lines.append("")

        if cluster.purpose:
            lines.append(f"**Purpose**: {cluster.purpose}")
        if cluster.parent:
            lines.append(f"**Parent**: {cluster.parent}")
        if cluster.business_context:
            lines.append(f"**Business Context**: {cluster.business_context}")

        lines.append("**Type**: Cluster")
        lines.append("")

        for col in cluster.columns:
            lines.append(self._render_column(col, level=3))

        # Nested sub-clusters
        for sub in cluster.sub_clusters:
            lines.append(self._render_sub_cluster(sub))

        return "\n".join(lines)
