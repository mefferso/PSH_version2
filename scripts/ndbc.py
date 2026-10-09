"""NDBC standard meteorological observations; headers determine units/columns."""
import datetime as dt
import gzip
import math
import re
import time
from urllib.parse import urlparse, parse_qs
import requests
from openpyxl.cell.cell import MergedCell

KNOTS_PER_MS = 1.9438444924406
ALLOWED = {"BUOY", "CMAN", "C-MAN", "WLON", "NDBC"}
BASE = "https://www.ndbc.noaa.gov"
HEADERS = {"YY","MM","DD","hh","mm","WDIR","WSPD","GST","PRES"}

def station_id(cell):
    link = cell.hyperlink.target if cell.hyperlink else ""
    url = urlparse(link or "")
    if url.hostname not in ("ndbc.noaa.gov", "www.ndbc.noaa.gov"):
        return None
    match = re.search(r"/(?:realtime2|stdmet)/([A-Za-z0-9]{4,7})\\.(?:txt|gz)$", url.path, re.I)
    value = match.group(1) if match else parse_qs(url.query).get("station", [""])[0]
    if not value:
        value = parse_qs(url.query).get("station_id", [""])[0]
    return value.upper() if re.fullmatch(r"[A-Za-z0-9]{4,7}", value or "") else None

def parse_text(content, start, end):
    headings = None
    obs = []
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        fields = line.lstrip("#").split()
        normalized = [x.lstrip("#") for x in fields]
        if "WSPD" in normalized and "PRES" in normalized and ("YY" in normalized or "YYYY" in normalized):
            headings = normalized
            continue
        if headings is None or line.startswith("#"):
            continue
        if len(fields) < len(headings):
            continue
        row = dict(zip(headings, fields))
        try:
            yr = int(row.get("YYYY", row.get("YY")))
            if yr < 100: yr += 2000 if yr < 70 else 1900
            minute = int(row.get("mm", "0"))
            moment = dt.datetime(yr, int(row["MM"]), int(row["DD"]), int(row["hh"]), minute,
                                 tzinfo=dt.timezone.utc)
        except (ValueError, KeyError, TypeError):
            continue
        if not (start <= moment.date() <= end):
            continue
        def number(key, lo, hi):
            try:
                v = float(row[key])
                return v if math.isfinite(v) and lo <= v <= hi else None
            except (KeyError, ValueError, TypeError):
                return None
        # NDBC WSPD/GST m/s and PRES hPa; do not treat missing 99/999 sentinels as data.
        wind = number("WSPD", 0, 75)
        gust = number("GST", 0, 90)
        pressure = number("PRES", 850, 1100)
        direction = number("WDIR", 0, 360)
        obs.append({"time":moment, "wind":wind*KNOTS_PER_MS if wind is not None else None,
                    "gust":gust*KNOTS_PER_MS if gust is not None else None,
                    "pressure":pressure, "dir":direction})
    if headings is None:
        raise ValueError("NDBC standard-meteorological column header not found")
    return obs

def retrieve(station, start, end, session=requests):
    # Current/recent 45 days: realtime2; older and future archive windows: annual stdmet.
    today = dt.datetime.now(dt.timezone.utc).date()
    urls = []
    samples = []
    if end >= today - dt.timedelta(days=44):
        urls.append(f"{BASE}/data/realtime2/{station}.txt")
    for year in range(start.year, end.year+1):
        urls.append(f"{BASE}/view_text_file.php?filename={station.lower()}h{year}.txt.gz&dir=data/historical/stdmet/")
    errors = []
    for url in urls:
        try:
            r = session.get(url, timeout=45, headers={"User-Agent":"LIX-PSH-V2/0.3"})
            if r.status_code == 404: continue
            r.raise_for_status()
            samples.extend(parse_text(r.text, start, end))
        except (requests.RequestException, ValueError) as exc:
            errors.append(f"{url}: {str(exc)[:90]}")
    dedup = {s["time"]:s for s in samples}
    return sorted(dedup.values(), key=lambda x:x["time"]), urls, errors

def setpeak(sheet, r, col, peak, dircol=None):
    if peak is None: return
    value, sample = peak
    when = sample["time"]
    sheet.cell(r,col).value = round(value,1)
    if dircol and sample["dir"] is not None:
        sheet.cell(r,dircol).value = int(sample["dir"])
    offset = col+2 if dircol else col+1
    for j,part in enumerate((when.strftime("%H%M"),when.day,when.month,when.year)):
        sheet.cell(r,offset+j).value = part

def populate(workbook, qc, start, end, counts):
    sheet = workbook["Wind and Pressure"]
    for row in range(2,sheet.max_row+1):
        site = str(sheet.cell(row,1).value or "").strip()
        network = str(sheet.cell(row,8).value or "").strip().upper()
        station = station_id(sheet.cell(row,1))
        if not station or network not in ALLOWED or not site:
            continue
        # Preserve source IDs and metadata; no ASOS/AWOS overwrite.
        for col in range(11,31):
            cell=sheet.cell(row,col)
            if not isinstance(cell,MergedCell):
                cell.value=None
        try:
            obs,urls,errors=retrieve(station,start,end)
            def peak(field,reverse=True):
                good=[(v[field],v) for v in obs if v[field] is not None]
                return (max if reverse else min)(good,key=lambda x:x[0]) if good else None
            w,g,p=peak("wind"),peak("gust"),peak("pressure",False)
            setpeak(sheet,row,11,w,12)
            setpeak(sheet,row,17,g,18)
            setpeak(sheet,row,23,p)
            collected=sum(x is not None for x in (w,g,p))
            status="COLLECTED" if collected==3 else "PARTIAL" if collected else "NO DATA"
            if errors and not obs: status="ERROR"
            counts["ndbc_"+status.lower().replace(" ","_")]+=1
            qc.append(["Wind and Pressure",site,network,status,
                       f"NDBC {station}; {len(obs)} observations; wind={w is not None}, gust={g is not None}, pressure={p is not None}; "+
                       ("; ".join(errors[:2]) if errors else ""),urls[0]])
        except Exception as exc:
            counts["ndbc_error"]+=1
            qc.append(["Wind and Pressure",site,network,"ERROR",str(exc)[:250],f"{BASE}/station_page.php?station={station.lower()}"])
        time.sleep(.1)
