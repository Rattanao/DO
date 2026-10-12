---
name: do
description: >
  "DO": types the demurrage / reefer-power / SPECIAL CONTAINER notes onto every page of a
  Heung-A Cargo Delivery Order PDF (input/DO*.pdf), taking the dates from CHECK DEM.xlsx
  (the check-dem report). Writes output/DO-DEM.pdf and a print-x2 copy output/DO-DEM-PRINT.pdf. Use whenever the user says "DO", "ทำ DO",
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
5. Status CFS/CFS or CY/CFS (the `xx/CFS` near the SAY line): no DEM. line.
6. `== ATTACHED RIDER ==` pages (page 2 of a B/L): no notes; the blue stamp from `stamp.pdf`
   (CERTIFIED TRUE & CORRECT COPY at 12.5pt, a little smaller than "CARGO" (14.5pt) on the
   D/O header, plus the round seal with a 2-baht ring, 21.75 mm) is placed centred under the container list. To change the stamp,
   edit and run `scripts/make_stamp.py`.
7. House B/L (`...038A`, `...038B`) not in CHECK DEM: dates come from its master B/L (letter dropped).
8. D/O page whose marks say `AS PER ATTACHED` (container list is on the rider): the round seal
   alone (`seal.pdf`) at 2-baht-coin size (ring 21.75 mm = 61.7pt; seal.pdf box 64.9pt), centred 60pt right of the marks' left
   edge and 42pt below their last line, in the empty Container No. column.
9. PDF text may use control characters as spaces (`\x03`); the script treats them as spaces.
10. Every filled page gets invisible text `DO-DEM-FILLED`. A page that has it (or, in older outputs,
    our stamp text or a `เริ่มเก็บค่า` note) is skipped, so feeding an output back in never stamps
    or notes twice. A file that is already doubled must be redone from the original DO.

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
   `python` may resolve to the Microsoft Store alias; if it says "Python was not found", use
   `%LOCALAPPDATA%\Python\bin\python.exe` (Git Bash: `$LOCALAPPDATA/Python/bin/python.exe`).
   Print x2 order (DO-DEM-PRINT.pdf): a B/L = its page + its ATTACHED RIDER pages. CY: each B/L
   twice in a row (1,1,2,2). CFS: each master B/L's set of house B/Ls twice as separate sets
   (A,B,C,A,B,C).
3. Render two or three pages of `output/DO-DEM.pdf` (one normal, one DG, one reefer) and look at
   them before reporting.
4. Report in Thai: pages per type with their dates, and flag any page marked
   `** ไม่มีวันที่ DEM ใน CHECK DEM **` (DEM. is `CHECK` or the B/L is not in the sheet) and any
   skipped page. Link `output/DO-DEM.pdf` and `output/DO-DEM-PRINT.pdf`.

For layout changes (size, position, underline) edit `scripts/fill_do.py`.
