# Isaias CPRA / USACE station audit — October 8–10, 2026

Exact interval: **2026-10-08T00:00:00Z ≤ observation time < 2026-10-10T00:00:00Z**. Storm label is the requested operational label; it does not establish cyclone attribution.

**27 of 31 stations have retrieved measured peaks (26 official CWMS, 1 secondary NWS HML archive). 11 have station-specific direct datum evidence and populate PSH NAVD88 fields. 16 additional measured peaks remain in review output. 4 have no retrieved observations. All stations require meteorologist review.**

No NAVD88 offsets were invented or shipped. Independently reviewed event-effective conversions remain supported through the existing datum registry. A CWMS location vertical datum/elevation describes the physical location and is not, by itself, evidence for measured stage datum. Testing a `datum=NAVD88` query on Bayou Boeuf returned unchanged NGVD29 stage; a requested datum parameter is therefore not used as evidence.

Incomplete measurements are retained and marked I. Review-only stages also carry I. Expected counts use the selected source sampling interval, not a requirement to invent missing hours. A complete returned grid is only coverage of that sampling cadence; it does not establish continuous coverage or the true storm maximum. Quality 0 (unscreened) and 3 (screened/okay) observations can contribute; other codes and invalid values remain archived for review and cannot create automatic peaks. Tied maxima use the first observed UTC time.

## Source investigation

- All 30 existing RiverGages hyperlinks returned HTTP 200 error pages (“page cannot be displayed”) in this environment; WCCL1 had no original hyperlink. This is an access failure, not proof that every station is discontinued. Every replacement observation URL was fetched and returned the exact expected CWMS series identity.
- Official source: [USACE CWMS API](https://cwms-data.usace.army.mil/cwms-data/), office MVN, `/locations`, `/catalog/TIMESERIES`, and paginated `/timeseries` JSON v2. Original numeric RiverGages SID is linked to the exact named CWMS location through official public-name/long-name metadata, with coordinates and gauge-side descriptions checked. No nearest-location lookup is used.
- [CPRA CIMS monitoring data](https://cims.coastal.la.gov/monitoring-data/) and [hourly requests](https://cims.coastal.la.gov/DataDownload/DataDownload.aspx?type=hydro_hourly) were investigated. Hourly downloads can involve an emailed CSV; [weekly full-table exports](https://cims.coastal.la.gov/FullTableExports.aspx) are very large. These 13 template rows identify flood-protection/sector-gate/hardened gauges, not verified CRMS wetland station IDs. No CRMS/SONRIS station substitution was verified or made. CIMS access was through web research; no email request was sent.
- USGS and NOAA routes were checked for exact-identity applicability. Tickfaw’s official page links an **additional** USGS gauge (07376300); the template already has a separate USGS TSPL1 row. It is not substituted for the USACE gauge. NOAA tide gauges use their own independently verified MHHW collector; no nearby NOAA tide gauge is substituted.
- Exact original NWS identifiers may use [IEM’s NWS HML observation archive](https://mesonet.agron.iastate.edu/cgi-bin/request/hml.py) only after no eligible primary peak. MBBL1 was recovered here despite an empty current CWMS legacy series. Secondary archived stage is always review-only. The failed primary attempt and successful secondary raw CSV are retained.
- CWMS catalog extents were stale (many ended September 14 despite real October observations). The collector always requests the actual interval and never declares a station unavailable from catalog extents alone.

## Station results

All values below are **feet in the observed datum**, with actual UTC timestamps. “Review” is not a NAVD88/MHHW elevation. Current SID is the verified official RiverGages SID; exact CWMS series and retrieval URLs follow for every row.

| Original ID | Current SID | Observed peak ft | Peak UTC | Datum / qualification | PSH | Count | Human review |
|---|---|---:|---|---|---|---:|---|
| BSGL1 | 82742 | 2.02 | 2026-10-08T01:15:00Z | UNVERIFIED GAGE STAGE | No | 192 | Yes |
| LBWL1 | 82875 | 1.67 | 2026-10-08T00:15:00Z | NAVD88 | Yes | 192 | Yes |
| SBEL1 | 76030 | 4.19 | 2026-10-09T20:30:00Z | UNVERIFIED GAGE STAGE | No | 179 | Yes |
| MBBL1 | 76025 | 1.95 | 2026-10-08T00:00:00Z | UNVERIFIED GAGE STAGE | No | 188 | Yes |
| RGTL1 | 85700LA | 3.02 | 2026-10-09T23:00:00Z | UNVERIFIED GAGE STAGE | No | 192 | Yes |
| 76065 | 76065 | 3.78 | 2026-10-09T22:45:00Z | NAVD88 | Yes | 192 | Yes |
| 76062 | 76062 | 3.45 | 2026-10-09T21:15:00Z | NAVD88 | Yes | 192 | Yes |
| 85750LA | 85750LA | — | — | UNVERIFIED GAGE STAGE | No | 0 | Yes |
| COCL1 | 85760 | 3.66 | 2026-10-09T23:45:00Z | UNVERIFIED GAGE STAGE | No | 192 | Yes |
| 01441 | 01441 | 1.36 | 2026-10-09T05:00:00Z | UNVERIFIED GAGE STAGE | No | 192 | Yes |
| WCCL1 | 76265 | 1.81 | 2026-10-08T00:00:00Z | UNVERIFIED GAGE STAGE | No | 48 | Yes |
| BDBL1 | 76010 | 4.69 | 2026-10-09T21:45:00Z | NAVD88 | Yes | 192 | Yes |
| 85667 | 85667 | — | — | UNVERIFIED GAGE STAGE | No | 0 | Yes |
| BBOL1 | 52800 | 2.91 | 2026-10-08T11:00:00Z | NGVD29 stage | No | 48 | Yes |
| TSPL1 | 85300 | 4.22 | 2026-10-09T22:00:00Z | NGVD29 stage | No | 48 | Yes |
| PRSL1 | 76040 | 3.58 | 2026-10-09T23:00:00Z | UNVERIFIED GAGE STAGE | No | 48 | Yes |
| CMPL1 | 85750 | — | — | UNVERIFIED GAGE STAGE | No | 0 | Yes |
| WEGL1 | 85625 | 3.18 | 2026-10-09T22:00:00Z | NAVD88 | Yes | 48 | Yes |
| PLAL1 | 85670 | 3.31 | 2026-10-09T23:00:00Z | NAVD88 | Yes | 48 | Yes |
| SBNL1 | 76060 | 3.45 | 2026-10-09T23:00:00Z | NAVD88 | Yes | 48 | Yes |
| MWBL1 | 01515 | 4.20 | 2026-10-09T20:00:00Z | NAVD88 | Yes | 48 | Yes |
| VNCL1 | 01480 | 4.26 | 2026-10-09T21:00:00Z | NAVD88 | Yes | 48 | Yes |
| HPGL1 | 01545 | 3.65 | 2026-10-09T19:00:00Z | UNVERIFIED GAGE STAGE | No | 48 | Yes |
| CKBL1 | 01575 | 3.66 | 2026-10-09T20:00:00Z | UNVERIFIED GAGE STAGE | No | 48 | Yes |
| SWBL1 | 01670 | 3.55 | 2026-10-09T23:00:00Z | UNVERIFIED GAGE STAGE | No | 48 | Yes |
| WPHL1 | 01400 | 5.26 | 2026-10-09T21:00:00Z | NAVD88 | Yes | 48 | Yes |
| BDAL1 | 82700 | 2.89 | 2026-10-09T07:00:00Z | NGVD29 stage | No | 48 | Yes |
| BCSL1 | 01280 | 7.72 | 2026-10-09T23:00:00Z | NGVD29 stage | No | 48 | Yes |
| BCFL1 | 85552 | 3.51 | 2026-10-09T22:00:00Z | UNVERIFIED GAGE STAGE | No | 48 | Yes |
| LPML1 | 85575 | — | — | UNVERIFIED GAGE STAGE | No | 0 | Yes |
| 76305 | 76305 | 2.55 | 2026-10-09T21:00:00Z | NAVD88 | Yes | 48 | Yes |

## Evidence and limitations for each station

### BSGL1 — Bayou Segnette Sector Gate

- IDs: original `BSGL1`; official SID `82742`; MVN location `B_Segnette_SGate`; series `B_Segnette_SGate.Stage.Inst.15Minutes.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=B_Segnette_SGate.Stage.Inst.15Minutes.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/B_Segnette_SGate?office=MVN); [historical retrieval for this run](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=B_Segnette_SGate.Stage.Inst.15Minutes.0.rev&begin=2026-10-08T00%3A00%3A00%2B00%3A00&end=2026-10-10T00%3A00%3A00%2B00%3A00&units=ft&page-size=500). Original link: [RiverGages](https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=82742&fid=&dt=S).
- Template coordinates: 29.8968, -90.1567; official source coordinates: 29.8968083, -90.1566805. Original station metadata retained.
- Historical observations: retrieved. Source: USACE MVN CWMS (primary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: CWMS location datum alone does not establish observed stage datum; no gage-zero documentation retrieved.; 192/192 expected observations; first 2026-10-08T00:00:00+00:00, last 2026-10-09T23:45:00+00:00; missing 0; conflicts 0; CWMS location datum alone does not establish observed stage datum; no gage-zero documentation retrieved.
- Official gauge description: Located on flood side (Southwest side) of Sector Gates on Bayou Segnette.  ***THIS GAGE IS MAINTAINED AND OPERATED BY THE LOUISIANA COASTAL PROTECTION  AND RESTORATION AUTHORITY  (CPRA)*** .
- Direct-datum policy: Review required; no automatic datum conversion..

### LBWL1 — Barataria Waterway at Lafitte

- IDs: original `LBWL1`; official SID `82875`; MVN location `Barataria_Bay_WW`; series `Barataria_Bay_WW.Stage.Inst.15Minutes.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Barataria_Bay_WW.Stage.Inst.15Minutes.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/Barataria_Bay_WW?office=MVN); [historical retrieval for this run](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Barataria_Bay_WW.Stage.Inst.15Minutes.0.rev&begin=2026-10-08T00%3A00%3A00%2B00%3A00&end=2026-10-10T00%3A00%3A00%2B00%3A00&units=ft&page-size=500). Original link: [RiverGages](https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=82875&fid=&dt=S).
- Template coordinates: 29.6674, -90.1103; official source coordinates: 29.6694445, -90.1105555. Original station metadata retained.
- Historical observations: retrieved. Source: USACE MVN CWMS (primary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: Gage zero is set to NAVD88 (2009.55) on Nov. 22, 2021; CWMS station-specific gauge description (not location elevation); 192/192 expected observations; first 2026-10-08T00:00:00+00:00, last 2026-10-09T23:45:00+00:00; missing 0; conflicts 0; Same SID, hardened tower installed Nov 2021 after Ida destroyed former gauge; location changed. Template coordinates retained; source coordinates exposed for review. Pre-Nov-2021 epoch differs.
- Official gauge description: New gage installed onto hardened gage tower in Nov. 2021. The gage is located on the East bank of Bayou Barataria across from the confluence of Bayou Rigolettes. The gage zero is set to NAVD88 (2009.55) on Nov. 22, 2021. See below regarding the former gage datum/epoch. Former gage was destroyed during Hurricane Ida in Sept. 2021. It was located near the end of La. Hwy 3257, south of Joe's Landing, on  the West bank of Bayou Barataria (29.68198, -90.10404).  Vertical datum was set to NAVD88 (2004.65) on Sept 24, 2007, all prior data at NGVD29.***THIS GAGE IS MAINTAINED AND OPERATED BY THE LOUISIANA COASTAL PROTECTION  AND RESTORATION AUTHORITY  (CPRA)***.
- Direct-datum policy: {"kind": "direct", "datum": "NAVD88", "effective_start_utc": "2021-11-22T00:00:00Z", "evidence_text": "Gage zero is set to NAVD88 (2009.55) on Nov. 22, 2021", "evidence_source": "CWMS station-specific gauge description (not location elevation)"}.

### SBEL1 — IHNC Surge Barrier East - Flood Side

- IDs: original `SBEL1`; official SID `76030`; MVN location `IHNC_SurgeBar_E`; series `IHNC_SurgeBar_E.Stage.Inst.15Minutes.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=IHNC_SurgeBar_E.Stage.Inst.15Minutes.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/IHNC_SurgeBar_E?office=MVN); [historical retrieval for this run](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=IHNC_SurgeBar_E.Stage.Inst.15Minutes.0.rev&begin=2026-10-08T00%3A00%3A00%2B00%3A00&end=2026-10-10T00%3A00%3A00%2B00%3A00&units=ft&page-size=500). Original link: [RiverGages](https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=76030&fid=&dt=S).
- Template coordinates: 30.0123, -89.9005; official source coordinates: 30.0123888, -89.9005278. Original station metadata retained.
- Historical observations: retrieved. Source: USACE MVN CWMS (primary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: Flood side identity verified; location datum alone cannot qualify stage.; 179/192 expected observations; first 2026-10-08T00:00:00+00:00, last 2026-10-09T23:45:00+00:00; missing 13; conflicts 0; Flood side identity verified; location datum alone cannot qualify stage.
- Official gauge description: Located on the East side (flood side) wall of the IHNC (Inner Harbor Navigation Canal) / Lake Borgne Surge Barrier. Installed Oct 2010. ***THIS GAGE IS MAINTAINED AND OPERATED BY THE LOUISIANA COASTAL PROTECTION AND RESTORATION AUTHORITY (CPRA)***.
- Direct-datum policy: Review required; no automatic datum conversion..

### MBBL1 — Bayou Bienvenue Flood Gate

- IDs: original `MBBL1`; official SID `76025`; MVN location `Bayou_Bienvenue-East`; series `Bayou_Bienvenue-East.Stage.Inst.1Hour.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Bayou_Bienvenue-East.Stage.Inst.1Hour.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/Bayou_Bienvenue-East?office=MVN); [historical retrieval for this run](https://mesonet.agron.iastate.edu/cgi-bin/request/hml.py?station=MBBL1&kind=obs&tz=UTC&fmt=csv&year1=2026&month1=10&day1=8&year2=2026&month2=10&day2=10). Original link: [RiverGages](https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=76025&fid=&dt=S).
- Template coordinates: 29.9978, -89.9165; official source coordinates: 29.9987138, -89.9153417. Original station metadata retained.
- Historical observations: retrieved. Source: NWS HML archived by IEM (secondary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: Secondary NWS HML stage retained; measured datum not independently established; 188/48 expected observations; first 2026-10-08T00:00:00+00:00, last 2026-10-09T23:45:00+00:00; missing 1; conflicts 0; Flood-side legacy series latest catalog extent 2022-10-11. West/protected side is a separate gauge and is not substituted.
- Official gauge description: Mounted on the East/flood side of the Bayou Bienvenue floodgate structure, near the Mississippi River Gulf Outlet (MRGO). Vertical datum set to NAVD88 (2004.65).***THIS GAGE IS MAINTAINED AND OPERATED BY THE LOUISIANA COASTAL PROTECTION  AND RESTORATION AUTHORITY  (CPRA)***.
- Direct-datum policy: Review required; no automatic datum conversion..

### RGTL1 — Rigolets at Hwy 90

- IDs: original `RGTL1`; official SID `85700LA`; MVN location `Rigolets_LA`; series `Rigolets_LA.Stage.Inst.15Minutes.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Rigolets_LA.Stage.Inst.15Minutes.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/Rigolets_LA?office=MVN); [historical retrieval for this run](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Rigolets_LA.Stage.Inst.15Minutes.0.rev&begin=2026-10-08T00%3A00%3A00%2B00%3A00&end=2026-10-10T00%3A00%3A00%2B00%3A00&units=ft&page-size=500). Original link: [RiverGages](https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=85700LA&fid=&dt=S).
- Template coordinates: 30.1704, -89.7345; official source coordinates: 30.170391666667, -89.734463833333. Original station metadata retained.
- Historical observations: retrieved. Source: USACE MVN CWMS (primary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: LOCAL location datum conflicts with description stating NAVD88 (2009.55); require datum review.; 192/192 expected observations; first 2026-10-08T00:00:00+00:00, last 2026-10-09T23:45:00+00:00; missing 0; conflicts 0; LOCAL location datum conflicts with description stating NAVD88 (2009.55); require datum review.
- Official gauge description: Located on new HSDRRS Bridge StructureGage set to NAVD88 (2009.55)¿**GAGE IS MAINTATINED BE A NON-FEDERAL LOCAL SPONSOR**.
- Direct-datum policy: Review required; no automatic datum conversion..

### 76065 — Seabrook Floodgate - Lake Side

- IDs: original `76065`; official SID `76065`; MVN location `Seabrook_Brdge_N`; series `Seabrook_Brdge_N.Stage.Inst.15Minutes.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Seabrook_Brdge_N.Stage.Inst.15Minutes.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/Seabrook_Brdge_N?office=MVN); [historical retrieval for this run](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Seabrook_Brdge_N.Stage.Inst.15Minutes.0.rev&begin=2026-10-08T00%3A00%3A00%2B00%3A00&end=2026-10-10T00%3A00%3A00%2B00%3A00&units=ft&page-size=500). Original link: [RiverGages](https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=76065&fid=&dt=S).
- Template coordinates: 30.0304, -90.0347; official source coordinates: 30.0304167, -90.0346667. Original station metadata retained.
- Historical observations: retrieved. Source: USACE MVN CWMS (primary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: Gage Zero: 0 Ft. NAVD88; RiverGages indexed official station page (search inspection 2026-10-10); live CWMS identity verified each run; 192/192 expected observations; first 2026-10-08T00:00:00+00:00, last 2026-10-09T23:45:00+00:00; missing 0; conflicts 0; Exact SID/name/coordinates and CWMS series verified; source sampling and epoch require human review.
- Official gauge description: Gage located on Lake Pontchartrain side or flood side of closure structure near Seabrook Bridge (Leon C. Simon Drive).***THIS GAGE IS MAINTAINED AND OPERATED BY THE LOUISIANA COASTAL PROTECTION  AND RESTORATION AUTHORITY  (CPRA)*** .
- Direct-datum policy: {"kind": "direct", "datum": "NAVD88", "effective_start_utc": "2026-10-08T00:00:00Z", "evidence_text": "Gage Zero: 0 Ft. NAVD88", "evidence_source": "RiverGages indexed official station page (search inspection 2026-10-10); live CWMS identity verified each run"}.

### 76062 — Seabrook Floodgate - INHC side

- IDs: original `76062`; official SID `76062`; MVN location `Seabrook_Brdge_S`; series `Seabrook_Brdge_S.Stage.Inst.15Minutes.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Seabrook_Brdge_S.Stage.Inst.15Minutes.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/Seabrook_Brdge_S?office=MVN); [historical retrieval for this run](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Seabrook_Brdge_S.Stage.Inst.15Minutes.0.rev&begin=2026-10-08T00%3A00%3A00%2B00%3A00&end=2026-10-10T00%3A00%3A00%2B00%3A00&units=ft&page-size=500). Original link: [RiverGages](https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=76062&fid=&dt=S).
- Template coordinates: 30.0302, -90.0346; official source coordinates: 30.0302362, -90.0346167. Original station metadata retained.
- Historical observations: retrieved. Source: USACE MVN CWMS (primary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: Gage Zero: 0 Ft. NAVD88; RiverGages indexed official station page (search inspection 2026-10-10); live CWMS identity verified each run; 192/192 expected observations; first 2026-10-08T00:00:00+00:00, last 2026-10-09T23:45:00+00:00; missing 0; conflicts 0; Exact SID/name/coordinates and CWMS series verified; source sampling and epoch require human review.
- Official gauge description: Gage located on IHNC (Inter Harbor Navigation Canal) side or protected side of closure structure near Seabrook Bridge (Leon C. Simon Drive).***THIS GAGE IS MAINTAINED AND OPERATED BY THE LOUISIANA COASTAL PROTECTION  AND RESTORATION AUTHORITY  (CPRA)***.
- Direct-datum policy: {"kind": "direct", "datum": "NAVD88", "effective_start_utc": "2026-10-08T00:00:00Z", "evidence_text": "Gage Zero: 0 Ft. NAVD88", "evidence_source": "RiverGages indexed official station page (search inspection 2026-10-10); live CWMS identity verified each run"}.

### 85750LA — Chef Pass nr Hwy 90

- IDs: original `85750LA`; official SID `85750LA`; MVN location `Chef_Pass_LA`; series `Chef_Pass_LA.Stage.Inst.15Minutes.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Chef_Pass_LA.Stage.Inst.15Minutes.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/Chef_Pass_LA?office=MVN); [historical retrieval for this run](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Chef_Pass_LA.Stage.Inst.15Minutes.0.rev&begin=2026-10-08T00%3A00%3A00%2B00%3A00&end=2026-10-10T00%3A00%3A00%2B00%3A00&units=ft&page-size=500). Original link: [RiverGages](https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=85750LA&fid=&dt=S).
- Template coordinates: 30.0682, -89.803; official source coordinates: 30.068188833333, -89.802975. Original station metadata retained.
- Historical observations: none retrieved in this interval. Source: USACE MVN CWMS (primary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: No eligible observed values in requested window. No observations in requested window; distinct hardened CPRA gauge, not legacy 85750/CMPL1.
- Official gauge description: Located on new HSDRRS Gage StructureGage set to NAVD88 (2009.55) ¿**GAGE IS MAINTATINED BE A NON-FEDERAL LOCAL SPONSOR**.
- Direct-datum policy: Review required; no automatic datum conversion..

### COCL1 — Caernarvon Canal - Flood Side

- IDs: original `COCL1`; official SID `85760`; MVN location `Caernarvon_SG_S`; series `Caernarvon_SG_S.Stage.Inst.15Minutes.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Caernarvon_SG_S.Stage.Inst.15Minutes.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/Caernarvon_SG_S?office=MVN); [historical retrieval for this run](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Caernarvon_SG_S.Stage.Inst.15Minutes.0.rev&begin=2026-10-08T00%3A00%3A00%2B00%3A00&end=2026-10-10T00%3A00%3A00%2B00%3A00&units=ft&page-size=500). Original link: [RiverGages](https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=85760&fid=&dt=S).
- Template coordinates: 29.8587, -89.9068; official source coordinates: 29.8586667, -89.9068333. Original station metadata retained.
- Historical observations: retrieved. Source: USACE MVN CWMS (primary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: Public-name calls 85760 protected side; description and coordinates identify southeast flood side. Identity/SIDE conflict requires review.; 192/192 expected observations; first 2026-10-08T00:00:00+00:00, last 2026-10-09T23:45:00+00:00; missing 0; conflicts 0; Public-name calls 85760 protected side; description and coordinates identify southeast flood side. Identity/SIDE conflict requires review.
- Official gauge description: Located on flood side (southeast) of Caernarvon Canal Sector Gate.***THIS GAGE IS MAINTAINED AND OPERATED BY THE LOUISIANA COASTAL PROTECTION  AND RESTORATION AUTHORITY  (CPRA)***.
- Direct-datum policy: Review required; no automatic datum conversion..

### 01441 — Empire Floodgate - Flood Side

- IDs: original `01441`; official SID `01441`; MVN location `Empire_FloodGate-WaterSide`; series `Empire_FloodGate-WaterSide.Stage.Inst.15Minutes.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Empire_FloodGate-WaterSide.Stage.Inst.15Minutes.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/Empire_FloodGate-WaterSide?office=MVN); [historical retrieval for this run](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Empire_FloodGate-WaterSide.Stage.Inst.15Minutes.0.rev&begin=2026-10-08T00%3A00%3A00%2B00%3A00&end=2026-10-10T00%3A00%3A00%2B00%3A00&units=ft&page-size=500). Original link: [RiverGages](https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=01441&fid=&dt=S).
- Template coordinates: 29.3768, -89.6017; official source coordinates: 29.3766667, -89.6016667. Original station metadata retained.
- Historical observations: retrieved. Source: USACE MVN CWMS (primary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: Description lists current +0.032 ft adjustment and prior epoch changes; independent event-effective conversion not verified.; 192/192 expected observations; first 2026-10-08T00:00:00+00:00, last 2026-10-09T23:45:00+00:00; missing 0; conflicts 0; Description lists current +0.032 ft adjustment and prior epoch changes; independent event-effective conversion not verified.
- Official gauge description: Located on southern water side of the Empire Flood gate structure in Barataria Basin, Plaquemines Parish, LATransmitting Gage 0 = NAVD88 (2009.55) -0.05 on 18 April 2022. Data prior to 18 April 2022 was referenced to "gage datum". Add -0.62' to data prior to 18 April 2022 to adjust data to NAVD88 (2009.55)Current adjustment to NAVD88 2009.55 is 0.032' (e.g. add 0.032' to gage data to adjust to NAVD88 2009.55)¿**GAGE IS MAINTATINED BE A NON-FEDERAL LOCAL SPONSOR AS PARt OF HSDRRS PROJECT**.
- Direct-datum policy: Review required; no automatic datum conversion..

### WCCL1 — West Closure Complex - Flood Side

- IDs: original `WCCL1`; official SID `76265`; MVN location `WestCC _FS`; series `WestCC _FS.Stage.Inst.1Hour.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=WestCC+_FS.Stage.Inst.1Hour.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/WestCC%20_FS?office=MVN); [historical retrieval for this run](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=WestCC+_FS.Stage.Inst.1Hour.0.rev&begin=2026-10-08T00%3A00%3A00%2B00%3A00&end=2026-10-10T00%3A00%3A00%2B00%3A00&units=ft&page-size=500). Original link: **missing**.
- Template coordinates: 29.8158, -90.0686; official source coordinates: 29.8157639, -90.0685778. Original station metadata retained.
- Historical observations: retrieved. Source: USACE MVN CWMS (primary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: Previously missing link. Exact flood-side name and coordinates identify 76265 / WestCC _FS (literal embedded space). Datum needs measured-stage evidence.; 48/48 expected observations; first 2026-10-08T00:00:00+00:00, last 2026-10-09T23:00:00+00:00; missing 0; conflicts 0; Previously missing link. Exact flood-side name and coordinates identify 76265 / WestCC _FS (literal embedded space). Datum needs measured-stage evidence.
- Official gauge description: Gage located on the South/Flood Side of the West Closure Complex.***THIS GAGE IS MAINTAINED AND OPERATED BY THE LOUISIANA COASTAL PROTECTION  AND RESTORATION AUTHORITY  (CPRA)***.
- Direct-datum policy: Review required; no automatic datum conversion..

### BDBL1 — Bayou Dupre Flood Gate

- IDs: original `BDBL1`; official SID `76010`; MVN location `Bayou_Dupre-East`; series `Bayou_Dupre-East.Stage.Inst.15Minutes.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Bayou_Dupre-East.Stage.Inst.15Minutes.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/Bayou_Dupre-East?office=MVN); [historical retrieval for this run](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Bayou_Dupre-East.Stage.Inst.15Minutes.0.rev&begin=2026-10-08T00%3A00%3A00%2B00%3A00&end=2026-10-10T00%3A00%3A00%2B00%3A00&units=ft&page-size=500). Original link: [RiverGages](https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=76010&fid=&dt=S).
- Template coordinates: 29.9351, -89.8366; official source coordinates: 29.9351805, -89.8365972. Original station metadata retained.
- Historical observations: retrieved. Source: USACE MVN CWMS (primary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: Vertical datum set to NAVD88 (2004.65); CWMS station-specific gauge description (not location elevation); 192/192 expected observations; first 2026-10-08T00:00:00+00:00, last 2026-10-09T23:45:00+00:00; missing 0; conflicts 0; Exact SID/name/coordinates and CWMS series verified; source sampling and epoch require human review.
- Official gauge description: Mounted on the East (or MRGO) side of the Bayou Dupre Sector Gate control structure near the Mississippi River Gulf Outlet (MRGO). Vertical datum set to NAVD88 (2004.65). ***THIS GAGE IS MAINTAINED AND OPERATED BY THE LOUISIANA COASTAL PROTECTION AND RESTORATION AUTHORITY (CPRA)***.
- Direct-datum policy: {"kind": "direct", "datum": "NAVD88", "effective_start_utc": "2026-10-08T00:00:00Z", "evidence_text": "Vertical datum set to NAVD88 (2004.65)", "evidence_source": "CWMS station-specific gauge description (not location elevation)"}.

### 85667 — Walker Drainage Structure - Flood Side

- IDs: original `85667`; official SID `85667`; MVN location `Walker_DS_FS`; series `Walker_DS_FS.Stage.Inst.15Minutes.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Walker_DS_FS.Stage.Inst.15Minutes.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/Walker_DS_FS?office=MVN); [historical retrieval for this run](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Walker_DS_FS.Stage.Inst.15Minutes.0.rev&begin=2026-10-08T00%3A00%3A00%2B00%3A00&end=2026-10-10T00%3A00%3A00%2B00%3A00&units=ft&page-size=500). Original link: [RiverGages](https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=85667&fid=&dt=S).
- Template coordinates: 29.9904, -90.2909; official source coordinates: 29.990408333333, -90.290941666667. Original station metadata retained.
- Historical observations: none retrieved in this interval. Source: USACE MVN CWMS (primary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: No eligible observed values in requested window. No observations in requested window. LOCAL metadata and no explicit measured-stage datum.
- Official gauge description: Gauge located on west or flood side Walker Drainage Structure. ***THIS GAGE IS MAINTAINED AND OPERATED BY THE LOUISIANA COASTAL PROTECTION  AND RESTORATION AUTHORITY  (CPRA)***.
- Direct-datum policy: Review required; no automatic datum conversion..

### BBOL1 — Bayou Boeuf at Amelia

- IDs: original `BBOL1`; official SID `52800`; MVN location `Bayou_Boeuf-Amelia`; series `Bayou_Boeuf-Amelia.Stage.Inst.1Hour.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Bayou_Boeuf-Amelia.Stage.Inst.1Hour.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/Bayou_Boeuf-Amelia?office=MVN); [historical retrieval for this run](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Bayou_Boeuf-Amelia.Stage.Inst.1Hour.0.rev&begin=2026-10-08T00%3A00%3A00%2B00%3A00&end=2026-10-10T00%3A00%3A00%2B00%3A00&units=ft&page-size=500). Original link: [RiverGages](https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=52800&fid=&dt=S).
- Template coordinates: 29.6684, -91.0984; official source coordinates: 29.8691, -90.5949917. Original station metadata retained.
- Historical observations: retrieved. Source: USACE MVN CWMS (primary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: CWMS coordinates conflict (~54 km) with template and official RiverGages indexed page. SID/name and HML observations agree. Preserve peak for identity/datum review. NGVD29; -1.40 ft offset dated 2025-04-14 needs independent verification.; 48/48 expected observations; first 2026-10-08T00:00:00+00:00, last 2026-10-09T23:00:00+00:00; missing 0; conflicts 0; CWMS coordinates conflict (~54 km) with template and official RiverGages indexed page. SID/name and HML observations agree. Preserve peak for identity/datum review. NGVD29; -1.40 ft offset dated 2025-04-14 needs independent verification.
- Official gauge description: Located just north of railroad and Hwy 90 bridges.  Current stage data relative to vertical datum NGVD29.     Adjustment for vertical datum NAVD88: -1.40' ft.(e.g. add -1.40' to gage data to adjust to NAVD88.) Adjustment valid as of 04/14/2025.
- Direct-datum policy: Review required; no automatic datum conversion..

### TSPL1 — Tickfaw River near Springfield

- IDs: original `TSPL1`; official SID `85300`; MVN location `Tickfaw_River-Springfield`; series `Tickfaw_River-Springfield.Stage.Inst.1Hour.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Tickfaw_River-Springfield.Stage.Inst.1Hour.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/Tickfaw_River-Springfield?office=MVN); [historical retrieval for this run](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Tickfaw_River-Springfield.Stage.Inst.1Hour.0.rev&begin=2026-10-08T00%3A00%3A00%2B00%3A00&end=2026-10-10T00%3A00%3A00%2B00%3A00&units=ft&page-size=500). Original link: [RiverGages](https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=85300&fid=&dt=S).
- Template coordinates: 30.3767, -90.5506; official source coordinates: 30.376555, -90.55111. Original station metadata retained.
- Historical observations: retrieved. Source: USACE MVN CWMS (primary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: RiverGages reports NGVD gage zero and -1.35 ft NAVD88 offset (2014-09-24), conflicting with CWMS location NAVD88. No automatic conversion.; 48/48 expected observations; first 2026-10-08T00:00:00+00:00, last 2026-10-09T23:00:00+00:00; missing 0; conflicts 0; RiverGages reports NGVD gage zero and -1.35 ft NAVD88 offset (2014-09-24), conflicting with CWMS location NAVD88. No automatic conversion.
- Official gauge description: Gage located on Highway 22 bridge, 3.7 miles south of Springfield, LA..
- Direct-datum policy: Review required; no automatic datum conversion..

### PRSL1 — GIWW nr Paris Rd Bridge

- IDs: original `PRSL1`; official SID `76040`; MVN location `GIWW_Paris_Rd`; series `GIWW_Paris_Rd.Stage.Inst.1Hour.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=GIWW_Paris_Rd.Stage.Inst.1Hour.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/GIWW_Paris_Rd?office=MVN); [historical retrieval for this run](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=GIWW_Paris_Rd.Stage.Inst.1Hour.0.rev&begin=2026-10-08T00%3A00%3A00%2B00%3A00&end=2026-10-10T00%3A00%3A00%2B00%3A00&units=ft&page-size=500). Original link: [RiverGages](https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=76040&fid=&dt=S).
- Template coordinates: 30.0067, -89.9374; official source coordinates: 30.0067055, -89.9373612. Original station metadata retained.
- Historical observations: retrieved. Source: USACE MVN CWMS (primary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: Location NAVD88 alone is insufficient to prove stage datum.; 48/48 expected observations; first 2026-10-08T00:00:00+00:00, last 2026-10-09T23:00:00+00:00; missing 0; conflicts 0; Location NAVD88 alone is insufficient to prove stage datum.
- Official gauge description: Located approximately 600 ft east of the Paris Road (I-510) bridge on the north bank of the Intracoastal Waterway..
- Direct-datum policy: Review required; no automatic datum conversion..

### CMPL1 — Chef Manteur Pass nr Lake Borgne

- IDs: original `CMPL1`; official SID `85750`; MVN location `Chef_Menteur`; series `Chef_Menteur.Stage.Inst.1Hour.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Chef_Menteur.Stage.Inst.1Hour.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/Chef_Menteur?office=MVN); [historical retrieval for this run](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Chef_Menteur.Stage.Inst.1Hour.0.rev&begin=2026-10-08T00%3A00%3A00%2B00%3A00&end=2026-10-10T00%3A00%3A00%2B00%3A00&units=ft&page-size=500). Original link: [RiverGages](https://rivergages.mvr.usace.army.mil/WaterControl/shefdata2.cfm?sid=85750&d=7&dt=S).
- Template coordinates: 30.0667, -89.801; official source coordinates: 30.066738833333, -89.801027833333. Original station metadata retained.
- Historical observations: none retrieved in this interval. Source: USACE MVN CWMS (primary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: No eligible observed values in requested window. Legacy gauge 85750 series ends 2024-02-20 in catalog. Nearby hardened 85750LA is separately inventoried; no replacement substitution.
- Official gauge description: (not provided).
- Direct-datum policy: Review required; no automatic datum conversion..

### WEGL1 — Lake Pontchartrain - West End

- IDs: original `WEGL1`; official SID `85625`; MVN location `Lake_Pont-WestEnd`; series `Lake_Pont-WestEnd.Stage.Inst.1Hour.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Lake_Pont-WestEnd.Stage.Inst.1Hour.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/Lake_Pont-WestEnd?office=MVN); [historical retrieval for this run](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Lake_Pont-WestEnd.Stage.Inst.1Hour.0.rev&begin=2026-10-08T00%3A00%3A00%2B00%3A00&end=2026-10-10T00%3A00%3A00%2B00%3A00&units=ft&page-size=500). Original link: [RiverGages](https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=85625&fid=&dt=S).
- Template coordinates: 30.0222, -90.1156; official source coordinates: 30.0221638, -90.1156444. Original station metadata retained.
- Historical observations: retrieved. Source: USACE MVN CWMS (primary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: Vertical datum set to NAVD88 (2004.65) on December 19, 2006; RiverGages indexed official station page (search inspection 2026-10-10); live CWMS identity verified each run; 48/48 expected observations; first 2026-10-08T00:00:00+00:00, last 2026-10-09T23:00:00+00:00; missing 0; conflicts 0; Official RiverGages indexed station page states zero NAVD88 and datum reset 2006-12-19; CWMS lacks datum. Exact coordinates and series checked.
- Official gauge description: Lake Pontchartrain at West End (85625).
- Direct-datum policy: {"kind": "direct", "datum": "NAVD88", "effective_start_utc": "2006-12-20T00:00:00Z", "evidence_text": "Vertical datum set to NAVD88 (2004.65) on December 19, 2006", "evidence_source": "RiverGages indexed official station page (search inspection 2026-10-10); live CWMS identity verified each run"}.

### PLAL1 — Lake Pontchartrain - Lakefront AP

- IDs: original `PLAL1`; official SID `85670`; MVN location `Lake_Pon_Lkfront`; series `Lake_Pon_Lkfront.Stage.Inst.1Hour.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Lake_Pon_Lkfront.Stage.Inst.1Hour.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/Lake_Pon_Lkfront?office=MVN); [historical retrieval for this run](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Lake_Pon_Lkfront.Stage.Inst.1Hour.0.rev&begin=2026-10-08T00%3A00%3A00%2B00%3A00&end=2026-10-10T00%3A00%3A00%2B00%3A00&units=ft&page-size=500). Original link: [RiverGages](https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=85670&fid=&dt=S).
- Template coordinates: 30.0399, -90.0188; official source coordinates: 30.0399445, -90.018813833333. Original station metadata retained.
- Historical observations: retrieved. Source: USACE MVN CWMS (primary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: Vertical datum set to NAVD88 (2004.65); CWMS station-specific gauge description (not location elevation); 48/48 expected observations; first 2026-10-08T00:00:00+00:00, last 2026-10-09T23:00:00+00:00; missing 0; conflicts 0; Exact SID/name/coordinates and CWMS series verified; source sampling and epoch require human review.
- Official gauge description: Located on east side of Lakefront Airport at the harbor.  Vertical datum set to NAVD88 (2004.65)..
- Direct-datum policy: {"kind": "direct", "datum": "NAVD88", "effective_start_utc": "2026-10-08T00:00:00Z", "evidence_text": "Vertical datum set to NAVD88 (2004.65)", "evidence_source": "CWMS station-specific gauge description (not location elevation)"}.

### SBNL1 — Seabrook Bridge at IHNC

- IDs: original `SBNL1`; official SID `76060`; MVN location `IHNC_S_Seabrook`; series `IHNC_S_Seabrook.Stage.Inst.1Hour.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=IHNC_S_Seabrook.Stage.Inst.1Hour.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/IHNC_S_Seabrook?office=MVN); [historical retrieval for this run](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=IHNC_S_Seabrook.Stage.Inst.1Hour.0.rev&begin=2026-10-08T00%3A00%3A00%2B00%3A00&end=2026-10-10T00%3A00%3A00%2B00%3A00&units=ft&page-size=500). Original link: [RiverGages](https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=76060&fid=&dt=S).
- Template coordinates: 30.0242, -90.0313; official source coordinates: 30.0241722, -90.0312945. Original station metadata retained.
- Historical observations: retrieved. Source: USACE MVN CWMS (primary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: Vertical datum NAVD88 (2004.65) established June 2, 2010; CWMS station-specific gauge description (not location elevation); 48/48 expected observations; first 2026-10-08T00:00:00+00:00, last 2026-10-09T23:00:00+00:00; missing 0; conflicts 0; Exact SID/name/coordinates and CWMS series verified; source sampling and epoch require human review.
- Official gauge description: - Located on east bank of Inner Habor Navigation Canal approx 900 yards south of the Seabrook Bridge.  Vertical datum NAVD88 (2004.65) established June 2, 2010, prior historic stage data is relative to datum NGVD..
- Direct-datum policy: {"kind": "direct", "datum": "NAVD88", "effective_start_utc": "2010-06-03T00:00:00Z", "evidence_text": "Vertical datum NAVD88 (2004.65) established June 2, 2010", "evidence_source": "CWMS station-specific gauge description (not location elevation)"}.

### MWBL1 — MS River at West Bay

- IDs: original `MWBL1`; official SID `01515`; MVN location `West_Bay`; series `West_Bay.Stage.Inst.1Hour.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=West_Bay.Stage.Inst.1Hour.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/West_Bay?office=MVN); [historical retrieval for this run](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=West_Bay.Stage.Inst.1Hour.0.rev&begin=2026-10-08T00%3A00%3A00%2B00%3A00&end=2026-10-10T00%3A00%3A00%2B00%3A00&units=ft&page-size=500). Original link: [RiverGages](https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=01515&fid=&dt=S).
- Template coordinates: 29.2401, -89.2984; official source coordinates: 29.2401306, -89.2983972. Original station metadata retained.
- Historical observations: retrieved. Source: USACE MVN CWMS (primary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: for data relative to NAVD88 since 28Jun2015, no adjustment is necessary; CWMS station-specific gauge description (not location elevation); 48/48 expected observations; first 2026-10-08T00:00:00+00:00, last 2026-10-09T23:00:00+00:00; missing 0; conflicts 0; Exact SID/name/coordinates and CWMS series verified; source sampling and epoch require human review.
- Official gauge description: Located on left descending bank of the Mississippi River on a Coast Guard tower which is across the river and slightly upstream from the CWPPRA West Bay Sediment Diversion channel.Adjustment for vertical datum NAVD88 (2009.55): 0.00 ft. as of 28Jun2015(e.g. for data relative to NAVD88 since 28Jun2015, no adjustment is necessary) Gage reset to vertical datum NAVD88 (2004.65) on 30Jan2009. All prior stage data is relative to NGVD29..
- Direct-datum policy: {"kind": "direct", "datum": "NAVD88", "effective_start_utc": "2015-06-29T00:00:00Z", "evidence_text": "for data relative to NAVD88 since 28Jun2015, no adjustment is necessary", "evidence_source": "CWMS station-specific gauge description (not location elevation)"}.

### VNCL1 — MS River at Venice

- IDs: original `VNCL1`; official SID `01480`; MVN location `Venice`; series `Venice.Stage.Inst.1Hour.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Venice.Stage.Inst.1Hour.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/Venice?office=MVN); [historical retrieval for this run](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Venice.Stage.Inst.1Hour.0.rev&begin=2026-10-08T00%3A00%3A00%2B00%3A00&end=2026-10-10T00%3A00%3A00%2B00%3A00&units=ft&page-size=500). Original link: [RiverGages](https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=01480&fid=&dt=S).
- Template coordinates: 29.2758, -89.3528; official source coordinates: 29.2732783, -89.35243. Original station metadata retained.
- Historical observations: retrieved. Source: USACE MVN CWMS (primary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: Gage zero reset to vertical datum NAVD88 (2009.55) on 28Jun2015; CWMS station-specific gauge description (not location elevation); 48/48 expected observations; first 2026-10-08T00:00:00+00:00, last 2026-10-09T23:00:00+00:00; missing 0; conflicts 0; Exact SID/name/coordinates and CWMS series verified; source sampling and epoch require human review.
- Official gauge description: Located on right descending bank at river mile 10.7 at Venice, LA.  Gage zero reset to vertical datum NAVD88 (2009.55) on 28Jun2015. All prior historic stage data is relative to NGVD29.  To adjust the prior historic data (from 03Jun1987 to 28Jun2015 only) to NAVD88 (2009.55), add -1.84 feet.To adjust NAVD88 (2009.55) values to 2007 Low Water Reference Plane (LWRP) datum relative to NAVD88, add -0.1 ft..
- Direct-datum policy: {"kind": "direct", "datum": "NAVD88", "effective_start_utc": "2015-06-29T00:00:00Z", "evidence_text": "Gage zero reset to vertical datum NAVD88 (2009.55) on 28Jun2015", "evidence_source": "CWMS station-specific gauge description (not location elevation)"}.

### HPGL1 — MS River Head of Passes

- IDs: original `HPGL1`; official SID `01545`; MVN location `Head_of_Passes`; series `Head_of_Passes.Stage.Inst.1Hour.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Head_of_Passes.Stage.Inst.1Hour.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/Head_of_Passes?office=MVN); [historical retrieval for this run](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Head_of_Passes.Stage.Inst.1Hour.0.rev&begin=2026-10-08T00%3A00%3A00%2B00%3A00&end=2026-10-10T00%3A00%3A00%2B00%3A00&units=ft&page-size=500). Original link: [RiverGages](https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=01545&fid=HPGL1&dt=S).
- Template coordinates: 29.1338, -89.2465; official source coordinates: 29.1337778, -89.2465278. Original station metadata retained.
- Historical observations: retrieved. Source: USACE MVN CWMS (primary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: Current -0.018 ft NAVD88 adjustment documented as of 2015-09-30; no independent event-effective conversion verified.; 48/48 expected observations; first 2026-10-08T00:00:00+00:00, last 2026-10-09T23:00:00+00:00; missing 0; conflicts 0; Current -0.018 ft NAVD88 adjustment documented as of 2015-09-30; no independent event-effective conversion verified.
- Official gauge description: Located on Mississippi River 0.6 mile downstream from the zero (0) mile point. Gage inspection from 1/15/08 showed new gage was set to the same water surface elevation as the existing gage; gage adjustment from NAVD88 (2004.65) to NGVD29 (1983) assumed to = 0.0'Adjustment for vertical datum NAVD88 (2009.55): -0.018 ft. as of 30Sep2015 (add -0.018' to gage data to adjust to NAVD88 2009.55).
- Direct-datum policy: Review required; no automatic datum conversion..

### CKBL1 — MS River at MM 7.5 - Burrwoood

- IDs: original `CKBL1`; official SID `01575`; MVN location `SWPass_BHP`; series `SWPass_BHP.Stage.Inst.1Hour.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=SWPass_BHP.Stage.Inst.1Hour.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/SWPass_BHP?office=MVN); [historical retrieval for this run](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=SWPass_BHP.Stage.Inst.1Hour.0.rev&begin=2026-10-08T00%3A00%3A00%2B00%3A00&end=2026-10-10T00%3A00%3A00%2B00%3A00&units=ft&page-size=500). Original link: [RiverGages](https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=01575&fid=&dt=S).
- Template coordinates: 29.0564, -89.3086; official source coordinates: 29.0563778, -89.3086306. Original station metadata retained.
- Historical observations: retrieved. Source: USACE MVN CWMS (primary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: Gauge moved from mile 9.2 to mile 7.5 BHP (Dec 2010); current -0.48 ft adjustment as of 2022-09-22 needs independent verification.; 48/48 expected observations; first 2026-10-08T00:00:00+00:00, last 2026-10-09T23:00:00+00:00; missing 0; conflicts 0; Gauge moved from mile 9.2 to mile 7.5 BHP (Dec 2010); current -0.48 ft adjustment as of 2022-09-22 needs independent verification.
- Official gauge description: Located on Mississippi River - Southwest Pass at mile 7.5 below Head of Passes (BHP).  Gage reinstalled December 2010 with vertical reference relative to datum NAVD88.  Previous gauge site was at mile 9.2 BHP.Adjustment for vertical datum NAVD88 (OPUS 2022): -0.48 ft. as of 22Sep2022(e.g. for data relative to NAVD88 since 22Sep2022, subtract 0.48 ft)Adjustment for vertical datum NAVD88 (2009.55): 0.00 ft. as of 29Jun2015 Gage reset to vertical datum NAVD88 (2004.65) on 19Aug2010. All prior stage data is relative to NGVD29..
- Direct-datum policy: Review required; no automatic datum conversion..

### SWBL1 — MS River SW Pass at East Jetty

- IDs: original `SWBL1`; official SID `01670`; MVN location `SWPass_EJetty`; series `SWPass_EJetty.Stage.Inst.1Hour.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=SWPass_EJetty.Stage.Inst.1Hour.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/SWPass_EJetty?office=MVN); [historical retrieval for this run](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=SWPass_EJetty.Stage.Inst.1Hour.0.rev&begin=2026-10-08T00%3A00%3A00%2B00%3A00&end=2026-10-10T00%3A00%3A00%2B00%3A00&units=ft&page-size=500). Original link: [RiverGages](https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=01670&fid=&dt=S).
- Template coordinates: 28.9323, -89.4071; official source coordinates: 28.9323056, -89.4071111. Original station metadata retained.
- Historical observations: retrieved. Source: USACE MVN CWMS (primary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: RiverGages reports gage datum and -0.48 ft NAVD88 offset as of 2018-09-29 despite CWMS NAVD88 location; no automatic conversion.; 48/48 expected observations; first 2026-10-08T00:00:00+00:00, last 2026-10-09T23:00:00+00:00; missing 0; conflicts 0; RiverGages reports gage datum and -0.48 ft NAVD88 offset as of 2018-09-29 despite CWMS NAVD88 location; no automatic conversion.
- Official gauge description: On left descending bank at Pilot Station, about 17.9 miles below or South of Head of Passes. The station is located on the railing of the concrete walkway leading to the Pilot Station.  Gage reinstalled on October 3, 2007..
- Direct-datum policy: Review required; no automatic datum conversion..

### WPHL1 — MS River nr W Point A La Hache

- IDs: original `WPHL1`; official SID `01400`; MVN location `West_Pointe`; series `West_Pointe.Stage.Inst.1Hour.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=West_Pointe.Stage.Inst.1Hour.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/West_Pointe?office=MVN); [historical retrieval for this run](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=West_Pointe.Stage.Inst.1Hour.0.rev&begin=2026-10-08T00%3A00%3A00%2B00%3A00&end=2026-10-10T00%3A00%3A00%2B00%3A00&units=ft&page-size=500). Original link: [RiverGages](https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=01400&fid=&dt=S).
- Template coordinates: 29.5711, -89.7969; official source coordinates: 29.5711111, -89.7969444. Original station metadata retained.
- Historical observations: retrieved. Source: USACE MVN CWMS (primary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: Gage zero reset again to NAVD88 (2009.55) on 01Jul2015; CWMS station-specific gauge description (not location elevation); 48/48 expected observations; first 2026-10-08T00:00:00+00:00, last 2026-10-09T23:00:00+00:00; missing 0; conflicts 0; Exact SID/name/coordinates and CWMS series verified; source sampling and epoch require human review.
- Official gauge description: Located on right descending bank at the ferry landing, river mile 48.7. Gage zero reset to NAVD88 (2004.65) on 29Nov2005. All prior historic stage data is relative to NGVD29.  To adjust prior historic data (from 24Oct1984 to 29Nov2005 only), to NAVD88 (2004.65), subtract 0.84 ft. Gage zero reset again to NAVD88 (2009.55) on 01Jul2015. To adjust prior NAVD88 (2004.65) data to NAVD88 (2009.55), subtract 0.21 feet. To adjust NAVD88 (2009.55) values to 2007 Low Water Reference Plane (LWRP) datum relative to NAVD88, subtract 0.3 ft..
- Direct-datum policy: {"kind": "direct", "datum": "NAVD88", "effective_start_utc": "2015-07-02T00:00:00Z", "evidence_text": "Gage zero reset again to NAVD88 (2009.55) on 01Jul2015", "evidence_source": "CWMS station-specific gauge description (not location elevation)"}.

### BDAL1 — Bayou Des Allemands at Des Allemands

- IDs: original `BDAL1`; official SID `82700`; MVN location `Bayou_Des_Allemands`; series `Bayou_Des_Allemands.Stage.Inst.1Hour.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Bayou_Des_Allemands.Stage.Inst.1Hour.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/Bayou_Des_Allemands?office=MVN); [historical retrieval for this run](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Bayou_Des_Allemands.Stage.Inst.1Hour.0.rev&begin=2026-10-08T00%3A00%3A00%2B00%3A00&end=2026-10-10T00%3A00%3A00%2B00%3A00&units=ft&page-size=500). Original link: [RiverGages](https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=82700&fid=&dt=S).
- Template coordinates: 29.8239, -90.4767; official source coordinates: 29.8238888, -90.4766667. Original station metadata retained.
- Historical observations: retrieved. Source: USACE MVN CWMS (primary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: NGVD29 observed stage; template NGVD29 retained, PSH NAVD88/MHHW not populated.; 48/48 expected observations; first 2026-10-08T00:00:00+00:00, last 2026-10-09T23:00:00+00:00; missing 0; conflicts 0; NGVD29 observed stage; template NGVD29 retained, PSH NAVD88/MHHW not populated.
- Official gauge description: Located on Highway 631 Bridge, Des Allemands, La..
- Direct-datum policy: Review required; no automatic datum conversion..

### BCSL1 — MS River at Bonnet Carre Spillway

- IDs: original `BCSL1`; official SID `01280`; MVN location `Bonnet_Carre`; series `Bonnet_Carre.Stage.Inst.1Hour.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Bonnet_Carre.Stage.Inst.1Hour.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/Bonnet_Carre?office=MVN); [historical retrieval for this run](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Bonnet_Carre.Stage.Inst.1Hour.0.rev&begin=2026-10-08T00%3A00%3A00%2B00%3A00&end=2026-10-10T00%3A00%3A00%2B00%3A00&units=ft&page-size=500). Original link: [RiverGages](https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=01280&fid=&dt=S).
- Template coordinates: 29.9974, -90.4248; official source coordinates: 29.9973889, -90.4248194. Original station metadata retained.
- Historical observations: retrieved. Source: USACE MVN CWMS (primary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: NGVD29 stage, documented -0.89 ft offset lacks independent event-effective evidence; no automatic conversion.; 48/48 expected observations; first 2026-10-08T00:00:00+00:00, last 2026-10-09T23:00:00+00:00; missing 0; conflicts 0; NGVD29 stage, documented -0.89 ft offset lacks independent event-effective evidence; no automatic conversion.
- Official gauge description: On left descending bank near lower guide levee of Bonnet Carre Spillway at Mile 126.9.Adjustment for vertical datum NAVD88 (2009.55):  -0.89ft. (e.g. add -0.89 to gage data to adjust to NAVD88) To adjust NAVD88 (2009.55) values to 2007 Low Water Reference Plane (LWRP) datum relative to NAVD88, subtract 0.9 ft..
- Direct-datum policy: Review required; no automatic datum conversion..

### BCFL1 — Lake Pontchartrain at Bonnet Carre Sp

- IDs: original `BCFL1`; official SID `85552`; MVN location `Lake_Pont_BC_I10`; series `Lake_Pont_BC_I10.Stage.Inst.1Hour.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Lake_Pont_BC_I10.Stage.Inst.1Hour.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/Lake_Pont_BC_I10?office=MVN); [historical retrieval for this run](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Lake_Pont_BC_I10.Stage.Inst.1Hour.0.rev&begin=2026-10-08T00%3A00%3A00%2B00%3A00&end=2026-10-10T00%3A00%3A00%2B00%3A00&units=ft&page-size=500). Original link: [RiverGages](https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=85552&fid=&dt=S).
- Template coordinates: 30.0679, -90.3899; official source coordinates: 30.06785, -90.389938888889. Original station metadata retained.
- Historical observations: retrieved. Source: USACE MVN CWMS (primary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: RiverGages says NAVD without epoch/version, CWMS location NAVD88; measured-stage datum requires review.; 48/48 expected observations; first 2026-10-08T00:00:00+00:00, last 2026-10-09T23:00:00+00:00; missing 0; conflicts 0; RiverGages says NAVD without epoch/version, CWMS location NAVD88; measured-stage datum requires review.
- Official gauge description: The station is located on I-10, at mile marker 213 on a “turn-around” on the Bonnet Carre Causeway, east of Laplace, LA.**Raw data, subject to change**.
- Direct-datum policy: Review required; no automatic datum conversion..

### LPML1 — Lake Pontchartrain - Mandeville

- IDs: original `LPML1`; official SID `85575`; MVN location `Lake_Pon_Mandvil`; series `Lake_Pon_Mandvil.Stage.Inst.1Hour.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Lake_Pon_Mandvil.Stage.Inst.1Hour.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/Lake_Pon_Mandvil?office=MVN); [historical retrieval for this run](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Lake_Pon_Mandvil.Stage.Inst.1Hour.0.rev&begin=2026-10-08T00%3A00%3A00%2B00%3A00&end=2026-10-10T00%3A00%3A00%2B00%3A00&units=ft&page-size=500). Original link: [RiverGages](https://rivergages.mvr.usace.army.mil/WaterControl/shefdata2.cfm?sid=85575&d=7&dt=S).
- Template coordinates: 30.3658, -90.0923; official source coordinates: 30.365797222222, -90.092288888889. Original station metadata retained.
- Historical observations: none retrieved in this interval. Source: USACE MVN CWMS (primary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: No eligible observed values in requested window. Historic-only old pier series ends 2023-11-16. Mandeville_LA hardened gauge is a different location (~430m); not substituted.
- Official gauge description: Mounted on pier on west side of harbor.  Vertical datum set to NAVD88 (2009.55). Historic data available only. Current stage data can be accessed by the HSDRRES hardened gage site .
- Direct-datum policy: Review required; no automatic datum conversion..

### 76305 — Bayou Petit Caillou at Cocodrie

- IDs: original `76305`; official SID `76305`; MVN location `Cocodrie`; series `Cocodrie.Stage.Inst.1Hour.0.rev`.
- [Current observations](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Cocodrie.Stage.Inst.1Hour.0.rev&units=ft); [official station metadata](https://cwms-data.usace.army.mil/cwms-data/locations/Cocodrie?office=MVN); [historical retrieval for this run](https://cwms-data.usace.army.mil/cwms-data/timeseries?office=MVN&name=Cocodrie.Stage.Inst.1Hour.0.rev&begin=2026-10-08T00%3A00%3A00%2B00%3A00&end=2026-10-10T00%3A00%3A00%2B00%3A00&units=ft&page-size=500). Original link: [RiverGages](https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=76305&fid=&dt=S).
- Template coordinates: 29.2543, -90.6635; official source coordinates: 29.25425, -90.6635278. Original station metadata retained.
- Historical observations: retrieved. Source: USACE MVN CWMS (primary). Returned units: ft. Observation timestamps: UTC from epoch milliseconds (CWMS) or explicit valid[UTC] column (HML).
- Qualification and availability: Gage zero set to NAVD88 (2004.65) on 10/11/2011; CWMS station-specific gauge description (not location elevation); 48/48 expected observations; first 2026-10-08T00:00:00+00:00, last 2026-10-09T23:00:00+00:00; missing 0; conflicts 0; Exact SID/name/coordinates and CWMS series verified; source sampling and epoch require human review.
- Official gauge description: On the small dock behind/west of the LUMCON building, 8124 Highway 56, Chauvin, La., 0.5 miles north of the end of State Hwy 56.Gage zero set to NAVD88 (2004.65) on 10/11/2011.
- Direct-datum policy: {"kind": "direct", "datum": "NAVD88", "effective_start_utc": "2011-10-12T00:00:00Z", "evidence_text": "Gage zero set to NAVD88 (2004.65) on 10/11/2011", "evidence_source": "CWMS station-specific gauge description (not location elevation)"}.

## Verification and operational deployment

The full actual Isaias pipeline was run with `STORM_NAME="Hurricane Isaias" START_UTC=2026-10-08 END_UTC=2026-10-09`. END_UTC is an **inclusive UTC date**, so October 9 produces the requested exclusive October 10 midnight bound. The rainfall collector retains its existing noon-to-noon convention unless both rainfall override timestamps are supplied; its window is separately stated in QC.

`python scripts/validate.py`, `python scripts/export_dashboard.py`, and `python scripts/validate.py --site` passed with 315 audited measurements, 9 workbook tabs plus Provenance, and all storm-specific downloads. Every coastal peak and timestamp was independently recomputed from captured source responses. The template patch changes only Water Level hyperlink XML and hyperlink relationships: exactly 31 links, no cell value/style/formula changes. Test results are recorded in verification.json and the PR.

After merge, open **Actions → Build PSH workbook → Run workflow**, select **main**, and enter storm_name `Hurricane Isaias`, start_utc `2026-10-08`, end_utc `2026-10-09`. Leave reviewed_import and datum_registry empty unless supplying committed, independently reviewed files. Optional Francine regression remains available. No PR or branch dispatch can publish. Main pushes run tests; only explicit main workflow_dispatch regenerates and deploys the operational website.

The collect job requires successful tests, validates workbook/provenance and site exports, uploads review artifacts, deploys GitHub Pages, and then fetches the public site to verify its complete manifest, Water Level tab, review data and coastal review CSV match the validated build. A stale or missing deployment fails this final check. Check `Verify deployed Water Level tab and station review` and the deployment URL before using the website.

Updated publication is intentionally **not performed before merge**. The PR contains a regenerated local export and review package. Post-merge production verification remains a future operational action, enforced by the new workflow check.
