"""Fill DEM / reefer power / SPECIAL CONTAINER notes into the D/O pages of every PDF in input/,
using CHECK DEM.xlsx (input/ or output/, optional), merge each B/L as D/O -> ATTACHED -> ใบเปิดตู้ / คำร้อง,
and check the ใบเปิดตู้ / คำร้อง against the D/O (vessel, arrival date, CNTR, CNEE, B/L NO., STATUS).
Usage: python fill_do.py [job folder]
Pages that already carry a typed note (annotation) are left untouched.
Output: output/DO-DEM.pdf and output/DO-DEM-PRINT x 2.pdf"""
import glob, json, os, re, struct, sys, datetime
import pymupdf, openpyxl

BASE = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
SRCS = sorted(glob.glob(os.path.join(BASE, "input", "*.pdf")))
if not SRCS:
    raise SystemExit("ไม่พบไฟล์ .pdf ใน input")
XLS = next((h for d in ("input", "output") for h in sorted(glob.glob(os.path.join(BASE, d, "CHECK DEM*.xlsx")))), None)
OUT = os.path.join(BASE, "output", "DO-DEM.pdf")
OUT_PRINT = os.path.join(BASE, "output", "DO-DEM-PRINT x 2.pdf")

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

ata, rows = None, {}
if XLS:
    ws = openpyxl.load_workbook(XLS).active
    grid = list(ws.iter_rows(values_only=True))
    ata = next((r[i + 1] for r in grid for i, v in enumerate(r[:-1]) if v == "ATA"), None)
    h = next(i for i, r in enumerate(grid) if "B/L No." in r)
    col = {str(v).strip(): i for i, v in enumerate(grid[h]) if v}
    rows = {r[col["B/L No."]]: (r[col["REC."]] if "REC." in col else None, r[col["DEM."]]) for r in grid[h + 1:] if r[col["B/L No."]]}
else:
    print("!! ไม่พบ CHECK DEM*.xlsx — เติมได้เฉพาะ SPECIAL CONTAINER หน้าไหนไม่มีวันที่จะแจ้งไว้\n")

arch = pymupdf.Archive(); arch.add((bold_font(), "angsab.ttf"))
CSS = ("@font-face{font-family:ang;src:url(angsab.ttf);} "
       "p{font-family:ang;font-size:15.5pt;margin:0;line-height:1.05;} u{text-decoration:underline;}")
SPECIAL = "<p>SPECIAL CONTAINER</p><p>.......DG..........OP..........FR</p>"

MARK = "DO-DEM-FILLED"
# pages we already filled: the marker, or (older outputs) the old stamp / Thai note text
DONE = re.compile(r"DO-DEM-FILLED|CERTIFIED\s*TRUE\s*&\s*CORRECT\s*COPY|เริ่มเก็บค่า")
CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")   # some re-saved PDFs write their spaces as control characters
RE_BL = re.compile(r"HASL\w+")
RE_STATUS = re.compile(r"\b(CY|CFS)\s*/\s*(CY|CFS)\b")
RE_CNTR = re.compile(r"\b[A-Z]{3}[UJZ]\d{7}\b")

# ---------- read every page: what it is, its B/L, its text lines ----------
def covers_of(src):
    """Cover-ups the web page made when correcting a ใบเปิดตู้ (PDF Keywords DOCOVERS:<json>, PDF units)."""
    m = re.search(r"DOCOVERS:(\[.*\])", src.metadata.get("keywords") or "")
    try: return json.loads(m.group(1)) if m else []
    except ValueError: return []

def lines_of(page, covers):
    """Text lines (top-down coords). Text under a web cover-up is dropped and its new value put back."""
    H, out = page.rect.height, []
    for c in covers:
        if c.get("v"): out.append({"x0": c["x"], "y0": H - c["y"] - c["h"], "y1": H - c["y"], "s": c["v"]})
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            spans = [sp for sp in l["spans"] if not any(
                c["x"] - 1 <= sp["origin"][0] < c["x"] + c["w"] - 1 and abs((H - c["y"]) - sp["origin"][1]) < c["h"] * 0.6 for c in covers)]
            s = CTRL.sub(" ", "".join(sp["text"] for sp in spans))
            s = re.sub(r"\s+", " ", s).strip()
            if s:
                out.append({"x0": spans[0]["bbox"][0], "y0": l["bbox"][1], "y1": l["bbox"][3], "s": s})
    return out

doc = pymupdf.open()
info, last_bl = [], "?"
for path in SRCS:
    src = pymupdf.open(path)
    covers = covers_of(src)
    for pi, pg in enumerate(src):
        text = CTRL.sub(" ", pg.get_text())
        for c in covers:
            if c["pi"] == pi and c.get("v"): text += "\n" + c["v"]
        kind = ("do" if re.search(r"CARGO\s*DELIVERY\s*ORDER", text)
                else "rider" if re.search(r"=\s*ATTACHED\s*RIDER\s*=", text)
                else "open1" if "เปิดตู้คอนเทนเนอร์" in text
                else "open2" if "อารักขาของศุลกากร" in text
                else "sheet")
        m = RE_BL.search(text)
        bl = m.group() if m else last_bl           # คำร้อง (page 2) has no B/L: it belongs to the form before it
        last_bl = bl
        info.append({"kind": kind, "bl": bl, "text": text, "file": os.path.basename(path), "own_bl": bool(m),
                     "lines": lines_of(pg, [c for c in covers if c["pi"] == pi])})
    doc.insert_pdf(src)

# A CFS D/O is 'split' when it is a house B/L (...A, ...B) or has house B/Ls in this job.
# Only split CFS sets go without DEM; a single (not split) CFS D/O is filled like CY.
ALL_BLS = {p["bl"] for p in info if p["kind"] == "do"}
def is_split(bl):
    return bl[-1].isalpha() or any(b != bl and b[:-1] == bl and b[-1].isalpha() for b in ALL_BLS)

# ---------- fill the D/O pages ----------
report, pages = [], []          # pages: (attached, cfs, master B/L) per page, for the print x2 file
for page in doc:
    p = info[page.number]
    text, bl, kind0 = p["text"], p["bl"], p["kind"]
    master = bl[:-1] if bl[-1].isalpha() else bl
    if kind0 in ("sheet", "open1", "open2"):   # ATTACHED sheet, ใบเปิดตู้, คำร้อง: never filled
        pages.append((True, pages[-1][1] if pages else False, master))
        report.append([page.number, bl, {"sheet": "ATTACHED SHEET", "open1": "ใบเปิดตู้", "open2": "คำร้อง"}[kind0] + f" ({p['file']})"])
        continue
    rider = kind0 == "rider"
    status = RE_STATUS.search(text)
    cfs = (pages[-1][1] if pages else False) if rider else bool(status and status.group(2) == "CFS")
    pages.append((rider, cfs, master))
    # old web stamps (pdf-lib embedPdf XObjects, always named EmbeddedPdfPage-<n>): blank them out
    old = [x[0] for x in page.get_xobjects() if x[1].startswith("EmbeddedPdfPage-")]
    for xref in old:
        doc.update_stream(xref, b" ")
    unstamped = " · ลบตรายางเก่าออกแล้ว" if old else ""
    if DONE.search(text):             # a DO-DEM output fed back in: never note twice
        report.append([page.number, bl, "เติมไว้แล้ว (ข้าม)" + unstamped]); continue
    page.insert_text((1, 3), MARK, fontsize=1, render_mode=3)   # invisible "already filled" marker
    if rider:                         # ATTACHED RIDER pages are left as they are
        report.append([page.number, bl, "ATTACHED RIDER (ไม่เติม)" + unstamped]); continue
    if page.first_annot:
        report.append([page.number, bl, "มีข้อความอยู่แล้ว (ข้าม)"]); continue
    # house B/L (HASL...A, B, ...) not in CHECK DEM -> use its master B/L
    row = rows.get(bl) or (rows.get(bl[:-1]) if bl[-1].isalpha() else None)
    rec0, dem = row if row else (None, None)
    dem_s = fmt(dem) if isinstance(dem, datetime.datetime) else None
    dg = bool(re.search(r"\bUN\s*(NO\.?)?\s*:?\s*\d{4}\b|\bCLASS\s*:?\s*\d|\bCL\s*\d", text))
    reefer = bool(re.search(r"\b(20|40|45)R[FH]|\bTEMP\b", text))
    tank = bool(re.search(r"ISO\s*TANK|\b\d\dTK\b", text))
    no_dem = cfs and is_split(bl)
    dem_p = "" if no_dem else f"<p>เริ่มเก็บค่า DEM. วันที่.&nbsp; <u>{dem_s}&nbsp;</u></p>" if dem_s else ""
    if tank and dg:
        kind, parts = "ISO TANK+DG", [(700, SPECIAL)]
    elif reefer:
        rec = rec0 if isinstance(rec0, datetime.datetime) else (ata + datetime.timedelta(days=3) if ata else None)
        kind = "REEFER"
        parts = [(704, f"<p>เริ่มเก็บค่าไฟวันที่ &nbsp;<u>&nbsp;{fmt(rec)}&nbsp;</u></p>" if rec else ""), (740, dem_p)]
        if dg: kind, parts = "REEFER+DG", [(684, SPECIAL)] + [(y + 20, h) for y, h in parts]
    elif dg:
        kind, parts = "DG", [(690, SPECIAL), (760, dem_p)]
    else:
        kind, parts = "ทั่วไป", [(728, dem_p)]
    if no_dem:
        kind += " (" + status.group(0).replace(" ", "") + " SPLIT ไม่เติม DEM)"
    elif cfs:
        kind += " (" + status.group(0).replace(" ", "") + " เดี่ยว เติมเหมือน CY)"
        if not dem_s: kind += "  ** ไม่มีวันที่ DEM ใน CHECK DEM **"
    elif not dem_s and not (tank and dg):
        kind += "  ** ไม่มีวันที่ DEM ใน CHECK DEM **"
    for y, html in parts:
        if html:
            page.insert_htmlbox(pymupdf.Rect(45, y, 300, y + 45), html, css=CSS, archive=arch, scale_low=1)
    report.append([page.number, bl, kind + " | " + " / ".join(re.sub(r"<[^>]+>|&nbsp;", " ", h).strip() for _, h in parts if h)])

# ---------- merge order: per D/O B/L -> D/O (+ rider) -> ATTACHED -> ใบเปิดตู้ / คำร้อง ----------
order, used, dropped = [], set(), []
def put(i):
    if i not in used: used.add(i); order.append(i)
for i, p in enumerate(info):
    if p["kind"] != "do" or i in used: continue
    put(i)
    j = i + 1
    while j < len(info) and info[j]["kind"] == "rider": put(j); j += 1
    # ATTACHED sheets right after the D/O, one copy of each (identical pages are dropped), in the order
    # of the user's example (C:\EDI\DO_DEM.pdf): the sheet with the B/L no. (UTCT form) -> the sheet
    # without a B/L no. -> the DEPOT sheet.
    seen = set()
    sheets = [k for k, q in enumerate(info) if q["kind"] == "sheet" and q["bl"] == p["bl"]]
    def rank(k):
        q = info[k]
        return 2 if re.search(r"DEPOT", q["text"]) else 0 if q["own_bl"] else 1
    for k in sorted(sheets, key=lambda k: (rank(k), k)):
        key = re.sub(r"\s+", " ", info[k]["text"]).strip()
        if key in seen: dropped.append(k); used.add(k); continue
        seen.add(key); put(k)
    for k, q in enumerate(info):
        if q["kind"] in ("open1", "open2") and q["bl"] == p["bl"]: put(k)
for i in range(len(info)): put(i)
doc.select(order)
pages = [pages[i] for i in order]
report = [report[i] for i in order]

def print_order(pages):
    """x2 for printing. A B/L = its page plus its ATTACHED RIDER / ATTACHED / ใบเปิดตู้ pages.
    CY: each B/L twice in a row (1,1,2,2). CFS: each master B/L's set of house B/Ls
    twice as separate sets (A,B,C,A,B,C)."""
    bls = []
    for i, (attached, cfs, master) in enumerate(pages):
        if attached and bls: bls[-1][2].append(i)
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

# ---------- ใบเปิดตู้ / คำร้อง vs D/O ----------
def under(lines, label, drop, width):
    lab = next((l for l in lines if re.search(label, l["s"], re.I)), None)
    if not lab: return ""
    got = [l for l in lines if 4 < l["y0"] - lab["y0"] < drop and lab["x0"] - 3 <= l["x0"] < lab["x0"] + width]
    return " ".join(l["s"] for l in sorted(got, key=lambda l: l["y0"]))

def norm(s): return re.sub(r"[^A-Z0-9]", "", str(s or "").upper())
MON3 = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
def ymd(s):
    m = re.search(r"(\d{4})\.(\d{1,2})\.(\d{1,2})", str(s))
    if m: return f"{m[1]}-{int(m[2]):02}-{int(m[3]):02}"
    m = re.search(r"(\d{1,2})[-\s]([A-Za-z]{3})[-\s](\d{2,4})", str(s))
    if m and m[2].upper() in MON3:
        y = "20" + m[3] if len(m[3]) == 2 else m[3]
        return f"{y}-{MON3.index(m[2].upper()) + 1:02}-{int(m[1]):02}"
    return ""

def same(key, d, f):
    if key == "date": return bool(ymd(d)) and ymd(d) == ymd(f)
    if key == "vessel": return norm(re.sub(r"\bV\s*\.\s*(?=\w)", "", d)) == norm(re.sub(r"\bV\s*\.\s*(?=\w)", "", f))
    if key == "cntr": return sorted(d.split(", ")) == sorted(f.split(", "))
    if key == "status":   # FCL = CY/CY or CFS/CY, CFS = เปิดตู้, LCL = ขนส่ง
        k = (re.search(r"\b(FCL|LCL|CFS)\b", f) or [None, None])[1]
        if d.endswith("/CY"): return k == "FCL"
        if d.endswith("CFS"): return k in ("CFS", "LCL")
        if "LCL" in d: return k == "LCL"
        return False
    if key == "cnee":   # the D/O box may go on with an address: a full company name on the form that starts it is fine
        return norm(d) == norm(f) or (bool(RE_COMPANY_END.search(f)) and norm(d).startswith(norm(f)))
    return norm(d) == norm(f)
RE_COMPANY_END = re.compile(r"(CO\.?\s*,?\s*LTD\.?|LIMITED|LTD\.?|INC\.?|CORP(ORATION)?\.?|COMPANY|PCL\.?|PLC\.?)\s*$", re.I)

def check_forms(date_fixes=None):
    out = []
    for di, d in enumerate(info):
        if d["kind"] != "do": continue
        forms_i = [k for k, p in enumerate(info) if p["kind"] in ("open1", "open2") and p["bl"] == d["bl"]]
        forms = [info[k] for k in forms_i]
        if not forms: continue
        # containers can be listed on the D/O's ATTACHED RIDER pages ("AS PER ATTACHED RIDER")
        rider_text, j = "", di + 1
        while j < len(info) and info[j]["kind"] == "rider": rider_text += "\n" + info[j]["text"]; j += 1
        st = RE_STATUS.search(d["text"])
        lcl = re.search(r"\bLCL\s*(\(\s*\w+\s*\))?", d["text"])
        dof = {"vessel": under(d["lines"], r"^Ocean\s*Vessel", 20, 150),
               "date": (re.search(r"Arrival\s*Date\s*:?\s*(\d{4}\.\d{1,2}\.\d{1,2})", d["text"]) or [None, ""])[1],
               "cntr": ", ".join(dict.fromkeys(RE_CNTR.findall(d["text"] + rider_text))),
               "cnee": under(d["lines"], r"^Consignee$", 60, 250),
               "bl": d["bl"],
               "status": st.group(0).replace(" ", "") if st else (re.sub(r"\s", "", lcl.group()) if lcl else "")}
        rows_ = []
        for key, label in [("vessel", "ชื่อเรือ"), ("date", "วันที่เรือเข้า"), ("cntr", "CNTR"), ("cnee", "CNEE"), ("bl", "B/L NO."), ("status", "STATUS")]:
            cells = []
            for fk, f in zip(forms_i, forms):
                L = f["lines"]
                if key == "vessel":
                    v = next((m.group().strip() for l in L for m in [re.search(r"[A-Z][A-Z0-9.&\- ]*?\s+V\s*\.\s*[A-Z0-9]+", l["s"])] if m), None)
                elif key == "date":
                    v = next((m.group() for l in L for m in [re.search(r"\b\d{1,2}[-\s][A-Za-z]{3}[-\s]\d{2,4}\b", l["s"])] if m), None)
                elif key == "cntr":
                    v = ", ".join(dict.fromkeys(RE_CNTR.findall(f["text"]))) or None
                elif key == "cnee":
                    lab = next((l for l in L if re.fullmatch(r"CNEE:?", l["s"])), None)
                    c = sorted([l for l in L if lab and 4 < l["y0"] - lab["y0"] < 30 and abs(l["x0"] - lab["x0"]) < 20], key=lambda l: l["y0"])
                    c = c[0] if c else next((l for l in L if norm(l["s"]) == norm(dof["cnee"])), None) or \
                        next((l for l in L if re.search(r"CO\.?,?\s*LTD|LIMITED|COMPANY", l["s"]) and "HEUNG A LINE" not in l["s"]), None)
                    v = None
                    if c:
                        # a long consignee wraps onto the next line(s) ("THAI SAMSUNG ELECTRONICS" / "CO.,LTD."): take them all
                        parts, prev = [c["s"]], c
                        if lab:
                            for l in sorted([l for l in L if l["y0"] > c["y0"] and abs(l["x0"] - c["x0"]) < 20], key=lambda l: l["y0"]):
                                if l["y0"] - prev["y1"] > (prev["y1"] - prev["y0"]) * 0.8 or len(parts) >= 3 or re.match(r"(ONE|B/L|STATUS)\b", l["s"]):
                                    break
                                parts.append(l["s"]); prev = l
                        v = " ".join(parts)
                elif key == "bl":
                    v = next((m.group() for l in L for m in [RE_BL.search(l["s"])] if m), None)
                else:
                    v = next((m.group() for l in L for m in [re.search(r"\b(FCL|LCL|CFS)\b(\s*\([^)]*\))?", l["s"])] if m), None)
                ok = None if v is None else same(key, dof[key], v)
                if key == "date" and ok is False and date_fixes is not None and ymd(dof["date"]):
                    y, mo, dd = ymd(dof["date"]).split("-")
                    date_fixes.append((fk, v, f"{int(dd)}-{MON3[int(mo) - 1].title()}-{y[2:]}"))
                cells.append((v, ok))
            rows_.append((label, dof[key], cells))
        out.append((d["bl"], [("ใบเปิดตู้" if f["kind"] == "open1" else "คำร้อง") for f in forms], rows_))
    return out

# dates on ใบเปิดตู้ / คำร้อง always follow the D/O: wrong ones are replaced in the output, then checked again
fixes = []
checks = check_forms(fixes)
for k, old, new in fixes:
    page = doc[order.index(k)]
    rects = page.search_for(old)
    for r in rects: page.add_redact_annot(r, fill=(1, 1, 1))
    page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE)
    for r in rects: page.insert_text((r.x0, r.y1 - r.height * 0.22), new, fontname="helv", fontsize=r.height * 0.75)
    info[k]["text"] = info[k]["text"].replace(old, new)
    for l in info[k]["lines"]: l["s"] = l["s"].replace(old, new)
if fixes:
    checks = check_forms()

os.makedirs(os.path.dirname(OUT), exist_ok=True)
doc.save(OUT, garbage=4, deflate=True)
done = pymupdf.open(OUT)
prn = pymupdf.open()
for i in print_order(pages):
    prn.insert_pdf(done, from_page=i, to_page=i)
prn.save(OUT_PRINT, garbage=4, deflate=True)
for n, r in enumerate(report, 1): print(n, *r[1:], sep=" | ")
print(f"\nไฟล์ปริ้น x2: {os.path.basename(OUT_PRINT)} ({len(prn)} หน้า)")
if dropped:
    print(f"ตัด ATTACHED ที่ซ้ำกันออก {len(dropped)} หน้า (เก็บไว้หน้าละ 1)")

if fixes:
    print(f"\nแก้วันที่ใบเปิดตู้ / คำร้องตาม DO ให้อัตโนมัติแล้ว {len(fixes)} ช่อง: " + ", ".join(f"{o} -> {n}" for _, o, n in fixes))
# only the B/Ls that need fixing are listed; matching ones are just counted
need = [c for c in checks if any(cell[1] is False for _, _, cells in c[2] for cell in cells)]
bad = 0
for bl, heads, rows_ in need:
    print(f"\n=== ใบเปิดตู้ / คำร้อง ต้องแก้  B/L {bl} ===")
    print(" | ".join(["หัวข้อ", "DO"] + heads + ["ผล"]))
    for label, dv, cells in rows_:
        ok = all(c[1] is not False for c in cells)
        bad += 0 if ok else sum(1 for c in cells if c[1] is False)
        print(" | ".join([label, dv or "-"] + ["(ฟอร์มนี้ไม่มีช่องนี้)" if v is None else v for v, _ in cells] + ["ตรง" if ok else "** ไม่ตรง **"]))
if checks:
    print(f"\nตรวจใบเปิดตู้ {len(checks)} B/L: ต้องแก้ {len(need)} B/L ({bad} ช่อง), ตรงทุกหัวข้อ {len(checks) - len(need)} B/L")
if bad:
    print("!! แก้ได้บนเว็บ https://rattanao.github.io/DO/ (ตาราง ตรวจใบเปิดตู้)")
