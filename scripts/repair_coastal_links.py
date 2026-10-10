"""Patch only the 31 audited workbook hyperlinks; preserve all other ZIP parts.

Avoid round-tripping the template through openpyxl, which can rewrite drawing,
style and application metadata. WCCL1 requires one new hyperlink relationship.
"""
import html
import re
import zipfile
from pathlib import Path
from openpyxl import load_workbook
from common import inventory
from coastal_water import load_mapping, match_template

def repair(source,target):
    source=Path(source);target=Path(target);wb=load_workbook(source);mapping=load_mapping()
    stations=[s for s in inventory(wb,'Water Level') if s['id'] in mapping and s['network'] in ('USACE','LA CPRA')]
    if len(stations)!=31 or any(not match_template(s,wb,mapping[s['id']]) for s in stations):
        raise ValueError('Template does not match all 31 audited station identities')
    with zipfile.ZipFile(source) as z:
        parts={n:z.read(n) for n in z.namelist()};infos=z.infolist()
    # Existing template and generated workbooks both retain Water Level sheet4.
    sheet_name='xl/worksheets/sheet4.xml';rels_name='xl/worksheets/_rels/sheet4.xml.rels'
    text=parts[sheet_name].decode();rels=parts[rels_name].decode()
    for st in stations:
        row=st['row'];m=mapping[st['id']];ref=f'A{row}';link=html.escape(m['observation_url'],quote=True)
        tags=re.findall(r'<hyperlink\b[^>]*/>',text)
        tag=next((t for t in tags if re.search(r'\bref="'+ref+r'"',t)),None)
        if tag:
            rid=re.search(r'\br:id="([^"]+)"',tag).group(1)
            pattern=r'(<Relationship\b[^>]*\bId="'+re.escape(rid)+r'"[^>]*\bTarget=")[^"]*(")'
            # Attribute ordering differs between Excel and openpyxl.
            rel_tag=next(t for t in re.findall(r'<Relationship\b[^>]*/>',rels) if re.search(r'\bId="'+re.escape(rid)+r'"',t))
            replacement=re.sub(r'\bTarget="[^"]*"','Target="'+link+'"',rel_tag)
            rels=rels.replace(rel_tag,replacement)
        else:
            if st['id']!='WCCL1':raise ValueError('Unexpected missing original hyperlink')
            rid='rIdCoastalWCCL1'
            if rid in rels:raise ValueError('Conflicting WCC relationship')
            rel=f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" Target="{link}" TargetMode="External"/>'
            rels=rels.replace('</Relationships>',rel+'</Relationships>')
            text=text.replace('</hyperlinks>',f'<hyperlink ref="{ref}" r:id="{rid}"/></hyperlinks>')
    parts[sheet_name]=text.encode();parts[rels_name]=rels.encode()
    temp=target.with_suffix('.tmp.xlsx')
    with zipfile.ZipFile(temp,'w') as z:
        for info in infos:z.writestr(info,parts[info.filename])
    temp.replace(target)

if __name__=='__main__':
    import sys
    source=Path(sys.argv[1] if len(sys.argv)>1 else 'Copy of PSHLIX_YYYYALXX_StormName_Data.xlsx')
    repair(source,Path(sys.argv[2]) if len(sys.argv)>2 else source)
