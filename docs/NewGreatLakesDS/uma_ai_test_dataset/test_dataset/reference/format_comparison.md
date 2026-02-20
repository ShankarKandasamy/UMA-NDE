# Field Data Format Comparison

## 2024 Format (Current Survey - Olympus 38DL Plus Export)
| Field Name | Example | Notes |
|------------|---------|-------|
| ID | 6-SG-101-01 | CML identifier |
| Reading | 0.217 | Thickness in inches |
| Units | in | Always "in" |
| Date | 2024-11-04 | ISO format (varies) |
| Time | 14:32:17 | 24-hour format |
| Operator | M. Chen | Inspector initials + surname |
| Gauge | 38DL-2847193 | Serial number |
| Probe | D790-SM | Probe model |
| Material | Steel | Material type |
| Velocity | 0.2330 | Sound velocity in/μs |
| Gain | 52.0 | dB |
| Notes | | Free text |

## 2019 Format (Historical Survey - Olympus 37DL Export)
| Field Name | Example | Notes |
|------------|---------|-------|
| Location ID | 6-SG-101-01 | CML identifier (same convention) |
| Piping Line | 6-SG-101 | Line number |
| Fitting Type | Elbow 90° | Component type |
| Measured Thickness (in) | 0.238 | Thickness reading |
| Nominal (in) | 0.280 | Nominal wall |
| Min Required (in) | 0.140 | t-min |
| Survey Date | Oct 15, 2019 | Text date format |
| Technician | J. Martinez | Full initial + surname |
| Equipment | Olympus 37DL | Gauge model only |
| Comments | | Free text |

## Key Differences for Processing:
1. Column name variations (ID vs Location ID, Reading vs Measured Thickness)
2. Date format (ISO vs text month)
3. 2019 includes nominal/t-min in export; 2024 doesn't
4. Different inspector name format
5. 2024 has more technical fields (velocity, gain, probe)

## Mapping for Corrosion Rate Calculation:
- 2024 "ID" → 2019 "Location ID"
- 2024 "Reading" → 2019 "Measured Thickness (in)"
- Rate = (2019_reading - 2024_reading) / 5 years × 1000 = mpy
