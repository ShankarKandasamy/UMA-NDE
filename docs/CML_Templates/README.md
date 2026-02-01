# UMA AI - CML Templates & Sample Data

Realistic Condition Monitoring Location (CML) templates and sample data for testing UT thickness survey report generation.

## Overview

This package contains templates and sample data representing typical field inspection forms used across North American oil & gas, petrochemical, and industrial facilities for:

1. **Piping** (API 570 / ASME B31.3)
2. **Pressure Vessels** (API 510 / ASME Section VIII)
3. **Storage Tanks** (API 653)

## Folder Structure

```
CML_Templates/
├── README.md
├── templates/              # Excel template files
├── csv_samples/            # Sample CSV data files
└── generators/             # Python scripts to regenerate data
```

## Files Included

### Excel Templates (`templates/`)

| File                                 | Contents                                                            |
| ------------------------------------ | ------------------------------------------------------------------- |
| `Piping_CML_Templates.xlsx`          | 5 sheets: 2 blank templates, 2 filled samples, 1 compact format     |
| `Vessel_CML_Templates.xlsx`          | 3 sheets: 1 blank template, 1 filled sample, 1 detailed zone format |
| `Tank_CML_Templates.xlsx`            | 2 sheets: 1 blank template, 1 filled sample                         |
| `UT_CML_Templates_Professional.xlsx` | Professional formatted template                                     |

### CSV Sample Data (`csv_samples/`)

| File                         | Description                 | Records       |
| ---------------------------- | --------------------------- | ------------- |
| `piping_FW_101.csv`          | Boiler Feedwater circuit    | 15 CMLs       |
| `piping_FW_102.csv`          | Boiler Feedwater circuit    | 12 CMLs       |
| `piping_CW_201.csv`          | Cooling Water circuit       | 20 CMLs       |
| `piping_CW_202.csv`          | Cooling Water Return        | 18 CMLs       |
| `piping_HC_301.csv`          | Hydrocarbon Process         | 25 CMLs       |
| `piping_HC_302.csv`          | Hydrocarbon Process         | 22 CMLs       |
| `piping_ST_401.csv`          | Steam Supply                | 10 CMLs       |
| `piping_ST_402.csv`          | Steam Condensate            | 14 CMLs       |
| `piping_AC_501.csv`          | Acid Service (SS)           | 8 CMLs        |
| `piping_CA_601.csv`          | Caustic Service             | 12 CMLs       |
| `piping_all_circuits.csv`    | Combined all piping         | ~156 CMLs     |
| `vessel_V_101.csv`           | Amine Contactor             | ~45 readings  |
| `vessel_V_102.csv`           | Amine Regenerator           | ~55 readings  |
| `vessel_V_201.csv`           | Flash Drum                  | ~35 readings  |
| `vessel_V_202.csv`           | Surge Drum                  | ~35 readings  |
| `vessel_V_301.csv`           | Separator                   | ~45 readings  |
| `vessel_V_302.csv`           | KO Drum                     | ~35 readings  |
| `vessel_all.csv`             | Combined all vessels        | ~250 readings |
| `tank_T_501.csv`             | Crude Oil Tank              | ~150 readings |
| `tank_T_502.csv`             | Crude Oil Tank              | ~150 readings |
| `tank_T_601.csv`             | Diesel Tank                 | ~100 readings |
| `tank_T_602.csv`             | Diesel Tank                 | ~100 readings |
| `tank_T_701.csv`             | Water Tank                  | ~80 readings  |
| `tank_T_801.csv`             | Slop Oil Tank               | ~50 readings  |
| `tank_all.csv`               | Combined all tanks          | ~630 readings |
| `instrument_export_38DL.csv` | Mimics Olympus 38DL+ export | ~100 readings |

## Data Schema

### Piping CML Data

```
Circuit_ID      - Piping circuit identifier (e.g., "FW-101")
CML             - Condition Monitoring Location number (e.g., "001")
Component       - Component type (Elbow, Straight, Tee, Reducer, etc.)
NPS             - Nominal Pipe Size in inches
Schedule        - Pipe schedule (40, 80, etc.)
Nominal_mm      - Original/nominal wall thickness
t_min_mm        - Minimum required thickness per code
Reading_1-4     - Individual thickness readings
Min_mm          - Minimum of all readings
Prev_mm         - Previous inspection reading
Prev_Date       - Date of previous inspection
Corr_Rate_mm_yr - Calculated corrosion rate
Remaining_Life_yr - Calculated remaining life
Condition       - Assessment (Good, Fair, ALERT)
Service         - Process service description
Material        - Pipe material specification
```

### Vessel CML Data

```
Vessel_ID       - Vessel tag number (e.g., "V-101")
Zone            - Inspection zone (TOP_HEAD, SHELL_1, BTM_HEAD, NOZZLE)
CML             - CML identifier (e.g., "SC1-N" = Shell Course 1, North)
Orientation     - Compass orientation or position
Elevation       - Vertical position on zone
Nominal_mm      - Original wall thickness
t_min_mm        - Minimum required thickness
Reading_mm      - Current thickness reading
Prev_mm         - Previous reading
Prev_Date       - Previous inspection date
Corr_Rate_mm_yr - Corrosion rate
Remaining_Life_yr - Remaining life calculation
Condition       - Assessment
Service         - Vessel service
```

### Tank CML Data

```
Tank_ID         - Tank identifier (e.g., "T-501")
Zone            - SHELL, FLOOR, or ANNULAR
Course          - Shell course number (1 = bottom)
Grid_Row        - Floor plate grid row (A, B, C...)
Grid_Col        - Floor plate grid column (1, 2, 3...)
Orientation     - Compass direction (N, NE, E, SE, S, SW, W, NW)
Original_mm     - As-built thickness
t_min_mm        - Minimum required thickness
Reading_mm      - Current reading
Service         - Tank service
```

## Mandatory Fields per Code

### API 570 (Piping) Required Documentation

- [ ] Equipment/circuit identification
- [ ] Date of inspection
- [ ] Inspector name & qualification
- [ ] Inspection procedure reference
- [ ] Instrument identification & calibration
- [ ] CML locations
- [ ] Thickness readings
- [ ] Previous readings (if available)
- [ ] Corrosion rate calculation
- [ ] Remaining life calculation
- [ ] Minimum required thickness (t-min)
- [ ] Condition assessment
- [ ] Recommendations

### API 510 (Vessels) Required Documentation

- [ ] Vessel identification (tag, NB number)
- [ ] Nameplate data (MAWP, design temp, material)
- [ ] Inspection date and type
- [ ] Inspector qualification
- [ ] Thickness data by zone
- [ ] Corrosion rate calculations
- [ ] Remaining life assessment
- [ ] Next inspection date recommendation

### API 653 (Tanks) Required Documentation

- [ ] Tank identification
- [ ] Construction details (diameter, height, capacity)
- [ ] Shell course readings by orientation
- [ ] Floor plate readings (grid)
- [ ] Annular plate readings
- [ ] Corrosion rate calculations
- [ ] Settlement data (if applicable)
- [ ] Recommendations

## Realistic Data Characteristics

The sample data includes realistic characteristics:

### Corrosion Patterns

- **Elbows**: Higher corrosion at extrados (outside of bend)
- **Tees**: Higher at branch connections
- **Control valves**: Downstream erosion/corrosion
- **Bottom heads**: Sludge zone corrosion
- **Shell course 2**: Liquid level interface corrosion
- **Tank floors**: Random pitting (5% of locations)
- **Annular plates**: Inner edge typically thinner

### Alert Conditions

- Some CMLs have readings approaching t-min
- Calculated remaining life < 10 years flagged as ALERT
- Remaining life 10-20 years flagged as Fair
- Realistic corrosion rates (0.05 - 0.25 mm/yr)

### Data Variations

- Multiple readings per CML (2-4 depending on component)
- Mix of metric (mm) and imperial references
- Schedules match NPS appropriately
- Materials match service appropriately

## Usage for MVP Testing

### Test Cases

1. **Basic Report Generation**

   - Import single piping circuit CSV
   - Generate formatted report with calculations

2. **Multi-Circuit Summary**

   - Import all piping circuits
   - Generate facility-wide summary with worst-case flagging

3. **Vessel Report**

   - Import vessel data
   - Generate zone-by-zone report

4. **Tank Report**

   - Import tank data
   - Generate shell + floor + annular combined report

5. **Instrument Data Import**

   - Parse 38DL export format
   - Map to CML structure

6. **Alert Detection**
   - Identify readings below alert threshold
   - Flag high corrosion rates
   - Calculate re-inspection intervals

## Regenerating Data

To regenerate with different parameters:

```bash
# Generate Excel templates
python generators/generate_cml_templates.py

# Generate CSV sample data
python generators/generate_csv_samples.py
```

Modify the generator scripts in `generators/` to adjust:

- Number of circuits/vessels/tanks
- Corrosion factors
- Problem area locations
- Date ranges

## License

This sample data is provided for UMA AI development and testing purposes.
