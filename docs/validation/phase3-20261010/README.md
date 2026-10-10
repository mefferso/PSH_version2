# Phase 3 observation verification

Isaias uses the **actual run #116 requested windows**: water/wind October 8 00 UTC to October 11 00 UTC, rain October 8 12 UTC to October 11 12 UTC. `END_UTC=2026-10-10` is an inclusive date, not an exclusive midnight boundary. The final collection cutoff is October 10 07:02:21 UTC, so both event windows remain provisional. Before/after values can differ because the second collection has additional elapsed observations. All coastal measured peaks were independently recomputed from archived raw CWMS/HML responses and matched.

- Coastal peaks: **27 → 27**; automatically datum-qualified PSH: **11 → 13** (SBEL1 and PRSL1 added). **14** remain datum review, **4** without measurements.
- Marine sustained top-10 has six eligible stations: PTBM6 36.9, SHBL1 31.1, NWCL1 29.0, GISL1 28.0, WYCM6 27.0, PILL1 25.1 kt.
- Marine gust top-10 has six eligible stations: PTBM6 52.1, PILL1 39.1, SHBL1 38.1, GISL1 36.0, WYCM6 36.0, NWCL1 35.0 kt.
- The apparent network exclusion was a height eligibility effect. These actual values remain correctly ranked; no raw elevated-platform or unknown-height wind was added. The review CSV explains every exclusion and separately documents missing measurement/averaging metadata.
- Rain: baseline 70 populated rows/3 positive; local rerun 43 populated rows/3 positive due to the primary CoCoRaHS host access failure. Supplementary archive review supplies **71 individual reports / 41 stations**, yielding **84 distinct stations with a measured rainfall amount**, with unknown clocks/intervals explicit. These daily reports are not storm totals. Positive partial PSH amounts: BIX 0.01, PQL 0.10, OLVL1 0.01 inches. LA-JF-05's archived daily report is 0.01 inches, kept separately.
- Francine: completed event, 30 coastal peaks, 7 qualified, workbook/exports validated; 196/206 comparable reference readings within tolerance, 10 discrepancies, 372 missing and 2 ambiguous. This does not demonstrate complete observational recovery.

`Isaias-review-outputs.zip` and `Francine-review-outputs.zip` contain regenerated workbooks, QC, measured-observation provenance, rainfall partial reports, exact CWMS/HML source responses, supplementary rainfall archive responses, marine exclusions, requested/elapsed coverage and all CSV downloads. They are review products; no website was published by this development branch.

`before-after.json`, `source-investigation.md`, `missing-investigation.json`, `marine-metadata-access.json`, `synoptic-native-response.json`, `Francine-regression.json`, and `verification.json` document the numerical comparison, primary evidence and limitations. Preserve original values/timestamps and human reporting authority.

## After merge: explicit operational deployment

1. Merge the PR manually when reviewed.
2. In GitHub Actions, open **Build PSH workbook**, choose **Run workflow**, select **main**.
3. To repeat run #116: storm `Hurricane Isaias`, start `2026-10-08`, inclusive end `2026-10-10`. Rain defaults to October 8 12 UTC–October 11 12 UTC. For the earlier two-day water window ending October 10 00 UTC, use inclusive end `2026-10-09` instead; set rainfall override inputs explicitly if needed.
4. Enable Francine regression if the historical comparison is wanted. Do not supply an unreviewed datum registry.
5. Wait for tests, collection, workbook/export validation, Pages deployment and postdeployment verification to succeed. The final verification compares all four operational tabs, complete manifest, provenance and review data to the validated local export; it also compares the coastal CSV byte for byte.
6. On https://mefferso.github.io/PSH_version2/ check the storm/window/commit and Summary, Wind and Pressure, Water Level and Rainfall tabs. Review marine exclusions, provisional status, partial rainfall and supplemental archives. SBEL1 and PRSL1 can now appear as NAVD88 for the audited 2026 period. In Water Level, unqualified stages remain separate from official datum-qualified fields.

PR/push tests do not deploy; operational Pages collection requires an explicit dispatch on main. Successful run #116 already demonstrated operational deployment and public workbook/website agreement. A future merge/deployment cannot be performed or claimed from this unmerged PR; the workflow enforces verification when it is triggered.
