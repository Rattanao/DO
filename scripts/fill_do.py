"""Fill DEM / reefer power / SPECIAL CONTAINER notes into input/DO*.pdf using CHECK DEM.xlsx (input/ or output/).
Usage: python fill_do.py [job folder]
Pages that already carry a typed note (annotation) are left untouched. Output: output/DO-DEM.pdf"""
import glob, os, re, struct, sys, datetime
import pymupdf, openpyxl

BASE = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")

def find(pattern, *dirs):
    for d in dirs:
        hits = sorted(glob.glob(os.path.join(BASE, d, pattern)))
        if hits: return hits[0]
    raise SystemExit(f"ไม่พบไฟล์ {pattern} ใน {', '.join(dirs)}")

SRC, XLS = find("DO*.pdf", "input"), find("CHECK DEM*.xlsx", "input", "output")
OUT = os.path.join(BASE, "output", "DO-DEM.pdf")
OUT_PRINT = os.path.join(BASE, "output", "DO-DEM-PRINT.pdf")

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

STAMP = pymupdf.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "stamp.pdf"))

def stamp_rect(page):
    """Centred under the rider's container list; page centre if the list runs too long."""
    w, h = STAMP[0].rect.width, STAMP[0].rect.height
    y = max(b[3] for b in page.get_text("blocks")) + 40
    if y + h > page.rect.height - 40:
        y = (page.rect.height - h) / 2
    x = (page.rect.width - w) / 2
    return pymupdf.Rect(x, y, x + w, y + h)

SEAL = pymupdf.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "seal.pdf"))
COIN = 64.9                     # seal.pdf box; its ring (76 of 80pt) = 2-baht coin, 21.75 mm

def seal_rect(page):
    """Under the marks that start with AS PER ATTACHED (Container No. column): centre 60pt right
    of the text's left edge, 42pt below its last line. None when the page has no such text."""
    lines = [(l["bbox"], re.sub(r"[\x00-\x1f]", " ", "".join(s["text"] for s in l["spans"])))
             for b in page.get_text("dict")["blocks"] for l in b.get("lines", [])]
    head = next((bb for bb, t in lines if re.search(r"AS\s*PER\s*ATTACHED", t)), None)
    if not head:
        return None
    col = sorted((bb for bb, t in lines if abs(bb[0] - head[0]) < 4 and bb[1] >= head[1] and t.strip()), key=lambda bb: bb[1])
    bottom = head[3]
    for bb in col:                    # consecutive marks lines only (stop at the first big gap)
        if bb[1] - bottom > 15: break
        bottom = max(bottom, bb[3])
    cx, cy = head[0] + 60, bottom + 42
    return pymupdf.Rect(cx - COIN / 2, cy - COIN / 2, cx + COIN / 2, cy + COIN / 2)

MARK = "DO-DEM-FILLED"
# pages we already filled: the marker, or (older outputs) our stamp / Thai note text
DONE = re.compile(r"DO-DEM-FILLED|CERTIFIED\s*TRUE\s*&\s*CORRECT\s*COPY|เริ่มเก็บค่า")

doc = pymupdf.open(SRC)
report, pages = [], []          # pages: (rider, cfs, master B/L) per page, for the print x2 file
for page in doc:
    # some re-saved PDFs write their spaces as control characters ("==\x03ATTACHED\x03RIDER\x03==")
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", " ", page.get_text())
    bl = re.search(r"HASL\w+", text).group()
    master = bl[:-1] if bl[-1].isalpha() else bl
    rider = bool(re.search(r"ATTACHED\s*RIDER", text))
    status = re.search(r"\b(CY|CFS)\s*/\s*(CY|CFS)\b", text)
    cfs = (pages[-1][1] if pages else False) if rider else bool(status and status.group(2) == "CFS")
    pages.append((rider, cfs, master))
    if DONE.search(text):             # a DO-DEM output fed back in: never stamp or note twice
        report.append((page.number + 1, bl, "เติมไว้แล้ว (ข้าม)")); continue
    page.insert_text((1, 3), MARK, fontsize=1, render_mode=3)   # invisible "already filled" marker
    if rider:
        page.show_pdf_page(stamp_rect(page), STAMP, 0)
        report.append((page.number + 1, bl, "ATTACHED RIDER | ประทับตรา CERTIFIED TRUE & CORRECT COPY")); continue
    sr = seal_rect(page)              # "AS PER ATTACHED" D/O: coin-size CORRECTION APPROVED seal
    if sr:
        page.show_pdf_page(sr, SEAL, 0)
    sealed = " + ตรากลม (AS PER ATTACHED)" if sr else ""
    if page.first_annot:
        report.append((page.number + 1, bl, "มีข้อความอยู่แล้ว (ข้าม)" + sealed)); continue
    # house B/L (HASL...A, B, ...) not in CHECK DEM -> use its master B/L
    row = rows.get(bl) or (rows.get(bl[:-1]) if bl[-1].isalpha() else None)
    rec0, dem = row if row else (None, None)
    dem_s = fmt(dem) if isinstance(dem, datetime.datetime) else None
    dg = bool(re.search(r"\bUN\s*(NO\.?)?\s*:?\s*\d{4}\b|\bCLASS\s*:?\s*\d|\bCL\s*\d", text))
    reefer = bool(re.search(r"\b(20|40|45)R[FH]|\bTEMP\b", text))
    tank = bool(re.search(r"ISO\s*TANK|\b\d\dTK\b", text))
    dem_p = "" if cfs else f"<p>เริ่มเก็บค่า DEM. วันที่.&nbsp; <u>{dem_s}&nbsp;</u></p>" if dem_s else ""
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
    if cfs:
        kind += " (" + status.group(0).replace(" ", "") + " ไม่เติม DEM)"
    elif not dem_s and not (tank and dg):
        kind += "  ** ไม่มีวันที่ DEM ใน CHECK DEM **"
    for y, html in parts:
        if html:
            page.insert_htmlbox(pymupdf.Rect(45, y, 300, y + 45), html, css=CSS, archive=arch, scale_low=1)
    report.append((page.number + 1, bl, kind + " | " + " / ".join(re.sub(r"<[^>]+>|&nbsp;", " ", h).strip() for _, h in parts if h) + sealed))

def print_order(pages):
    """x2 for printing. A B/L = its page plus any ATTACHED RIDER pages after it.
    CY: each B/L twice in a row (1,1,2,2). CFS: each master B/L's set of house B/Ls
    twice as separate sets (A,B,C,A,B,C)."""
    bls = []
    for i, (rider, cfs, master) in enumerate(pages):
        if rider and bls: bls[-1][2].append(i)
        else: bls.append((cfs, master, [i]))
    order, k = [], 0
    while k < len(bls):
        cfs, master, idx = bls[k]
        if not cfs:
            order += idx + idx; k += 1; continue
        group = []
        while k < len(bls) and bls[k][0] and bls[k][1] == master:
            group += bls[k][2]; k += 1
        order += group + group
    return order

os.makedirs(os.path.dirname(OUT), exist_ok=True)
doc.save(OUT, garbage=4, deflate=True)
done = pymupdf.open(OUT)
prn = pymupdf.open()
for i in print_order(pages):
    prn.insert_pdf(done, from_page=i, to_page=i)
prn.save(OUT_PRINT, garbage=4, deflate=True)
for r in report: print(*r, sep=" | ")
print(f"\nไฟล์ปริ้น x2: {os.path.basename(OUT_PRINT)} ({len(prn)} หน้า)")
