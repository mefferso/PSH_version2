"""Initial PSH GitHub collector: only IEM archived ASOS/AWOS data is active.
Other station networks are deliberately NOT treated as completed.
"""
import csv
import datetime as dt
import io
import json
import os
import pathlib
import re
import sys
import time
from collections import Counter

import requests
from openpyxl import load_workbook
from openpyxl.cell.cell import MergedCell
from openpyxl.styles import Font, PatternFill

TEMPLATE = pathlib.Path("Copy of PSHLIX_YYYYALXX_StormName_Data.xlsx")
OUT = pathlib.Path("output")
IEM_URL = "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py"
REQUEST_TIMEOUT = 45

def utc_date(raw):
    return dt.date.fromisoformat(raw)

def site_id(value):
    value = str(value or "").strip().upper()
    return value[1:] if len(value) == 4 and value.startswith("K") else value

def optional_float(x):
    try:
        n = float(x)
        return n if abs(n) < 1e7 else None
    except (ValueError, TypeError):
        return None

def when_utc(raw):
    try:
        t = dt.datetime.strptime(raw.strip(), "%Y-%m-%d %H:%M")
        return t.replace(tzinfo=dt.timezone.utc)
    except (ValueError, AttributeError):
        return None

def fetch_iem(station, start, end):
    # IEM endpoint end date is exclusive.
    end_exclusive = end + dt.timedelta(days=1)
    params = {
        "station": station,
        "data": ["sknt", "gust", "drct", "mslp"],
        "year1": start.year, "month1": start.month, "day1": start.day,
        "year2": end_exclusive.year, "month2": end_exclusive.month, "day2": end_exclusive.day,
        "tz": "Etc/UTC", "format": "onlycomma", "latlon": "no",
        "missing": "M", "trace": "T", "direct": "no",
    }
    response = requests.get(IEM_URL, params=params, timeout=REQUEST_TIMEOUT,
                            headers={"User-Agent": "LIX-PSH-GitHub/0.1"})
    response.raise_for_status()
    reader = csv.DictReader(io.StringIO(response.text))
    if not reader.fieldnames or "valid" not in reader.fieldnames:
        raise ValueError("IEM CSV invalid/unexpected schema")
    samples = []
    for row in reader:
        t = when_utc(row.get("valid"))
        if not t or t.date() < start or t.date() > end:
            continue
        samples.append((t, row))
    return samples, response.url

def peak(samples, key, mode):
    valid = []
    for t, row in samples:
        v = optional_float(row.get(key))
        if v is None: continue
        if key in ("gust", "sknt") and not (0 <= v <= 180): continue
        if key == "mslp" and not (850 <= v <= 1100): continue
        valid.append((v, t, row))
    if not valid:
        return None
    return (max if mode == "max" else min)(valid, key=lambda a: a[0])

def stamp(sheet, row, value_col, direction_col, time_col, day_col, month_col, year_col, reading):
    if not reading: return
    value, t, raw = reading
    sheet.cell(row, value_col, round(value, 1))
    if direction_col:
        direction = optional_float(raw.get("drct"))
        if direction is not None and 0 <= direction <= 360:
            sheet.cell(row, direction_col, int(direction))
    sheet.cell(row, time_col, t.strftime("%H%M"))
    sheet.cell(row, day_col, t.day)
    sheet.cell(row, month_col, t.month)
    sheet.cell(row, year_col, t.year)

def build():
    OUT.mkdir(exist_ok=True)
    name = os.environ["STORM_NAME"].strip()
    start = utc_date(os.environ["START_UTC"])
    end = utc_date(os.environ["END_UTC"])
    if not name or not re.fullmatch(r"[A-Za-z0-9 -]{2,70}", name):
        raise ValueError("Invalid storm name")
    if start > end or (end - start).days > 35:
        raise ValueError("Invalid date range (maximum 36 inclusive days)")
    if not TEMPLATE.exists():
        raise FileNotFoundError("Upload the original PSH workbook to the repository root first (README).")
    wb = load_workbook(TEMPLATE)
    needed = {"Summary", "Wind and Pressure", "Rainfall", "Water Level", "Tornadoes"}
    if not needed.issubset(set(wb.sheetnames)):
        raise ValueError(f"Workbook is missing required tabs: {needed - set(wb.sheetnames)}")
    wind = wb["Wind and Pressure"]
    summary = wb["Summary"]
    summary["B3"] = name
    summary["B5"] = "New Orleans/Baton Rouge"
    summary["B7"] = f"{start:%m/%d/%Y} - {end:%m/%d/%Y}"
    qc = wb["QC"] if "QC" in wb else wb.create_sheet("QC")
    qc.append(["Tab", "Site ID", "Network", "Status", "Details", "Source URL"])
    # Remove old/example observations from a reused template before collecting.
    # Station metadata, names, links, and WeatherFlow manual values remain intact.
    for sheet_name, first_col, last_col in (
        ("Rainfall", 8, 10),
        ("Water Level", 7, 7),
        ("Water Level", 9, 12),
        ("Water Level", 14, 15),
    ):
        sheet = wb[sheet_name]
        for row_num in range(2, sheet.max_row + 1):
            sid = str(sheet.cell(row_num, 1).value or "").strip()
            if not sid or sid.startswith("["): continue
            if "WXFLOW" in str(sheet.cell(row_num, 7).value or "").upper(): continue
            for col in range(first_col, last_col + 1):
                cell = sheet.cell(row_num, col)
                if not isinstance(cell, MergedCell):
                    cell.value = None
    # Sample tornado placeholders aren't verified tornadoes.
    tornado = wb["Tornadoes"]
    for row_num in range(2, tornado.max_row + 1):
        first = str(tornado.cell(row_num, 1).value or "")
        if first.startswith("[Insert"):
            for col in range(1, 12):
                cell = tornado.cell(row_num, col)
                if not isinstance(cell, MergedCell):
                    cell.value = None
    totals = Counter()
    for row in range(2, wind.max_row + 1):
        sid = str(wind.cell(row, 1).value or "").strip()
        network = str(wind.cell(row, 8).value or "").upper().strip()
        if not sid or sid.startswith("["):
            continue
        if "WXFLOW" in network or "WEATHERFLOW" in network:
            totals["weatherflow_manual"] += 1
            continue
        # Clear stale wind/pressure measurements on all non-WeatherFlow stations.
        for col in range(11, 31):
            cell = wind.cell(row, col)
            if not isinstance(cell, MergedCell):
                cell.value = None
        if network not in ("ASOS", "AWOS"):
            totals["other_network_pending"] += 1
            continue
        station = site_id(sid)
        try:
            samples, url = fetch_iem(station, start, end)
            sustained = peak(samples, "sknt", "max")
            gust = peak(samples, "gust", "max")
            pressure = peak(samples, "mslp", "min")
            if sustained:
                stamp(wind, row, 11, 12, 13, 14, 15, 16, sustained)
            if gust:
                stamp(wind, row, 17, 18, 19, 20, 21, 22, gust)
            if pressure:
                stamp(wind, row, 23, None, 24, 25, 26, 27, pressure)
            populated = sum(bool(x) for x in (sustained, gust, pressure))
            status = "COLLECTED" if populated == 3 else "PARTIAL" if populated else "NO DATA"
            qc.append(["Wind and Pressure", sid, network, status,
                       f"{len(samples)} rows; wind={bool(sustained)}, gust={bool(gust)}, mslp={bool(pressure)}", url])
            totals[status] += 1
        except Exception as exc:
            qc.append(["Wind and Pressure", sid, network, "ERROR", str(exc)[:250], IEM_URL])
            totals["ERROR"] += 1
        time.sleep(0.15)
    # The original 2025 template's Summary uses Google QUERY formulas, which cannot
    # recalculate in Excel. Do not claim the Summary top-10 blocks are populated.
    qc.append(["Summary", "", "", "REVIEW REQUIRED",
               "Google QUERY formulas will not recalculate in exported Excel; use native Google Sheet or implement explicit top-10 rendering.", ""])
    for tab in ("Rainfall", "Water Level", "Tornadoes", "Inland Flooding", "Impacts"):
        if tab in wb:
            qc.append([tab, "", "", "NOT AUTOMATED", "No data collected by this initial version", ""])
    qc.freeze_panes = "A2"
    qc.auto_filter.ref = f"A1:F{qc.max_row}"
    for cell in qc[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="17365D")
    for col, width in zip("ABCDEF", [22, 20, 20, 20, 90, 65]):
        qc.column_dimensions[col].width = width
    slug = re.sub(r"[^A-Za-z0-9_-]+", "_", name)
    target = OUT / f"PSHLIX_{start.year}_{slug}_PARTIAL.xlsx"
    wb.save(target)
    report = {"storm": name, "start_utc": str(start), "end_utc": str(end),
              "coverage": "PARTIAL ASOS/AWOS ONLY", "counts": dict(totals),
              "manual_networks": ["WeatherFlow"], "not_yet_automated": [
                  "CO-OPS", "USGS", "USACE", "NDBC", "Synoptic", "WeatherSTEM",
                  "CoCoRaHS", "Tornadoes", "Inland Flooding", "Impacts", "Summary top 10"]}
    (OUT / "QC.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    try:
        build()
    except Exception as exc:
        pathlib.Path("output").mkdir(exist_ok=True)
        pathlib.Path("output/ERROR.txt").write_text(str(exc) + "\n")
        raise
