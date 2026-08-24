# Spec: make catalog reuse actually work

**Status:** BUILT, 2026-08-24. See "What actually happened" at the end.
**Scope:** the Colab notebook and `form2sdc`. One server-side prerequisite, already fixed.

---

## The situation

**Catalog reuse is already built.** Cell 5 of `notebooks/form_to_template.ipynb` queries the SDCStudio component catalog, dedupes by `ct_id`, correctly skips `Cluster` types (md2pd has no cluster-level `ReuseComponent`), and feeds the matches to Gemini as context so it emits `**ReuseComponent**:` instead of inventing a component.

**It has never returned a single result.** Three independent reasons, none of them the notebook's logic.

---

## Why it produced nothing

### 1. The endpoint was broken. ✅ Fixed 2026-08-24

`/api/v1/catalog/components/` answered every query with `{"count": 0, "results": []}` while the database held thousands of published, public components.

`CatalogComponentSerializer` asked `PredObj` for `ct_id` and `label`, neither of which exists, so serialization raised `AttributeError` on the first row of every component type. The view wrapped each model query in a bare `except` that logged a warning and continued, turning a total crash into a `200` with an empty list.

Fixed in SDCStudio (`2ae2056c`): `PredObj` removed from the public payload entirely, and a wholly failed catalog now returns `503` rather than looking empty. **Locally the endpoint now returns 1,349 components.** Nothing in this spec works until that reaches production.

### 2. It is gated behind an API key it does not need

The whole feature sits behind `if sdcstudio_key:`, and cell 3 tells the user to create an account and generate a key.

**The catalog endpoint is `AllowAny`.** It requires no authentication at all. Anonymous callers get a lower rate limit; that is the only difference.

Gating on a key throws away the property that makes this tool worth having: a stranger with a PDF and a Google API key gets a template without an SDCStudio account, without an install, and without spending credits. Requiring a login to *discover reuse* inverts the funnel, because reuse is exactly what makes a first template cheap.

### 3. It searches by name only, never by type

`form2sdc` already infers an SDC4 type per column (`ColumnDefinition`, `resolve_sdc4_type`). The catalog already accepts `?type=xdquantity`. The notebook uses neither together: it sends `?search=<field name>` alone.

So a field called "Weight" matches an `XdString` named "Weight" as readily as the `XdQuantity` that is actually correct, and a wrong-typed suggestion is worse than none, because `md2pd` will reject the template at parse time.

---

## What to build

### A. Drop the API key requirement

- Run the catalog search **unconditionally**.
- Keep `sdcstudio_key` as an optional input, sent when present, for the higher rate limit only.
- Rewrite cell 3: reuse works for everyone; a key raises your rate limit.

### B. Filter by the inferred type

For each column, query with **both** parameters:

```
GET /api/v1/catalog/components/?search=<term>&type=<inferred type, lowercased>
```

Accept a match only when `component_type` equals the inferred type. A name match at the wrong type is a rejected template, not a helpful suggestion.

Keep the existing `Cluster` skip. It is correct and the reason is worth preserving in a comment.

### C. Use `reuse_ref` verbatim

The catalog returns the exact string the template syntax wants:

```json
{ "ct_id": "…", "label": "BMI", "component_type": "XdQuantity",
  "project_name": "NIH_CDE", "reuse_ref": "@NIH_CDE:BMI", "units": "kg/m2" }
```

`reuse_ref` is already `@Project:Label`, the recommended `**ReuseComponent**:` form. **Do not rebuild it from `project_name` and `label`** — labels contain colons and spaces (`@Default:Address (Line 1)`), and reconstructing it locally is how the two drift.

### D. Batch the queries

One request per field is slow and burns the anonymous rate limit on a wide form. Query once per **distinct inferred type**, cache the results, and match locally. A 60-field form drops from 60 requests to at most a dozen.

> **Superseded during the build.** This assumed the client can choose `page_size`. It cannot: the server hardcodes `page_size = 50` and ignores the parameter. Pulling one type whole costs 32 requests for XdString alone and ~135 for the catalog, and the view serializes the *entire* queryset before slicing in Python, so each of those is a full serialization of 1,551 rows.
>
> Built instead as **one request per distinct (field name, type) pair**, cached, which is item B applied per column. Search narrows hard enough that this is cheaper than the batch for any real form: "Address" against XdString returns 42 rows, most terms return single digits.

### E. Report what happened

Print a short summary: fields matched, fields with no candidate, and any rate-limit or network failure. The current handler is `except Exception: pass`, which is the same silence that hid the server bug for weeks. **Never let this fail invisibly.**

---

## Acceptance

1. A form converted **without** any SDCStudio key emits at least one `**ReuseComponent**: @Project:Label` when a published component of the matching type exists.
2. No suggestion is ever emitted whose `component_type` differs from the column's inferred type.
3. The generated template passes `form2sdc.validator` and parses in `md2pd`.
4. With the catalog unreachable, generation still succeeds without reuse, and says so out loud.
5. A wide form issues one request per distinct type, not one per field.

---

## Why this matters more than it looks

`design_docs/design-time-cost-of-binding.md` in SDCStudio put numbers on it: platform charges are under 0.5% of design-time cost, expert time is effectively all of it, and **that cost amortizes only through reuse**. A generator blind to the catalog mints every component fresh, which is the expensive path, incurred at the exact moment a newcomer forms their impression of what SDC costs.

The whole change is a query parameter, a removed conditional, and a cache.

---

## Out of scope

**Do not turn this into an SDCStudio API client.** The value here is the zero-friction on-ramp: no account, no install, no credits, and the `Form2SDCTemplate.md` path still works with any LLM including a local one in an air-gapped setting. SDCBench and SDC_Agents already serve the authenticated, installed case. This tool should remain the one that asks for nothing.

---

## What actually happened

Built and verified against production on 2026-08-24. Two of the five items rested on assumptions that did not survive contact with the running server.

**The zero-results cause was mine, not the server's.** With the server fix deployed, the first end-to-end run still matched nothing. Two client bugs:

1. `str(column.column_type)` returns `"ColumnType.DATE"`, not `"date"`. `ColumnType` is a `(str, Enum)` mixin, so `__str__` comes from `Enum`. `resolve_sdc4_type` passed the unrecognized string through unchanged and every type comparison failed silently. `TemplateBuilder` already used `.value`; the fix was to match it.
2. Pagination looped `while len(rows) < requested_page_size`, and the server caps `page_size` at 50 regardless of what is asked, so the loop exited after the first page and only ever saw the first 50 labels alphabetically. "Date of Birth" is in the catalog as an XdTemporal and was simply never reached.

**Partial matching was implemented, then removed.** Accepting a column name contained in a catalog label bound a column named "Weight" to a component named "Body Weight". The column could as easily have been shipping weight. The bind is silent, is emitted as a genuine `ReuseComponent`, and survives into published data, so it costs more than minting a duplicate. Matching is now exact normalized label plus exact type. A test pins this.

**Item E paid for itself immediately.** `ReuseReport.available` initially read `not (errors and not matched and not unmatched)`, which reported an unreachable catalog as available, because a failed lookup also leaves its column unmatched. Caught by the acceptance-4 test, not by inspection.

### Acceptance, as verified

| # | Criterion | Result |
|---|---|---|
| 1 | Reuse emitted with no API key | Pass. `@Default:Address (Line 1)` and `@NIH_CDE:Date of Birth`, anonymous. |
| 2 | Never a type mismatch | Pass. Type checked server-side and re-checked client-side; test pinned. |
| 3 | Passes `form2sdc.validator` and parses in md2pd | Pass. `valid=True`; md2pd `parse()` resolved both references with zero errors and zero warnings. |
| 4 | Unreachable catalog still generates, and says so | Pass. Test asserts generation continues, `available` is False, and the summary says why. |
| 5 | One request per distinct type, not per field | Adapted, see item D. One per distinct (name, type), cached; test asserts a repeated field name costs one request. |

### Server side, fixed separately

`catalog_components_view` serialized the full queryset before slicing, so every page request serialized all matching rows and discarded all but 50, and it had an N+1 on `units` because only `project` was `select_related`. Fixed in SDCStudio (`362e8255`): paging now happens in the database, `page_size` is client-controllable up to 200, and a 28-row XdQuantity page went from 29 queries to 2.

The client does **not** depend on that deploy. It asks for `page_size=200` and stops on the `count` the response reports, so it is correct whether the server honours the parameter or caps it at 50.
