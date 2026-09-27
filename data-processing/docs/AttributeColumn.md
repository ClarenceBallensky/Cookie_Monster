# OPP-115 Annotation File — Attribute Column & Next Steps

## 1. What the attribute JSON column actually is

Column index 6 in the raw annotation CSVs (no header row) is a **JSON dictionary of attribute-level labels**, nested one level deep inside each top-level category annotation.

**Structure:**
- **Keys** = attribute names specific to the row's category (e.g., `Purpose`, `Collection Mode`, `Identifiability` for First Party; `Change Type`, `Notification Type` for Policy Change)
- **Values** = a small object with four fields:
  - `value` — the actual label chosen (e.g., `"Personalization/Customization"`, `"Unspecified"`, `"Does"`)
  - `selectedText` — the exact policy text snippet the annotator highlighted as evidence
  - `startIndexInSegment` / `endIndexInSegment` — character offsets of that snippet within the segment

**Key behaviors observed:**
- Number of attribute keys per row varies by category — as few as 1 (Other) up to 9 (First Party / Third Party)
- When `startIndexInSegment`/`endIndexInSegment` = `-1`, there is no `selectedText` — the annotator chose a value (often `"Unspecified"`) without pointing to specific text
- This column carries the actual analytical substance: category tells you *what kind* of practice, this JSON tells you *what data, for what purpose, whether identifiable, what user control exists*

---

## 2. Handling the column before compression (no cleaning/removing yet)

Goal here is **restructuring for size and queryability**, not deleting information.

- **Parse once, store flat.** Explode the JSON into a long-format table (`policy_id, seg_id, annotator, category, attribute, value, start_idx, end_idx, selected_text`) rather than compressing the raw string repeatedly per file. Repeated key names (`"startIndexInSegment"`, etc.) are the biggest source of bloat — flattening removes that repetition once, up front.
- **Separate spans from values.** Consider splitting into two tables: one small table of `(policy_id, seg_id, annotator, category, attribute, value)` for analysis, and one larger table of the span/text evidence (`start_idx, end_idx, selected_text`) for cases where you need to trace back to source text. The first table is what you'll query constantly; the second is mostly for spot-checks.
- **Don't duplicate `selectedText` unnecessarily.** Since the segment text is already in the HTML files, `selectedText` is a derivable substring (`segment_text[start:end]`). Keeping both the index and the raw text is useful for validation, but if compression matters, the index alone plus the source segment is sufficient — the text string is redundant information.
- **Standard compressed formats to consider (comparison, not a decision yet):**
  - **Parquet** — columnar, compresses well, keeps types (int spans stay ints), fast to query with pandas
  - **Feather** — similar benefits, faster read/write, less universal
  - **gzip/csv** — simplest, but repeated JSON keys compress less efficiently than a flattened columnar format
- **Keep the raw files untouched** as your source of truth, and treat the flattened/compressed version as a derived artifact you can regenerate if the parsing logic changes.

---

## 3. Next steps for analysis

1. **Confirm column names against `documentation/manual.txt`** (referenced in `readme.txt` but not yet provided) — validate the 9-column layout before finalizing the loader.
2. **Write one loader function** that takes a raw annotation CSV + its matching HTML file and returns the three tidy tables: policies, segments, annotations (long format, JSON exploded).
3. **Run the loader across all 115 policies** and check that every Policy UID has both an HTML and CSV file — flag any mismatches.
4. **Re-check the "batch" column across more files.** IMDb showed two distinct batch values (`..._upitt`, `..._fordham_ddddd`) where Atlantic had only one — worth checking whether **annotator IDs are unique across batches** or get reused, since that affects your agreement calculations.
5. **Resolve the ABC News file.** It didn't match any UID in either policy list — confirm whether it belongs to a different folder/version before including it in the master dataset.
6. **Run annotator agreement metrics** (Cohen's/Fleiss' kappa) once the full dataset is loaded, given the variation in labels-per-segment you've already seen across annotators.
7. **Scale the category/attribute EDA from one policy to all 115** — check whether the imbalance seen in the Atlantic and IMDb files (Third Party / First Party dominating, Access-Edit-Deletion smallest) holds corpus-wide or varies by site/sector.
8. **Cross-reference `policies_opp115.csv` and `policies_at100.csv` overlap** (15 shared UIDs found so far) — decide whether AT-100 is a separate holdout set or should be merged in.

---

## 4. Additional details worth flagging

- **Document ID ≠ Policy UID.** Column 3 (e.g., `3741` for IMDb, `3635` for Atlantic) is an internal doc ID, not the UID used in the master policy lists — always join on filename prefix / UID, not this column.
- **Date and URL columns are static per file** — they repeat the policy's last-updated date and source URL on every row rather than carrying per-row information. Useful for validation joins against the master list, not for analysis.
- **Segment IDs are the reliable join key** between the CSV annotations and the `|||`-delimited HTML segments — confirmed consistent (0–35, 36 segments) across both files checked so far.
- **Attribute keys are category-specific**, not universal — build your attribute schema per category rather than assuming one shared set (e.g., `Retention Period` only appears under Data Retention, `Audience Type` only under International and Specific Audiences).