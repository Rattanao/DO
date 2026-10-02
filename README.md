# DO — เติมวันที่ DEM / ค่าไฟ / SPECIAL CONTAINER ลงใน Cargo Delivery Order

โปรแกรมเติมข้อความท้ายใบ D/O (Heung-A Cargo Delivery Order, PDF หนึ่ง B/L ต่อหนึ่งหน้า)
โดยดึงวันที่จากไฟล์ `CHECK DEM.xlsx` (รายงานจาก [Check-dem](https://github.com/Rattanao/Check-dem))
แล้วบันทึกเป็น `output/DO.pdf`

## เงื่อนไขการเติม

| เห็นอะไรในใบ D/O | ข้อความที่เติม |
|---|---|
| ทุกใบ (ทั่วไป) | `เริ่มเก็บค่า DEM. วันที่.  18-OCT-2026` |
| DG (มี UN / CLASS / CL9) | `SPECIAL CONTAINER`<br>`.......DG..........OP..........FR`<br>และบรรทัด DEM |
| ตู้เย็น (20RF / 40RH / TEMP) | `เริ่มเก็บค่าไฟวันที่  07-OCT-2026`<br>`เริ่มเก็บค่า DEM. วันที่.  09-OCT-2026` |
| ISO TANK และมี DG | `SPECIAL CONTAINER`<br>`.......DG..........OP..........FR` เท่านั้น (ไม่มีบรรทัด DEM) |

- วันที่ DEM = ช่อง `DEM.` ใน CHECK DEM ของ B/L นั้น
- วันที่ค่าไฟ = ช่อง `REC.` ใน CHECK DEM ถ้าช่องว่างใช้ ATA + 3 วัน
- ตัวหนังสือ Angsana New ตัวหนา 15.5pt มุมล่างซ้ายของหน้า ขีดเส้นใต้เฉพาะวันที่
- หน้าที่มีข้อความพิมพ์เติมไว้แล้ว (annotation) จะถูกข้าม
- B/L ที่ไม่มีวันที่ DEM ใน CHECK DEM (เช่น ช่อง DEM. เป็น `CHECK`) จะถูกแจ้งในผลลัพธ์ว่า `** ไม่มีวันที่ DEM ใน CHECK DEM **`

## สิ่งที่ต้องมี

- Windows (ใช้ฟอนต์ `C:\Windows\Fonts\angsana.ttc`)
- Python 3.9 ขึ้นไป
- ติดตั้งไลบรารี:
  ```bash
  pip install -r requirements.txt
  ```

## วิธีใช้

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

4. เปิดไฟล์ `output/DO.pdf` ตรวจดูก่อนพิมพ์ (ไฟล์ใน `input/` ไม่ถูกแก้ไข)

## ใช้เป็น skill ของ Claude Code

คัดลอกทั้งโฟลเดอร์นี้ไปไว้ที่ `~/.claude/skills/do/`

```bash
git clone https://github.com/Rattanao/DO "%USERPROFILE%\.claude\skills\do"
```

จากนั้นเปิด Claude Code ในโฟลเดอร์งาน แล้วพิมพ์คำสั่ง `DO`

## ไฟล์ในโปรเจกต์

| ไฟล์ | หน้าที่ |
|---|---|
| `scripts/fill_do.py` | โค้ดโปรแกรม |
| `SKILL.md` | คำสั่งสำหรับ Claude Code (skill `do`) |
| `requirements.txt` | ไลบรารีที่ต้องติดตั้ง |

## ปรับรูปแบบ

แก้ใน `scripts/fill_do.py`
- ขนาดตัวหนังสือ: `font-size:15.5pt` ในตัวแปร `CSS`
- ตำแหน่ง: ตัวเลข `y` ในรายการ `parts` (หน่วย pt จากขอบบนของหน้า A4) และ `x = 45` ใน `pymupdf.Rect(45, ...)`
- เงื่อนไข DG / ตู้เย็น / ISO TANK: ตัวแปร `dg`, `reefer`, `tank`
