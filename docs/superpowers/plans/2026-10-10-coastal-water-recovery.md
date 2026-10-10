# CPRA / USACE historical water recovery

Goal: retrieve exact-station observed peaks, keep partial data, prevent unqualified stages entering PSH elevations, and expose review records in workbook/dashboard/downloads.

1. Audit template IDs/names/coordinates/links against MVN CWMS locations and timeseries catalog; capture raw official responses and document discrepancies/moves/discontinued records. No nearby replacements.
2. Add JSON inventory keyed by original ID with exact RiverGages and CWMS identities, evidence, datum rules and review limitations. Add bounded, retrying, paginated CWMS collector with UTC half-open filtering, explicit units, quality codes and retained observations. Verify direct datum only from station-specific evidence; conversions still require existing reviewed registry.
3. Add structured JSON/CSV station audit and observation series, plus Water Level review tab. Qualified peaks populate existing G:N; unqualified peaks stay in review output. Every partial/unknown coverage is I; original values and timestamps retained.
4. Integrate with build, QC, provenance, dashboard and validation. Keep original template metadata/styles except audited hyperlinks. Disable legacy duplicate metadata/HML collection in operational builds; preserve fallback only for verified IDs and label source.
5. Regression tests: all 31 mappings; raw CWMS fixtures; pagination; timestamps and exact interval; partial/missing/invalid; unit and datum safety; identity conflicts; workbook/dashboard/download validation; workflow branch publication guard.
6. Run whole test suite and live exact Isaias build; independently verify peaks against captured observations. Commit code and evidence; push branch; open PR. Document main-only operational Pages workflow inputs and post-merge verification.
