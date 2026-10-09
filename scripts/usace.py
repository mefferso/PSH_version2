"""USACE RiverGages source inventory and datum safety gate.

USACE RiverGages pages primarily provide stage, with individual gage-zero datum
definitions and potentially dated NAVD88 adjustments. Never reinterpret stage
as NAVD88 or MHHW without station-specific validated conversion history.
"""
import re
from urllib.parse import urlparse, parse_qs

HOST = "rivergages.mvr.usace.army.mil"
IDENT = re.compile(r"[A-Za-z0-9]{3,12}$")
SOURCES = {"USACE", "LA CPRA"}

def station_link(cell):
    link = cell.hyperlink.target if cell.hyperlink else ""
    parsed = urlparse(link or "")
    if parsed.hostname != HOST or not parsed.path.lower().startswith("/watercontrol/"):
        return None
    sid = parse_qs(parsed.query).get("sid", [""])[0]
    if not IDENT.fullmatch(sid):
        return None
    return sid, link

def populate(workbook, qc, start, end, counts):
    sheet = workbook["Water Level"]
    for row in range(2, sheet.max_row + 1):
        site = str(sheet.cell(row, 1).value or "").strip()
        network = str(sheet.cell(row, 13).value or "").strip().upper()
        ref = station_link(sheet.cell(row, 1))
        if not ref or not site:
            continue
        sid, url = ref
        if network not in SOURCES:
            counts["rivergages_source_mismatch"] += 1
            qc.append(["Water Level", site, network, "CHECK SOURCE",
                       "RiverGages linked station "+sid+" but source network not USACE/LA CPRA", url])
            continue
        counts["rivergages_datum_pending"] += 1
        qc.append(["Water Level", site, network, "DATUM REVIEW",
                   "RiverGages station "+sid+
                   ": source link mapped; stage-to-elevation conversion requires validated "+
                   "gage zero, NAVD88 epoch and effective dates. No water level inserted.",url])
