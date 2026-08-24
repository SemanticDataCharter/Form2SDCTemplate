# Spec: make catalog reuse actually work

**Status:** ready to build. 2026-08-24.
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
