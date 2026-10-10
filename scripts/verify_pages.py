"""After an operational deployment, verify Pages serves this validated dataset."""
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlparse
import requests

def matches(local,remote):
    return (local.get('meta')==remote.get('meta') and
            local.get('tabs')==remote.get('tabs') and
            local.get('water_review')==remote.get('water_review') and
            local.get('audit')==remote.get('audit'))

def verify(url,site=Path('site'),attempts=12):
    p=urlparse(url)
    if p.scheme!='https' or p.hostname!='mefferso.github.io' or p.username or p.password:
        raise ValueError('Expected official PSH GitHub Pages deployment URL')
    base=url.rstrip('/')+'/'
    local=json.loads((Path(site)/'data/latest.json').read_text())
    for attempt in range(attempts):
        try:
            r=requests.get(base+'data/latest.json',params={'psh_commit':local['meta']['commit'],'attempt':attempt},timeout=(5,20),headers={'Cache-Control':'no-cache'})
            r.raise_for_status();remote=r.json()
            if matches(local,remote):
                download=requests.get(base+'coastal_water_review.csv',params={'psh_commit':local['meta']['commit']},timeout=(5,20),headers={'Cache-Control':'no-cache'})
                download.raise_for_status()
                if download.content==(Path(site)/'coastal_water_review.csv').read_bytes():
                    print(f'Pages verified: commit {local["meta"]["commit"]}; Water Level tab and coastal review match validated export')
                    return True
        except (requests.RequestException,ValueError):pass
        if attempt+1<attempts:time.sleep(10)
    raise RuntimeError('Pages does not serve the validated manifest, Water Level tab and review CSV; inspect deployment/cache')

if __name__=='__main__':verify(sys.argv[1])
