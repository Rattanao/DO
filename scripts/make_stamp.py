"""Build stamp.pdf: the blue "CERTIFIED TRUE & CORRECT COPY" stamp with the round
CORRECTION APPROVED seal, as vector graphics. fill_do.py and index.html overlay it on
ATTACHED RIDER pages. CERTIFIED line 12.5pt (CARGO on the D/O header is 14.5pt); seal unchanged.
Usage: python make_stamp.py  (writes ../stamp.pdf)"""
import math, os
import pymupdf

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "stamp.pdf")
BLUE = (0.10, 0.25, 0.80)
OPACITY = 0.85
SIZE = 12.5                      # a little smaller than CARGO (14.5pt) on the D/O header
LINE = "CERTIFIED TRUE & CORRECT COPY"
R = 38                           # seal radius, pt
GAP = 14

times = pymupdf.Font("tibo")     # Times-Bold
helv = pymupdf.Font("hebo")      # Helvetica-Bold
text_w = times.text_length(LINE, SIZE)
W, H = text_w + GAP + 2 * R + 4, 2 * R + 4
cx, cy = text_w + GAP + R + 2, H / 2

doc = pymupdf.open()
page = doc.new_page(width=W, height=H)
kw = dict(color=BLUE, fill_opacity=OPACITY)
page.insert_text((0, cy + SIZE * 0.35), LINE, fontname="tibo", fontsize=SIZE, **kw)

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
        page.insert_text(start, c, fontname="hebo", fontsize=size, morph=(start, pymupdf.Matrix(deg)), **kw)
        a = a - w / radius if top else a + w / radius

page.draw_circle((cx, cy), R, color=BLUE, width=1.6, stroke_opacity=OPACITY)
arc_text("CORRECTION APPROVED", 8.6, R - 11, top=True)
arc_text("BANGKOK", 8.6, R - 3.5, top=False)
arc_text("HEUNG A LINE (THAILAND) CO.,LTD.", 4.6, R - 19, top=True)
doc.save(OUT)
print(OUT, round(W, 1), "x", round(H, 1), "pt")

# seal.pdf: the round seal alone, for "AS PER ATTACHED" D/O pages (placed at 1-baht-coin size)
seal = pymupdf.open()
box = pymupdf.Rect(cx - R - 2, cy - R - 2, cx + R + 2, cy + R + 2)
seal.new_page(width=box.width, height=box.height).show_pdf_page(pymupdf.Rect(0, 0, box.width, box.height), doc, 0, clip=box)
seal.save(os.path.join(os.path.dirname(OUT), "seal.pdf"))
