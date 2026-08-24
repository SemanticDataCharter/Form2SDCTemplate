"""
Tests for catalog-driven component reuse.

No network. ``FakeClient`` replaces :meth:`CatalogClient._fetch` with canned
pages, so pagination, type filtering and error handling are all exercised
against the real client code rather than a mock of it.

The shape of the canned rows mirrors production exactly, including the
HTML-escaped label, which is a real row in the catalog and the reason
``_normalize`` unescapes before comparing.
"""
import urllib.error

from form2sdc.catalog import CatalogClient, _normalize, apply_catalog_reuse
from form2sdc.types import (
    ClusterDefinition,
    ColumnDefinition,
    FormAnalysis,
    PartyDefinition,
)


def row(label, ctype, project="Default", **kw):
    return {
        "ct_id": kw.get("ct_id", f"ct_{label.lower().replace(' ', '_')}"),
        "label": label,
        "description": kw.get("description", ""),
        "component_type": ctype,
        "project_name": project,
        "reuse_ref": f"@{project}:{label}",
        "units": kw.get("units", ""),
    }


class FakeClient(CatalogClient):
    """CatalogClient with the HTTP call replaced by a canned corpus."""

    def __init__(self, corpus, fail=False, **kw):
        super().__init__(**kw)
        self._corpus = corpus
        self._fail = fail
        self.calls = []

    def _fetch(self, params):
        self.requests += 1
        self.calls.append(params)
        if self._fail:
            raise urllib.error.URLError("connection refused")
        term = params["search"].lower()
        want = params["type"]
        hits = [r for r in self._corpus
                if r["component_type"].lower() == want
                and (term in r["label"].lower() or term in r["description"].lower())]
        page = params.get("page", 1)
        start = (page - 1) * 50
        return {"count": len(hits), "page": page, "page_size": 50,
                "results": hits[start:start + 50]}


CORPUS = [
    row("Date of Birth", "XdTemporal", "NIH_CDE"),
    row("Birth Date", "XdTemporal", "NIH_CDE"),
    row("Address (Line 1)", "XdString"),
    row("Address (Line 2)", "XdString"),
    row("Weight", "XdString", "Wrong"),          # right name, wrong type
    row("Body Weight", "XdQuantity", "NIH_CDE", units="kg"),
    row("% &lt;poverty line Neighborhood PhenX", "XdCount", "NIH_CDE"),
    row("Consent Cluster", "Cluster", "NIH_CDE"),
]


def analysis_with(*columns, **sections):
    return FormAnalysis(
        dataset_name="Test",
        dataset_description="Fixture.",
        data=ClusterDefinition(name="Data", description="", columns=list(columns)),
        **sections,
    )


def col(name, ctype="text"):
    return ColumnDefinition(name=name, column_type=ctype, description="")


# ── _normalize ───────────────────────────────────────────────────────


def test_normalize_collapses_punctuation_and_case():
    assert _normalize("Address (Line 1)") == "address line 1"


def test_normalize_unescapes_entities_before_comparing():
    """Catalog labels carry literal entities; both sides must land the same."""
    assert _normalize("% &lt;poverty line") == _normalize("% <poverty line")


# ── best_match ───────────────────────────────────────────────────────


def test_exact_label_match_is_returned():
    c = FakeClient(CORPUS)
    m = c.best_match(col("Date of Birth", "date"))
    assert m is not None
    assert m.label == "Date of Birth"
    assert m.reuse_ref == "@NIH_CDE:Date of Birth"


def test_wrong_type_is_never_matched():
    """"Weight" exists as XdString, but a text column of that name is XdString.

    The XdString "Weight" lives in project "Wrong"; a decimal column resolves
    to XdQuantity and must not reach it. Accepting a cross-type name match
    produces a template md2pd rejects at parse time.
    """
    c = FakeClient(CORPUS)
    m = c.best_match(col("Weight", "text"))
    assert m is not None and m.component_type == "XdString"
    assert c.best_match(col("Weight", "decimal")) is None


def test_partial_name_never_matches():
    """"Address" appears in two labels and is not itself a component."""
    c = FakeClient(CORPUS)
    assert c.best_match(col("Address", "text")) is None


def test_generic_name_does_not_absorb_a_specific_component():
    """"Weight" must not bind to "Body Weight"; it could be shipping weight.

    Containment matching was removed for exactly this case. The bind would be
    silent, emitted as a real ReuseComponent, and would survive into published
    data.
    """
    c = FakeClient(CORPUS)
    assert c.best_match(col("Weight", "decimal")) is None


def test_exact_match_on_a_specific_label_is_accepted():
    c = FakeClient(CORPUS)
    m = c.best_match(col("Body Weight", "decimal"))
    assert m is not None and m.reuse_ref == "@NIH_CDE:Body Weight"


def test_unknown_field_matches_nothing():
    c = FakeClient(CORPUS)
    assert c.best_match(col("Wholly Invented Field")) is None


def test_cluster_components_are_never_returned():
    """md2pd has no cluster-level ReuseComponent; a Cluster would fail parse."""
    c = FakeClient(CORPUS)
    assert c.search("Consent Cluster", "Cluster") == []


# ── apply_catalog_reuse ──────────────────────────────────────────────


def test_sets_reuse_component_and_reports():
    a = analysis_with(col("Date of Birth", "date"), col("Nothing Here"))
    report = apply_catalog_reuse(a, client=FakeClient(CORPUS))

    assert a.data.columns[0].reuse_component == "@NIH_CDE:Date of Birth"
    assert a.data.columns[1].reuse_component in (None, "")
    assert report.matched == [("Date of Birth", "@NIH_CDE:Date of Birth")]
    assert report.unmatched == ["Nothing Here"]
    assert report.available


def test_existing_reuse_component_is_not_overwritten():
    c = col("Date of Birth", "date")
    c.reuse_component = "@Mine:Something Deliberate"
    apply_catalog_reuse(analysis_with(c), client=FakeClient(CORPUS))
    assert c.reuse_component == "@Mine:Something Deliberate"


def test_all_party_sections_are_traversed():
    """Reuse must reach Workflow and the party sections, not just Data."""
    a = analysis_with(
        col("Address (Line 1)"),
        workflow=ClusterDefinition(name="W", description="",
                                   columns=[col("Birth Date", "date")]),
        subject=PartyDefinition(name="S", party_type="subject",
                                columns=[col("Body Weight", "decimal")]),
        participations=[PartyDefinition(name="P", party_type="participation",
                                        columns=[col("Address (Line 2)")])],
    )
    report = apply_catalog_reuse(a, client=FakeClient(CORPUS))
    assert len(report.matched) == 4
    assert a.workflow.columns[0].reuse_component == "@NIH_CDE:Birth Date"
    assert a.subject.columns[0].reuse_component == "@NIH_CDE:Body Weight"
    assert a.participations[0].columns[0].reuse_component == "@Default:Address (Line 2)"


def test_repeated_field_names_are_cached_not_refetched():
    """Acceptance 5: one request per distinct (term, type), not per field."""
    a = analysis_with(
        col("Date of Birth", "date"),
        workflow=ClusterDefinition(name="W", description="",
                                   columns=[col("Date of Birth", "date")]),
    )
    client = FakeClient(CORPUS)
    report = apply_catalog_reuse(a, client=client)
    assert report.requests == 1
    assert len(report.matched) == 2


# ── failure is never silent ──────────────────────────────────────────


def test_unreachable_catalog_still_builds_and_says_so():
    """Acceptance 4. A bare `except: pass` here hid a server bug for weeks."""
    a = analysis_with(col("Date of Birth", "date"))
    report = apply_catalog_reuse(a, client=FakeClient(CORPUS, fail=True))

    assert a.data.columns[0].reuse_component in (None, "")   # generation continues
    assert report.errors                                      # and is reported
    assert not report.available
    assert "Catalog unavailable" in report.summary()


def test_summary_names_matches_when_catalog_works():
    a = analysis_with(col("Date of Birth", "date"))
    report = apply_catalog_reuse(a, client=FakeClient(CORPUS))
    assert "@NIH_CDE:Date of Birth" in report.summary()


def test_api_key_is_sent_only_when_present():
    assert CatalogClient(api_key=None)._api_key is None
    assert CatalogClient(api_key="")._api_key is None
    assert CatalogClient(api_key="abc")._api_key == "abc"


# ── round trip into the template ─────────────────────────────────────


def test_builder_emits_reuse_reference_verbatim():
    """The reuse_ref must survive into the markdown unaltered.

    md2pd resolves it with an exact ``label=`` lookup, so any reconstruction
    or re-escaping on our side breaks the resolution.
    """
    from form2sdc.template_builder import TemplateBuilder

    a = analysis_with(col("Address (Line 1)"))
    apply_catalog_reuse(a, client=FakeClient(CORPUS))
    md = TemplateBuilder().build(a)

    assert "**ReuseComponent**: @Default:Address (Line 1)" in md


def test_generated_template_still_validates():
    from form2sdc.template_builder import TemplateBuilder
    from form2sdc.validator import Form2SDCValidator

    a = analysis_with(col("Address (Line 1)"), col("Date of Birth", "date"))
    apply_catalog_reuse(a, client=FakeClient(CORPUS))
    result = Form2SDCValidator().validate(TemplateBuilder().build(a))

    assert result.valid, [e.message for e in result.errors]
