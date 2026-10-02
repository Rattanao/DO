"""Fill DEM / reefer power / SPECIAL CONTAINER notes into input/DO*.pdf using CHECK DEM.xlsx (input/ or output/).
Usage: python fill_do.py [job folder]
Pages that already carry a typed note (annotation) are left untouched. Output: output/DO.pdf"""
import glob, os, re, struct, sys, datetime
import pymupdf, openpyxl

BASE = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")

def find(pattern, *dirs):
    for d in dirs:
        hits = sorted(glob.glob(os.path.join(BASE, d, pattern)))
        if hits: return hits[0]
    raise SystemExit(f"ไม่พบไฟล์ {pattern} ใน {', '.join(dirs)}")

SRC, XLS = find("DO*.pdf", "input"), find("CHECK DEM*.xlsx", "input", "output")
OUT = os.path.join(BASE, "output", "DO.pdf")

def ttc_faces(data):
    """Split a .ttc into standalone .ttf byte strings (no fontTools needed)."""
    n = struct.unpack(">I", data[8:12])[0]
    for off in struct.unpack(f">{n}I", data[12:12 + 4 * n]):
        nt = struct.unpack(">H", data[off + 4:off + 6])[0]
        recs = [struct.unpack(">4sIII", data[off + 12 + 16 * i:off + 28 + 16 * i]) for i in range(nt)]
        head, body, pos = data[off:off + 12], b"", 12 + 16 * nt
        for tag, cs, o, ln in recs:
            head += struct.pack(">4sIII", tag, cs, pos + len(body), ln)
            body += data[o:o + ln] + bytes(-ln % 4)
        yield head + body

def bold_font():
    for ttf in ttc_faces(open("C:/Windows/Fonts/angsana.ttc", "rb").read()):
        f = pymupdf.Font(fontbuffer=ttf)
        if f.is_bold and not f.is_italic:
            return ttf
    raise SystemExit("Angsana New Bold not found")

def fmt(d):
    return d.strftime("%d-%b-%Y").upper()

ws = openpyxl.load_workbook(XLS).active
grid = list(ws.iter_rows(values_only=True))
ata = next(r[i + 1] for r in grid for i, v in enumerate(r[:-1]) if v == "ATA")
h = next(i for i, r in enumerate(grid) if "B/L No." in r)
col = {str(v).strip(): i for i, v in enumerate(grid[h]) if v}
rows = {r[col["B/L No."]]: (r[col["REC."]], r[col["DEM."]]) for r in grid[h + 1:] if r[col["B/L No."]]}

arch = pymupdf.Archive(); arch.add((bold_font(), "angsab.ttf"))
CSS = ("@font-face{font-family:ang;src:url(angsab.ttf);} "
       "p{font-family:ang;font-size:15.5pt;margin:0;line-height:1.05;} u{text-decoration:underline;}")
SPECIAL = "<p>SPECIAL CONTAINER</p><p>.......DG..........OP..........FR</p>"

doc = pymupdf.open(SRC)
report = []
for page in doc:
    text = page.get_text()
    bl = re.search(r"HASL\w+", text).group()
    if page.first_annot:
        report.append((page.number + 1, bl, "มีข้อความอยู่แล้ว (ข้าม)")); continue
    row = rows.get(bl)
    rec0, dem = row if row else (None, None)
    dem_s = fmt(dem) if isinstance(dem, datetime.datetime) else None
    dg = bool(re.search(r"\bUN\s*(NO\.?)?\s*:?\s*\d{4}\b|\bCLASS\s*:?\s*\d|\bCL\s*\d", text))
    reefer = bool(re.search(r"\b(20|40|45)R[FH]|\bTEMP\b", text))
    tank = bool(re.search(r"ISO\s*TANK|\b\d\dTK\b", text))
    dem_p = f"<p>เริ่มเก็บค่า DEM. วันที่.&nbsp; <u>{dem_s}&nbsp;</u></p>" if dem_s else ""
    if tank and dg:
        kind, parts = "ISO TANK+DG", [(700, SPECIAL)]
    elif reefer:
        rec = rec0 if isinstance(rec0, datetime.datetime) else ata + datetime.timedelta(days=3)
        kind = "REEFER"
        parts = [(704, f"<p>เริ่มเก็บค่าไฟวันที่ &nbsp;<u>&nbsp;{fmt(rec)}&nbsp;</u></p>"), (740, dem_p)]
        if dg: kind, parts = "REEFER+DG", [(684, SPECIAL)] + [(y + 20, h) for y, h in parts]
    elif dg:
        kind, parts = "DG", [(690, SPECIAL), (760, dem_p)]
    else:
        kind, parts = "ทั่วไป", [(728, dem_p)]
    if not dem_s and not (tank and dg):
        kind += "  ** ไม่มีวันที่ DEM ใน CHECK DEM **"
    for y, html in parts:
        if html:
            page.insert_htmlbox(pymupdf.Rect(45, y, 300, y + 45), html, css=CSS, archive=arch, scale_low=1)
    report.append((page.number + 1, bl, kind + " | " + " / ".join(re.sub(r"<[^>]+>|&nbsp;", " ", h).strip() for _, h in parts if h)))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
doc.save(OUT, garbage=4, deflate=True)
for r in report: print(*r, sep=" | ")
