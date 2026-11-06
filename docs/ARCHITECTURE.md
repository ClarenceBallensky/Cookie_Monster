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
  OPP-115 dataset ──► data-processing            ──► fine-tune 
                      preprocessing,                 attribute extractor
                      segment/attribute labels       

Inference time, per site:
Site's privacy policy ──► script extracts ──► fine-tuned model
                          cookie-related 
                          snippets                          │                                  
                                                            ▼
                                                   structured policy claims
                                                            │
                                                            ▼
                                                        PostgreSQL
                                                      (via backend)

Open Cookie Database ──► cookie/vendor lookup table ──► PostgreSQL
```

## Where the crosswalk fits

The crosswalk sits at the comparison step: it takes the
**observed cookies** (classified by vendor/category from the Open Cookie
Database) and the **disclosed claims** (classified by category/attribute from
the fine-tuned OPP-115 model), maps the two category vocabularies onto each
other, and produces the four-quadrant result.

```
observed cookies (attributes)  ──┐
                                 ├──► comaprison logic ──► crosswalk table ──► four-quadrant result
disclosed claims (attributes)  ──┘        
```

See [`DATA_CONTRACTS.md`](DATA_CONTRACTS.md) for the exact schemas at each
arrow above.
