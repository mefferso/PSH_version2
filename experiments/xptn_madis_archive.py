#!/usr/bin/env python3
"""XPTN-only MADIS archive investigation; independent of PSH production collectors."""
import gzip
import json
import tempfile
from pathlib import Path

import netCDF4
import numpy as np
import requests

TARGET_LAT, TARGET_LON = 30.1999, -90.1231
# Deliberately bounded: look across hours/days without downloading hundreds of ~32 MB archives.
HOURS = ["20261008_0000", "20261008_0600", "20261008_1200",
         "20261008_1800", "20261009_0000", "20261009_1200",
         "20261010_0000", "20261010_1200"]
ROOTS = ["https://madis-data.ncep.noaa.gov/madisPublic1/data/archive",
         "https://madis-data.ncep.noaa.gov/madisPublic/data/archive"]
session = requests.Session()
session.headers["User-Agent"] = "PSH-version2-XPTN-MADIS-investigation/2.0"
out = {"target": {"id":"XPTN","latitude":TARGET_LAT,"longitude":TARGET_LON},
       "hours": HOURS, "attempts": [], "matches": [], "nearby": [], "provider_samples": [],
       "notes": ["Public archive only; restricted NOAA archives are not tested.",
                 "No-match in these sampled hours does not establish absence from MADIS."]}

def get_text(dataset, name, index):
    if name not in dataset.variables:
        return ""
    var = dataset.variables[name]
    if not var.dimensions or var.dimensions[0] != "recNum":
        return ""
    value = var[index]
    try:
        if hasattr(value, "tobytes"):
            return value.tobytes().decode("utf-8", "replace").strip("\x00 ")
        if isinstance(value, bytes):
            return value.decode("utf-8","replace").strip("\x00 ")
    except Exception:
        pass
    return str(value).strip("\x00 ")

def get_scalar(ds, name, idx):
    if name not in ds.variables:
        return None
    var = ds.variables[name]
    if not var.dimensions or var.dimensions[0] != "recNum" or len(var.shape) != 1:
        return None
    value = var[idx]
    if np.ma.is_masked(value):
        return None
    try:
        v = float(value)
        return v if np.isfinite(v) else None
    except (ValueError, TypeError):
        return None

def details(ds, idx, stamp, why):
    text_names = ("stationId", "providerId", "stationName", "dataProvider",
                  "stationType", "homeWFO", "handbook5Id")
    numeric = ("latitude","longitude","elevation","observationTime","reportTime",
               "windSpeed","windGust","windDir","stationPressure","seaLevelPressure",
               "temperature")
    return {"hour":stamp, "record_index":int(idx),"reason":why,
            "text":{name:get_text(ds,name,idx) for name in text_names},
            "values":{name:{"value":get_scalar(ds,name,idx),
                             "units":getattr(ds.variables[name],"units",None)}
                      for name in numeric if name in ds.variables}}

for stamp in HOURS:
    year, month, day = stamp[:4], stamp[4:6], stamp[6:8]
    got_file = False
    for root in ROOTS:
        url = f"{root}/{year}/{month}/{day}/LDAD/mesonet/netCDF/{stamp}.gz"
        a = {"hour":stamp,"url":url}
        out["attempts"].append(a)
        try:
            with session.get(url, stream=True, timeout=(15,120)) as response:
                a["http_status"] = response.status_code
                if response.status_code != 200:
                    a["detail"] = response.text[:100] if response.status_code in (401,403,404) else "HTTP error"
                    continue
                with tempfile.TemporaryDirectory() as folder:
                    zipped = Path(folder) / "archive.gz"
                    plain = Path(folder) / "archive.nc"
                    downloaded = 0
                    with zipped.open("wb") as fh:
                        for part in response.iter_content(1024*1024):
                            downloaded += len(part)
                            if downloaded > 80_000_000:
                                raise ValueError("compressed archive exceeds safety cap")
                            fh.write(part)
                    a["compressed_bytes"] = downloaded
                    with gzip.open(zipped,"rb") as src, plain.open("wb") as dst:
                        while (chunk := src.read(1024*1024)):
                            dst.write(chunk)
                    with netCDF4.Dataset(plain) as ds:
                        count = len(ds.dimensions["recNum"])
                        a["record_count"] = count
                        lat = np.ma.filled(ds.variables["latitude"][:], np.nan).astype(float)
                        lon = np.ma.filled(ds.variables["longitude"][:], np.nan).astype(float)
                        # Proximity first: efficient numeric vectorization, even if station IDs differ.
                        valid = np.isfinite(lat) & np.isfinite(lon)
                        dist = np.sqrt(((lat-TARGET_LAT)*111.0)**2 +
                                       ((lon-TARGET_LON)*111.0*np.cos(np.deg2rad(TARGET_LAT)))**2)
                        near = np.where(valid & (dist <= 8.0))[0]
                        a["within_8km"] = int(len(near))
                        nearest = sorted(near.tolist(), key=lambda i:dist[i])
                        a["closest_record_distances_km"] = [round(float(dist[i]),3) for i in nearest[:5]]
                        for idx in nearest[:25]:
                            record = details(ds,idx,stamp,f"within {dist[idx]:.3f} km")
                            record["distance_km"] = round(float(dist[idx]),3)
                            out["nearby"].append(record)
                            if dist[idx] <= 0.75:
                                out["matches"].append(record)
                        # Decode the station ID char matrix properly, then inspect exact code matches.
                        if "stationId" in ds.variables:
                            chars = ds.variables["stationId"][:]
                            try:
                                station_ids = netCDF4.chartostring(chars)
                                ids = np.asarray([str(x.decode() if isinstance(x,bytes) else x).strip("\x00 ").upper()
                                                  for x in station_ids])
                                indices = np.where(ids == "XPTN")[0]
                                a["exact_id_matches"] = int(len(indices))
                                for idx in indices[:50]:
                                    out["matches"].append(details(ds,int(idx),stamp,"exact stationId XPTN"))
                            except Exception as ex:
                                a["id_scan_error"] = str(ex)[:200]
                        # Inventory of provider IDs among stations closest to target; no bulk record export.
                        for idx in nearest[:10]:
                            sample = {"hour":stamp,"distance_km":round(float(dist[idx]),3),
                                      "stationId":get_text(ds,"stationId",idx),
                                      "providerId":get_text(ds,"providerId",idx),
                                      "dataProvider":get_text(ds,"dataProvider",idx)}
                            if sample not in out["provider_samples"]:
                                out["provider_samples"].append(sample)
                got_file = True
                break
        except Exception as exc:
            a["error"] = f"{type(exc).__name__}: {str(exc)[:240]}"
    if not got_file:
        out["notes"].append(f"No accessible file at {stamp} from tested public paths.")

Path("xptn_madis_result.json").write_text(json.dumps(out,indent=2))
with open("xptn_madis_report.md","w") as report:
    report.write("# XPTN MADIS archive — expanded investigation\n\n")
    report.write("Target XPTN (30.1999, -90.1231). Station ID plus coordinate proximity (0.75 km candidate; 8 km context).\n\n")
    report.write(f"**Candidate matches:** {len(out['matches'])} (duplicates may occur when ID and position both match)\n\n")
    report.write("| UTC hour | Public root | HTTP | Records | Within 8 km | Exact XPTN IDs |\n|---|---|---:|---:|---:|---:|\n")
    for a in out["attempts"]:
        report.write(f"| {a['hour']} | {('madisPublic1' if 'madisPublic1' in a['url'] else 'madisPublic')} | {a.get('http_status','error')} | {a.get('record_count','—')} | {a.get('within_8km','—')} | {a.get('exact_id_matches','—')} |\n")
    report.write("\nSee JSON artifact for nearest stations, provider details, wind/gust/pressure fields and reported units.\n")
    report.write("\nMissing public-hour files or absent matches do not establish XPTN is absent from NOAA's operational/restricted MADIS holdings.\n")
print(json.dumps({"attempts":out["attempts"],"matches":out["matches"][:20],
                  "nearby_preview":out["nearby"][:10],"notes":out["notes"]},indent=2)[:25000])
