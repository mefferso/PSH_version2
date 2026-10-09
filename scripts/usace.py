"""USACE/CPRA RiverGages metadata audit with strict datum safety gate.

Metadata is not proof of a conversion; no elevation is written without
confirmed NAVD88 adjustment and archived water level series.
"""
import html
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from urllib.parse import urlparse, parse_qs
import requests

HOST = "rivergages.mvr.usace.army.mil"
IDENT = re.compile(r"[A-Za-z0-9]{3,12}$")
SOURCES = {"USACE", "LA CPRA"}
METADATA_LIMIT = 320

class PageText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        if tag in ("p", "tr", "td", "br", "div", "h1", "h2"):
            self.parts.append(" ")
    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip:
            self.skip -= 1
        if tag in ("p", "tr", "td", "br", "div"):
            self.parts.append(" ")
    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)

def station_link(cell):
    link = cell.hyperlink.target if cell.hyperlink else ""
    parsed = urlparse(link or "")
    if parsed.hostname != HOST or not parsed.path.lower().startswith("/watercontrol/"):
        return None
    sid = parse_qs(parsed.query).get("sid", [""])[0]
    if not IDENT.fullmatch(sid):
        return None
    return sid, link

def metadata_from_html(source):
    parser = PageText()
    parser.feed(source)
    text = re.sub(r"\s+", " ", html.unescape(" ".join(parser.parts))).strip()
    zero = re.search(r"Gage Zero\s*:?\s*(.{1,90}?)(?=\s+Longitude\s*:|\s+Latitude\s*:|\s+River Mile\s*:|\s+Record High|\s+Location of Gage|$)", text, re.I)
    if not zero:
        zero = re.search(r"Gage Zero\s*:?\s*(.{1,80})", text, re.I)
    descriptions = []
    for pattern in (r"gage zero set to.{0,140}", r"current adjustment is.{0,120}",
                    r"adjust.{0,100}NAVD88.{0,100}", r"NAVD88\s*\([^)]*\).{0,100}"):
        matches = re.findall(pattern, text, re.I)
        descriptions.extend(matches[:2])
    return {
        "gage_zero": zero.group(1).strip() if zero else "",
        "datum_notes": "; ".join(dict.fromkeys(descriptions))[:METADATA_LIMIT],
        "has_navd88_reference": bool(re.search(r"NAVD\s*88", text, re.I)),
        "has_gage_reference": bool(re.search(r"Gage Zero", text, re.I)),
    }

def fetch_station_metadata(sid, session=requests):
    url = f"https://{HOST}/WaterControl/stationinfo2.cfm"
    response = session.get(url, params={"sid":sid}, timeout=7,
                           headers={"User-Agent":"LIX-PSH-V2/0.5 (metadata audit)"})
    response.raise_for_status()
    if len(response.content) > 1_000_000:
        raise ValueError("Unexpectedly large RiverGages station page")
    return metadata_from_html(response.text), response.url

def populate(workbook, qc, start, end, counts):
    sheet = workbook["Water Level"]
    station_ids = {}
    for row_num in range(2, sheet.max_row + 1):
        name = str(sheet.cell(row_num, 1).value or "").strip()
        ref = station_link(sheet.cell(row_num, 1))
        network = str(sheet.cell(row_num, 13).value or "").strip().upper()
        if name and ref and network in SOURCES:
            station_ids[ref[0]] = ref[1]
    cache = {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(fetch_station_metadata, ident): ident for ident in station_ids}
        for future in as_completed(futures):
            ident = futures[future]
            try:
                cache[ident] = future.result()
                counts["rivergages_metadata_retrieved"] += 1
            except (requests.RequestException, ValueError) as exc:
                cache[ident] = (None, station_ids[ident])
                counts["rivergages_metadata_errors"] += 1
    for row in range(2, sheet.max_row + 1):
        site = str(sheet.cell(row, 1).value or "").strip()
        network = str(sheet.cell(row, 13).value or "").strip().upper()
        ref = station_link(sheet.cell(row, 1))
        if not ref or not site:
            continue
        sid, link = ref
        if network not in SOURCES:
            counts["rivergages_source_mismatch"] += 1
            qc.append(["Water Level", site, network, "CHECK SOURCE",
                       "RiverGages linked station "+sid+" but source network not USACE/LA CPRA", link])
            continue
        counts["rivergages_datum_pending"] += 1
        meta, url = cache.get(sid, (None, link))
        if meta is None:
            description = f"RiverGages station {sid}: metadata page unavailable. Datum unverified; no measurement inserted."
            status = "METADATA UNAVAILABLE"
        else:
            zero = meta["gage_zero"] or "not provided"
            notes = meta["datum_notes"] or "No specific NAVD88 adjustment described"
            description = (f"RiverGages {sid}; gage zero: {zero}; {notes}; "
                           "datum conversion not verified; no measurement inserted.")
            status = "DATUM REVIEW"
            if meta["has_navd88_reference"]:
                counts["rivergages_navd88_mentioned"] += 1
        qc.append(["Water Level", site, network, status, description[:600], url])
