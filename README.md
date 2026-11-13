# DO — เติมวันที่ DEM / ค่าไฟ / SPECIAL CONTAINER ลงใน Cargo Delivery Order

**English** — Web: https://rattanao.github.io/DO/ (guide in Thai / English: https://rattanao.github.io/DO/guide.html)

1. **① CHECK DEM** (`index.html`, the first page): drop the Freedays file, enter the ATA, press **Calculate** — the result goes to step ② by itself.
2. **② DO** (`do.html`, can also be used on its own): drop the DO / ATTACHED / container-opening form PDFs (any order) and press **Process**.
   Each B/L gets its DEM / reefer-power / SPECIAL CONTAINER notes (written in Thai on the document) and is merged as
   DO → ATTACHED → opening form → removal request. The forms are checked against the D/O (vessel, arrival date — corrected
   automatically, CNTR, CNEE, B/L NO., STATUS); wrong fields can be corrected on the page.
3. **Download DO-DEM.pdf (x1 + x2)** or **Print x2**.

Desktop: put the files in `input/`, double-click `run-do.bat`, results in `output/`. Claude Code: type `DO`.

---


โปรแกรมเติมข้อความท้ายใบ D/O (Heung-A Cargo Delivery Order, PDF หนึ่ง B/L ต่อหนึ่งหน้า)
โดยดึงวันที่จากไฟล์ `CHECK DEM.xlsx` (รายงานจาก [Check-dem](https://github.com/Rattanao/Check-dem))
แล้วบันทึกเป็น `output/DO-DEM.pdf` และไฟล์สำหรับปริ้น x2 `output/DO-DEM-PRINT x 2.pdf`

## เงื่อนไขการเติม

| เห็นอะไรในใบ D/O | ข้อความที่เติม |
|---|---|
| ทุกใบ (ทั่วไป) | `เริ่มเก็บค่า DEM. วันที่.  18-OCT-2026` |
| DG (มี UN / CLASS / CL9) | `SPECIAL CONTAINER`<br>`.......DG..........OP..........FR`<br>และบรรทัด DEM |
| ตู้เย็น (20RF / 40RH / TEMP) | `เริ่มเก็บค่าไฟวันที่  07-OCT-2026`<br>`เริ่มเก็บค่า DEM. วันที่.  09-OCT-2026` |
| ISO TANK และมี DG | `SPECIAL CONTAINER`<br>`.......DG..........OP..........FR` เท่านั้น (ไม่มีบรรทัด DEM) |
| STATUS `CFS/CFS` หรือ `CY/CFS` แบบ SPLIT (B/L หลัก + A, B, C…) | ไม่เติมบรรทัด DEM |
| STATUS `CFS/CFS` เดี่ยว (ไม่ SPLIT) | เติม DEM และอย่างอื่นเหมือน CY |
| หน้า ATTACHED (attached sheet) / ใบเปิดตู้ / คำร้อง | ไม่เติม — รวมไฟล์ต่อท้าย DO ของ B/L นั้น และตรวจใบเปิดตู้ |
| หน้า `== ATTACHED RIDER ==` (หน้า 2 ของ B/L) | ไม่เติมอะไร |

- วันที่ DEM = ช่อง `DEM.` ใน CHECK DEM ของ B/L นั้น (House B/L เช่น `...038A` ที่ไม่มีใน CHECK DEM ใช้วันที่ของ B/L หลัก `...038`)
- วันที่ค่าไฟ = ช่อง `REC.` ใน CHECK DEM ถ้าช่องว่างใช้ ATA + 3 วัน
- ตัวหนังสือ Angsana New ตัวหนา 15.5pt มุมล่างซ้ายของหน้า ขีดเส้นใต้เฉพาะวันที่
- หน้าที่มีข้อความพิมพ์เติมไว้แล้ว (annotation) จะถูกข้าม
- ใส่ไฟล์ที่เติมไปแล้ว (DO-DEM.pdf) ซ้ำ หน้าที่เติมแล้วจะถูกข้าม ไม่เติมวันที่ซ้อน และตรายางเก่า (CERTIFIED TRUE & CORRECT COPY / ตรากลม) จะถูกลบออก
- **ปริ้น x2** (หนึ่ง B/L = หน้า D/O + หน้า ATTACHED RIDER ของมัน)
  - CY: ซ้อนกันทีละ B/L เช่น 1,1,2,2
  - CFS/CFS: แยกเป็น 2 ชุดต่อ B/L หลัก เช่น 038,038A,038B, 038,038A,038B
- B/L ที่ไม่มีวันที่ DEM ใน CHECK DEM (เช่น ช่อง DEM. เป็น `CHECK`) จะถูกแจ้งในผลลัพธ์ว่า `** ไม่มีวันที่ DEM ใน CHECK DEM **`

## รวมไฟล์และตรวจใบเปิดตู้

ใส่ DO, ATTACHED และใบเปิดตู้ (ใบขออนุญาตเปิดตู้ + คำร้องขอนำตู้ออก) มาพร้อมกันได้ ลำดับไหนก็ได้

- รวมเป็นไฟล์เดียวทีละ B/L เรียง **DO → ATTACHED → ใบเปิดตู้ → คำร้อง**
- ตรวจใบเปิดตู้ / คำร้อง เทียบกับ DO: **ชื่อเรือ, วันที่เรือเข้า, CNTR, CNEE, B/L NO., STATUS**
  - **วันที่เรือเข้าที่ไม่ตรง แก้ตาม DO ให้อัตโนมัติ** ไม่ต้องแก้เอง
  - STATUS: FCL = CY/CY หรือ CFS/CY · CFS = เปิดตู้ · LCL = ขนส่ง (DO xx/CFS ใช้ CFS หรือ LCL ได้, DO LCL(AGENT) = LCL)
  - ตารางแสดงเฉพาะ B/L ที่ต้องแก้ B/L ที่ตรงทุกหัวข้อแค่นับจำนวนไว้
  - ช่องที่ไม่ตรงขึ้นสีแดง พร้อมคำเตือนด้านบนของเว็บ
- **แก้บนเว็บได้**: แก้ค่าในช่องสีแดง (มีค่าที่ถูกจาก DO ใส่ไว้ให้) แล้วกด **แก้ไขใบเปิดตู้ตามช่องที่แก้** → เว็บปิดค่าเดิมด้วยพื้นขาว พิมพ์ค่าใหม่ทับ แล้วตรวจซ้ำเป็นสีเขียว
  - **บันทึกทับไฟล์เดิม** (Chrome / Edge ครั้งแรกเบราว์เซอร์จะขออนุญาต) หรือ **ดาวน์โหลดใบเปิดที่แก้แล้ว** (`…-แก้ไข.pdf`)
  - ค่าเดิมยังอยู่ใต้พื้นขาวในไฟล์ (มองไม่เห็นและไม่ออกตอนปริ้น) ไฟล์ที่แก้แล้วเว็บและโปรแกรมอ่านเป็นค่าใหม่

## ใช้งานผ่านเว็บ (ไม่ต้องติดตั้งอะไร)

เว็บมี 2 ขั้นต่อกัน เลือกจากเมนูด้านบน: **① CHECK DEM → ② DO**

- **① CHECK DEM** (https://rattanao.github.io/DO/ หน้าแรก): ลากไฟล์ Freedays ใส่ ATA กด **คำนวณ** แล้วกด **ใช้กับ DO ต่อ →**
  **กดคำนวณเสร็จ CHECK DEM ถูกส่งไปหน้า ② DO ให้เองทันที** (หน้า DO ที่เปิดอยู่อีกแท็บจะรับและประมวลผลใหม่ให้เอง) หรือกดดาวน์โหลด CHECK DEM.xlsx ก็ได้
  — หน้านี้มาจาก [Check-dem](https://github.com/Rattanao/Check-dem) กฎคำนวณเหมือนกัน
- **② DO** (https://rattanao.github.io/DO/do.html ใช้เดี่ยว ๆ ได้ ไม่ต้องทำ ① ก่อน): ทำตามขั้นตอนด้านล่าง

เปิดที่ **https://rattanao.github.io/DO/do.html**

1. ลากไฟล์ DO / ATTACHED / ใบเปิดตู้ (.pdf) มาวาง ใส่ได้หลายไฟล์ เว็บแยกชนิดและเรียงให้เอง ไฟล์ `CHECK DEM.xlsx` จะใส่หรือไม่ใส่ก็ได้
2. ใส่ไฟล์ DO แล้วเว็บจะประมวลผลให้ทันที วันที่มาจาก
   - ไฟล์ CHECK DEM (ถ้าใส่)
   - ช่อง **DEM. วันที่** และ **ค่าไฟ วันที่** ด้านบน ใช้กับทุก B/L ที่ CHECK DEM ไม่มีวันที่ (ถ้าไม่ใส่ CHECK DEM ก็คือทุก B/L)
   - ช่องวันที่ในตาราง แก้เฉพาะ B/L นั้น (มีผลเหนือกว่าสองแบบแรก) ช่องที่ยังไม่มีวันที่จะเป็นสีแดง

   เติมวันที่อย่างใดอย่างหนึ่งหรือทั้งสองอย่าง แล้วกด **ประมวลผล** (การแก้วันที่จะมีผลเมื่อกดปุ่มนี้) และกด **ลบไฟล์** เพื่อล้างไฟล์ วันที่ และผลลัพธ์ เริ่มงานใหม่
3. ตารางจะแสดงทีละหน้าว่าเป็นแบบใด (ทั่วไป / DG / REEFER / ISO TANK+DG) และเติมข้อความอะไร คลิกป้ายแบบเพื่อซ่อนหรือแสดง คลิกแถวเพื่อดูตัวอย่างหน้านั้น
4. กด **ดาวน์โหลด DO-DEM.pdf (x1 + x2)** จะได้ 2 ไฟล์: `DO-DEM.pdf` (ชุดเดียว) และ `DO-DEM-PRINT x 2.pdf` (x2 เรียงตามลำดับปริ้น) หรือกด **ปริ้น x2** เพื่อสั่งพิมพ์ทันที

- ปรับขนาดตัวหนังสือได้ที่ช่อง "ขนาดตัวหนังสือ" (ค่าเริ่มต้น 15.5)
- ใช้ฟอนต์ Angsana New ของเครื่อง (Windows) ถ้าเครื่องไม่มีจะใช้ Sarabun แทน
- ข้อความที่เว็บเติมเป็นรูปภาพความละเอียดสูงฝังลงในหน้า PDF
- ไฟล์ถูกประมวลผลในเบราว์เซอร์ของเครื่องที่ใช้อยู่เท่านั้น ไม่มีการอัปโหลดข้อมูลไปที่ใด ตัวเว็บคือไฟล์ [`do.html`](do.html)

## สิ่งที่ต้องมี (สำหรับโปรแกรม Python)

- Windows (ใช้ฟอนต์ `C:\Windows\Fonts\angsana.ttc`)
- Python 3.9 ขึ้นไป
- ติดตั้งไลบรารี:
  ```bash
  pip install -r requirements.txt
  ```

## วิธีใช้ (โปรแกรม Python)

1. สร้างโฟลเดอร์งาน แล้ววางไฟล์ตามนี้

   ```
   โฟลเดอร์งาน/
   └── input/
       ├── DO.pdf            ← ใบ D/O ที่พิมพ์จากระบบ (ชื่อขึ้นต้นด้วย DO)
       └── CHECK DEM.xlsx    ← รายงาน Check DEM (วางใน input/ หรือ output/ ก็ได้)
   ```

2. รันโปรแกรม โดยระบุโฟลเดอร์งาน (ไม่ระบุ = โฟลเดอร์ปัจจุบัน)

   ```bash
   python -X utf8 scripts/fill_do.py "C:\path\to\โฟลเดอร์งาน"
   ```

3. โปรแกรมจะแสดงรายการทีละหน้า เช่น

   ```
   4 | HASLC03260900122 | DG | SPECIAL CONTAINER  .......DG..........OP..........FR / เริ่มเก็บค่า DEM. วันที่.   09-OCT-2026
   12 | HASLC03260900964 | REEFER | เริ่มเก็บค่าไฟวันที่    07-OCT-2026 / เริ่มเก็บค่า DEM. วันที่.   09-OCT-2026
   ```

4. เปิดไฟล์ `output/DO-DEM.pdf` ตรวจดู แล้วพิมพ์จาก `output/DO-DEM-PRINT x 2.pdf` (x2) (ไฟล์ใน `input/` ไม่ถูกแก้ไข)

## ใช้เป็น skill ของ Claude Code

คัดลอกทั้งโฟลเดอร์นี้ไปไว้ที่ `~/.claude/skills/do/`

```bash
git clone https://github.com/Rattanao/DO "%USERPROFILE%\.claude\skills\do"
```

จากนั้นเปิด Claude Code ในโฟลเดอร์งาน แล้วพิมพ์คำสั่ง `DO`

## ไฟล์ในโปรเจกต์

| ไฟล์ | หน้าที่ |
|---|---|
| `do.html` | หน้าเว็บ ② DO |
| `index.html` | หน้าเว็บ ① CHECK DEM หน้าแรก (มาจาก Check-dem) ส่งผลต่อให้หน้า DO |
| `checkdem.html` | ลิงก์เดิม ส่งต่อไปหน้าแรก |
| `guide.html` | หน้าคู่มือ + ปุ่มดาวน์โหลดโปรแกรม (https://rattanao.github.io/DO/guide.html) |
| `run-do.bat` | ดับเบิลคลิกเพื่อรันโปรแกรมกับไฟล์ในโฟลเดอร์ `input` |
| `scripts/fill_do.py` | โค้ดโปรแกรม Python |
| `SKILL.md` | คำสั่งสำหรับ Claude Code (skill `do`) |
| `requirements.txt` | ไลบรารีที่ต้องติดตั้ง |

## ปรับรูปแบบ

แก้ใน `scripts/fill_do.py`
- ขนาดตัวหนังสือ: `font-size:15.5pt` ในตัวแปร `CSS`
- ตำแหน่ง: ตัวเลข `y` ในรายการ `parts` (หน่วย pt จากขอบบนของหน้า A4) และ `x = 45` ใน `pymupdf.Rect(45, ...)`
- เงื่อนไข DG / ตู้เย็น / ISO TANK: ตัวแปร `dg`, `reefer`, `tank`
