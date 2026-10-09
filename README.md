# PSH Version 2 — GitHub-powered data collection

This project is the successor to PSH_project. GitHub Actions runs the collection and creates an auditable workbook. **WeatherFlow stays manual.**

## Run a test

1. The uploaded original **Copy of PSHLIX_YYYYALXX_StormName_Data.xlsx** is already at the repository root. Keep it there, including its hyperlinks and formatted sheets.
2. Open **Actions → Build PSH workbook → Run workflow**.
3. Supply storm name, start and end UTC dates. Download the `PSH-...` workflow artifact after the run.
4. Inspect the `QC` tab before considering observations operational.

**Current implementation is an initial foundation, not full-source operational coverage.** The collector supports IEM archived ASOS/AWOS wind and pressure and NOAA CO-OPS water levels for preloaded NOS stations and NDBC standard-meteorological data for linked Buoy/C-MAN/WLON rows with validated station hyperlinks. CO-OPS elevations are explicitly requested in feet relative to MHHW and are always marked for review before issuance. Other network adapters (USGS, USACE, WeatherSTEM, Synoptic/MesoWest and CoCoRaHS) and tornado/impact narratives are **not yet wired up**. The workflow leaves their observations untouched, instead of inventing values or silently marking them complete. A run must not be treated as a complete PSH.

The shipped code:
- uses the template station metadata and keeps WeatherFlow observations manually editable;
- validates event dates, records source URLs and separates missing from suspicious data;
- writes one peak sustained wind, peak gust and minimum sea-level pressure per station, including independently determined UTC observation times;
- preserves original workbook formulas, formatting and hyperlinks as far as the spreadsheet library permits;
- publishes an XLSX artifact rather than pushing automatically to the live NOAA Google Sheet.

## Architecture

GitHub Actions is the runner. The checked-in LIX workbook is the station inventory and output template. Source adapters collect measurements by *actual observing-site identifier* and the parser records provenance and timing. QC rejects ambiguous units, nonnumeric values, and missing-time records. Generated files are workflow artifacts.

**Required next stages before replacing the older PSH automation:** inventory and validate all hyperlinks; validate CO-OPS results against a completed storm; USGS parameter/datum checks; USACE station mappings; WeatherSTEM and Synoptic/MesoWest adapters; daily CoCoRaHS storm totals with observation-window handling; optional verified tornado summaries; regression comparisons with Francine/Bertha; optional authenticated Google Sheets updates. In the original NWS guidance, unique station IDs and no blank rows in reported CSV data are mandatory. Do not erase existing station metadata or historical links.

No credential needs to be committed to the repository. If Google Sheets writeback is added, use GitHub Actions secrets and a properly authorized account rather than personal credentials in code.


## Browser dashboard (GitHub Pages)

The latest run can be viewed at **https://mefferso.github.io/PSH_version2/** once Pages is enabled.

**One-time setup:** In the GitHub repository, go to **Settings → Pages → Build and deployment → Source: GitHub Actions**. Then run **Actions → Build PSH workbook → Run workflow** again with the selected storm and UTC range. Each successful run will deploy the data dashboard and current XLSX, so you do **not** have to download workbooks merely to inspect changes.

The dashboard has per-tab tables, station hyperlinks, search/filter, and a QC tab. It displays only the observational data the collector actually wrote; unimplemented networks and the original Google Sheets-only summary QUERY formulas remain clearly marked incomplete. **The public Pages site exposes station information and the generated XLSX publicly; do not put confidential observations or credentials in the template.**

Do not use Actions' **Re-run jobs** on runs created before the dashboard workflow was added: start a **new Run workflow** to publish the site.


### NDBC collector (new, awaiting live regression check)

Linked NDBC Buoy, C-MAN, and WLON stations are retrieved using the source station ID (not a nearby substitute). The adapter prefers the NDBC last-45-days feed for recent dates and attempts annual standard-meteorological archives for older dates. Winds/gusts convert from m/s to knots; sea-level pressure remains hPa/mb. Missing values are excluded, and each independently timed extreme populates the existing Wind and Pressure columns. Data that cannot be retrieved is shown as **NO DATA/ERROR** in QC, not as a successful observation. NDBC sampling periods and metadata vary by station; validate these against the station page before operational use. Please initiate a **new** workflow run to test these changes. The workflow includes NDBC parser unit tests.


### RiverGages USACE / Louisiana CPRA audit

The source inventory now checks original RiverGages station hyperlinks against the station source (USACE or LA CPRA) and writes each match into the QC tab with a **DATUM REVIEW** status. Many RiverGages series are stage with station-specific gage zero, historical NAVD88 adjustments and effective dates. There is **no automated USACE/CPRA water-level ingestion yet**; this audit does not count as collected data. Before numerical collection is implemented, each site needs an independently verified datum and archive endpoint. Unverified stage-to-NAVD88 conversions remain prohibited.
