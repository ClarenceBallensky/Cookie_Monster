# OPP-115 Annotation File — Category Column

## 1. What this column contains

Column index 5 in the raw annotation CSVs is the **top-level data practice category** — a single label per annotation row, chosen from a fixed set of 9 categories defined by the OPP-115 annotation scheme.

**The 9 categories observed across files so far:**

| Category | What it represents |
|---|---|
| **First Party Collection/Use** | What the company itself collects and how it uses that data |
| **Third Party Sharing/Collection** | Data shared with, or collected by, outside entities (ad networks, analytics providers, affiliates) |
| **User Choice/Control** | Opt-outs, cookie preferences, ways to limit tracking |
| **Data Retention** | How long data is kept and under what conditions |
| **Data Security** | Statements about how data is protected (often generic) |
| **Policy Change** | How/whether users are notified of policy updates |
| **International and Specific Audiences** | Provisions for children, EU users, California residents, etc. |
| **User Access, Edit and Deletion** | User rights to view, correct, or delete their data |
| **Other** | Catch-all for text that doesn't describe a specific data practice (intros, contact info) |

**Key behaviors observed across the two files checked:**
- Distribution is consistently skewed: First Party and Third Party dominate (76 + 67 in Atlantic; 43 + 49 in IMDb), while User Access/Edit/Deletion and Data Retention are consistently the smallest
- A single segment can carry **multiple category labels** — from the same annotator or different ones — since one chunk of text can describe more than one kind of practice (e.g., a sentence mentioning both collection and sharing)
- This column determines **which attribute keys appear** in the JSON column — each category has its own fixed attribute schema (covered in the previous document), so this column is effectively the schema selector for column 6

---

## 2. What we can do with it

- **Corpus-wide category distribution.** Aggregate counts across all 115 policies to see whether the skew (Third Party / First Party dominating, Access/Edit/Deletion smallest) holds universally or varies by sector (news vs. e-commerce vs. social media)
- **Per-policy category profile.** Compare category proportions across individual policies as a fingerprint — some sites may emphasize security language, others may lean heavily on third-party disclosure
- **Co-occurrence analysis.** Build a segment-by-category matrix to see which categories tend to appear together in the same segment (e.g., does "User Choice/Control" often co-occur with "Third Party Sharing/Collection"?)
- **Annotator agreement by category.** Some categories may show more disagreement between annotators than others — categories with more subjective boundaries (e.g., "Other" vs. a specific category) are worth checking first
- **Join key into the attribute schema.** Use this column to decide which attribute-parsing logic to apply to column 6, since attribute keys are category-specific, not universal

---

## 3. Handling during compression (no cleaning/removing yet)

- **Convert to a categorical dtype**, not a plain string. In pandas, `astype("category")` stores the 9 labels as small integer codes internally rather than repeating the full string on every row — this is a straightforward, lossless size reduction with no information removed. Do this before any file compression pass.
- **Keep it in the same row as segment ID and annotator ID.** This column is compact (9 fixed values) and cheap to store — it's not a compression concern on its own. The real savings come from the attribute JSON column, not this one.
- **If storing in Parquet**, categorical/dictionary encoding is handled automatically and compresses very efficiently for low-cardinality columns like this — another reason Parquet is worth considering over flat CSV for the derived tables.
- **Preserve the raw label text somewhere** (a small lookup table of the 9 category names) rather than converting to bare integers permanently — you'll want the readable names for plots and summaries, and categorical dtype in pandas keeps both underneath.

---

## 4. Additional details worth flagging

- **This column is not one-hot by nature** — a segment can have several rows (one per category the annotator tagged), so counting "categories per segment" requires grouping by segment ID, not just counting rows.
- **"Other" deserves a periodic sanity check.** If its share grows unusually large in certain policies once you scale to all 115, it may indicate segments that don't fit the scheme well, or possible mis-tagging — worth flagging in your findings log rather than treating as just another category.
- **Category imbalance affects any modeling step down the line** (if classification is part of the eventual goal) — worth noting in your log now, even though you're not at that stage yet, since it will shape train/test splitting and evaluation metrics later.
- **Cross-check this column against the batch column** noted in the previous document — worth verifying whether category distributions differ meaningfully between annotation batches (e.g., `..._upitt` vs. `..._fordham_ddddd`), which could point to batch-specific annotator tendencies rather than true differences in the policies themselves.