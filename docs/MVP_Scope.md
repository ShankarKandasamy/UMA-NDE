### Summary: What UMA Capture Needs to Handle

| Inspection Type   | Primary Photos                        | Primary Data                  |
| ----------------- | ------------------------------------- | ----------------------------- |
| UT Piping         | CML markers, instrument, anomalies    | CML × readings table          |
| UT Vessels        | Nameplate, CML markers, nozzles       | Zone × CML × readings         |
| UT Tanks          | Nameplate, courses, floor grid        | Course × compass + floor grid |
| PAUT Pipe Welds   | Weld tag, scanner setup, sector scans | Weld info + indication table  |
| PAUT Vessel Welds | Weld ID, setup, sector scans          | Weld info + indication table  |

## INSPECTION REPORT SECTION — PHOTOS THAT FEED IT

---

### 1. HEADER / IDENTIFICATION

- **Equipment ID** ← Pipe tag photo
- **Service** ← Pipe tag photo
- **Material** ← Pipe tag / line spec photo
- **P&ID reference** ← P&ID photo

---

### 2. INSPECTION DETAILS

- **Inspector** ← (from login / manual entry)
- **Date** ← (photo EXIF / manual entry)
- **Instrument** ← Instrument photo (serial visible)
- **Calibration status** ← Calibration sticker photo

---

### 3. CML DATA TABLE

- **CML locations** ← CML marker photos (verify)
- **Component types** ← Component overview photos
- **Readings** ← Instrument display photos (optional)
- **Grid reference** ← Paint pen marking photos

---

### 4. CALCULATIONS (auto-generated)

- **Corrosion rate** ← (from current vs. previous readings)
- **Remaining life** ← (from rate + t-min)
- **t-min per code** ← (from design data)

---

### 5. CONDITION ASSESSMENT

- **External condition** ← Coating / corrosion photos
- **Insulation condition** ← Insulation photos
- **Support condition** ← Support contact photos

---

### 6. FINDINGS

- **Below-min locations** ← Anomaly photos + instrument readings
- **Active corrosion** ← Corrosion photos
- **CUI indicators** ← Coating / insulation damage photos

---

### 7. RECOMMENDATIONS

- **Repair locations** ← Marked rejection area photos
- **Re-inspection interval** ← (calculated from rate)
- **Further evaluation needed** ← Anomaly photos as reference

---

### 8. ATTACHMENTS

- **CML location sketch** ← Isometric / P&ID photos (OCR or trace)
- **Photo log** ← All photos with captions
- **Data sheets** ← (auto-generated from readings)

## Minimum Photo Set for a Complete Report

---

### Routine Circuit (No Issues, 5–10 CMLs)

| Photo                            | Qty        | Purpose               |
| -------------------------------- | ---------- | --------------------- |
| Pipe tag                         | 1          | Equipment ID          |
| Instrument + calibration sticker | 1          | QA                    |
| Each CML marker                  | 5–10       | Location verification |
| Component overview (if needed)   | 2–3        | Context               |
| **Total**                        | **~10–15** |                       |

---

### Circuit With Findings

| Photo                                | Qty             | Purpose      |
| ------------------------------------ | --------------- | ------------ |
| All of the above                     | ~10–15          | Baseline     |
| Each anomaly (instrument + location) | 2–3 per anomaly | Evidence     |
| Corrosion / damage close-ups         | 2–5             | Findings     |
| Extent markings                      | 1–2             | Repair scope |
| **Total**                            | **~20–30**      |              |

## INSPECTION SUBMITTAL PACKAGE

- **1. INSPECTION REPORT**  
  _(The CML data we just created)_

- **2. SUPPORTING DOCUMENTS**  
  _(Pre-inspection)_

- **3. PHOTOGRAPHIC EVIDENCE**  
  _(Field captured)_

- **4. CALIBRATION RECORDS**

- **5. SKETCHES & DRAWINGS**

- **6. PREVIOUS INSPECTION DATA**

- **7. CERTIFICATIONS**
