# Data Contracts

This is the single source of truth for the shapes of data passed between roles.
**Read this before writing code that produces or consumes data across a boundary.**
If you change a shape here, update this file in the same PR and tag the owner(s)
on the other side of the boundary for review.

Every contract below is a skeleton — fill in real field names/types as soon as
they're agreed, ideally in Week 1–2.

---

## Contract 0: manual policy-snippet extraction → `ml-model` (inference)

**Owner (producer):** Whole team, manual task

**Owner (consumer):** ML people

For each site in the starter set, a team member manually extracts the
cookie-related sections of that site's privacy policy (ctrl+F against a
predetermined keyword list) and records it in this format. This is separate
from OPP-115 training data (Contract 1) — this is real per-site input text
that the *already fine-tuned* model classifies at inference time.

```json
{
  "domain": "string",
  "policy_url": "string",
  "policy_version_or_accessed_date": "string",
  "extracted_by": "string",
  "keyword_matches": ["string"],
  "raw_text": "string"
}
```

Suggested storage: one row per site in a shared CSV/JSON file, e.g.
`data-processing/policy-snippets/`, committed to the repo so it's versioned
alongside everything else (these are just extracted text excerpts, not full
scraped policies — should be small enough to check in directly).

Open questions:
- [ ] Who maintains the keyword list, and where does it live?
- [ ] One combined text blob per site, or kept as separate matched snippets?

---

## Contract 1: `data-processing` → `ml-models`

**Owner (producer):** Data science people

**Owner (consumer):** ML people

Preprocessed OPP-115 segments, ready for model **training** (contrast with
Contract 0 above, which is real per-site text at **inference** time).

```json
{
  "segment_id": "string",
  "policy_id": "string",
  "text": "string",
  "labels": {
    "category": "string",          // e.g. "User choice/control"
    "attributes": {
      "purpose": "string | null",
      "does_or_does_not": "Does | Does Not | null",
      "entity": "string | null"   // e.g. "Third party"
    }
  }
}
```

Open questions to resolve early:
- [ ] How multi-label segments are represented
- [ ] Train/val/test split strategy and who owns it

---

## Contract 2: `ml-models` → `backend` (Postgres write)

**Owner (producer):** ML

**Owner (consumer):** Backend 

**Ingestion script owner:** Backend. ML people are only responsible for producing output in the JSON shape below — The backend people write and own the script that reads it and inserts it into Postgres.

```json
{
  "policy_id": "string",
  "domain": "string",
  "claims": [
    {
      "category": "string",
      "purpose": "string | null",
      "does_or_does_not": "Does | Does Not",
      "entity": "string | null",
      "confidence": 0.0
    }
  ]
}
```

Open questions:
- [ ] Batch write or streaming/per-policy?
- [ ] Confidence threshold for including a claim at all?

---

## Contract 3: cookie capture → `crosswalk`

**Owner (producer):** Frontend via `backend`

**Owner (consumer):** Tech lead

Observed cookies for a given site visit, matched against the Open Cookie
Database using **cookie name + the cookie's own setting domain together**. The website `domain` is separate: it's just the identifier for which site's policy this batch of cookies should be compared against; it plays no role in classifying any individual cookie.

```json
{
  "domain": "string",
  "visited_at": "ISO 8601 timestamp",
  "cookies": [
    {
      "name": "string",
      "known_vendor": "string | null",   // from Open Cookie Database match
      "category": "string | null"        // e.g. "Analytics", "Advertising"
    }
  ]
}
```

Open questions:
- [ ] Behavior when a cookie name isn't found in Open Cookie Database (unknown vendor)
- [ ] How categories here map to OPP-115 categories (this mapping *is* the crosswalk table)

---

## Contract 4: `backend` → `extension`

**Owner (producer):** Backend

**Owner (consumer):** Frontend

Final per-site comparison result served to the extension for display.

```json
{
  "domain": "string",
  "generated_at": "ISO 8601 timestamp",
  "quadrants": {
    "observed_disclosed": ["string"],
    "observed_undisclosed": ["string"],
    "not_observed_disclosed": ["string"],
    "not_observed_not_disclosed": ["string"]
  }
}
```

Note: quadrant entries are raw sanitized claim/observation strings only —
deliberately no `explanation` or `summary` field. See `SCOPE_DECISIONS.md`
("No natural-language explanation of comparison results"). The extension
renders these as a table; it does not interpret them for the user.

Open questions:
- [ ] Caching strategy — is this computed on-demand or pre-computed per site?
- [ ] What the extension shows when a domain has no policy on file yet