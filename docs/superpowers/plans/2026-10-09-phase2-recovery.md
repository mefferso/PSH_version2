# PSH Phase 2 Recovery Implementation Plan

Goal: recover real exact-station rainfall and historical observations without forcing agreement with Francine.
Architecture: retain existing workbook and audit interfaces; add archive adapters and per-field evidence exports. Qualified complete rainfall intervals populate the original table; other reports remain explicit QC candidates. Existing date/datum/unit gates remain.
Spec: the user's Phase 2 assignment, including five ordered priorities and definition of done.

User explicitly authorized autonomous implementation, refactoring, testing and publication; design/plan approval handoffs are waived by that instruction. Fresh clone on phase2-recovery provides isolation from user work.

## Tasks
- [ ] Rain: reproduce contracts; add failing tests for official local-time daily export, DST, exact IDs, missing reports, duplicate conflicts and multiday overlap; implement CoCoRaHS export recovery and documented Synoptic intervals with reconstruction labels.
- [ ] Archives: test/report IEM daily climate and SHEF/HADS alternate sources, raw precipitation counters and candidate retention. Recover verified peak gust observations without substituting stations or averaging periods.
- [ ] Investigations: produce one row for each original missing match, map network/source/QC/alternates; individually investigate 11 discrepancies and available water datum evidence. Never classify request failure as unavailable data.
- [ ] Publication: run entire unit suite and live builds; compare to 599 reference fields; publish development and Francine artifacts on every meaningful push, verify Actions/Pages and document before/after counts.

Review focus: fabricated UTC offsets; DST daily lengths; overlapping rain reports; station aliases without identity evidence; mistaken wind peak averaging periods; stage/elevation confusion; partial current-day rainfall; source access failures mistaken for no observations.

Ledger: baseline commit 120c5bb. Initial test attempt lacked dependencies; install frozen dependencies and rerun before edits. Scientific approval is not inferred from a reference match.
