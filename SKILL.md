---
name: do
description: >
  "DO": types the demurrage / reefer-power / SPECIAL CONTAINER notes onto every page of a
  Heung-A Cargo Delivery Order PDF (input/DO*.pdf), taking the dates from CHECK DEM.xlsx
  (the check-dem report). Writes output/DO.pdf. Use whenever the user says "DO", "ทำ DO",
  "เติม DO", "เติมวันที่ DEM ใน DO", or points to a folder with input/ holding a DO PDF plus
  a CHECK DEM.xlsx.
---

# DO

Rattana's confirmed layout. Run the bundled script; do not place the text by hand.

## Rules (already implemented in the script)

One B/L per page; the page is matched to CHECK DEM.xlsx by its B/L No. Columns are found by
heading (`REC.`, `DEM.`, `B/L No.`), ATA from the cell after `ATA`.

1. Every DO: `เริ่มเก็บค่า DEM. วันที่.  <DEM.>`
2. DG seen (UN no. / CLASS / CL9 in the goods text): add above it
   `SPECIAL CONTAINER` / `.......DG..........OP..........FR`
3. Reefer seen (20RF / 40RH / TEMP): `เริ่มเก็บค่าไฟวันที่  <REC.>` then the DEM. line.
   REC. blank in the sheet → ATA + 3 days.
4. ISO TANK with DG: only the SPECIAL CONTAINER block, no DEM. line.

Format: Angsana New Bold 15.5pt (a little smaller than the "HEUNG A LINE (THAILAND) CO.,LTD."
line on the right), bottom-left of the page, dates as `09-OCT-2026`, **underline on the date
only** (the DG line is not underlined). Pages that already carry a typed annotation are skipped.

## Steps

1. Job folder = the working directory (needs `input/DO*.pdf`; `CHECK DEM*.xlsx` in `input/` or
   `output/`). If CHECK DEM.xlsx is missing, run the check-dem skill first.
2. Run:
   ```bash
   python -X utf8 "<skill dir>/scripts/fill_do.py" "<job folder>"
   ```
   Requires `pymupdf`, `openpyxl`, and Windows' `angsana.ttc`.
3. Render two or three pages of `output/DO.pdf` (one normal, one DG, one reefer) and look at
   them before reporting.
4. Report in Thai: pages per type with their dates, and flag any page marked
   `** ไม่มีวันที่ DEM ใน CHECK DEM **` (DEM. is `CHECK` or the B/L is not in the sheet) and any
   skipped page. Link `output/DO.pdf`.

For layout changes (size, position, underline) edit `scripts/fill_do.py`.
