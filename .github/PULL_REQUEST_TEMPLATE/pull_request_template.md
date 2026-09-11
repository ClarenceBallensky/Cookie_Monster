## What changed

<!-- Short description of the change -->

## Area

- [ ] extension
- [ ] data-processing
- [ ] ml-models
- [ ] backend
- [ ] crosswalk
- [ ] docs / infra

## Does this touch a data contract?

<!--
A "data contract" is any schema/format that another role depends on:
data-processing -> ml-models, ml-models -> backend (Postgres write),
backend -> extension, or anything -> crosswalk.
-->

- [ ] No — internal change only
- [ ] Yes — and `docs/DATA_CONTRACTS.md` has been updated in this PR
- [ ] Yes — but contract is unchanged (shape/fields identical)

## How was this tested?

<!-- Manual steps, test commands, screenshots, etc. -->

## Checklist

- [ ] Runs locally via `docker-compose up` (if backend/db touched)
- [ ] No secrets or `.env` values committed
- [ ] Linked to a tracked issue/card, if applicable
