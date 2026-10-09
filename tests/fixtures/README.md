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
