"""Export PSH workbook data for the static GitHub Pages review dashboard."""
import json
import os
from pathlib import Path
from datetime import date, datetime
from openpyxl import load_workbook

def clean(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)

def export():
    files = list(Path("output").glob("*_PARTIAL.xlsx"))
    if not files:
        raise FileNotFoundError("No PSH workbook in output/")
    book = load_workbook(files[0], data_only=False, read_only=False)
    meta = json.loads(Path("output/QC.json").read_text())
    result = {"meta": meta, "tabs": {}, "download": files[0].name}
    # Maintain traceable hyperlinks for stations. Numeric values are original cell contents,
    # not cosmetically rounded by the dashboard.
    for sheet in book:
        headers = [clean(sheet.cell(1, c).value) for c in range(1, sheet.max_column + 1)]
        if sheet.title == "Summary":
            # Formula-driven Google summary cannot be evaluated by openpyxl.
            result["tabs"][sheet.title] = {"status": "NOT CALCULATED", "headers": [], "rows": [],
                "notice": "The template uses Google QUERY formulas. Summary results are not calculated in this XLSX."}
            continue
        rows = []
        for r in range(2, sheet.max_row + 1):
            first = sheet.cell(r, 1).value
            if first is None or str(first).strip() == "":
                continue
            if str(first).lower().startswith(("latest update", "update detail", "remarks:", "rainfall start", "rainfall end")):
                continue
            values = [clean(sheet.cell(r, c).value) for c in range(1, sheet.max_column + 1)]
            if isinstance(first, str) and first.strip().startswith(("Example", "[", "Site ID")):
                continue
            links = {}
            for c in range(1, sheet.max_column + 1):
                link = sheet.cell(r, c).hyperlink
                if link and link.target and link.target.startswith(("https://", "http://")):
                    links[str(c-1)] = link.target
            if all(x is None for x in values[1:]) and not links:
                continue
            rows.append({"v": values, "links": links})
        result["tabs"][sheet.title] = {"status": "REVIEW", "headers": headers, "rows": rows}
    Path("site/data").mkdir(parents=True, exist_ok=True)
    Path("site/data/latest.json").write_text(json.dumps(result, ensure_ascii=False, default=str))
    (Path("site") / files[0].name).write_bytes(files[0].read_bytes())
    (Path("site") / ".nojekyll").write_text("")
    print(f"Dashboard export: {len(result['tabs'])} tabs; {sum(len(t.get('rows',[])) for t in result['tabs'].values())} entries")

if __name__ == "__main__":
    export()
