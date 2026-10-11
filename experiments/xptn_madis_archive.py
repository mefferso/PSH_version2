#!/usr/bin/env python3
"""Isolated XPTN MADIS historical test. No production PSH imports or credentials."""
import gzip, json, os, re, tempfile
from pathlib import Path
import requests

DATES = ["20261008_1200", "20261009_1200", "20261010_1200"]
ROOTS = [
    "https://madis-data.ncep.noaa.gov/madisPublic1/data/archive",
    "https://madis-data.ncep.noaa.gov/madisPublic/data/archive",
]
TARGET = "XPTN"
out = {"station": TARGET, "test_dates_utc": DATES, "attempts": [], "matches": [], "notes": []}
session = requests.Session()
session.headers["User-Agent"] = "PSH-version2-XPTN-MADIS-test/1.0"

try:
    import netCDF4
    import numpy as np
except ImportError as exc:
    out["notes"].append(f"netCDF parser unavailable: {exc}")
    netCDF4 = None

def preview(v):
    try:
        arr = np.ma.asarray(v)
        if arr.size > 100: return f"array shape {arr.shape}"
        return str(np.ma.filled(arr, np.nan).tolist())[:300]
    except Exception:
        return str(v)[:300]

for stamp in DATES:
    year, month, day = stamp[:4], stamp[4:6], stamp[6:8]
    for root in ROOTS:
        url = f"{root}/{year}/{month}/{day}/LDAD/mesonet/netCDF/{stamp}.gz"
        attempt = {"url": url}
        out["attempts"].append(attempt)
        try:
            with session.get(url, stream=True, timeout=(15, 90)) as response:
                attempt["http_status"] = response.status_code
                attempt["content_type"] = response.headers.get("content-type")
                if response.status_code != 200:
                    attempt["detail"] = (response.text[:160] if response.status_code in (401,403,404) else "non-200 response")
                    continue
                with tempfile.TemporaryDirectory() as tdir:
                    zipped = Path(tdir) / "hour.gz"
                    ncfile = Path(tdir) / "hour.nc"
                    n = 0
                    with zipped.open("wb") as stream:
                        for chunk in response.iter_content(1024 * 1024):
                            n += len(chunk)
                            if n > 80_000_000:
                                raise RuntimeError("download larger than 80 MB safety limit")
                            stream.write(chunk)
                    attempt["compressed_bytes"] = n
                    with gzip.open(zipped, "rb") as source, ncfile.open("wb") as dest:
                        while True:
                            block = source.read(1024 * 1024)
                            if not block: break
                            dest.write(block)
                    if not netCDF4:
                        attempt["detail"] = "downloaded but could not decode"
                        break
                    with netCDF4.Dataset(ncfile) as ds:
                        attempt["dimensions"] = {k: len(v) for k,v in ds.dimensions.items()}
                        attempt["variables"] = list(ds.variables)[:100]
                        found = []
                        for name, var in ds.variables.items():
                            if not any(word in name.lower() for word in ("station", "id", "name")):
                                continue
                            if len(var.shape) == 0 or len(var.shape) > 2:
                                continue
                            try:
                                if var.dtype.kind not in "SU" and var.dtype.kind != "O": continue
                                raw = var[:]
                                if raw.ndim == 2:
                                    strings = netCDF4.chartostring(raw)
                                else:
                                    strings = raw
                                for idx, value in enumerate(strings):
                                    value = value.decode(errors="replace") if isinstance(value, bytes) else str(value)
                                    if value.strip("\x00 ").upper() == TARGET:
                                        found.append((name, idx, var.dimensions[0]))
                            except Exception as error:
                                attempt.setdefault("scan_errors", []).append(f"{name}: {str(error)[:100]}")
                        attempt["station_matches"] = [{"id_variable":n,"index":i,"dimension":d} for n,i,d in found]
                        for name, idx, dim in found:
                            record = {"hour":stamp,"source_url":url,"id_variable":name,"index":idx,"fields":{}}
                            for key, var in ds.variables.items():
                                if dim not in var.dimensions: continue
                                if not any(v in key.lower() for v in ("wind","gust","press","time","latitude","longitude","elev","station")): continue
                                try:
                                    values = var[idx] if var.dimensions[0] == dim else None
                                    if values is not None:
                                        record["fields"][key]={"value":preview(values),"units":getattr(var,"units",None),"dimensions":var.dimensions}
                                except Exception as error:
                                    record.setdefault("errors",[]).append(f"{key}: {str(error)[:120]}")
                            out["matches"].append(record)
                break
        except Exception as error:
            attempt["error"] = f"{type(error).__name__}: {str(error)[:220]}"
    else:
        out["notes"].append(f"No accessible archive file for {stamp} at attempted roots")
Path("xptn_madis_result.json").write_text(json.dumps(out,indent=2))
with open("xptn_madis_report.md","w") as report:
    report.write("# XPTN MADIS historical archive experiment\n\n")
    report.write("Tested hourly files at 1200 UTC on October 8, 9, and 10, 2026. A missing match in three hours does not establish historical absence.\n\n")
    report.write(f"**Decoded XPTN station matches:** {len(out['matches'])}\n\n")
    report.write("| UTC hour | Access | HTTP | Bytes | XPTN matches |\n|---|---|---|---|---|\n")
    for a in out["attempts"]:
        report.write(f"| {a['url'].split('/')[-1]} | {a['url'].split('/')[3]} | {a.get('http_status','error')} | {a.get('compressed_bytes','—')} | {len(a.get('station_matches',[]))} |\n")
    report.write("\nFull response metadata and any station observations are in the JSON artifact. Do not interpret absence in the public dataset as absence in NOAA-restricted MADIS.\n")
print(json.dumps({"attempts":out["attempts"],"matches":out["matches"],"notes":out["notes"]},indent=2)[:14000])
