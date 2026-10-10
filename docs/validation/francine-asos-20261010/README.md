# Francine ASOS sustained-wind investigation — 2026-10-10 UTC

Requested interval: **2024-09-10 00:00 UTC inclusive through 2024-09-13 00:00 UTC exclusive** (September 10–12). All speeds below are knots. **The appropriate available PSH sustained peaks are KBTR 27, KMSY 50, KNEW 42, KPQL 23.** KBTR required a collector correction; the other three generated peaks are retained.

| Station | Reference | NOAA/IEM minute archive: highest 2-minute mean | Routine METAR/SPECI: highest 2-minute mean | Five-minute aviation report: highest 2-minute mean | Selected PSH |
|---|---:|---|---|---|---:|
| KBTR | 27 | Unavailable: IEM returns header only; no KBTR file in NOAA September directory | 24 at Sep 12 03:05 | 27 at Sep 12 01:00 | **27**, corrected from 24 |
| KMSY | 43 | 50 at Sep 12 02:01 | 35 at Sep 12 01:53 and 02:04 | 43 at Sep 12 01:20 | **50**, retained |
| KNEW | 37 | 42 at Sep 12 02:02 | 37 at Sep 12 00:12, 01:10, 02:13 | 37 at Sep 12 02:00 and 02:15 | **42**, retained |
| KPQL | 20 | 23 at Sep 12 05:25 | 19 at Sep 12 05:28 | 20 at Sep 12 06:05 | **23**, retained |

Times are UTC. A five-minute *report interval* does not mean a five-minute wind average. The ASOS sustained wind is a running two-minute mean; the NOAA minute archive reports that mean once per minute. Its five-second peak is a different field and was not used as sustained wind. No speed or averaging-period conversion was applied. The three higher minute peaks are not METAR gusts, PK WND remarks, or mph mistaken for knots.

## Original observations and decoding

Original NOAA Page 1 peak lines, with whitespace preserved in `peaks.json` and the source ZIP:

```text
12916KMSY MSY2024091120010201    5.335  N                               98   50   97   66     M
53917KNEW NEW2024091120020202   11.530  N                               74   42   74   54
53858KPQL PQL2024091123250525    1.724  N                              140   23  143   28
```

The header contains the **local standard date/time**, followed by UTC hour/minute. For these stations local standard time is UTC−6, including September; it is not daylight time. Thus KMSY `20240911 2001 0201` is **September 12 02:01 UTC**, not September 11. Wind fields are direction/2-minute speed/direction/5-second peak, respectively `98/50/97/66`, `74/42/74/54`, and `140/23/143/28`.

An independent fixed-field scan of every NOAA row in the UTC event interval (`noaa-independent-check.json`) finds exactly the same peaks, timestamps and available wind counts as IEM: KMSY **4,317**, KNEW **4,320**, KPQL **4,176**. Out of 4,320 possible minute timestamps, KMSY lacks three valid sustained readings and KPQL lacks 144; these gaps do not invalidate their measured maxima. KNEW's available sustained minute count covers the entire requested grid. All remain human-review candidates with I in the existing review workbook. NOAA describes limited station QC and no NCEI correction of transmission errors; archive agreement verifies source authenticity/decoding, not an independent instrument calibration.

The surrounding seven sustained readings support coherent observed peaks rather than an isolated misplaced gust field: MSY 35/38/43/**50**/45/37/35 kt (01:58–02:04), NEW 37/37/38/**42**/39/35/34 (01:59–02:05), PQL 16/18/22/**23**/20/21/19 (05:22–05:28). The raw minute responses preserve these neighboring records.

KBTR's recovered source record is:

```text
KBTR 120100Z AUTO 03027G35KT 6SM +RA FEW018 BKN042 OVC070 24/22 A2951 RMK P0003 T02400220 MADISHF
```

`03027G35KT` means 030° sustained **27 kt**, gust 35 kt. The timestamp is September 12 01:00 UTC, inside the window. Its original IEM CSV speed is `27.00`, direction `30.00`. This is a high-frequency ASOS/MADIS aviation report, not a routine hourly METAR. No NOAA minute maximum can be claimed for KBTR from the available archive. Absence of that station-month does not establish station discontinuation.

Original routine/SPECI maximum records (ties included):

```text
KBTR 120305Z 01024G38KT 10SM -RA FEW017 BKN037 OVC045 24/22 A2951 RMK AO2 PK WND 01038/0305 P0001 T02440217
KMSY 120153Z 10035G51KT 1SM +RA BR VV009 26/25 A2936 RMK AO2 PK WND 07068/0120 SLP944 P0209 T02560250 RVRNO $
KMSY 120204Z 10035G66KT 3/4SM +RA BKN009 OVC017 25/ A2933 RMK AO2 PK WND 10066/0201 P0027 T0250 RVRNO
KNEW 120012Z AUTO 08037G51KT 1 3/4SM VCTS +RA BR BKN009 OVC014 26/24 A2950 RMK AO2 PK WND 07051/0008 LTG DSNT SE P0018 T02560244
KNEW 120110Z AUTO 08037G50KT 3/4SM VCTS +RA BR BKN011 OVC018 26/24 A2945 RMK AO2 PK WND 07050/0110 LTG DSNT NE AND SE PRESFR P0030 T02560244
KNEW 120213Z AUTO 08037G52KT 1/2SM +RA FG VV008 26/25 A2940 RMK AO2 PK WND 07054/0202 LTG DSNT NE AND E P0077 T02610250
KPQL 120528Z AUTO 14019G34KT 4SM +RA BR SCT007 BKN013 OVC035 27/24 A2965 RMK AO2 PK WND 14034/0524 P0006 T02670244
```

The reference workbook's values **and timestamps** can be reproduced in the actual archive: KBTR 27 at 01:00, KMSY 43 at 01:20, KPQL 20 at 06:05 are five-minute reports; KNEW 37 at 00:12 is a special aviation observation. This explains all four differences without assuming the reference is the event's exhaustive maximum. The reference does not include the higher between-report two-minute means available for MSY, NEW and PQL.

## Official sources and exact retrieval URLs

- [NOAA Page 1 documentation](https://www.ncei.noaa.gov/data/automated-surface-observing-system-one-minute-pg1/doc/asos-1min-pg1_documentation.pdf): two-minute sustained mean, five-second peak, knots, local/UTC header and QC limitations.
- [NOAA ASOS User's Guide](https://www.weather.gov/media/asos/aum-toc.pdf), §3.2.2: running two-minute mean, updated once per minute for reports.
- [NOAA September 2024 directory](https://www.ncei.noaa.gov/data/automated-surface-observing-system-one-minute-pg1/access/2024/09/): MSY/NEW/PQL station-month files present; BTR absent.
- [KMSY original NOAA file](https://www.ncei.noaa.gov/data/automated-surface-observing-system-one-minute-pg1/access/2024/09/asos-1min-pg1-KMSY-202409.dat), [KNEW](https://www.ncei.noaa.gov/data/automated-surface-observing-system-one-minute-pg1/access/2024/09/asos-1min-pg1-KNEW-202409.dat), [KPQL](https://www.ncei.noaa.gov/data/automated-surface-observing-system-one-minute-pg1/access/2024/09/asos-1min-pg1-KPQL-202409.dat).
- [IEM minute service documentation](https://mesonet.agron.iastate.edu/request/asos/1min.phtml) and linked [IEM NOAA ingestion decoder](https://github.com/akrherz/iem/blob/main/scripts/ingestors/asos_1minute/parse_ncei_asos1minute.py).
- [IEM aviation API documentation](https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?help): supported report types **1=HFMETAR, 3=routine, 4=special**. Captured comparison requests and implemented retrieval use only these documented report types. Fresh production-collector retrieval reproduced the peaks.
- **[peaks.json](peaks.json)** contains each station's complete, replayable minute, routine/SPECI, and all-aviation request URL, peak records and ties. The raw responses and URL files are in **[source-records.zip](source-records.zip)**; **[source-hashes.json](source-hashes.json)** records SHA-256 hashes. The KBTR NOAA 404 response is retained too.

## Targeted correction and verification

Previously `iem.collect()` requested only report types 3/4. KBTR has no minute-archive data, so its fallback missed the valid 27 kt HFMETAR and returned the routine/SPECI maximum 24. The correction requests 1/3/4, labels `MADISHF` high-frequency records separately, and excludes their precipitation from routine hourly accumulation and partial rainfall reports. The current minute→METAR collector order in `build.py` is retained, but a populated sustained wind no longer suppresses a higher observed aviation two-minute mean. Gust/pressure precedence is unchanged.

Selected wind provenance now includes original source records, averaging periods, source kind, both aviation-source maxima, and selection policy. The source comparison also appears in the existing provenance Details column; the dashboard exports the structured records in its audit JSON. Empty minute queries are explicitly `NO DATA` with fallback explanation.

The four stations were rerun through the actual `asos1min.populate()` and `iem.populate()` collectors against live archives. **[Francine-targeted-review-outputs.zip](Francine-targeted-review-outputs.zip)** contains the regenerated workbook, provenance, QC, CSV and other review outputs. Other stations and collectors' observations are preserved from the prior Phase 3 Francine collection, not claimed as refetched. Workbook and dashboard/ZIP validators passed. The prior Phase 3 Francine regression artifact remains a historical baseline; this targeted correction resolves the KBTR sustained-wind discrepancy while documenting the three valid higher peaks.

Regression tests replay the captured archive responses, verify all eight maxima, preserve larger minute peaks, recover KBTR with exact timestamp/raw record, qualify the averaging period, exclude five-minute rainfall, and verify supported request types. The full-suite result is recorded in `verification.json`.

No reference observations were modified, no values were adjusted to match them, and no merge or deployment was performed.
