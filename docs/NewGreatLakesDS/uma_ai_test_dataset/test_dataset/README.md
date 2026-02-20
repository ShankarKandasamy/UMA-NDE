# UMA AI MVP Test Dataset
## Amine Unit UT Survey - Great Lakes Chemical Processing

This synthetic test dataset simulates a complete pipe thickness survey project for testing UMA AI's document processing, data validation, and report generation capabilities.

---

## Quick Start

```
test_dataset/
├── README.md                    # This file
├── documents/                   # PDF documents (RFQ, certs, JSA)
├── data/                        # CSV data files (CML readings)
├── isometrics/                  # SVG piping drawings
├── photos/                      # Photo manifest (JSON/CSV)
└── reference/                   # Error key, field notes, format docs
```

---

## Scenario Overview

| Item | Value |
|------|-------|
| **Client** | Great Lakes Chemical Processing (GLCP) |
| **Location** | Hamilton Plant, Ontario |
| **Unit** | Amine Treating Unit (ATU-100) |
| **Contractor** | Precision NDE Services Inc. (PNDE) |
| **Scope** | 150 CMLs across 18 piping lines |
| **Survey Dates** | November 4-7, 2024 |
| **Historical Data** | October 2019 survey |

---

## File Inventory

### `/documents/` - PDF Documents (7 files)

| File | Description | Test Purpose |
|------|-------------|--------------|
| `GLCP-RFQ-2024-089.pdf` | Client RFQ with scope details | Extract CML counts, line list, requirements |
| `CalCert_38DL-2847193.pdf` | UT gauge calibration cert (Marcus) | Validate cert dates, equipment tracking |
| `CalCert_38DL-2901456.pdf` | UT gauge calibration cert (Sarah) | Validate cert dates, equipment tracking |
| `CalCert_PNDE-CS-001.pdf` | Calibration block cert | Reference standard traceability |
| `PersonnelCert_Marcus_Chen.pdf` | Lead inspector certification | Personnel qualification check |
| `PersonnelCert_Sarah_Thompson.pdf` | Inspector certification | Personnel qualification check |
| `PNDE-JSA-20241025-031.pdf` | Job Safety Analysis | Safety documentation extraction |

### `/data/` - CSV Data Files (7 files)

| File | Records | Description | Test Purpose |
|------|---------|-------------|--------------|
| `master_cml_list.csv` | 150 | Ground truth CML database | Reference for validation |
| `field_data_20241104.csv` | 40 | Day 1 gauge export | Parse with errors, date formats |
| `field_data_20241105.csv` | 40 | Day 2 gauge export | Parse with errors |
| `field_data_20241106.csv` | 41 | Day 3 gauge export | Includes spurious entry |
| `field_data_20241107.csv` | 29 | Day 4 gauge export | Parse with errors |
| `field_data_combined.csv` | 150 | Merged field data | CML matching, status |
| `historical_survey_2019.csv` | 150 | Previous survey data | Different format, corrosion rate calc |

### `/isometrics/` - Piping Drawings (2 files)

| File | Description | Test Purpose |
|------|-------------|--------------|
| `ISO_4-RA-101.svg` | 4" Rich Amine line isometric | Visual with CML markers, critical finding |
| `ISO_6-RA-103.svg` | 6" Rich Amine header isometric | Complex header with branches |

### `/photos/` - Photo Documentation (2 files)

| File | Records | Description | Test Purpose |
|------|---------|-------------|--------------|
| `photo_manifest.json` | 226 | Full manifest with image prompts | Photo-to-CML matching, AI image gen |
| `photo_manifest.csv` | 226 | Summary without prompts | Quick reference |

### `/reference/` - Reference Materials (3 files)

| File | Description | Test Purpose |
|------|-------------|--------------|
| `embedded_errors_key.csv` | List of all intentional errors | Validation benchmark |
| `format_comparison.md` | 2019 vs 2024 format differences | Schema mapping logic |
| `field_notes.txt` | Daily inspector notes | Context extraction, NLP |

---

## Embedded Data Quality Issues

The dataset intentionally includes these errors to test UMA AI's validation and error handling:

### CML ID Errors
| CML ID | Error Type | Bad Value | Expected Behavior |
|--------|------------|-----------|-------------------|
| 4-RA-101-06 | Typo | `4-RA-101-O6` | Fuzzy match, flag for confirmation |
| 4-LA-102-03 | Format | `4LA10203` | Normalize, match to correct CML |
| 3-RV-101-02 | Format | `3-RV-101-2` | Normalize single digit |
| 6-RA-103-07 | Format | `6-RA103-07` | Fix missing dash |
| 4-RA-101-15 | Spurious | N/A | Flag as unknown CML |

### Reading Errors
| CML ID | Error Type | Bad Value | Expected Behavior |
|--------|------------|-----------|-------------------|
| 8-TG-101-05 | Missing | blank | Flag incomplete, manual entry |
| 6-LA-103-05 | Transposed | digits swapped | Range validation warning |
| 3-RF-101-04 | Decimal | `1.87` (should be 0.187) | Out of range alert |
| 4-RA-102-05 | Duplicate | two different values | User selection prompt |

### Other Issues
- **Date formats:** Mix of `YYYY-MM-DD`, `MM/DD/YYYY`, `DD-Mon-YYYY`, `Month DD, YYYY`
- **Missing photo:** 6-SG-102-04 has no associated photo
- **Format mismatch:** 2019 data uses different column names

---

## Critical Findings

CMLs that should trigger alerts or notifications:

| CML ID | Reading | t-min | Status | Required Action |
|--------|---------|-------|--------|-----------------|
| 4-RA-101-06 | 0.142" | 0.150" | **CRITICAL** | Immediate engineering review |
| 4-RA-102-09 | 0.161" | 0.150" | Alert | 1-year re-inspection |
| 6-RA-103-11 | 0.168" | 0.180" | **CRITICAL** | Engineering review (localized) |
| 3-RV-101-04 | 0.195" | 0.140" | Monitor | Process review (12 mpy rate) |
| Multiple 2-RF-102 | Various | 0.085" | **CRITICAL** | Stainless steel line issues |

### Inaccessible CMLs
| CML ID | Reason | Documentation |
|--------|--------|---------------|
| 6-LA-103-08 | Scaffold couldn't reach | Photo + note in manifest |
| 2-ST-101-03 | Insulated, client declined | CUI inspection recommended |

### Anomaly
| Line | CMLs | Issue |
|------|------|-------|
| 3-CW-101 | 01, 02, 04 | Readings > nominal (scale deposit) |

---

## Column Mappings

### Master CML List (`master_cml_list.csv`)
```
cml_index          - Sequential number (1-150)
cml_id             - Unique identifier (e.g., 4-RA-101-06)
line_number        - Piping line (e.g., 4-RA-101)
service            - Process service description
pipe_size_in       - Pipe diameter in inches
material           - Material specification
design_pressure_psig - Design pressure
design_temp_f      - Design temperature
schedule           - Pipe schedule (40, 80, 40S)
nominal_wall_in    - Nominal wall thickness
tmin_in            - Minimum required thickness
component          - Component type (Elbow, Tee, etc.)
location           - Physical location description
reading_2019_in    - Historical thickness reading
reading_2024_in    - Current thickness reading (or blank)
corrosion_rate_mpy - Calculated rate in mils per year
risk_level         - High/Medium/Low
status             - CRITICAL/Alert/Monitor/Acceptable/Inaccessible
note               - Comments and findings
```

### Field Data (2024 Format)
```
ID, Reading, Units, Date, Time, Operator, Gauge, Probe, Material, Velocity, Gain, Notes
```

### Historical Data (2019 Format)
```
Location ID, Piping Line, Fitting Type, Measured Thickness (in), Nominal (in), 
Min Required (in), Survey Date, Technician, Equipment, Comments
```

---

## Photo Manifest Structure

Each photo record in `photo_manifest.json` contains:

```json
{
  "photo_id": "IMG_0001",
  "filename": "IMG_0001.jpg",
  "cml_id": "6-SG-101-01",
  "photo_type": "cml_location",
  "description": "CML location photo for 6-SG-101-01...",
  "inspector": "Marcus Chen",
  "date": "2024-11-04",
  "timestamp": "2024-11-04T08:15:32",
  "image_generation_prompt": "Industrial petrochemical plant..."
}
```

### Photo Types
- `cml_location` - CML tag and surrounding area (148 photos)
- `gauge_display` - UT gauge showing reading (53 photos)
- `surface_condition` - Pipe surface at measurement (7 photos)
- `calibration_check` - Daily cal verification (8 photos)
- `inaccessible_documentation` - Access issues (2 photos)
- `anomaly` - Unusual findings (3 photos)
- `general_site` - Unit overview (5 photos)

---

## Test Scenarios

### 1. Data Ingestion
- [ ] Parse all date formats correctly
- [ ] Handle UTF-8 encoding in CSV files
- [ ] Match 2024 field data to master CML list
- [ ] Map 2019 historical data despite different schema

### 2. Error Detection
- [ ] Flag CML ID typos and format issues
- [ ] Detect missing readings
- [ ] Identify duplicate entries
- [ ] Catch out-of-range values (decimal errors)
- [ ] Alert on spurious CMLs not in master list

### 3. Critical Threshold Detection
- [ ] Flag readings below t-min as CRITICAL
- [ ] Flag readings within 10% of t-min as Alert
- [ ] Calculate corrosion rates from historical data
- [ ] Flag accelerated corrosion (>10 mpy)

### 4. Document Processing
- [ ] Extract scope from RFQ PDF
- [ ] Validate certification expiry dates
- [ ] Parse personnel qualifications
- [ ] Extract CML locations from isometrics

### 5. Photo Association
- [ ] Match photos to CMLs by ID
- [ ] Identify CMLs missing photos
- [ ] Associate gauge display photos with readings

### 6. Report Generation
- [ ] Generate summary statistics
- [ ] List critical findings with context
- [ ] Calculate overall corrosion trends
- [ ] Produce client-ready inspection report

---

## Personnel Reference

### PNDE (Contractor)
| Name | Role | Cert# | Contact |
|------|------|-------|---------|
| Marcus Chen | Lead Inspector, UT Level II | PNDE-UT2-0847 | Gauge: 38DL-2847193 |
| Sarah Thompson | Inspector, UT Level II | PNDE-UT2-1203 | Gauge: 38DL-2901456 |
| David Park | PM, UT Level III | PNDE-UT3-0215 | Approving authority |

### GLCP (Client)
| Name | Role |
|------|------|
| Jennifer Walsh | Inspection Coordinator |
| Robert Hendricks | Unit Engineer |
| Tom Bradley | Area Operator |
| Mike Sullivan | Safety Coordinator |

---

## Document Numbers

| Document | Number |
|----------|--------|
| RFQ | GLCP-RFQ-2024-089 |
| Work Order | WO-20241025-031 |
| JSA | PNDE-JSA-20241025-031 |
| Final Report | PNDE-RPT-20241025-031-R0 |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-11-14 | Initial test dataset |

---

## Notes for Developers

1. **All data is synthetic** - no real company information
2. **Errors are intentional** - see `embedded_errors_key.csv`
3. **Photo prompts** can be used with image generation APIs
4. **Ground truth** is in `master_cml_list.csv`
5. **2019 format differs** - tests schema mapping capabilities
