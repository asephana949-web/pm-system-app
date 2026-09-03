import os
import sys
import pymysql

# =========================================================
# DATA MAPPING: dihasilkan otomatis dari Excel Revisi 3
# =========================================================
MAPPING = [
    ('RLL-BJ-001', 'RLL-BJ-001', 'Conveyor roll', 'Desirable', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('MTR-BJ-002', 'MTR-BJ-002', 'Motor Conveyor roll', 'Desirable', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('AGT-BJ-003', 'AGT-BJ-003', 'Agt. Hydra Pulper', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('PMP-BJ-004', 'PMP-BJ-005', 'Hydra Pulper Pump', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('MTR-BJ-005', 'MTR-BJ-006', 'Motor Hydra Pulper Pump', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('PMP-BJ-006', 'PMP-BJ-007', 'Indocat Pump', 'Desirable', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('MTR-BJ-007', 'MTR-BJ-008', 'Motor Indocat Pump', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('MTR-BJ-008', 'MTR-BJ-009', 'Agt.Indocat  motor', 'Desirable', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('PMP-BJ-009', 'PMP-BJ-010', 'Kaolin Pump', 'Desirable', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('MTR-BJ-010', 'MTR-BJ-011', 'Motor Kaolin Pump', 'Desirable', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('MTR-BJ-011', 'MTR-BJ-012', 'Agt.Kaolin  Motor', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('MTR-BJ-012', 'MTR-BJ-013', 'Motor Hi Base Pump', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('AGT-BJ-013', 'AGT-BJ-014', 'Chest 2 Agitator', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('MTR-BJ-014', 'MTR-BJ-015', 'Motor Chest 2 Agitator', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('AGT-BJ-015', 'AGT-BJ-016', 'Chest 3 Agitator', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('MTR-BJ-016', 'MTR-BJ-017', 'Motor Chest 3 Agitator', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('AGT-BJ-017', 'AGT-BJ-018', 'Chest 4 Agitator', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('MTR-BJ-018', 'MTR-BJ-019', 'Motor Chest 4 Agitator', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('PMP-BJ-019', 'PMP-BJ-020', 'Chest 2 Disc Pump', 'Desirable', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('MTR-BJ-020', 'MTR-BJ-021', 'Motor Chest 2 Disc Pump', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('PMP-BJ-021', 'PMP-BJ-022', 'Chest 3 Disc Pump', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('MTR-BJ-022', 'MTR-BJ-023', 'Motor Chest 3 Disc Pump', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('PMP-BJ-023', 'PMP-BJ-024', 'Chest 4 Disc Pump', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('MTR-BJ-024', 'MTR-BJ-025', 'Motor Chest 4 Disc Pump', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('RFN-BJ-025', 'RFN-BJ-026', 'TDR 1', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('MTR-BJ-026', 'MTR-BJ-027', 'Motor TDR 1', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('RFN-BJ-027', 'RFN-BJ-028', 'TDR 2', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('MTR-BJ-028', 'MTR-BJ-029', 'Motor TDR 2', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('RFN-BJ-029', 'RFN-BJ-030', 'Waterseal TDR', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('MTR-BJ-030', 'MTR-BJ-031', 'Motor Waterseal TDR', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('RFN-BJ-031', 'RFN-BJ-032', 'Deflaker', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('MTR-BJ-032', 'MTR-BJ-033', 'Motor Deflaker', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('AGT-BJ-033', 'AGT-BJ-034', 'Agt.Broke dump chest', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('MTR-BJ-034', 'MTR-BJ-035', 'Motor Agt.Broke dump chest', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('PMP-BJ-035', 'PMP-BJ-036', 'Broke dump disc. pump', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('MTR-BJ-036', 'MTR-BJ-037', 'Motor Broke dump disc. Pump', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('AGT-BJ-037', 'AGT-BJ-038', 'Agt.Broke Chest', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('MTR-BJ-038', 'MTR-BJ-039', 'Motor Agt.Broke Chest', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('PMP-BJ-039', 'PMP-BJ-040', 'Broke Disc. pump', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('MTR-BJ-040', 'MTR-BJ-041', 'Motor Broke Disc. Pump', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('AGT-BJ-041', 'AGT-BJ-042', 'Agt.Short Fiber Chest', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('MTR-BJ-042', 'MTR-BJ-043', 'Motor Agt.Short Fiber Chest', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('AGT-BJ-043', 'AGT-BJ-044', 'Agt.Long Fiber Chest', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('MTR-BJ-044', 'MTR-BJ-045', 'Motor Agt.Long Fiber Chest', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('AGT-BJ-045', 'AGT-BJ-046', 'Agt.Long Fiber refiner Chest', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('MTR-BJ-046', 'MTR-BJ-047', 'Motor Agt.Long Fiber refiner Chest', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('PMP-BJ-047', 'PMP-BJ-048', 'Short - Long Fiber Refiner Disc. pump', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('MTR-BJ-048', 'MTR-BJ-049', 'Motor Short - Long Fiber Refiner Disc. Pump', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('AGT-BJ-049', 'AGT-BJ-050', 'Agt.Blending Chest', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('MTR-BJ-050', 'MTR-BJ-051', 'Motor Agt.Blending Chest', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('PMP-BJ-051', 'PMP-BJ-052', 'Blending Disc. Pump', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('MTR-BJ-052', 'MTR-BJ-053', 'Motor Blending Disc. Pump', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('AGT-MK1-001', 'AGT-MK1-001', 'Agt. Machine Chest', 'Vital', 'MESIN KERTAS 1', ''),
    ('MTR-MK1-002', 'MTR-MK1-002', 'Motor Agt. Machine Chest', 'Vital', 'MESIN KERTAS 1', ''),
    ('AGT-MK1-003', 'AGT-MK1-003', 'Agt. Finish Chest', 'Vital', 'MESIN KERTAS 1', ''),
    ('MTR-MK1-004', 'MTR-MK1-004', 'Motor  Agt. Finish Chest', 'Vital', 'MESIN KERTAS 1', ''),
    ('PMP-MK1-005', 'PMP-MK1-005', 'Machine Chest Pump', 'Essential', 'MESIN KERTAS 1', ''),
    ('MTR-MK1-006', 'MTR-MK1-006', 'Motor Machine Chest Pump', 'Essential', 'MESIN KERTAS 1', ''),
    ('PMP-MK1-007', 'PMP-MK1-007', 'Finish Chest Pump', 'Essential', 'MESIN KERTAS 1', ''),
    ('MTR-MK1-008', 'MTR-MK1-008', 'Motor Finish Chest Pump', 'Essential', 'MESIN KERTAS 1', ''),
    ('MSC-MK1-009', 'MSC-MK1-009', 'Tumbler', 'Desirable', 'MESIN KERTAS 1', ''),
    ('MTR-MK1-010', 'MTR-MK1-010', 'Motor Tumbler', 'Desirable', 'MESIN KERTAS 1', ''),
    ('RFN-MK1-011', 'RFN-MK1-011', 'Brushing Refiner', 'Vital', 'MESIN KERTAS 1', ''),
    ('MTR-MK1-012', 'MTR-MK1-012', 'Motor Brushing Refiner', 'Vital', 'MESIN KERTAS 1', ''),
    ('PMP-MK1-013', 'PMP-MK1-013', 'Booster Pump', 'Essential', 'MESIN KERTAS 1', ''),
    ('MTR-MK1-014', 'MTR-MK1-014', 'Motor Booster Pump', 'Essential', 'MESIN KERTAS 1', ''),
    ('PMP-MK1-015', 'PMP-MK1-015', 'Header Pump', 'Essential', 'MESIN KERTAS 1', ''),
    ('MTR-MK1-016', 'MTR-MK1-016', 'Motor Header Pump', 'Essential', 'MESIN KERTAS 1', ''),
    ('PMP-MK1-017', 'PMP-MK1-017', 'Centri Cleaner Pump', 'Essential', 'MESIN KERTAS 1', ''),
    ('MTR-MK1-018', 'MTR-MK1-018', 'Motor Centri Cleaner Pump', 'Essential', 'MESIN KERTAS 1', ''),
    ('MSC-MK1-019', 'MSC-MK1-019', 'Cone stage 1 - 2', 'Vital', 'MESIN KERTAS 1', ''),
    ('MSC-MK1-020', 'MSC-MK1-020', 'Pressure Screen', 'Vital', 'MESIN KERTAS 1', ''),
    ('MTR-MK1-021', 'MTR-MK1-021', 'Motor Pressure Screen', 'Vital', 'MESIN KERTAS 1', ''),
    ('MSC-MK1-022', 'MSC-MK1-022', 'Shacking Machine', 'Vital', 'MESIN KERTAS 1', ''),
    ('MTR-MK1-023', 'MTR-MK1-023', 'Motor Shacking Machine', 'Vital', 'MESIN KERTAS 1', ''),
    ('PMP-MK1-024', 'PMP-MK1-024', 'Vang stuff pump', 'Essential', 'MESIN KERTAS 1', ''),
    ('MTR-MK1-025', 'MTR-MK1-025', 'Motor Vang stuff pump', 'Essential', 'MESIN KERTAS 1', ''),
    ('PMP-MK1-026', 'PMP-MK1-026', 'White Water Pump', 'Essential', 'MESIN KERTAS 1', ''),
    ('MTR-MK1-027', 'MTR-MK1-027', 'Motor White Water Pump', 'Essential', 'MESIN KERTAS 1', ''),
    ('PMP-MK1-028', 'PMP-MK1-028', 'Drain Pump', 'Essential', 'MESIN KERTAS 1', ''),
    ('MTR-MK1-029', 'MTR-MK1-029', 'Motor Drain Pump', 'Essential', 'MESIN KERTAS 1', ''),
    ('PMP-MK1-030', 'PMP-MK1-030', 'Nash Pump', 'Vital', 'MESIN KERTAS 1', ''),
    ('MTR-MK1-031', 'MTR-MK1-031', 'Motor Nash Pump', 'Vital', 'MESIN KERTAS 1', ''),
    ('PMP-MK1-032', 'PMP-MK1-032', 'Suction Felt Pump 1', 'Essential', 'MESIN KERTAS 1', ''),
    ('MTR-MK1-033', 'MTR-MK1-033', 'Motor Suction Felt Pump 1', 'Essential', 'MESIN KERTAS 1', ''),
    ('PMP-MK1-034', 'PMP-MK1-034', 'Suction Felt Pump 2', 'Essential', 'MESIN KERTAS 1', ''),
    ('MTR-MK1-035', 'MTR-MK1-035', 'Motor Suction Felt Pump 2', 'Essential', 'MESIN KERTAS 1', ''),
    ('PMP-MK1-036', 'PMP-MK1-036', 'Vacuum Pump', 'Vital', 'MESIN KERTAS 1', ''),
    ('MTR-MK1-037', 'MTR-MK1-037', 'Motor Vacuum Pump', 'Vital', 'MESIN KERTAS 1', ''),
    ('PMP-MK1-038', 'PMP-MK1-038', 'Couch Pit Pump', 'Essential', 'MESIN KERTAS 1', ''),
    ('MTR-MK1-039', 'MTR-MK1-039', 'Motor Couch Pit Pump', 'Essential', 'MESIN KERTAS 1', ''),
    ('MSC-MK1-040', 'MSC-MK1-040', 'Agitator Couch Pit', 'Essential', 'MESIN KERTAS 1', ''),
    ('MTR-MK1-041', 'MTR-MK1-041', 'Motor Agitator Couch Pit', 'Essential', 'MESIN KERTAS 1', ''),
    ('PMP-MK1-042', 'PMP-MK1-042', 'Drain pit Pump', 'Essential', 'MESIN KERTAS 1', ''),
    ('MTR-MK1-043', 'MTR-MK1-043', 'Motor Drain pit Pump', 'Essential', 'MESIN KERTAS 1', ''),
    ('RLL-MK1-044', 'RLL-MK1-044', 'Holley roll', 'Vital', 'MESIN KERTAS 1', ''),
    ('MTR-MK1-045', 'MTR-MK1-045', 'Motor Holley roll', 'Vital', 'MESIN KERTAS 1', ''),
    ('RLL-MK1-046', 'RLL-MK1-046', 'Breast roll', 'Vital', 'MESIN KERTAS 1', ''),
    ('RLL-MK1-047', 'RLL-MK1-047', 'Table roll', 'Essential', 'MESIN KERTAS 1', ''),
    ('RLL-MK1-048', 'RLL-MK1-048', 'Wire roll', 'Vital', 'MESIN KERTAS 1', ''),
    ('RLL-MK1-049', 'RLL-MK1-049', 'Guide roll', 'Vital', 'MESIN KERTAS 1', ''),
    ('RLL-MK1-050', 'RLL-MK1-050', 'Dandy roll', 'Essential', 'MESIN KERTAS 1', ''),
    ('RLL-MK1-051', 'RLL-MK1-051', 'Couch roll', 'Vital', 'MESIN KERTAS 1', ''),
    ('MTR-MK1-052', 'MTR-MK1-052', 'DC motor Couch roll', 'Vital', 'MESIN KERTAS 1', ''),
    ('RLL-MK1-053', 'RLL-MK1-053', 'Top roll Press 1', 'Vital', 'MESIN KERTAS 1', ''),
    ('RLL-MK1-054', 'RLL-MK1-054', 'Bottom roll  Press 1', 'Vital', 'MESIN KERTAS 1', ''),
    ('MTR-MK1-055', 'MTR-MK1-055', 'DC motor  Press 1', 'Vital', 'MESIN KERTAS 1', ''),
    ('RLL-MK1-056', 'RLL-MK1-056', 'Top roll Press 2', 'Vital', 'MESIN KERTAS 1', ''),
    ('RLL-MK1-057', 'RLL-MK1-057', 'Bottom roll  Press 2', 'Vital', 'MESIN KERTAS 1', ''),
    ('MTR-MK1-058', 'MTR-MK1-058', 'DC motor  Press 2', 'Vital', 'MESIN KERTAS 1', ''),
    ('RLL-MK1-059', 'RLL-MK1-059', 'Top roll Press 3', 'Vital', 'MESIN KERTAS 1', ''),
    ('RLL-MK1-060', 'RLL-MK1-060', 'Bottom roll  Press 3', 'Vital', 'MESIN KERTAS 1', ''),
    ('MTR-MK1-061', 'MTR-MK1-061', 'DC motor  Press 3', 'Vital', 'MESIN KERTAS 1', ''),
    ('RLL-MK1-062', 'RLL-MK1-062', 'Felt Roll Press 1', 'Essential', 'MESIN KERTAS 1', ''),
    ('RLL-MK1-063', 'RLL-MK1-063', 'Felt Roll Press 2', 'Essential', 'MESIN KERTAS 1', ''),
    ('RLL-MK1-064', 'RLL-MK1-064', 'Felt Roll Press 3', 'Essential', 'MESIN KERTAS 1', ''),
    ('RLL-MK1-065', 'RLL-MK1-065', 'Worm Roll Press 1', 'Essential', 'MESIN KERTAS 1', ''),
    ('RLL-MK1-066', 'RLL-MK1-066', 'Worm Roll Press 2', 'Essential', 'MESIN KERTAS 1', ''),
    ('RLL-MK1-067', 'RLL-MK1-067', 'Kitnir roll press 1', 'Essential', 'MESIN KERTAS 1', ''),
    ('RLL-MK1-068', 'RLL-MK1-068', 'Kitnir roll press 2', 'Essential', 'MESIN KERTAS 1', ''),
    ('RLL-MK1-069', 'RLL-MK1-069', 'Kitnir roll press 3', 'Essential', 'MESIN KERTAS 1', ''),
    ('RLL-MK1-070', 'RLL-MK1-070', 'Wind/paper roll', 'Essential', 'MESIN KERTAS 1', ''),
    ('FAN-MK1-071', 'FAN-MK1-071', 'Cooling fan', 'Vital', 'MESIN KERTAS 1', ''),
    ('MTR-MK1-072', 'MTR-MK1-072', 'Motor Cooling fan', 'Vital', 'MESIN KERTAS 1', ''),
    ('RLL-MK1-073', 'RLL-MK1-073', 'Drum Dryer roll', 'Vital', 'MESIN KERTAS 1', ''),
    ('RLL-MK1-074', 'RLL-MK1-074', 'Spand/felt roll', 'Essential', 'MESIN KERTAS 1', ''),
    ('RLL-MK1-075', 'RLL-MK1-075', 'Wind/paper roll', 'Essential', 'MESIN KERTAS 1', ''),
    ('MTR-MK1-076', 'MTR-MK1-076', 'DC motor Dryer', 'Vital', 'MESIN KERTAS 1', ''),
    ('RLL-MK1-077', 'RLL-MK1-077', 'Spreader roll', 'Essential', 'MESIN KERTAS 1', ''),
    ('RLL-MK1-078', 'RLL-MK1-078', 'Top Calander roll', 'Vital', 'MESIN KERTAS 1', ''),
    ('RLL-MK1-079', 'RLL-MK1-079', 'Bottom Calander roll', 'Vital', 'MESIN KERTAS 1', ''),
    ('MTR-MK1-080', 'MTR-MK1-080', 'DC motor  Calander', 'Vital', 'MESIN KERTAS 1', ''),
    ('RLL-MK1-081', 'RLL-MK1-081', 'Banana roll', 'Vital', 'MESIN KERTAS 1', ''),
    ('MSC-MK1-082', 'MSC-MK1-082', 'Pope Reel', 'Vital', 'MESIN KERTAS 1', ''),
    ('MTR-MK1-083', 'MTR-MK1-083', 'DC motor  Pope Reel', 'Vital', 'MESIN KERTAS 1', ''),
    ('RLL-MK1-084', 'RLL-MK1-084', 'Spool roll', 'Desirable', 'MESIN KERTAS 1', ''),
    ('MSC-F1-001', 'MSC-F1-001', 'Rewinder 1', 'Essential', 'FINISHING 1', ''),
    ('MSC-F1-002', 'MSC-F1-002', 'Rewinder 2', 'Essential', 'FINISHING 1', ''),
    ('RLL-F1-003', 'RLL-F1-003', 'Roll To Sheet 1', 'Essential', 'FINISHING 1', ''),
    ('RLL-F1-004', 'RLL-F1-004', 'Roll To Sheet 2', 'Essential', 'FINISHING 1', ''),
    ('MSC-F1-005', 'MSC-F1-005', 'Guillotine', 'Essential', 'FINISHING 1', ''),
    ('MSC-F1-006', 'MSC-F1-006', 'Wrapping', 'Essential', 'FINISHING 1', ''),
    ('FAN-BOI-001', 'FAN-BOI-001', 'FD fan', 'Vital', 'BOILER', 'SEKSI PRODUKSI UAP'),
    ('FAN-BOI-002', 'FAN-BOI-002', 'ID fan', 'Vital', 'BOILER', 'SEKSI PRODUKSI UAP'),
    ('PMP-BOI-003', 'PMP-BOI-003', 'Feed Water Pump I-II', 'Vital', 'BOILER', 'SEKSI PRODUKSI UAP'),
    ('MSC-BOI-004', 'MSC-BOI-004', 'Rotary Valve', 'Vital', 'BOILER', 'SEKSI PRODUKSI UAP'),
    ('MSC-BOI-005', 'MSC-BOI-005', 'Scrubber Valve', 'Vital', 'BOILER', 'SEKSI PRODUKSI UAP'),
    ('MSC-BOI-006', 'MSC-BOI-006', 'Ash Screw I-II', 'Vital', 'BOILER', 'SEKSI PRODUKSI UAP'),
    ('PMP-BOI-007', 'PMP-BOI-007', 'Raw Water Pump I-II', 'Vital', 'BOILER', 'SEKSI PRODUKSI UAP'),
    ('MSC-BOI-008', 'MSC-BOI-008', 'Screw Fending I-II', 'Vital', 'BOILER', 'SEKSI PRODUKSI UAP'),
    ('CNV-BOI-009', 'CNV-BOI-009', 'Conveyor', 'Vital', 'BOILER', 'SEKSI PRODUKSI UAP'),
    ('RLL-SP-001', 'RLL-SP-001', 'Conveyor roll', 'Desirable', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-002', 'MTR-SP-002', 'Motor Conveyor roll', 'Desirable', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MSC-SP-003', 'MSC-SP-003', 'Agitator Hydra Pulper', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-004', 'MTR-SP-004', 'Motor Agitator Hydra Pulper', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-005', 'PMP-SP-005', 'Hydra Pulper Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-006', 'MTR-SP-006', 'Motor Hydra Pulper Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-007', 'PMP-SP-007', 'Cycling Chest BKP Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-008', 'MTR-SP-008', 'Motor Cycling Chest BKP Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-009', 'PMP-SP-009', 'Cycling C Straw Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-010', 'MTR-SP-010', 'Motor Cycling C Straw Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-011', 'PMP-SP-011', 'BKP Refiner C Pump', 'Desirable', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-012', 'MTR-SP-012', 'Motor BKP Refiner C Pump', 'Desirable', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-013', 'PMP-SP-013', 'Straw Refiner C Pump', 'Desirable', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-014', 'MTR-SP-014', 'Motor Straw Refiner C Pump', 'Desirable', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-015', 'PMP-SP-015', 'Mixing Chest Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-016', 'MTR-SP-016', 'Motor Mixing Chest Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-017', 'PMP-SP-017', 'Refiner Broke C Pump', 'Desirable', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-018', 'MTR-SP-018', 'Motor Refiner Broke C Pump', 'Desirable', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('AGT-SP-019', 'AGT-SP-019', 'Agitator Ref. Broke Chest', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-020', 'MTR-SP-020', 'Motor Agitator Ref. Broke Chest', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-021', 'PMP-SP-021', 'Finished Chest Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-022', 'MTR-SP-022', 'Motor Finished Chest Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-023', 'PMP-SP-023', 'Setling Over Pump (W.W)', 'Desirable', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-024', 'MTR-SP-024', 'Motor Setling Over Pump (W.W)', 'Desirable', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-025', 'PMP-SP-025', 'Machine Chest Pump', 'Vital', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-026', 'MTR-SP-026', 'Motor Machine Chest Pump', 'Vital', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-027', 'PMP-SP-027', 'White water Seal Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-028', 'MTR-SP-028', 'Motor White water Seal Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-029', 'PMP-SP-029', 'White water Over Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-030', 'MTR-SP-030', 'Motor White water Over Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-031', 'PMP-SP-031', 'White Water Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-032', 'MTR-SP-032', 'Motor White Water Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-033', 'PMP-SP-033', 'Cospit Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-034', 'MTR-SP-034', 'Motor Cospit Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MSC-SP-035', 'MSC-SP-035', 'Agitator Cospit', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-036', 'MTR-SP-036', 'Motor Agitator Cospit', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-037', 'PMP-SP-037', 'Booster Pump', 'Vital', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-038', 'MTR-SP-038', 'Motor Booster Pump', 'Vital', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MSC-SP-039', 'MSC-SP-039', 'Agitator Broke Pulper', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-040', 'MTR-SP-040', 'Motor Agitator Broke Pulper', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-041', 'PMP-SP-041', 'Broke Pulper Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-042', 'MTR-SP-042', 'Motor Broke Pulper Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-043', 'PMP-SP-043', 'Condensate Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-044', 'MTR-SP-044', 'Motor Condensate Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-045', 'PMP-SP-045', 'Sirculation oil Pump 1', 'Vital', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-046', 'MTR-SP-046', 'Motor Sirculation oil Pump 1', 'Vital', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-047', 'PMP-SP-047', 'Sirculation oil Pump 2', 'Vital', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-048', 'MTR-SP-048', 'Motor Sirculation oil Pump 2', 'Vital', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-049', 'PMP-SP-049', 'Vacuum Pump 1', 'Vital', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-050', 'MTR-SP-050', 'Motor Vacuum Pump 1', 'Vital', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-051', 'PMP-SP-051', 'Vacuum Pump 2', 'Vital', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-052', 'MTR-SP-052', 'Motor Vacuum Pump 2', 'Vital', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-053', 'PMP-SP-053', 'Vacuum Pump 3', 'Vital', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-054', 'MTR-SP-054', 'Motor Vacuum Pump 3', 'Vital', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-055', 'PMP-SP-055', 'Vacuum Pump 4', 'Vital', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-056', 'MTR-SP-056', 'Motor Vacuum Pump 4', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-057', 'PMP-SP-057', 'Drain Vacuum Pump 1', 'Vital', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-058', 'MTR-SP-058', 'Motor Drain Vacuum Pump 1', 'Vital', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-059', 'PMP-SP-059', 'Drain Vacuum Pump 2', 'Vital', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-060', 'MTR-SP-060', 'Motor Drain Vacuum Pump 2', 'Vital', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-061', 'PMP-SP-061', 'Hydrant pump', 'Desirable', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-062', 'MTR-SP-062', 'Motor Hydrant pump', 'Desirable', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-063', 'PMP-SP-063', 'CaCo3/Clay Pump (Storage)', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-064', 'MTR-SP-064', 'Motor CaCo/Clay Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MSC-SP-065', 'MSC-SP-065', 'Agitator CaCo3 (1)', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-066', 'MTR-SP-066', 'Motor  Agitator CaCo3 (1)', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MSC-SP-067', 'MSC-SP-067', 'Agitator CaCo3 (2)', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-068', 'MTR-SP-068', 'Motor   Agitator CaCo3 (2)', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MSC-SP-069', 'MSC-SP-069', 'Agitator Clay (1)', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-070', 'MTR-SP-070', 'Motor   Agitator Clay (1)', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MSC-SP-071', 'MSC-SP-071', 'Agitator Clay (2)', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-072', 'MTR-SP-072', 'Motor   Agitator Clay (2)', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-073', 'PMP-SP-073', 'Kaolin Pump  Agt', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-074', 'MTR-SP-074', 'Motor Kaolin Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MSC-SP-075', 'MSC-SP-075', 'Vibrating  Kaolin', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-076', 'MTR-SP-076', 'Motor Vibrating  Kaolin', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-077', 'PMP-SP-077', 'Indocat Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-078', 'MTR-SP-078', 'Motor Indocat Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MSC-SP-079', 'MSC-SP-079', 'Agitator indocat', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-080', 'MTR-SP-080', 'Motor Agitator indocat', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-081', 'PMP-SP-081', 'Broke Pulper Chest Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-082', 'MTR-SP-082', 'Motor Broke Pulper Chest Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('AGT-SP-083', 'AGT-SP-083', 'Agt Broke Pulper Chest', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-084', 'MTR-SP-084', 'Motor Agt Broke Pulper Chest', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-085', 'PMP-SP-085', 'BKP Dump Chest Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-086', 'MTR-SP-086', 'Motor BKP Dump Chest Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('AGT-SP-087', 'AGT-SP-087', 'Agt.BKP Dump Chest', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-088', 'MTR-SP-088', 'Motor Agt.BKP Dump Chest', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-089', 'PMP-SP-089', 'Straw Dump Chest Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-090', 'MTR-SP-090', 'Motor Straw Dump Chest Pump', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('AGT-SP-091', 'AGT-SP-091', 'Agt.Straw D. Chest', 'Desirable', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-092', 'MTR-SP-092', 'Motor Agt.Straw D. Chest', 'Desirable', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('RFN-SP-093', 'RFN-SP-093', 'Deflaker', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-094', 'MTR-SP-094', 'Motor Deflaker', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('RFN-SP-095', 'RFN-SP-095', 'TDR 1', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-096', 'MTR-SP-096', 'Motor TDR 1', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('RFN-SP-097', 'RFN-SP-097', 'TDR 2', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-098', 'MTR-SP-098', 'Motor TDR 2', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('AGT-SP-099', 'AGT-SP-099', 'Agt. BKP Refiner Chest', 'Desirable', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-100', 'MTR-SP-100', 'Motor Agt. BKP Refiner Chest', 'Desirable', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('AGT-SP-101', 'AGT-SP-101', 'Agt. Straw Ref. Chest', 'Desirable', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-102', 'MTR-SP-102', 'Motor Agt. Straw Ref. Chest', 'Desirable', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('AGT-SP-103', 'AGT-SP-103', 'Agt. Mixing Chest', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-104', 'MTR-SP-104', 'Motor Agt. Mixing Chest', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('AGT-SP-105', 'AGT-SP-105', 'Agt. Finish Chest', 'Vital', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-106', 'MTR-SP-106', 'Motor Agt. Finish Chest', 'Vital', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('AGT-SP-107', 'AGT-SP-107', 'Agt. Machine Chest', 'Vital', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-108', 'MTR-SP-108', 'Motor Agt. Machine Chest', 'Vital', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-109', 'MTR-SP-109', 'Agt. Fourstage  motor', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MSC-SP-110', 'MSC-SP-110', 'Tumbler', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-111', 'MTR-SP-111', 'Motor Tumbler', 'Essential', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('RFN-SP-112', 'RFN-SP-112', 'Jordan Refiner', 'Vital', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-113', 'MTR-SP-113', 'Motor Jordan Refiner', 'Vital', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-114', 'PMP-SP-114', 'Reffler Pump', 'Vital', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-115', 'MTR-SP-115', 'Motor Reffler Pump', 'Vital', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MSC-SP-116', 'MSC-SP-116', 'Liquid cyclone', 'Vital', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MSC-SP-117', 'MSC-SP-117', 'Pressure  Screen', 'Vital', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-118', 'MTR-SP-118', 'Motor Pressure  Screen', 'Vital', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('PMP-SP-119', 'PMP-SP-119', 'Booster Pump II', 'Desirable', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('MTR-SP-120', 'MTR-SP-120', 'Motor Booster Pump II', 'Desirable', 'STOCK PREPARATION', 'SEKSI KERTAS UNIT 2'),
    ('RLL-MK3-001', 'RLL-MK3-001', 'Holley Roll 1', 'Vital', 'MESIN KERTAS 3', ''),
    ('MTR-MK3-002', 'MTR-MK3-002', 'Motor + Gearbox Holley Roll', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-003', 'RLL-MK3-003', 'Holley Roll 2', 'Vital', 'MESIN KERTAS 3', ''),
    ('MSC-MK3-004', 'MSC-MK3-004', 'Shaking Machine', 'Vital', 'MESIN KERTAS 3', ''),
    ('MTR-MK3-005', 'MTR-MK3-005', 'Motor + Gearbox Shaking Machine', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-006', 'RLL-MK3-006', 'Breast Roll', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-007', 'RLL-MK3-007', 'Table roll', 'Essential', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-008', 'RLL-MK3-008', 'Wire Roll', 'Essential', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-009', 'RLL-MK3-009', 'Wire Guide Roll', 'Essential', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-010', 'RLL-MK3-010', 'Dandy Roll', 'Essential', 'MESIN KERTAS 3', ''),
    ('MTR-MK3-011', 'MTR-MK3-011', 'Motor DC Dandy Roll', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-012', 'RLL-MK3-012', 'Suction Couch Roll', 'Vital', 'MESIN KERTAS 3', ''),
    ('MTR-MK3-013', 'MTR-MK3-013', 'DC Motor Suction Couch Roll', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-014', 'RLL-MK3-014', 'Wire Drive Roll', 'Vital', 'MESIN KERTAS 3', ''),
    ('MTR-MK3-015', 'MTR-MK3-015', 'DC Motor Wire Drive Roll', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-016', 'RLL-MK3-016', 'Suction Pick Roll (Press 1)', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-017', 'RLL-MK3-017', 'Stone Roll (Press 1)', 'Vital', 'MESIN KERTAS 3', ''),
    ('MTR-MK3-018', 'MTR-MK3-018', 'DC Motor Suction Pick Up', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-019', 'RLL-MK3-019', 'Wringer (Plain Press Roll)', 'Essential', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-020', 'RLL-MK3-020', 'Wringer (Grooved Press Roll)', 'Essential', 'MESIN KERTAS 3', ''),
    ('MTR-MK3-021', 'MTR-MK3-021', 'DC Motor Wringer', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-025', 'RLL-MK3-022', 'Press Felt Roll Press 1', 'Essential', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-026', 'RLL-MK3-023', 'Press Felt Worm Roll Press 1', 'Essential', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-027', 'RLL-MK3-024', 'Paper Roll Press 1', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-022', 'RLL-MK3-025', 'Press 2 (Plain Press Roll)', 'Essential', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-023', 'RLL-MK3-026', 'Press 2 (Grooved Press Roll)', 'Essential', 'MESIN KERTAS 3', ''),
    ('MTR-MK3-024', 'MTR-MK3-027', 'DC Motor Press 2', 'Essential', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-028', 'RLL-MK3-031', 'Breaker Stack Top Roll', 'Essential', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-029', 'RLL-MK3-032', 'Breaker Stack Bottom Roll', 'Essential', 'MESIN KERTAS 3', ''),
    ('MTR-MK3-030', 'MTR-MK3-033', 'DC Motor Breaker Stack', 'Essential', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-031', 'RLL-MK3-034', 'Chemical Press Top Roll', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-032', 'RLL-MK3-035', 'Chemical Press Bottom Roll', 'Vital', 'MESIN KERTAS 3', ''),
    ('MSC-MK3-033', 'MSC-MK3-036', 'Chemical press Aplicator', 'Vital', 'MESIN KERTAS 3', ''),
    ('MTR-MK3-034', 'MTR-MK3-037', 'DC Motor Chemical', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-035', 'RLL-MK3-038', 'Marking press Top Roll', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-036', 'RLL-MK3-039', 'Marking press Middle roll', 'Vital', 'MESIN KERTAS 3', ''),
    ('MSC-MK3-037', 'MSC-MK3-040', 'Marking press Bottom R', 'Vital', 'MESIN KERTAS 3', ''),
    ('MTR-MK3-038', 'MTR-MK3-041', 'DC Motor Marking', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-039', 'RLL-MK3-042', 'Paper Dryer Roll Group 1', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-040', 'RLL-MK3-043', 'Felt Drayer Roll Group 1', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-041', 'RLL-MK3-044', 'Drayer Felt Roll Group 1', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-042', 'RLL-MK3-045', 'Dryer Paper Roll Group 1', 'Vital', 'MESIN KERTAS 3', ''),
    ('MTR-MK3-043', 'MTR-MK3-046', 'DC Motor Dryer Group 1', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-044', 'RLL-MK3-047', 'Paper Dryer Roll  Group 2', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-045', 'RLL-MK3-048', 'Felt Drayer Roll Group 2', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-046', 'RLL-MK3-049', 'Drayer Felt Roll Group 2', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-047', 'RLL-MK3-050', 'Dryer Paper Roll Group 2', 'Vital', 'MESIN KERTAS 3', ''),
    ('MTR-MK3-048', 'MTR-MK3-051', 'DC Motor Dryer Group 2', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-049', 'RLL-MK3-052', 'Paper Dryer Roll Group 3', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-050', 'RLL-MK3-053', 'Felt Drayer Roll Group 3', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-051', 'RLL-MK3-054', 'Drayer Felt Roll Group 3', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-052', 'RLL-MK3-055', 'Dryer Paper Roll Group 3', 'Vital', 'MESIN KERTAS 3', ''),
    ('MTR-MK3-053', 'MTR-MK3-056', 'DC Motor Dryer Group 3', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-054', 'RLL-MK3-057', 'Paper Dryer Roll Group 4', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-055', 'RLL-MK3-058', 'Felt Drayer Roll Group 4', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-056', 'RLL-MK3-059', 'Drayer Felt Roll Group 4', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-057', 'RLL-MK3-060', 'Dryer Paper Roll Group 4', 'Vital', 'MESIN KERTAS 3', ''),
    ('MTR-MK3-058', 'MTR-MK3-061', 'DC Motor Dryer Group 4', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-059', 'RLL-MK3-062', 'Dryer Spring Roll', 'Essential', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-060', 'RLL-MK3-063', 'Cooling roll 1', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-061', 'RLL-MK3-064', 'Cooling roll 2', 'Vital', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-062', 'RLL-MK3-065', 'Banana Roll', 'Essential', 'MESIN KERTAS 3', ''),
    ('MSC-MK3-063', 'MSC-MK3-066', 'Reel drum', 'Vital', 'MESIN KERTAS 3', ''),
    ('MTR-MK3-064', 'MTR-MK3-067', 'DC Motor Reel Drum', 'Vital', 'MESIN KERTAS 3', ''),
    ('MSC-MK3-065', 'MSC-MK3-068', 'Reel Spool', 'Desirable', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-066', 'RLL-MK3-069', 'Reel Pinch Roll', 'Desirable', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-067', 'RLL-MK3-070', 'Reel Paper Roll', 'Desirable', 'MESIN KERTAS 3', ''),
    ('MSC-F2-001', 'MSC-F2-001', 'DR. Cutter', 'Essential', 'FINISHING 2', ''),
    ('MSC-F2-002', 'MSC-F2-002', 'Rewinder', 'Essential', 'FINISHING 2', ''),
    ('MSC-F2-003', 'MSC-F2-003', 'Guillotine', 'Essential', 'FINISHING 2', ''),
]

# Item BARU (perlu di-INSERT sebagai mesin baru)
NEW_ITEMS = [
    ('MTR-BJ-004', 'Motor Agt Hydra Pulper', 'Essential', 'BAHAN JADI', 'SEKSI KERTAS UNIT 1'),
    ('RLL-MK3-028', 'Press Felt Roll Press 2', 'Essential', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-029', 'Press Felt  Worm Roll Press 2', 'Essential', 'MESIN KERTAS 3', ''),
    ('RLL-MK3-030', 'Paper Roll Press 2', 'Vital', 'MESIN KERTAS 3', ''),
]

def get_db_connection():
    return pymysql.connect(
        host=os.environ.get('DB_HOST'),
        port=int(os.environ.get('DB_PORT', 4000)),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_NAME'),
        ssl={'ssl': {}},  
        autocommit=False,
    )

def main():
    id_berubah = [m for m in MAPPING if m[0] != m[1]]
    atribut_saja = [m for m in MAPPING if m[0] == m[1]]

    print(f"Total mesin di mapping           : {len(MAPPING)}")
    print(f"  - ID berubah (perlu rename)    : {len(id_berubah)}")
    print(f"  - ID sama, atribut saja berubah: {len(atribut_saja)}")
    print(f"Mesin baru yang akan di-INSERT   : {len(NEW_ITEMS)}\n")

    konfirmasi = input("Lanjutkan migrasi ke database? Ketik 'YA' untuk lanjut: ")
    if konfirmasi.strip().upper() != 'YA':
        print("Dibatalkan oleh user.")
        sys.exit(0)

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:

            # ============================================================
            # TAHAP 1: Rename ke ID SEMENTARA (dengan pengecekan)
            # ============================================================
            print("\nTahap 1/5: Memindahkan id_mesin ke ID sementara...")
            for id_lama, id_baru, nama, kategori, area, wilayah in id_berubah:
                tmp_id = f"TMP-{id_lama}"
                cur.execute("SELECT id_mesin FROM master_mesin WHERE id_mesin = %s", (id_lama,))
                
                # Jika ID lama masih ada di DB, ubah ke TMP. Jika tidak ada, LEWATI dengan santai.
                if cur.fetchone():
                    cur.execute("UPDATE master_mesin SET id_mesin = %s WHERE id_mesin = %s", (tmp_id, id_lama))
                else:
                    print(f"  [INFO] {id_lama} tidak ditemukan (Mungkin sudah selesai di-update sebelumnya).")

            # ============================================================
            # TAHAP 2: Rename ke ID BARU FINAL
            # ============================================================
            print("\nTahap 2/5: Memindahkan id_mesin ke ID final baru...")
            for id_lama, id_baru, nama, kategori, area, wilayah in id_berubah:
                tmp_id = f"TMP-{id_lama}"
                
                # Coba update dari TMP ke ID Baru
                cur.execute(
                    """UPDATE master_mesin
                       SET id_mesin = %s, nama_mesin = %s, kategori = %s, area = %s, wilayah = %s
                       WHERE id_mesin = %s""",
                    (id_baru, nama, kategori, area, wilayah, tmp_id)
                )
                
                # Jika tidak ada yang diupdate dari TMP (karena sudah ter-skip di Tahap 1)
                # Maka pastikan saja nama/kategori dari ID BARU-nya (jika memang sudah ada) tetap diperbarui.
                if cur.rowcount == 0:
                    cur.execute(
                        """UPDATE master_mesin
                           SET nama_mesin = %s, kategori = %s, area = %s, wilayah = %s
                           WHERE id_mesin = %s""",
                        (nama, kategori, area, wilayah, id_baru)
                    )

            # ============================================================
            # TAHAP 3: Update atribut untuk mesin yang ID-nya TETAP
            # ============================================================
            print("\nTahap 3/5: Update nama/kategori untuk mesin yang ID-nya tetap...")
            for id_lama, id_baru, nama, kategori, area, wilayah in atribut_saja:
                cur.execute(
                    """UPDATE master_mesin
                       SET nama_mesin = %s, kategori = %s, area = %s, wilayah = %s
                       WHERE id_mesin = %s""",
                    (nama, kategori, area, wilayah, id_lama)
                )

            # ============================================================
            # TAHAP 4: Insert mesin baru dengan "INSERT IGNORE"
            # ============================================================
            print("\nTahap 4/5: Insert mesin baru...")
            for id_baru, nama, kategori, area, wilayah in NEW_ITEMS:
                cur.execute(
                    """INSERT IGNORE INTO master_mesin (id_mesin, nama_mesin, area, kategori, wilayah)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (id_baru, nama, area, kategori, wilayah)
                )

            # ============================================================
            # TAHAP 5: Update referensi ID di tabel lain
            # ============================================================
            print("\nTahap 5/5: Update referensi id_mesin di tabel terkait...")
            total_jadwal = total_riwayat = total_log = 0
            
            # Kita jalankan UPDATE ke tabel referensi TANPA peduli tahap 1 berhasil atau di-skip,
            # untuk menyapu bersih semua sisa data lama yang mungkin tertinggal.
            for id_lama, id_baru, nama, kategori, area, wilayah in id_berubah:
                cur.execute("UPDATE jadwal_pm SET id_mesin = %s WHERE id_mesin = %s", (id_baru, id_lama))
                total_jadwal += cur.rowcount

                cur.execute("UPDATE riwayat_perbaikan SET nama_alat = %s WHERE nama_alat = %s", (id_baru, id_lama))
                total_riwayat += cur.rowcount

                cur.execute("UPDATE log_ai_analysis SET id_mesin = %s WHERE id_mesin = %s", (id_baru, id_lama))
                total_log += cur.rowcount

            print(f"   - jadwal_pm baris terupdate        : {total_jadwal}")
            print(f"   - riwayat_perbaikan baris terupdate: {total_riwayat}")
            print(f"   - log_ai_analysis baris terupdate  : {total_log}")

        conn.commit()
        print("\n============================================================")
        print("🎉 MIGRASI BERHASIL & SUDAH DI-COMMIT!")
        print("============================================================")

    except Exception as e:
        conn.rollback()
        print("\n============================================================")
        print("TERJADI ERROR - SEMUA PERUBAHAN DI-ROLLBACK.")
        print(f"Detail error: {e}")
        print("============================================================")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    main()