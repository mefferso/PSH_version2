# PSH Version 2

A GitHub Actions system for collecting **review candidates** into the original LIX PSH workbook and publishing its tabs, sources, QC, provenance and downloads at [the dashboard](https://mefferso.github.io/PSH_version2/). It never issues an official PSH or writes to NOAA systems. Accurate unsupported fields remain blank; a green workflow means the products passed consistency checks, not that every source was available.

## Run and review

Changes to the collection, tests, dashboard, dependencies, template or `reviewed/` trigger verification and Pages publication automatically. The **Build PSH workbook** workflow also accepts storm name and inclusive UTC dates. Its development defaults are **Hurricane Isaias, October 8–9, 2026**: this label does not establish historical cyclone attribution. An unfinished current day cannot provide a complete rainfall total.

Every reading has a source URL, exact template station row/identifier, units, UTC time, original value/unit and QC. Water elevations also require datum evidence. The original binary template is unchanged. Generated workbooks clear example observations and impact narratives, preserve station metadata, links and formatting, replace spreadsheet-specific summary formulas with native top-ten tables, and add QC. Download the workbook or ZIP from Pages, and examine QC and provenance before using a value.

| Source | Automatic behavior | Remaining limitations |
|---|---|---|
| ASOS/AWOS | IEM archived METAR wind, gust and sea-level pressure; NOAA/IEM minute archive for exact ASOS stations adds documented two-minute winds, five-second peaks and fully covered minute rainfall | Minute archive can lag; missing periods, traces and incomplete routine METAR intervals prevent rainfall totals. Station pressures are never relabelled MSLP. AWOS minute coverage is not assumed. |
| NDBC buoy/C-MAN/WLON links | Recent 45-day and annual standard-meteorological wind, gust, pressure; header units verified; m/s to knots | Missing archives/access errors flagged. Conflicting timestamp records withheld. Mean-wind direction is not used as gust direction. Monthly-only archives and differing sampling periods need review. |
| NOAA CO-OPS | Water-level maximum explicitly requested in feet MHHW, with station datum metadata | Datum request/metadata failures leave blank. Qualified samples retain their source flags and review status. |
| USGS | Direct NAVD88 elevations from explicitly verified parameter codes 63160, 62620, 62615, with exact site and single-series gates | Public requests are rate limited; optional free `USGS_API_KEY` uses headers. Stage 00065 has no inferred offset. USGS rain/wind rows need verified series semantics and remain unsupported. 62020 is not an elevation code. |
| USACE / Louisiana CPRA | Exact RiverGages station metadata audit; historical HML stage collection and NAVD88 conversion supported only with an independently reviewed, event-effective station registry | No offsets are supplied or auto-approved. Current gage-zero text alone does not prove a historical conversion. All unverified stations stay blank. |
| WeatherSTEM | Exact linked station/sensor archive; explicit-unit ten-minute gusts; sustained wind only with explicit averaging metadata; MSLP only when explicitly identified | Public metadata often lacks sustained averaging or sea-level pressure identity. Rain counter/reset semantics and historical sensor changes are unverified. No nearby-station substitution. |
| Synoptic / MesoWest | Exact CWOP/RAWS wind/gust/MSLP timeseries with `SYNOPTIC_TOKEN`; exact ASOS/AWOS/COOP/HADS/RAWS precipitation queries | Sensor ambiguity, units, access and availability are checked. Internally inconsistent gust/speed records are quarantined. Generic speed without explicit 1/2/8/10-minute averaging metadata stays out of the sustained column; its source peak/time is retained in QC. Aggregate endpoints/counts alone do not prove complete rainfall; explicit contiguous accumulation intervals are required. |
| CoCoRaHS | Official exact-station historical requests, pagination, padded-ID normalization and documented-interval aggregation | Observed public responses lack `numDays` and have unresolved UTC/local-clock semantics. Those totals are withheld, even if summing displayed daily values resembles an issued report. |
| Tornadoes | Confirmed NCEI Storm Events, LIX records explicitly naming the storm, source timezone converted to UTC | Archive publication lag and missing storm association prevent completeness. No match leaves the tornado count blank and does not prove zero tornadoes; preliminary reports are not confirmed records. |
| Other linked networks | COOP/HADS/RAWS rainfall queried through exact-ID Synoptic; all inventory rows receive QC | Exact archive mapping and accumulation semantics can be absent. TPCG rows lack usable source links; no nearby substitute is invented. |
| WeatherFlow | Original metadata retained; dashboard reviewed-entry form and JSON import template | Automatic collection intentionally excluded. |
| Inland flooding / impacts | Tabs and county metadata preserved, stale examples cleared, missing narratives/counts explicitly flagged | Requires verified storm-specific records and human review. Fatality/injury/evacuation values are never invented. |

## Reporting conventions

The [NWSI 10-601 guide, August 17, 2026](https://www.weather.gov/media/directives/010_pdfs/pd01006001curr.pdf), section 8, controls candidate thresholds: gust **greater than 33 kt** or sea-level pressure **less than 1005 mb**, rainfall **at least 3 inches**, and explicit water datums. Lower readings remain in review exports. Wind candidate CSV has the guide's 29 columns; rain 9, water 14, tornado 11. CSVs contain headers and populated records, no blank/footer rows; ambiguous duplicate station IDs are excluded and flagged. Template rows are preserved. Candidate CSVs still require meteorologist review, storm attribution and operational decisions.

Rain defaults to midnight UTC on the first date through midnight after the last date. Set both `rain_start_utc` and `rain_end_utc` workflow inputs, or local `RAIN_START_UTC`/`RAIN_END_UTC`, for another interval. Every rain adapter, reviewed import, workbook heading and validator uses the same interval. Missing/trace reports are never silently zero and overlapping daily/rolling amounts are not added.

## Manual additions and datum registries

Use **Add WeatherFlow** on the dashboard, select the original station, enter a measurement in the displayed units, UTC time and source URL, and explicitly attest review. Download the staged JSON. The form stages observations locally; it does not publish them immediately. Commit a reviewed file such as `reviewed/weatherflow.json`, then select its path in the workflow's `reviewed_import` input. Locally use `PSH_IMPORT_FILE=/path/to/reviewed.json`. Imports validate the complete batch, exact tab/row/site/network, units, ranges and dates before changes. A reviewed override replaces the active audit and stores superseded readings; omitted directions are cleared.

Other reviewed observations use the same schema; see `scripts/imports.py`. Rain needs `interval_start_utc` and the full interval endpoint. Water requires `datum` plus two independently hosted evidence citations. For a USACE/CPRA registry, use `datum_registry` or `PSH_DATUM_REGISTRY`. Each record requires `site_id`, exact original `rivergages_sid`, `datum: "NAVD88"`, numeric `offset_ft`, `reviewed: true`, `effective_start_utc`, `effective_end_utc`, and `evidence` URLs from two independent hosts. See `scripts/datums.py` and tests. Citations record a human-reviewed conversion; mere hostname independence does not automatically validate its substance.

## Development and verification

Python 3.12 and Node 24 are used in CI. Install frozen Python dependencies and dashboard DOM-test dependencies:

```bash
python3 -m venv /workspace/psh-venv
source /workspace/psh-venv/bin/activate
python -m pip install -r requirements.lock.txt
npm ci --ignore-scripts --cache /tmp/psh-npm-cache
python -m unittest discover -s tests -v
STORM_NAME='Hurricane Isaias' START_UTC=2026-10-08 END_UTC=2026-10-09 python scripts/build.py
python scripts/validate.py
python scripts/export_dashboard.py
python scripts/validate.py --site
```

Tests exercise the real workbook, source identity/unit/time errors, missing intervals, datums, reviewed overrides, reporting thresholds, stale narratives, summary/CSV tampering, downloads and dashboard interactions. DOM tests execute the shipped JavaScript; they do not assert browser pixel appearance. Chromium could not complete in the onboarding container.

The publication gate checks template checksum, original station metadata/styles/links and merged structure, one active audit per measurement, UTC fields and rain intervals, exact values/datums, recomputed top-ten tables, CSVs and dashboard/download consistency. Only current manifested artifacts enter the ZIP. Network failures remain distinguishable from missing observations in QC.

The unmodified completed Francine workbook from `mefferso/PSH_project` is in `tests/fixtures/`, with its provenance and checksum documented there. Run a separate live Francine collection for September 10–12, 2024, then compare. Use the reference rainfall window **2024-09-10 12:00 UTC to 2024-09-12 12:00 UTC**; calendar-day totals cover a different period. The workflow’s optional `francine_regression` input runs this separate live case and uploads its full audit/comparison without replacing the requested dashboard storm. Locally compare:

```bash
python scripts/regression.py output/PSHLIX_2024_Hurricane_Francine_REVIEW.xlsx
```

Tolerance: wind/gust 1 kt, pressure 0.5 mb, rainfall 0.12 inches, water 0.15 feet. Missing and ambiguous readings are counted separately, never as agreement. Do not widen tolerances to hide source differences. See [validation records](docs/validation/) for actual live results and unresolved discrepancies.

`SYNOPTIC_TOKEN` is an Actions secret confirmed by the repository owner. No secrets are committed or included in URLs. It need not be present in the cloud shell; credentialed validation runs in Actions. Saved cloud setup instructions reproduce the dependency installation and checks; changes to that environment draft require publication in environment settings for future tasks.
