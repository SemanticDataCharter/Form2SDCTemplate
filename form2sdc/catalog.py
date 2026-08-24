"""
Look up reusable components in the public SDCStudio catalog.

Reuse is the whole economic argument for SDC: a component is authored once, by
someone who knows what it means, and every later model assembles it instead of
paying for it again. A generator blind to the catalog mints everything fresh,
which is the expensive path, incurred exactly where a newcomer forms their
impression of what SDC costs.

Three things this module is deliberate about.

**No authentication.** ``/api/v1/catalog/components/`` is public. A key only
raises the rate limit. Requiring an account to discover reuse would invert the
funnel, because reuse is what makes a first template cheap.

**Matched on type as well as name.** A field called "Weight" matches an
XdString named "Weight" as readily as the XdQuantity that is correct, and md2pd
rejects a template whose ReuseComponent points at the wrong type. A wrong-typed
suggestion is worse than none.

**Deterministic.** The match is assigned to ``ColumnDefinition.reuse_component``
directly. The template builder emits it verbatim. No second LLM round trip, and
no chance of the model declining to comply.
"""
from __future__ import annotations

import html
import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Iterable

from form2sdc.types import ColumnDefinition, FormAnalysis, resolve_sdc4_type

DEFAULT_CATALOG_URL = "https://sdcstudio.axius-sdc.com/api/v1/catalog/components/"

# md2pd has no cluster-level ReuseComponent: reuse is per column only. A Cluster
# from the catalog would parse as a column and fail validation.
UNUSABLE_TYPES = {"Cluster"}

# The server fixes its page size at 50 and ignores any ``page_size`` we send, so
# this is an observed constant rather than a request parameter. Confirmed
# against production 2026-08-24: asking for 100, 200 or 500 all return 50.
_SERVER_PAGE_SIZE = 50

# A search narrow enough to be useful returns well under one page. If a term is
# broad enough to exceed this many pages it is too broad to match confidently,
# and walking it costs requests for candidates we would reject anyway.
_MAX_PAGES = 3


@dataclass
class CatalogMatch:
    """One catalog component that can stand in for a column."""

    ct_id: str
    label: str
    component_type: str
    project_name: str
    reuse_ref: str
    description: str = ""
    units: str = ""


@dataclass
class ReuseReport:
    """What the lookup actually did, so it never fails silently."""

    matched: list[tuple[str, str]] = field(default_factory=list)   # (column, reuse_ref)
    unmatched: list[str] = field(default_factory=list)
    requests: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def available(self) -> bool:
        """
        False when the catalog could not be reached at all.

        Judged on errors against matches, never on ``unmatched``: a lookup that
        fails also leaves its column unmatched, so counting that as evidence of
        a working catalog reports an outage as a normal empty result.
        """
        return not (self.errors and not self.matched)

    def summary(self) -> str:
        lines = []
        if self.errors and not self.matched:
            lines.append("Catalog unavailable, so the template was built without reuse:")
            lines.extend(f"  {e}" for e in self.errors[:3])
            return "\n".join(lines)
        lines.append(
            f"Catalog: {len(self.matched)} field(s) matched, "
            f"{len(self.unmatched)} without a candidate, "
            f"in {self.requests} request(s)."
        )
        for name, ref in self.matched:
            lines.append(f"  reuse  {name}  ->  {ref}")
        if self.errors:
            lines.append(f"  {len(self.errors)} lookup(s) failed:")
            lines.extend(f"    {e}" for e in self.errors[:3])
        return "\n".join(lines)


def _normalize(text: str) -> str:
    """
    Lowercase, strip punctuation, collapse whitespace, for label comparison.

    Entities are unescaped first: some catalog labels carry them literally,
    e.g. "% &lt;poverty line Neighborhood PhenX". Without this, "<" normalizes
    to "lt" on one side and to nothing on the other, and the two never meet.
    Comparison only. ``reuse_ref`` is always emitted exactly as the server
    returned it.
    """
    keep = [c.lower() if (c.isalnum() or c.isspace()) else " " for c in html.unescape(text)]
    return " ".join("".join(keep).split())


class CatalogClient:
    """Reads the public component catalog. Authentication is optional."""

    def __init__(self, url: str = DEFAULT_CATALOG_URL, api_key: str | None = None,
                 timeout: int = 20):
        self._url = url
        self._api_key = api_key or None
        self._timeout = timeout
        self._cache: dict[tuple[str, str], list[CatalogMatch]] = {}
        self.requests = 0
        self.errors: list[str] = []

    def _fetch(self, params: dict) -> dict:
        req = urllib.request.Request(f"{self._url}?{urllib.parse.urlencode(params)}")
        if self._api_key:
            # Only to raise the rate limit, 200/hour anonymous to 2000/hour with
            # a key. The endpoint itself is AllowAny.
            req.add_header("Authorization", f"Token {self._api_key}")
        self.requests += 1
        with urllib.request.urlopen(req, timeout=self._timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def search(self, term: str, sdc4_type: str) -> list[CatalogMatch]:
        """
        Published, public components of one type whose label or description
        contains *term*.

        Searching per column rather than downloading each type whole is
        deliberate. The server pages at a fixed 50 and serializes the full
        queryset before slicing, so pulling all 1,551 XdStrings would cost 32
        requests and 32 full serializations, for one form. A search narrows to
        a handful: "Address" against XdString returns 42, and most terms return
        single digits.

        Results are cached on (term, type), so repeated field names across
        sections cost one request, not one per occurrence.
        """
        key = (_normalize(term), sdc4_type)
        if key in self._cache:
            return self._cache[key]
        if sdc4_type in UNUSABLE_TYPES or not term.strip():
            self._cache[key] = []
            return []

        found: list[CatalogMatch] = []
        try:
            page = 1
            while page <= _MAX_PAGES:
                payload = self._fetch({
                    "search": term,
                    "type": sdc4_type.lower(),
                    "page": page,
                })
                rows = payload.get("results", [])
                for r in rows:
                    if r.get("component_type") in UNUSABLE_TYPES:
                        continue
                    if not r.get("ct_id") or not r.get("reuse_ref"):
                        continue
                    found.append(CatalogMatch(
                        ct_id=r["ct_id"],
                        label=r.get("label", ""),
                        component_type=r.get("component_type", ""),
                        project_name=r.get("project_name", ""),
                        # Used verbatim. Rebuilding it from project_name and
                        # label is how the two drift: labels contain spaces and
                        # colons, e.g. "@Default:Address (Line 1)".
                        reuse_ref=r["reuse_ref"],
                        description=r.get("description", "") or "",
                        units=r.get("units", "") or "",
                    ))
                if len(rows) < _SERVER_PAGE_SIZE:
                    break
                page += 1
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError,
                json.JSONDecodeError, KeyError) as exc:
            # Never silently. A bare `except: pass` here is what let an empty
            # catalog look like a working one for weeks.
            self.errors.append(f"{term!r} ({sdc4_type}): {type(exc).__name__}: {exc}")

        self._cache[key] = found
        return found

    def best_match(self, column: ColumnDefinition) -> CatalogMatch | None:
        """
        The best catalog component for a column, or None.

        Type must agree exactly and the normalized label must match exactly.

        Partial matching was tried and removed. Treating a column name
        contained in a label as a match binds "Weight" to "Body Weight", and
        the column could as easily have been shipping weight. The bind is
        silent, it is emitted as a real ReuseComponent, and it survives into
        published data, so the cost of being wrong is far higher than the cost
        of minting a component that already exists somewhere. Exact is the only
        rule a name comparison can honestly defend.
        """
        # ``.value``, not ``str()``: ColumnType is a plain Enum, so str() gives
        # "ColumnType.DATE" and resolve_sdc4_type passes it through unchanged,
        # which silently makes every type comparison fail. Same access the
        # template builder uses.
        sdc4_type = resolve_sdc4_type(column.column_type.value)
        if sdc4_type in UNUSABLE_TYPES:
            return None

        target = _normalize(column.name)
        if not target:
            return None

        # The type filter is applied server side, but a mismatch here would
        # produce a template md2pd rejects, so it is re-checked rather than
        # trusted.
        candidates = [c for c in self.search(column.name, sdc4_type)
                      if c.component_type == sdc4_type]
        if not candidates:
            return None

        for c in candidates:
            if _normalize(c.label) == target:
                return c

        return None


def _all_columns(analysis: FormAnalysis) -> Iterable[ColumnDefinition]:
    """
    Every column that can carry a ReuseComponent.

    That is the Data and Workflow clusters plus the party sections. Attestation,
    Audit and Links have no reusable columns, and md2pd supports reuse only per
    column, never at section level.
    """
    for node in (analysis.data, analysis.workflow, analysis.subject, analysis.provider):
        if node is not None:
            yield from node.columns or []
    for party in analysis.participations or []:
        yield from party.columns or []


def apply_catalog_reuse(analysis: FormAnalysis, client: CatalogClient | None = None,
                        api_key: str | None = None) -> ReuseReport:
    """
    Set ``reuse_component`` on every column with a type-correct catalog match.

    Mutates the analysis in place and returns a report. The template builder
    emits ``**ReuseComponent**:`` for any column where this set a value, so no
    further prompting is needed.
    """
    client = client or CatalogClient(api_key=api_key)
    report = ReuseReport()

    for col in _all_columns(analysis):
        if col.reuse_component:
            continue  # already decided, do not overwrite
        match = client.best_match(col)
        if match is None:
            report.unmatched.append(col.name)
            continue
        col.reuse_component = match.reuse_ref
        report.matched.append((col.name, match.reuse_ref))

    report.requests = client.requests
    report.errors = list(client.errors)
    return report
