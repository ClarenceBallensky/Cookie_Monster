# Architecture Overview

## High-level flow

```
┌──────────────────┐
│ Firefox          │  1. User visits a site
│ Extension        │  2. Captures cookies via chrome.cookies.getAll()/webRequest
│ Frontend         │  3. Looks up each cookie by NAME + its own setting
│                  │     domain against the Open Cookie Database to
│                  │     determine what it's actually used for
│                  │  4. Sends the classified cookies + the site's policy
│                  │     to compare against to the backend
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ FastAPI Backend  │  5. Fetches that site's pre-analyzed policy claims (Postgres)
│ Backend          │  6. Runs crosswalk comparison logic
│                  │  7. Returns four-quadrant result to extension
└────────┬─────────┘
         │
         ▼ (reads from / writes to)
┌──────────────────┐
│ PostgreSQL       │  Stores: policy claims, cookie/vendor lookups,
│                  │  per-site comparison results
└──────────────────┘
```

Cookie classification (step 3) matches on **cookie name + the cookie's own
setting domain** (e.g. `.doubleclick.net`). Open Cookie
Database entries are keyed by name and domain together, since common cookie
names (`session`, `id`, `token`) are reused across unrelated vendors and
sites. 

## Offline pipeline (feeds Postgres ahead of time)

Two separate paths feed the same fine-tuned model — one at **training** time,
one at **inference** time, per site:

```
Training time:
  OPP-115 dataset ──► data-processing              ──► fine-tune category filter
                      preprocessing,                   + attribute extractor
                      segment/attribute labels       

Inference time, per site (MVP: manual extraction):
Site's privacy policy ──► team manually extracts ──► fine-tuned model
                          cookie-related sections     
                          (ctrl+F, keyword list)                 │
                                                                 ▼
                                                   structured policy claims
                                                                 │
                                                                 ▼
                                                            PostgreSQL
                                                         (via backend)

Open Cookie Database ──► cookie/vendor lookup table ──► PostgreSQL
```

Note: the manual extraction step means the model never sees a full privacy
policy — only the pre-isolated cookie-related excerpt. Automating that
isolation step (so a URL alone is enough) is a stretch goal, not MVP.

## Where the crosswalk fits

The crosswalk sits at the comparison step: it takes the
**observed cookies** (classified by vendor/category from the Open Cookie
Database) and the **disclosed claims** (classified by category/attribute from
the fine-tuned OPP-115 model), maps the two category vocabularies onto each
other, and produces the four-quadrant result.

```
observed cookies (categories)  ──┐
                                   ├──► crosswalk table ──► four-quadrant result
disclosed claims (categories)  ──┘        + comparison
                                             logic
```

See [`DATA_CONTRACTS.md`](DATA_CONTRACTS.md) for the exact schemas at each
arrow above.

## Key architectural decisions
- **Cookie classification matches on name + cookie's own domain**: each
  cookie is looked up against the Open Cookie Database using **both** its
  name and the domain that set it, not name alone — the database's own
  entries are keyed that way, since common cookie names get reused across
  unrelated vendors. This "cookie domain" (from `chrome.cookies.getAll()`)
  is distinct from the site/page domain, which is only used to select which
  privacy policy to compare against. Domain-based tracker lists (matching by
  which domain a cookie came from when the name itself is unrecognized, e.g.
  DuckDuckGo Tracker Radar) remain a separate stretch goal.
- **Live capture, not static comparison**: the extension captures real
  cookie activity per visit rather than comparing two pre-built datasets —
  this is the core value proposition.
- **Manual, not automated, policy-section extraction (MVP)**: the team
  manually identifies cookie-related sections of each site's privacy policy
  rather than parsing full policies automatically. This keeps model error
  isolated to the classification step while the pipeline is being proven out.
