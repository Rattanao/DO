"""Build the stamps as vector graphics:
- seal.pdf:  the round CORRECTION APPROVED seal alone (80pt box, ring 76pt). fill_do.py and index.html
             place it on "AS PER ATTACHED" D/O pages, scaled so the ring is a 2-baht coin (21.75 mm).
- stamp.pdf: "CERTIFIED TRUE & CORRECT COPY" (12.5pt; CARGO on the D/O header is 14.5pt) + the same
             seal at the same 2-baht ring size, for ATTACHED RIDER pages.
Usage: python make_stamp.py  (writes ../seal.pdf and ../stamp.pdf)"""
import math, os
import pymupdf

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
BLUE = (0.10, 0.25, 0.80)
OPACITY = 0.85
SIZE = 12.5                      # a little smaller than CARGO (14.5pt) on the D/O header
LINE = "CERTIFIED TRUE & CORRECT COPY"
R = 38                           # seal radius in seal.pdf, pt
RING = 21.75 / 25.4 * 72         # 2-baht coin, 21.75 mm = 61.7pt: ring diameter on the page
GAP = 12

kw = dict(color=BLUE, fill_opacity=OPACITY)
helv = pymupdf.Font("hebo")      # Helvetica-Bold

# ---- seal.pdf ----
seal = pymupdf.open()
sp = seal.new_page(width=2 * R + 4, height=2 * R + 4)
cx = cy = R + 2

def arc_text(text, size, radius, top):
    """Write text along the circle: top = reads clockwise over the top, glyphs pointing out;
    otherwise reads left to right under the bottom, glyphs pointing in."""
    widths = [helv.text_length(c, size) for c in text]
    span = sum(widths) / radius
    a = math.pi / 2 + span / 2 if top else 3 * math.pi / 2 - span / 2
    for c, w in zip(text, widths):
        mid = a - w / 2 / radius if top else a + w / 2 / radius
        x, y = cx + radius * math.cos(mid), cy - radius * math.sin(mid)   # glyph centre on the baseline
        deg = math.degrees(mid) - 90 if top else math.degrees(mid) + 90     # reading direction
        t = math.radians(deg)
        start = pymupdf.Point(x - w / 2 * math.cos(t), y + w / 2 * math.sin(t))
        sp.insert_text(start, c, fontname="hebo", fontsize=size, morph=(start, pymupdf.Matrix(deg)), **kw)
        a = a - w / radius if top else a + w / radius

sp.draw_circle((cx, cy), R, color=BLUE, width=1.6, stroke_opacity=OPACITY)
arc_text("CORRECTION APPROVED", 8.6, R - 11, top=True)
arc_text("BANGKOK", 8.6, R - 3.5, top=False)
arc_text("HEUNG A LINE (THAILAND) CO.,LTD.", 4.6, R - 19, top=True)
seal.save(os.path.join(DIR, "seal.pdf"))

# ---- stamp.pdf: text + seal scaled so its ring is RING ----
box = RING * sp.rect.width / (2 * R)          # seal.pdf box size that gives that ring
text_w = pymupdf.Font("tibo").text_length(LINE, SIZE)
W, H = text_w + GAP + box, box
doc = pymupdf.open()
page = doc.new_page(width=W, height=H)
page.insert_text((0, H / 2 + SIZE * 0.35), LINE, fontname="tibo", fontsize=SIZE, **kw)
page.show_pdf_page(pymupdf.Rect(W - box, 0, W, H), seal, 0)
doc.save(os.path.join(DIR, "stamp.pdf"))
print(f"stamp.pdf {W:.1f} x {H:.1f} pt, ring {RING:.1f} pt; seal.pdf box {sp.rect.width:.0f} pt (place at {box:.1f} pt)")
