---
name: do
description: >
  "DO": types the demurrage / reefer-power / SPECIAL CONTAINER notes onto every Heung-A Cargo
  Delivery Order page in input/ (dates from CHECK DEM.xlsx, the check-dem report), merges each B/L
  as D/O -> ATTACHED sheet -> ใบเปิดตู้ / คำร้อง, and checks the ใบเปิดตู้ / คำร้อง against the D/O
  (vessel, arrival date, CNTR, CNEE, B/L NO., STATUS). Writes output/DO-DEM.pdf and a print-x2 copy
  output/DO-DEM-PRINT x 2.pdf. Use whenever the user says "DO", "ทำ DO", "เติม DO", "เติมวันที่ DEM ใน DO",
  "รวม DO ATTACHED ใบเปิด", "ตรวจใบเปิดตู้", or points to a folder with input/ holding a DO PDF
  (with or without ATTACHED.pdf / ใบเปิด.pdf) plus a CHECK DEM.xlsx.
---

# DO

Rattana's confirmed layout. Run the bundled script; do not place the text by hand.

## Rules (already implemented in the script and in index.html)

Every PDF in `input/` is read and each page is classified by its text: D/O (`CARGO DELIVERY ORDER`),
ATTACHED RIDER (`== ATTACHED RIDER ==`), ใบเปิดตู้ (`ขออนุญาตเปิดตู้คอนเทนเนอร์`), คำร้อง (`อารักขาของศุลกากร`,
belongs to the ใบเปิดตู้ before it), otherwise ATTACHED sheet. A D/O page is matched to CHECK DEM.xlsx by
its B/L No. Columns are found by heading (`REC.`, `DEM.`, `B/L No.`), ATA from the cell after `ATA`.

1. Every DO: `เริ่มเก็บค่า DEM. วันที่.  <DEM.>`
2. DG seen (UN no. / CLASS / CL9 in the goods text): add above it
   `SPECIAL CONTAINER` / `.......DG..........OP..........FR`
3. Reefer seen (20RF / 40RH / TEMP): `เริ่มเก็บค่าไฟวันที่  <REC.>` then the DEM. line.
   REC. blank in the sheet → ATA + 3 days.
4. ISO TANK with DG: only the SPECIAL CONTAINER block, no DEM. line.
5. Status CFS/CFS or CY/CFS: **split** set (a house B/L ending in any letter: `...A`, `...B`, `...N` (confirmed 2026-11-11), or a master B/L whose house B/Ls
   are in the job) → no DEM. line. **Single CFS D/O (not split)** → DEM and everything else like CY.
6. `== ATTACHED RIDER ==` pages (page 2 of a B/L): left as they are (no notes, no stamp). A rider page is
   recognised by the `== ATTACHED RIDER ==` heading and no CARGO DELIVERY ORDER header; a D/O page whose
   description says "AS PER ATTACHED RIDER" is a normal page and gets its DEM line.
7. House B/L (`...038A`, `...038B`) not in CHECK DEM: dates come from its master B/L (letter dropped).
8. No rubber-stamp graphics are added anywhere (removed at the user's request, 2026-10-12). Old stamps
   in a file fed back in (pdf-lib XObjects named `EmbeddedPdfPage-<n>`, only ever drawn by the old
   stamp feature) are blanked out, so re-running an old output removes them.
9. PDF text may use control characters as spaces (`\x03`); the script treats them as spaces.
10. Every filled page gets invisible text `DO-DEM-FILLED`. A page that has it (or, in older outputs,
    the old CERTIFIED stamp text or a `เริ่มเก็บค่า` note) is skipped, so feeding an output back in
    never notes twice. A file that is already doubled must be redone from the original DO.
11. **Merge order** per D/O B/L: D/O (+ its rider pages) → ATTACHED sheet → ใบเปิดตู้ → คำร้อง. Pages of a
    B/L with no D/O go at the end. ATTACHED / ใบเปิดตู้ / คำร้อง pages are never filled.
12. **ใบเปิดตู้ / คำร้อง check** against the D/O, every mismatch flagged. Only B/Ls that need fixing are listed
    (web table and script output); B/Ls that match on every field are only counted.
    - ชื่อเรือ: D/O "DONGJIN CONFIDENT 0153S" = form "DONGJIN CONFIDENT V.0153S" ("V." ignored)
    - วันที่เรือเข้า: D/O `Vessel Arrival Date : 2026.11.04` = form `4-Nov-26` (both form pages). A wrong date is
      **corrected automatically** to the D/O date (web: written onto the form file, save buttons appear; script:
      replaced in DO-DEM.pdf with a real redaction) and reported as "แก้วันที่…ให้อัตโนมัติแล้ว N ช่อง".
    - CNTR (owner code + U/J/Z + 7 digits; the D/O side includes its ATTACHED RIDER pages), B/L NO.
    - CNEE: under the form's `CNEE:` label, **all its lines** (long names wrap: "THAI SAMSUNG ELECTRONICS" /
      "CO.,LTD."). Matches if equal, or if the D/O box only adds an address after a full company name.
      A corrected long value is wrapped onto the same number of lines and the old extra lines are covered.
    - STATUS: FCL = D/O CY/CY or CFS/CY; CFS = เปิดตู้ and LCL = ขนส่ง both match a CFS D/O (xx/CFS); D/O LCL(AGENT) = LCL.
      The form may add Thai, e.g. `LCL (ขนส่งแรงงาน-เรือ)`; the FCL/LCL/CFS keyword is what counts.
    - A form that has no such field (คำร้อง has no B/L / STATUS) shows "(ฟอร์มนี้ไม่มีช่องนี้)", not a mismatch.
13. **Correcting a form** is done on the web page only (table "ตรวจใบเปิดตู้"): the old value is covered
    white and the new one drawn by the browser (Thai works), shifted left / shrunk to stay on the paper.
    Each correction is recorded in the PDF Keywords `DOCOVERS:<json>` ({pi, x, y, w, h, base, v}, PDF
    units); both the web page and this script read it, so a corrected file re-checks as matching.
    Buttons: "บันทึกทับไฟล์เดิม" (Chrome/Edge, writes back to the chosen file) and "ดาวน์โหลดใบเปิดที่แก้แล้ว"
    (`<name>-แก้ไข.pdf`).

Format: Angsana New Bold 15.5pt (a little smaller than the "HEUNG A LINE (THAILAND) CO.,LTD."
line on the right), bottom-left of the page, dates as `09-OCT-2026`, **underline on the date
only** (the DG line is not underlined). Pages that already carry a typed annotation are skipped.

## Steps

1. Job folder = the working directory (needs the D/O PDF(s) in `input/`, optionally ATTACHED / ใบเปิด PDFs;
   `CHECK DEM*.xlsx` in `input/` or `output/`). Without CHECK DEM the script still runs: D/O pages without
   a date are flagged `** ไม่มีวันที่ DEM ใน CHECK DEM **`. To make one, run the check-dem skill first.
2. Run:
   ```bash
   python -X utf8 "<skill dir>/scripts/fill_do.py" "<job folder>"
   ```
   Requires `pymupdf`, `openpyxl`, and Windows' `angsana.ttc`.
   `python` may resolve to the Microsoft Store alias; if it says "Python was not found", use
   `%LOCALAPPDATA%\Python\bin\python.exe` (Git Bash: `$LOCALAPPDATA/Python/bin/python.exe`).
   Print x2 order (DO-DEM-PRINT x 2.pdf): a B/L = its page + its ATTACHED RIDER / ATTACHED / ใบเปิดตู้
   pages. CY: each B/L twice in a row (1,1,2,2). CFS: each master B/L's set of house B/Ls twice as separate
   sets (A,B,C,A,B,C).
3. Render two or three pages of `output/DO-DEM.pdf` (one normal, one DG, one reefer) and look at
   them before reporting.
4. Report in Thai: pages per type with their dates, the merge order, and the ใบเปิดตู้ check table; flag any
   page marked `** ไม่มีวันที่ DEM ใน CHECK DEM **` (DEM. is `CHECK` or the B/L is not in the sheet), any
   skipped page and every `** ไม่ตรง **` form field (fix on https://rattanao.github.io/DO/). Link
   `output/DO-DEM.pdf` and `output/DO-DEM-PRINT x 2.pdf`.

For layout changes (size, position, underline) edit `scripts/fill_do.py` and `index.html` together.

The web pages are in English (the guide is Thai / English with a switch); text printed onto documents stays Thai.
The web site has two steps (menu at the top): `checkdem.html` (① CHECK DEM, a copy of
https://github.com/Rattanao/Check-dem's page) and `index.html` (② DO). "ใช้กับ DO ต่อ →" passes the CHECK DEM
workbook to the DO page by itself as soon as it is calculated (localStorage `doCheckDem`). It stays on the DO page
(refresh, "Clear" on DO) until "Clear files" on ①; a CHECK DEM dropped on DO by hand wins. A DO page already open in
another tab takes it at once and re-processes its D/O files.
If the Check-dem rules change, copy its page again and keep the menu, buildXlsx() and the hand-off button
(synced with Check-dem 63453a0, 2026-11-05: Freedays before TOTAL, POL after B/L No., wider reefer TPSZ rule).
The CHECK DEM page keeps its file, ATA and result (localStorage `checkDemState`) when you go to ② DO and back,
until "Clear files" is pressed; a restored result is shown again but not re-sent to DO.
