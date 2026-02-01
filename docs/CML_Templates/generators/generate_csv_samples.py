"""
Generate CSV sample datasets for testing UMA MVP
These represent typical exported data from field instruments or manual entry
"""

import csv
import random
from datetime import datetime, timedelta
import os

OUTPUT_DIR = '/home/claude/cml_templates/csv_samples'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================================
# PIPING DATA GENERATORS
# ============================================================================

def generate_piping_circuit(circuit_id, service, material, num_cmls, base_nominal, 
                            corrosion_factor=1.0, has_problem_areas=True):
    """Generate realistic piping circuit data"""
    
    components = ['90° Elbow', 'Straight', 'Tee-Run', 'Tee-Branch', '45° Elbow', 
                  'Reducer', 'Control Valve', 'Flange', 'Weldolet']
    
    schedules = {'6': 80, '4': 80, '8': 40, '12': 40, '2': 80, '3': 80}
    nominals = {'6': 7.11, '4': 6.02, '8': 8.18, '12': 10.31, '2': 3.91, '3': 5.49}
    
    data = []
    prev_date = (datetime.now() - timedelta(days=random.randint(365, 730))).strftime('%Y-%m-%d')
    
    for i in range(1, num_cmls + 1):
        cml = f'{i:03d}'
        component = random.choice(components)
        
        # Determine pipe size (weighted towards common sizes)
        sizes = ['6', '4', '8', '4', '6', '4', '6', '3', '2']
        nps = random.choice(sizes)
        schedule = schedules.get(nps, 40)
        nominal = nominals.get(nps, base_nominal)
        
        t_min = nominal * 0.5  # Simplified t-min calculation
        
        # Generate readings with realistic variation
        base_reading = nominal * random.uniform(0.88, 0.98) * corrosion_factor
        
        # Add problem areas
        if has_problem_areas and i in [3, 7, 9]:  # Specific CMLs with issues
            base_reading = nominal * random.uniform(0.65, 0.78)
        
        readings = []
        num_readings = 4 if component in ['90° Elbow', 'Tee-Run', 'Tee-Branch', 'Control Valve'] else 2
        for _ in range(num_readings):
            reading = base_reading + random.uniform(-0.15, 0.15)
            readings.append(round(reading, 2))
        
        while len(readings) < 4:
            readings.append('')
        
        min_reading = min([r for r in readings if r != ''])
        prev_reading = round(min_reading + random.uniform(0.08, 0.25), 2)
        
        years_since_prev = random.uniform(1.5, 2.5)
        corr_rate = round((prev_reading - min_reading) / years_since_prev, 2)
        remaining_life = round((min_reading - t_min) / corr_rate, 1) if corr_rate > 0 else 999
        
        condition = 'Good'
        if remaining_life < 10:
            condition = 'ALERT'
        elif remaining_life < 20:
            condition = 'Fair'
        
        data.append({
            'Circuit_ID': circuit_id,
            'CML': cml,
            'Component': component,
            'NPS': nps,
            'Schedule': schedule,
            'Nominal_mm': nominal,
            't_min_mm': round(t_min, 2),
            'Reading_1': readings[0],
            'Reading_2': readings[1],
            'Reading_3': readings[2] if readings[2] else '',
            'Reading_4': readings[3] if readings[3] else '',
            'Min_mm': min_reading,
            'Prev_mm': prev_reading,
            'Prev_Date': prev_date,
            'Corr_Rate_mm_yr': corr_rate,
            'Remaining_Life_yr': remaining_life,
            'Condition': condition,
            'Service': service,
            'Material': material,
        })
    
    return data


def write_piping_csv():
    """Generate multiple piping circuit CSV files"""
    
    circuits = [
        ('FW-101', 'Boiler Feedwater', 'A106 Gr.B', 15, 7.11, 0.95, True),
        ('FW-102', 'Boiler Feedwater', 'A106 Gr.B', 12, 7.11, 0.92, True),
        ('CW-201', 'Cooling Water', 'A53 Gr.B', 20, 10.31, 0.88, True),
        ('CW-202', 'Cooling Water Return', 'A53 Gr.B', 18, 10.31, 0.90, False),
        ('HC-301', 'Hydrocarbon Process', 'A106 Gr.B', 25, 8.18, 0.85, True),
        ('HC-302', 'Hydrocarbon Process', 'A106 Gr.B', 22, 8.18, 0.87, True),
        ('ST-401', 'Steam Supply', 'A106 Gr.B', 10, 7.11, 0.96, False),
        ('ST-402', 'Steam Condensate', 'A106 Gr.B', 14, 6.02, 0.88, True),
        ('AC-501', 'Acid Service', '316L SS', 8, 3.40, 0.92, True),
        ('CA-601', 'Caustic Service', 'A106 Gr.B', 12, 7.11, 0.90, True),
    ]
    
    all_data = []
    
    for circuit in circuits:
        data = generate_piping_circuit(*circuit)
        all_data.extend(data)
        
        # Write individual circuit file
        filename = f'{OUTPUT_DIR}/piping_{circuit[0].replace("-", "_")}.csv'
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"Created: {filename}")
    
    # Write combined file
    combined_file = f'{OUTPUT_DIR}/piping_all_circuits.csv'
    with open(combined_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=all_data[0].keys())
        writer.writeheader()
        writer.writerows(all_data)
    print(f"Created: {combined_file}")


# ============================================================================
# VESSEL DATA GENERATORS
# ============================================================================

def generate_vessel_data(vessel_id, service, num_shell_courses=3):
    """Generate realistic pressure vessel data"""
    
    data = []
    
    # Head data
    head_nominal = 19.05  # 3/4" typical for heads
    head_tmin = 9.53
    
    for zone, positions in [('TOP_HEAD', ['Center', 'N', 'E', 'S', 'W']),
                             ('BTM_HEAD', ['Center', 'N', 'E', 'S', 'W'])]:
        for pos in positions:
            base = head_nominal * random.uniform(0.92, 0.98)
            if zone == 'BTM_HEAD':
                base *= 0.94  # Bottom heads corrode faster
            
            reading = round(base + random.uniform(-0.1, 0.1), 2)
            prev = round(reading + random.uniform(0.15, 0.35), 2)
            rate = round((prev - reading) / 2, 2)
            life = round((reading - head_tmin) / rate, 1) if rate > 0 else 999
            
            data.append({
                'Vessel_ID': vessel_id,
                'Zone': zone,
                'CML': f"{zone[:2]}-{pos[0]}",
                'Orientation': pos,
                'Elevation': '-',
                'Nominal_mm': head_nominal,
                't_min_mm': head_tmin,
                'Reading_mm': reading,
                'Prev_mm': prev,
                'Prev_Date': '2022-04-15',
                'Corr_Rate_mm_yr': rate,
                'Remaining_Life_yr': life,
                'Condition': 'Good' if life > 50 else 'Fair',
                'Service': service,
            })
    
    # Shell courses
    shell_nominal = 25.40  # 1" typical for shell
    shell_tmin = 12.70
    
    for course in range(1, num_shell_courses + 1):
        for orientation in ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']:
            # Course 2 often has more corrosion (liquid level zone)
            factor = 0.90 if course == 2 else 0.96
            base = shell_nominal * random.uniform(factor - 0.03, factor + 0.03)
            
            reading = round(base + random.uniform(-0.1, 0.1), 2)
            prev = round(reading + random.uniform(0.18, 0.40), 2)
            rate = round((prev - reading) / 2, 2)
            life = round((reading - shell_tmin) / rate, 1) if rate > 0 else 999
            
            data.append({
                'Vessel_ID': vessel_id,
                'Zone': f'SHELL_{course}',
                'CML': f"SC{course}-{orientation}",
                'Orientation': orientation,
                'Elevation': 'Mid',
                'Nominal_mm': shell_nominal,
                't_min_mm': shell_tmin,
                'Reading_mm': reading,
                'Prev_mm': prev,
                'Prev_Date': '2022-04-15',
                'Corr_Rate_mm_yr': rate,
                'Remaining_Life_yr': life,
                'Condition': 'Good' if life > 50 else ('Fair' if life > 20 else 'ALERT'),
                'Service': service,
            })
    
    # Nozzles
    nozzle_nominal = 11.13  # Schedule 80 nozzle neck
    nozzle_tmin = 5.57
    
    for nozzle in ['N1-Inlet', 'N2-Outlet', 'N3-Drain', 'MH-Manway']:
        reading = round(nozzle_nominal * random.uniform(0.92, 0.98), 2)
        prev = round(reading + random.uniform(0.10, 0.25), 2)
        rate = round((prev - reading) / 2, 2)
        life = round((reading - nozzle_tmin) / rate, 1) if rate > 0 else 999
        
        data.append({
            'Vessel_ID': vessel_id,
            'Zone': 'NOZZLE',
            'CML': nozzle,
            'Orientation': nozzle.split('-')[1],
            'Elevation': '-',
            'Nominal_mm': nozzle_nominal,
            't_min_mm': nozzle_tmin,
            'Reading_mm': reading,
            'Prev_mm': prev,
            'Prev_Date': '2022-04-15',
            'Corr_Rate_mm_yr': rate,
            'Remaining_Life_yr': life,
            'Condition': 'Good',
            'Service': service,
        })
    
    return data


def write_vessel_csv():
    """Generate vessel CSV files"""
    
    vessels = [
        ('V-101', 'Amine Contactor', 3),
        ('V-102', 'Amine Regenerator', 4),
        ('V-201', 'Flash Drum', 2),
        ('V-202', 'Surge Drum', 2),
        ('V-301', 'Separator', 3),
        ('V-302', 'KO Drum', 2),
    ]
    
    all_data = []
    
    for vessel in vessels:
        data = generate_vessel_data(*vessel)
        all_data.extend(data)
        
        filename = f'{OUTPUT_DIR}/vessel_{vessel[0].replace("-", "_")}.csv'
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"Created: {filename}")
    
    combined_file = f'{OUTPUT_DIR}/vessel_all.csv'
    with open(combined_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=all_data[0].keys())
        writer.writeheader()
        writer.writerows(all_data)
    print(f"Created: {combined_file}")


# ============================================================================
# TANK DATA GENERATORS
# ============================================================================

def generate_tank_data(tank_id, service, num_courses=8, floor_grid_size=8):
    """Generate realistic storage tank data"""
    
    data = []
    
    # Shell course original thicknesses (decreasing up the tank)
    course_originals = [25.40, 22.23, 19.05, 15.88, 12.70, 9.53, 9.53, 9.53]
    course_tmins = [12.70, 11.12, 9.53, 7.94, 6.35, 4.76, 4.76, 4.76]
    
    orientations = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    
    # Shell readings
    for course in range(1, min(num_courses + 1, len(course_originals) + 1)):
        nominal = course_originals[course - 1]
        tmin = course_tmins[course - 1]
        
        for orientation in orientations:
            # Lower courses corrode more
            factor = 0.92 - (0.02 * (num_courses - course))
            reading = round(nominal * random.uniform(factor - 0.02, factor + 0.02), 2)
            
            data.append({
                'Tank_ID': tank_id,
                'Zone': 'SHELL',
                'Course': course,
                'Grid_Row': '',
                'Grid_Col': '',
                'Orientation': orientation,
                'Original_mm': nominal,
                't_min_mm': tmin,
                'Reading_mm': reading,
                'Service': service,
            })
    
    # Floor readings
    floor_original = 6.35
    floor_tmin = 2.54
    
    rows = 'ABCDEFGH'[:floor_grid_size]
    
    for row in rows:
        for col in range(1, floor_grid_size + 1):
            # Add some random pitting locations
            is_pit = random.random() < 0.05  # 5% chance of pitting
            if is_pit:
                reading = round(floor_original * random.uniform(0.70, 0.82), 2)
            else:
                reading = round(floor_original * random.uniform(0.88, 0.96), 2)
            
            data.append({
                'Tank_ID': tank_id,
                'Zone': 'FLOOR',
                'Course': '',
                'Grid_Row': row,
                'Grid_Col': col,
                'Orientation': '',
                'Original_mm': floor_original,
                't_min_mm': floor_tmin,
                'Reading_mm': reading,
                'Service': service,
            })
    
    # Annular plate readings
    annular_original = 12.70
    annular_tmin = 6.35
    
    for location in ['Inner_Edge', 'Mid', 'Outer_Edge']:
        for orientation in orientations:
            factor = 0.88 if location == 'Inner_Edge' else (0.92 if location == 'Mid' else 0.95)
            reading = round(annular_original * random.uniform(factor - 0.02, factor + 0.02), 2)
            
            data.append({
                'Tank_ID': tank_id,
                'Zone': 'ANNULAR',
                'Course': '',
                'Grid_Row': location,
                'Grid_Col': '',
                'Orientation': orientation,
                'Original_mm': annular_original,
                't_min_mm': annular_tmin,
                'Reading_mm': reading,
                'Service': service,
            })
    
    return data


def write_tank_csv():
    """Generate tank CSV files"""
    
    tanks = [
        ('T-501', 'Crude Oil', 8, 8),
        ('T-502', 'Crude Oil', 8, 8),
        ('T-601', 'Diesel', 6, 6),
        ('T-602', 'Diesel', 6, 6),
        ('T-701', 'Water', 5, 6),
        ('T-801', 'Slop Oil', 4, 4),
    ]
    
    all_data = []
    
    for tank in tanks:
        data = generate_tank_data(*tank)
        all_data.extend(data)
        
        filename = f'{OUTPUT_DIR}/tank_{tank[0].replace("-", "_")}.csv'
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"Created: {filename}")
    
    combined_file = f'{OUTPUT_DIR}/tank_all.csv'
    with open(combined_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=all_data[0].keys())
        writer.writeheader()
        writer.writerows(all_data)
    print(f"Created: {combined_file}")


# ============================================================================
# INSTRUMENT EXPORT FORMAT (mimics Olympus 38DL+ export)
# ============================================================================

def generate_instrument_export():
    """Generate data that mimics an Olympus 38DL+ CSV export"""
    
    data = []
    
    # Header info that would come from instrument
    file_info = {
        'Instrument': 'Olympus 38DL Plus',
        'Serial': '12345678',
        'Software': 'v2.3.1',
        'Export_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Operator': 'JSMITH',
        'Probe': 'D7906-SM 5MHz',
        'Cal_Block': 'CB-001',
    }
    
    # Generate readings in instrument format
    reading_num = 1
    for file_id in range(1, 4):  # 3 files
        for id_num in range(1, 16):  # 15 IDs per file
            for reading in range(1, random.randint(2, 5)):  # 1-4 readings per ID
                thickness = round(random.uniform(4.5, 12.0), 3)
                
                data.append({
                    'Reading_No': reading_num,
                    'File_ID': f'FILE{file_id:02d}',
                    'ID': f'ID{id_num:03d}',
                    'Reading': reading,
                    'Thickness_mm': thickness,
                    'Thickness_in': round(thickness / 25.4, 4),
                    'Velocity_m_s': 5890,
                    'Gate_Start_mm': 0.5,
                    'Gate_Width_mm': 25.0,
                    'Gain_dB': 45.5,
                    'Date': datetime.now().strftime('%Y-%m-%d'),
                    'Time': f'{random.randint(8,16):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}',
                    'Flags': '',
                })
                reading_num += 1
    
    filename = f'{OUTPUT_DIR}/instrument_export_38DL.csv'
    with open(filename, 'w', newline='') as f:
        # Write instrument header
        f.write(f"# Instrument Export\n")
        for key, value in file_info.items():
            f.write(f"# {key}: {value}\n")
        f.write("#\n")
        
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    
    print(f"Created: {filename}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("Generating CSV sample datasets...\n")
    
    write_piping_csv()
    print()
    
    write_vessel_csv()
    print()
    
    write_tank_csv()
    print()
    
    generate_instrument_export()
    
    print("\nAll CSV files generated successfully!")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == '__main__':
    main()
