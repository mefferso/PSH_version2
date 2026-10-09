# PSH Automation Implementation Plan

> Execute inline using superpowers:executing-plans; the user requested continuous autonomous work.

**Goal:** An accurate, traceable workbook/dashboard pipeline with all inventory networks addressed.
**Architecture:** Exact-identifier adapters, shared measurement audit and safe workbook writers, verified output export, and gated Pages workflow.
**Tech Stack:** Python 3.12, requests, openpyxl, unittest, static JavaScript, GitHub Actions.
**Spec:** ../specs/2026-10-09-psh-design.md

## Global Constraints
- WeatherFlow automatic collection excluded; manual data retained.
- No guessed datum conversions, timestamps, nearby stations or storm totals.
- Original workbook binary remains unchanged.
- The development window is 2026-10-08 through 2026-10-09 UTC, labeled Hurricane Isaias for testing only.

## Review Focus
- Duplicate workbook IDs with different source identities must be flagged and excluded from ambiguous CSVs.
- Partial current-day data must not imply a complete historical event.
- Rainfall traces, missing periods and overlapping accumulations must not become fabricated totals.
- Raw stage/NGVD29 and station pressure must not be relabeled NAVD88/MSLP.
- Stale artifacts and template examples must not leak into published observations or summary.

### Task 1: Shared inventory, provenance and safe output
Files: scripts/common.py, scripts/products.py, tests/test_products.py.
Interfaces: inventory(wb, tab) yields station rows; Audit records written measurements; summaries(wb) renders existing ranges; export_csv(wb, target) writes review data.
- [ ] Write failing tests for metadata preservation, duplicate IDs, summary sorting/height filters, finite values and rainfall coverage.
- [ ] Run unittest and confirm failures for absent interfaces.
- [ ] Implement inventory, provenance, conservative QC/aggregation, summary and CSV logic.
- [ ] Run entire unittest suite; commit.

### Task 2: Historical adapters and verified datum safety
Files: scripts/iem.py, scripts/coops.py, scripts/usgs.py, scripts/ndbc.py, scripts/synoptic.py, scripts/imports.py; adapter tests.
Interfaces: collect(station, start, end) returns validated observations and source URLs; populate adapters write safe workbook values and Audit entries.
- [ ] Add failing tests for exact identity, units, UTC bounds, rainfall duplicate/coverage handling, NOAA datum evidence, USGS single-series selection, NDBC conflicting duplicates, credential redaction and reviewed imports.
- [ ] Run tests and confirm failures, implement adapters and safe imports, rerun suite.
- [ ] Investigate live network schemas and source access; record exact blockers rather than claiming unvalidated adapters ready.
- [ ] Commit verified changes.

### Task 3: Integration, dashboard and publish gating
Files: scripts/build.py, scripts/export_dashboard.py, scripts/validate.py, site/index.html, .github/workflows/build-psh.yml; tests/test_pipeline.py.
Interfaces: build produces manifest-selected workbook, provenance/QC, review CSVs; export renders all tabs and links; validate exits nonzero on structural/measurement errors.
- [ ] Write failing end-to-end tests using the real workbook with controlled source fixtures, no external downloads.
- [ ] Implement orchestration, all-network QC, manual templates, dashboard summary/provenance and downloads.
- [ ] Gate Actions deployment on unit tests and artifact validation; expose optional credentials through secrets.
- [ ] Run offline pipeline, repeatability and preservation validation; commit.

### Task 4: Live regression, documentation and publication
Files: docs/validation/*, README.md, requirements.lock.txt; cloud draft install/start instructions.
- [ ] Run representative live source checks and Francine comparisons against available authoritative references.
- [ ] Correct discrepancies with failing regression tests before fixes.
- [ ] Save tested environment install/start configuration.
- [ ] Review full diff, push authorized changes, trigger and inspect actual Actions and dashboard.
- [ ] Document passed/unrun checks, source limitations and blocking external actions. Do not claim final completion while publication/live accuracy remain unverified.
