# Francine reference provenance

The completed/issued workbook was copied without modification from
`mefferso/PSH_project` commit `5ebb9b8a0a7a5d0ae0d03d7f2ae132f04d4acfb9`.
Its upstream source manifest identifies it as a user-uploaded authoritative
regression reference. SHA-256:
`7347750b44507e7e9025baa25c9db68a7aa686868d6d7d1baee0e03fa468c16f`.

The expected JSON and IEM daily CSV come from that same commit. The CSV is a
**deterministic edge-case fixture**, not an independently downloaded live archive.
A passed fixture test does not constitute live Francine validation.

Known upstream discrepancy: Tiger Stadium native WeatherSTEM gust was reported
as 44.32 kt versus 48 kt issued. Do not alter the reference or increase tolerances
to hide this discrepancy. Max-minute anemometer values are not automatically
proof of the PSH sustained-wind averaging convention.

`iem_hml_BBOL1_20240910-12.csv` is an unmodified live IEM HML CSV captured October 9, 2026 from https://mesonet.agron.iastate.edu/cgi-bin/request/hml.py?station=BBOL1&kind=obs&tz=UTC&fmt=csv&year1=2024&month1=9&day1=10&year2=2024&month2=9&day2=13 . Its explicit `valid[UTC]` and `Stage[ft]` headers verify the historical retrieval contract; its 4.4-foot stage maximum is not asserted to be NAVD88 or inundation. No datum offset is inferred from this fixture.

CWMS fixtures `cwms_SBEL1_20261008-10.json` and `cwms_76305_20261008-10.json`
were captured from the official USACE MVN `/cwms-data/timeseries` JSON v2
endpoint on 2026-10-10, requested in ft for the exact October 8 midnight to
October 10 midnight interval. They retain actual epoch-millisecond timestamps,
quality codes, partial/missing observations and the endpoint-inclusive final
sample (which the collector excludes from the requested half-open window).
The first verifies a 179/192 sample partial peak of 4.19 ft; the second verifies
48 hourly observations and a 2.55 ft peak. These are preliminary source values,
not an official cyclone attribution or datum conversion.
