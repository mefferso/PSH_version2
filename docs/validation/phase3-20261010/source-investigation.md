# Phase 3 source investigation — 2026-10-10

The baseline is successful operational run [#116](https://github.com/mefferso/PSH_version2/actions/runs/38031186696), main `cbc0af9`. Its public workbook and Pages manifest were fetched and compared: all 600 exported rows in Summary, Wind and Pressure, Water Level and Rainfall matched the downloaded workbook. Actions artifact downloads were unavailable through the execution network; the public operational downloads supplied the baseline.

## Marine rankings

`products.summaries` already admitted every observing network classified `M`. Its height rule explained the apparently WLON-only rankings. The new implementation makes that decision shared, auditable and independently ranks mean wind and gust from the actual Wind and Pressure cells. Neither value is recalculated from another network or normalized to another height. Unknown heights require review; heights >=20 m remain excluded. Unknown/incompatible sustained averaging periods are explicitly excluded from sustained tables; they do not exclude an independently qualified gust.

Current primary metadata reviewed:

| Station | Official NOAA anemometer height above site | Site elevation MSL | Source |
|---|---:|---:|---|
| BURL1 | 38 m | 0 m | https://www.ndbc.noaa.gov/station_page.php?station=burl1 |
| PTBM6 | 4.6 m | unspecified | https://www.ndbc.noaa.gov/station_page.php?station=ptbm6 |
| GISL1 | 6.6 m | 2.7 m | https://www.ndbc.noaa.gov/station_page.php?station=gisl1 |
| NWCL1 | 9.9 m | 1.7 m | https://www.ndbc.noaa.gov/station_page.php?station=nwcl1 |
| PILL1 | 9.5 m | 2.3 m | https://www.ndbc.noaa.gov/station_page.php?station=pill1 |
| SHBL1 | 15.6 m | 0 m | https://www.ndbc.noaa.gov/station_page.php?station=shbl1 |
| WYCM6 | 9.9 m | 0 m | https://www.ndbc.noaa.gov/station_page.php?station=wycm6 |

The template heights for GISL1, NWCL1 and PILL1 equal anemometer height plus site elevation. Both documented heights and template heights are below 20 m, so the reference distinction does not alter these eligibility decisions. Original metadata and formatting remain intact; the separate metadata inventory preserves the distinction. Current metadata cannot establish a historical relocation date. KPZZ (25 m), KMTK (49.9 m), and other offshore template heights remain exclusions, with original source links and review notes. Do not assign a new height without station-specific evidence.

KCYD and KGLX: official FAA identifier documentation and NWS observations establish the AWOS identities but searches did not establish the anemometer heights. FAA document https://www.faa.gov/documentLibrary/media/Order/7350.9BB_LID_dtd_7-14-22.pdf identifies Mississippi Canyon 807 AWOS-3 / CYD; https://tgftp.nws.noaa.gov/weather/current/KGLX.html publishes KGLX METARs. Neither supplies an anemometer mounting height. Station elevation/platform height cannot substitute. PTFL1 is also listed with unavailable anemometer height in https://www.ndbc.noaa.gov/faq/bmanht.shtml . Execution HTTP requests to NDBC station metadata pages returned 403; indexed official page content supplied the documented NOAA heights. These are explicit access/metadata limits, not proof of station discontinuation.

Means and gusts remain separate: METAR `sknt` is mean wind, `gust` and PK WND remarks are gust observations. A mean maximum can exceed the maximum **reported** gust from another time if the strongest mean observation did not report a gust; missing gusts are never backfilled with mean speed. NDBC header WSPD/GST are m/s, converted independently to knots, while pressure is hPa. Normalized WSPD10M/WSPD20M are not used. Template averaging metadata is retained; station-specific historic averaging and exposure remain review items. In run #116 all marine rows with a sustained value also had a gust value, while some sources supplied neither. No absent gust was invented. New tests explicitly cover independent wind-only and gust-only eligibility.

## Coastal datum evidence

Two newly reviewed primary station documents explicitly establish direct NAVD88 gage zero:

- SBEL1 / 76030: https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?dt=E&sid=76030 — gage zero 0 ft NAVD88; IHNC east/flood side, coordinates 30.0123888,-89.9005277, installed October 2010. Live CWMS identity matches.
- PRSL1 / 76040: https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?dt=S&sid=76040 — gage zero 0 ft NAVD88; GIWW near Paris Road, coordinates 30.0067055,-89.9373611. Live CWMS identity matches.

No offset was applied. Undated current datum evidence conservatively qualifies only the requested October 2026 period starting October 8; it does not qualify Francine 2024. Live descriptions, vertical metadata and exact station identity must still match the reviewed snapshot.

Remaining stations were investigated against the exact CWMS snapshots, primary USACE station/SHEF documents and prior Phase 2 audit. Outcome by station:

| ID | Finding / reason for continued review |
|---|---|
| BSGL1 | Exact 82742 sector-gate identity; no independent measured-gage zero retrieved. Nearby Lapalco 82740 datum documentation is a different station and is not used. |
| MBBL1 | 76025 east/flood-side legacy gauge is historic-only. USACE documents zero NAVD88 (2004.65), but recovered observations are secondary NWS HML; current HML datum and exact instrument epoch remain unverified. Protected-side 76024 is not substituted. |
| RGTL1 | Exact hardened 85700LA series has LOCAL metadata versus NAVD88 description. Older 85700 has a +0.21 ft adjustment and is discontinued; that different ID cannot resolve the hardened gauge conflict. |
| COCL1 | USACE basin listing identifies 85760 south/flood side and 85765 north/protected side; CWMS public-name for 85760 still calls it protected side. Description and coordinates favor flood side, but no independent measured datum evidence resolves all conflicting metadata. |
| 01441 | Current +0.032 ft description and prior datum epochs need independent event-effective conversion evidence. |
| WCCL1 | Exact 76265 WestCC _FS identity preserved; measured-stage datum remains undocumented. |
| BBOL1 | Official 52800 coordinates differ ~54 km from CWMS location; official stage NGVD29, -1.40 ft NAVD88 adjustment effective 2025-04-14. Do not apply a conversion while identity conflicts. |
| TSPL1 | USACE 85300 is NGVD with -1.35 ft OPUS 2014 adjustment effective 2014-09-24; CWMS NAVD location metadata does not prove raw stage already converted. Additional USGS 07376300 gauge is explicitly a separate instrument, not a replacement. |
| HPGL1 | USACE latest documentation specifies -0.018 ft NAVD88 (2009.55) adjustment as of 2022-07-27; older CWMS text says 2015-09-30. No independent epoch verification applied. |
| CKBL1 | Southwest Pass gauge relocation Dec 2010 and -0.48 ft adjustment dated 2022 need independent confirmation. |
| SWBL1 | USACE -0.48 ft since 2018-09-29; reset 2008-01-15, zero adjustment 2015-06-29. No independent confirmation of the raw CWMS observed datum/offset for either event. |
| BDAL1 | USACE 82700 explicitly NGVD29; no verified conversion retrieved. |
| BCSL1 | USACE 01280 currently says GAGE, -0.89 ft NAVD88 (2009.55), with separate LWRP conversion. Datum and applicability not independently established; neither location elevation nor LWRP is substituted. |
| BCFL1 | USACE 85552 gage-zero label NAVD lacks explicit version/epoch. Adjacent discontinued 85555 explicitly NAVD88 is a different gauge. |

Sources: each exact station's links are preserved in `coastal_water_audit.json` and `scripts/coastal_water_stations.json`. Additional verified documents include https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=01545 , https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=01670 , https://rivergages.mvr.usace.army.mil/WaterControl/shefdata2.cfm?dt=S&sid=85300 , https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?dt=S&fid=&sid=52800 , https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?dt=S&fid=NORL1&sid=01280 and the Lake Pontchartrain official basin inventory https://rivergages.mvr.usace.army.mil/watercontrol/new/layout.cfm?basin=46&dist=5&rd_in=S . Identical text repeated on USACE station/SHEF pages is not independent survey verification of a datum conversion. No unverified offsets shipped.

## Four missing coastal gauges

The MVN catalog was searched for **all Stage series at each exact mapped location**, and each was requested for the Isaias interval. There was one exact-location Stage series per gauge; all returned valid empty observations with no retrieval error. These attempts are captured in `missing-investigation.json`.

- 85750LA / Chef_Pass_LA: active official basin listing, no requested-period values in CWMS. No source outage/discontinuation assertion made.
- 85667 / Walker_DS_FS: active official basin listing, no requested-period values in CWMS. Protected-side 85666 is not substituted.
- CMPL1 / 85750 / Chef_Menteur: official historic-only; catalog ends 2024-02-20. Hardened 85750LA is a separate inventory row. Exact-ID HML fallback also attempted by the collector.
- LPML1 / 85575 / Lake_Pon_Mandvil: official historic-only; catalog ends 2023-11-16. New 85575LA / Mandeville_LA is ~430 m away and not substituted. Exact-ID HML fallback also attempted by the collector.

Current listings do not guarantee historical API availability. Catalog extents can be stale; actual data requests, not extents, decide availability. No API failure is labeled permanent unavailability.

## Rainfall source findings

A live credentialed Synoptic KMSY request returned a successful sensor-keyed `OBSERVATIONS.precip_accum_one_hour` response, not the unified `precipitation` list previously parsed. Native schema support is added without changing existing source priority, sensor qualification, count checks or overlap rules. Parallel sensor series are ambiguous and are never summed. The original source timestamps are retained. KMSY's reported 24-hour interval was 11:53 UTC to 11:53 UTC, crossing the noon requested boundary; it is correctly withheld as an exact storm total. The source response is captured separately as evidence, not interpreted as a noon accumulation.

Daily CoCoRaHS/COOP/HADS reports and hourly ASOS reports have different due times. Coverage uses actual reported periods. A daily interval still underway is pending, not missing. Source outages, unknown cadence, partial measured zero/trace and a complete observed zero remain distinct review states. Neither partial rainfall nor provisional accumulated rainfall is called a complete storm total. Existing useful partial measurements remain populated with I; no incompatible windows are added or interpolated.

The managed execution network blocked the official CoCoRaHS export host (`ProxyError`), whereas GitHub Actions run #116 successfully retrieved it. This is **not** a station availability finding. Consequently the live local PSH rain fields have 43 populated partial values rather than the baseline's 70. Thirty previously populated CoCoRaHS rows could not be freshly retrieved from their primary host. The operational collector remains intact and first in priority for those rows; no working source was disabled.

A supplementary exact-station IEM CoCoRaHS archive recovery now runs **only** after a primary CoCoRaHS retrieval failure and for an otherwise blank row. The documented daily-summary service provides precipitation in inches (trace sentinel 0.0001); its API returns exact original CoCoRaHS identifiers, names, calendar dates and measurements. Example: https://mesonet.agron.iastate.edu/api/1/daily.json?network=LA_COCORAHS&date=2026-10-09 contains LA-JF-5, River Ridge 0.7 N, 0.01 inches, consistent with the previously retrieved official run #116 amount. Unit documentation: https://mesonet.agron.iastate.edu/request/daily.phtml . Full archive responses are retained. No `temp_hour` or nominal observer time is promoted to an actual UTC timestamp. Report dates are not fabricated UTC observation times. Current local reporting dates are excluded; source dates at requested-window boundaries remain review-only because interval endpoints are unknown.

For Isaias this preserved 71 reports at 41 stations, including River Ridge's 0.01-inch report on October 9. Combined with the 43 populated PSH rainfall rows, 84 distinct stations now have a measured amount available for review, versus 70 previously. These archive reports do **not** populate PSH cells and are **not summed** into storm totals. The three positive partial PSH accumulations are BIX 0.01 inches, PQL 0.10 inches and newly recovered OLVL1 0.01 inches; the archive independently preserves LA-JF-05's 0.01-inch daily measurement. Zero measurements remain separate from missing amounts and primary failures. Francine's archive fallback preserved 168 reports at 60 stations. These are additional actual observations, with interval qualification explicitly unresolved.

## Completed Francine reference comparison

The full historical collection used September 10–12, 2024 for wind/water, and the exact reference rainfall window September 10 12 UTC–September 12 12 UTC. Workbook preservation and all exports validated. The new direct SBEL1/PRSL1 rules do not qualify those 2024 observations. Thirty coastal stations have measured peaks; seven qualify automatically under existing dated evidence. The event is completed, not provisional.

Of 206 numerically comparable issued-reference observations, 196 are within existing tolerances (95.15%); 10 differ, 372 are missing and 2 are ambiguous. Missing values do not count as agreement. The precise 0.12-inch BCCM6 boundary is now compared inclusively despite binary floating-point representation; physical tolerances were not increased. These results are a source comparison, not 95% coverage or complete operational correctness.

Remaining numerical differences: sustained wind KBTR (24 vs 27 kt), KMSY (50 vs 43), KNEW (42 vs 37), KPQL (23 vs 20); WSEBRTigerStadium gust (44.3 vs 48 kt); rain BBNL1 (6.91 vs 7.87 in), SHCM6 (1.64 vs 2.30), GRBM6 (1.30 vs 1.70), MPAM6 (0.21 vs 2.02), MCB (2.01 vs 1.88). Different source sampling/reporting and incomplete accumulation coverage require meteorologist reconciliation. No issued reference was changed and no discrepancy was concealed. Full per-observation results are in `Francine-regression.json`.
