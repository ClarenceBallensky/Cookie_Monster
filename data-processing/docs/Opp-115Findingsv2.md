# OPP-115 Corpus — Findings Summary

**Prepared for team discussion | Full corpus run: 115/115 policies, 3,792 segments, 146,926 attribute rows, 23,194 unique data practices**

---

## 1. What the corpus is

OPP-115 is 115 annotated website privacy policies from Carnegie Mellon's Usable Privacy Policy Project. Each policy is split into segments (roughly paragraph-length), and three annotators independently labeled each segment with zero or more "data practices." A data practice consists of:
- a **category** (one of 10)
- a set of **attribute-value pairs** specific to that category
- optional **text spans** showing where in the segment the annotator found evidence

---

## 2. The 10 categories

| Category | What it captures |
|---|---|
| First Party Collection/Use | What the company itself collects and how it's used |
| Third Party Sharing/Collection | Data shared with or collected by outside entities |
| User Choice/Control | Opt-outs, cookie preferences, tracking limits |
| Data Retention | How long data is kept |
| Data Security | How data is protected |
| Policy Change | Notification of policy updates |
| Do Not Track | Whether/how DNT signals are honored |
| International and Specific Audiences | Rules for children, EU users, CA residents, etc. |
| User Access, Edit and Deletion | User rights to view/correct/delete their data |
| Other | Catch-all: intros, boilerplate, contact info |

"Do Not Track" is rare corpus-wide (90 of 23,194 practices, 0.4%) — easy to miss when sampling only a few files.

---

## 3. Category distribution, corpus-wide

Counted by **unique data practice** (not by exploded attribute row — see Appendix A for why this matters):

| Category | Count | Share |
|---|---|---|
| First Party Collection/Use | 8,935 | 38.5% |
| Third Party Sharing/Collection | 5,221 | 22.5% |
| Other | 3,548 | 15.3% |
| User Choice/Control | 1,789 | 7.7% |
| Data Security | 1,008 | 4.4% |
| International and Specific Audiences | 939 | 4.1% |
| User Access, Edit and Deletion | 746 | 3.2% |
| Policy Change | 548 | 2.4% |
| Data Retention | 370 | 1.6% |
| Do Not Track | 90 | 0.4% |

*See attached chart: `category_distribution_full_corpus.png`*

**Takeaway:** First Party and Third Party dominate. "Other" is larger than expected (3rd highest) — flagged as an open question below.

---

## 4. Contract 1 schema — mapping and coverage

Contract 1 specifies three target fields per record: `purpose`, `does_or_does_not`, `entity`.

| Category | → purpose | → does_or_does_not | → entity | Match quality |
|---|---|---|---|---|
| First Party Collection/Use | Purpose | Does/Does Not | (implied: first party; no direct attribute) | Direct match |
| Third Party Sharing/Collection | Purpose | Does/Does Not | Third Party Entity | Direct match |
| User Choice/Control | Purpose | Choice Type (see note) | No direct attribute | Partial match |
| Data Retention | Retention Purpose (close, not exact) | No direct attribute | No direct attribute | Partial match |
| All other categories (6) | No direct attribute | No direct attribute | No direct attribute | No match |

**Note on the Partial match row:** `Choice Type` describes the *mechanism* of a user choice (opt-in, opt-out), not whether a practice occurs — it's a softer match and probably shouldn't be treated as equivalent to `does_or_does_not` without discussion.

### What "mapped vs. unmapped" actually measures

This is about **categories**, not individual field values. It asks: does this practice's category even have attributes corresponding to Contract 1's schema? Only First Party and Third Party qualify as a full match.

> **61.0% of all data practices** (14,156 of 23,194) fall into a category Contract 1 can fully populate. The remaining **39.0%** (9,038 practices) belong to categories — Data Security, Do Not Track, Policy Change, etc. — that don't have a `Purpose` or `Does/Does Not` field at all. This is a structural gap, not a data quality issue.

*See attached chart: `mapped_vs_unmapped.png`*

---

## 5. Field reliability within the mapped categories

Even among the 61% that structurally qualifies, the three target fields are not equally reliable:

| Attribute | Rows | % Specified (real value) | % Unspecified | % not-selected |
|---|---|---|---|---|
| Purpose | 15,945 | 71.7% | 28.3% | 0.0% |
| Does/Does Not | 14,156 | 100% | 0.0% | 0.0% |
| Third Party Entity | 5,221 | 88.8% | 11.2% | 0.0% |

*See attached charts: `purpose_value_breakdown.png`, `does_does_not_split.png`, `top_third_party_entities.png`, `target_fields_reliability.png`*

**Note:** `Purpose`'s row count (15,945) exceeds the mapped-category count (14,156) — at least one additional category (likely User Choice/Control) also uses a `Purpose` attribute. Needs confirmation before treating "Purpose" as exclusive to First/Third Party.

**What "Unspecified" means, precisely:** it does NOT mean the practice fell outside First/Third Party into some other category. It means the annotation is already inside a category that has this attribute, but the policy's own text didn't clearly state the value. "Unspecified" is an annotator's answer, not an absence of the field. Six real examples below illustrate this directly.

---

## 6. Real examples — what "Specified" vs. "Unspecified" actually look like in the text

| Field | Case | Value | Highlighted text | Segment excerpt |
|---|---|---|---|---|
| Purpose | Specified | Basic service/feature | "other purposes, for example when you report a problem with our site" | "...we may also ask you for information for other purposes, for example when you report a problem with our site" |
| Purpose | Unspecified | Unspecified | *(none selected)* | "...details of your visits to our site including, but not limited to, traffic data, location data, weblogs and other communication data." |
| Does/Does Not | Does | Does | *(none selected — confirmed from context)* | "Sci-News.com may collect and process the following data about you: information that you provide by filling in forms..." |
| Does/Does Not | Does Not | Does Not | "does not" | "Sci-News.com does not sell, trade or rent your personal information to third parties." |
| Third Party Entity | Specified ("Unnamed third party") | Unnamed third party | "to third parties" | "Sci-News.com does not sell, trade or rent your personal information to third parties. If we choose to do so in the future, you will be notified..." |
| Third Party Entity | Unspecified | Unspecified | "Third Party Advertising" | "The ads appearing on this Web site are delivered to users by our ad serving software. Information about users' visit to this site... is used to serve ads..." |

### Two nuances worth flagging to the team

1. **"Unnamed third party" is a distinct, deliberate value — not the same as "Unspecified."** When a policy says "we don't share with third parties" without naming any, annotators had a specific option for that (the company acknowledges a third-party relationship exists or could exist, but names no one). "Unspecified" is different: the text is too vague to tell whether a real third party is involved at all. These should not be collapsed into one "missing" bucket in any downstream model.

2. **"Specified" doesn't always mean there's a highlighted span.** The "Does" example above has a real, confident value but no highlighted text — the annotator judged it from the whole segment's context rather than one quoted phrase. `Purpose` and `Does Not`, by contrast, usually do have a specific highlighted phrase when specified. Span presence and value reliability are two separate things and shouldn't be assumed to move together across fields.

---

## 7. Data quality notes

- **47.0%** of all attribute-value rows have no usable text span (marked by `(-1,-1)` or `(0,0)` indices, per the corpus manual's documented errata). This reflects annotators selecting values like "Unspecified" or "not-selected" without highlighting text — not a parsing error.
- **781 rows (0.5%)** are flagged in the corpus's own `errant_span_indexes` files as having a known tool bug affecting their span. These are separate from the missing-span count above and should be excluded from any span-based analysis regardless of how their indices look numerically.
- **"Unspecified" and "not-selected" are distinct values**, per the corpus manual. `Unspecified` means the annotator selected it as a real, deliberate answer. `not-selected` marks an optional attribute the annotator wasn't required to fill in at all. These should not be collapsed into one "missing" bucket.

---

## 8. Open questions for the team

1. **Contract 1 decision** — given 61% mapped / 39% unmapped, and the reliability gaps shown in Section 5-6, which path does the team want: accept nulls for unmapped categories, add a generic catch-all field, or document this as a known limitation for now?
2. **Is "Other" (15.3% of the corpus) genuinely boilerplate**, or does it contain data practices that are being mis-categorized? Needs a qualitative read of a sample before the team treats it as low-value.
3. **Should "Unnamed third party" be treated as a specified value or folded into "no entity given" for modeling purposes?** It's semantically different from Unspecified but may need similar handling downstream.
4. **UID 186 mismatch** — `186_abcnews.com.csv` exists in the annotations folder, but the master policy lists map UID 186 to `disneyprivacycenter.com`. Unresolved — may be a legitimate shared policy (ABC is a Disney property) or a corpus inconsistency.
5. **Annotator agreement** has not yet been analyzed (raw annotations only so far, no consolidation comparison) — planned as a follow-up once the team aligns on the Contract 1 schema question.

---

## Appendix A: Why two different category counts exist

A single data practice can have up to 9 attribute-value pairs (First Party / Third Party) or as few as 1 (Other). Counting by exploded attribute row therefore over-represents categories with many attributes — by row, First+Third Party = 87.1% of the corpus; by unique practice, it's 61.0%. **All figures in this document use the practice-level count**, the more accurate representation of how much of the corpus each category represents.

## Appendix B: Charts referenced in this document

- `category_distribution_full_corpus.png` — Section 3
- `mapped_vs_unmapped.png` — Section 4
- `purpose_value_breakdown.png` — Section 5
- `does_does_not_split.png` — Section 5
- `top_third_party_entities.png` — Section 5
- `target_fields_reliability.png` — Section 5 (all three fields side by side)