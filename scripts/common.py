"""Shared exact-station inventory, finite QC, UTC windows and provenance."""
import datetime as dt
import json
import math
from pathlib import Path
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

UTC = dt.timezone.utc
NETWORK_COL = {'Wind and Pressure':8, 'Rainfall':7, 'Water Level':13}

def identifier(value):
    if isinstance(value,(float,int)) and not isinstance(value,bool) and float(value).is_integer():
        return str(int(value))
    return str(value or '').strip()

def finite(value, low=-1e7, high=1e7):
    try:
        n=float(value)
        return n if math.isfinite(n) and low <= n <= high else None
    except (TypeError,ValueError):
        return None

def inventory(wb, tab):
    sheet=wb[tab]
    for r in range(2,sheet.max_row+1):
        sid=identifier(sheet.cell(r,1).value)
        if not sid or sid.startswith('['):continue
        # A station has coordinates; footer text never does.
        if finite(sheet.cell(r,3).value,-90,90) is None or finite(sheet.cell(r,4).value,-180,180) is None:continue
        c=sheet.cell(r,1)
        yield {'row':r,'id':sid,'network':str(sheet.cell(r,NETWORK_COL[tab]).value or '').strip(),
               'url':c.hyperlink.target if c.hyperlink else '', 'name':sheet.cell(r,2).value}

def bounds(start,end):
    return dt.datetime.combine(start,dt.time(),UTC),dt.datetime.combine(end+dt.timedelta(days=1),dt.time(),UTC)

def timestamp(value):
    try:
        t=dt.datetime.fromisoformat(str(value).replace('Z','+00:00'))
        return t.astimezone(UTC) if t.tzinfo else None
    except (ValueError,TypeError):return None

def public_url(url):
    p=urlparse(url)
    if p.scheme not in ('https','http') or not p.hostname or p.username or p.password:
        raise ValueError('Invalid provenance URL')
    query=[(k,v) for k,v in parse_qsl(p.query,keep_blank_values=True)
           if k.lower() not in ('token','api_key','apikey','key','access_token')]
    return urlunparse(p._replace(query=urlencode(query)))

def interval_total(readings,start,end):
    """Sum only a complete tiled window. No interpolation, reset guessing or overlaps."""
    cursor=start;total=0.0
    for a,b,value in sorted(readings,key=lambda x:x[0]):
        if a!=cursor or b<=a or b>end or finite(value,0,1000) is None:return None
        cursor=b;total+=value
    return total if cursor==end else None

class Audit:
    def __init__(self):self.entries=[]
    def add(self,tab,row,site,variable,value,unit,when,url,*,datum=None,evidence=None,
            raw_value=None,raw_unit=None,status='REVIEW REQUIRED',interval_start=None,details=''):
        if finite(value) is None or when.tzinfo is None:raise ValueError('Invalid value or UTC time')
        if variable=='water' and (datum not in ('NAVD88','MHHW') or not evidence):
            raise ValueError('Water observation requires verified datum evidence')
        entry={'tab':tab,'row':row,'site_id':identifier(site),'variable':variable,'value':value,'unit':unit,
               'time_utc':when.astimezone(UTC).isoformat(),'source_url':public_url(url),
               'datum':datum,'datum_evidence':evidence,'original_value':value if raw_value is None else raw_value,
               'original_unit':raw_unit or unit,'status':status,'details':details}
        if interval_start:entry['interval_start_utc']=interval_start.astimezone(UTC).isoformat()
        self.entries.append(entry)
        return entry
    def save(self,path):Path(path).write_text(json.dumps(self.entries,indent=2,allow_nan=False))
