-- RainForge Demo Seed Data
-- Populates 10 installers and 30 demo jobs for testing

-- ============================================================
-- INSTALLERS (10)
-- ============================================================

INSERT INTO installers (id, name, company, phone, email, lat, lng, rpi_score, capacity_estimate, cert_level, sla_compliance_pct) VALUES
(1, 'Jal Mitra Solutions', 'Jal Mitra Pvt Ltd', '9811234567', 'contact@jalmitra.in', 28.6139, 77.2090, 92.5, 8, 'advanced', 95.0),
(2, 'AquaSave India', 'AquaSave Technologies', '9822345678', 'info@aquasave.in', 28.5355, 77.3910, 85.0, 5, 'certified', 88.0),
(3, 'RainCatch Delhi', 'RainCatch Services', '9833456789', 'hello@raincatch.in', 28.7041, 77.1025, 78.5, 10, 'basic', 82.0),
(4, 'EcoWater Systems', 'EcoWater Pvt Ltd', '9844567890', 'support@ecowater.in', 28.4595, 77.0266, 88.0, 3, 'master', 91.0),
(5, 'Varsha RWH', 'Varsha Enterprises', '9855678901', 'contact@varsharhw.in', 28.6692, 77.4538, 70.0, 7, 'basic', 75.0),
(6, 'BlueDrop Tech', 'BlueDrop Technologies', '9866789012', 'sales@bluedrop.in', 28.5672, 77.3219, 95.0, 2, 'master', 98.0),
(7, 'Monsoon Masters', 'Monsoon RWH Solutions', '9877890123', 'info@monsoonmasters.in', 28.6304, 77.2177, 82.0, 6, 'certified', 85.0),
(8, 'Jaldhara Services', 'Jaldhara Water Solutions', '9888901234', 'help@jaldhara.in', 28.4089, 77.3178, 65.0, 9, 'basic', 70.0),
(9, 'AquaTech Pro', 'AquaTech Professional', '9899012345', 'pro@aquatech.in', 28.7271, 77.0946, 90.0, 4, 'advanced', 92.0),
(10, 'HarvestRain Co', 'HarvestRain Company', '9800123456', 'contact@harvestrain.in', 28.5921, 77.2290, 75.5, 5, 'certified', 80.0)
ON CONFLICT (id) DO UPDATE SET
    rpi_score = EXCLUDED.rpi_score,
    capacity_estimate = EXCLUDED.capacity_estimate,
    cert_level = EXCLUDED.cert_level,
    sla_compliance_pct = EXCLUDED.sla_compliance_pct;

-- ============================================================
-- JOBS (30)
-- ============================================================

INSERT INTO jobs (id, address, lat, lng, roof_area_sqm, tank_size_liters, estimated_cost_inr, status, allocation_mode, assigned_installer_id) VALUES
-- Completed installations
(101, 'Govt Primary School, Sector 5, Noida', 28.5355, 77.3910, 150, 15000, 96000, 'completed', 'gov_optimized', 1),
(102, 'Community Hall Block A, Rohini', 28.7041, 77.1025, 200, 20000, 125000, 'completed', 'gov_optimized', 2),
(103, 'Primary Health Center, Dwarka', 28.5921, 77.0266, 100, 10000, 65000, 'completed', 'user_choice', 3),
(104, 'Municipal Office Complex, Lajpat Nagar', 28.5672, 77.2431, 300, 30000, 185000, 'completed', 'gov_optimized', 4),
(105, 'Anganwadi Center Ward 7', 28.6304, 77.2177, 80, 8000, 52000, 'completed', 'equitable', 5),
(106, 'Public Library, Connaught Place', 28.6315, 77.2167, 180, 18000, 115000, 'completed', 'gov_optimized', 6),
(107, 'Govt Girls School, Karol Bagh', 28.6519, 77.1910, 170, 17000, 108000, 'completed', 'user_choice', 7),
(108, 'Sports Complex, Mayur Vihar', 28.6072, 77.2933, 250, 25000, 155000, 'completed', 'gov_optimized', 1),
(109, 'Ration Shop, Shahdara', 28.6731, 77.2879, 60, 6000, 42000, 'completed', 'equitable', 8),
(110, 'Police Station, Vasant Kunj', 28.5200, 77.1600, 140, 14000, 90000, 'completed', 'gov_optimized', 9),

-- In progress
(111, 'Fire Station, Okhla', 28.5300, 77.2700, 160, 16000, 102000, 'in_progress', 'gov_optimized', 2),
(112, 'Post Office, Saket', 28.5200, 77.2100, 90, 9000, 58000, 'in_progress', 'user_choice', 10),
(113, 'Govt Hospital Annex, RK Puram', 28.5600, 77.1800, 220, 22000, 140000, 'in_progress', 'gov_optimized', 4),
(114, 'Bus Depot, Narela', 28.8500, 77.0900, 350, 35000, 215000, 'in_progress', 'gov_optimized', 1),
(115, 'Community Center, Janakpuri', 28.6200, 77.0800, 130, 13000, 84000, 'in_progress', 'equitable', 3),

-- Pending allocation (open for bids)
(116, 'New School Building, Najafgarh', 28.6100, 76.9800, 180, 18000, 115000, 'pending', 'gov_optimized', NULL),
(117, 'Water Treatment Plant Office, Hauz Khas', 28.5500, 77.2000, 110, 11000, 72000, 'pending', 'user_choice', NULL),
(118, 'Skill Development Center, Pitampura', 28.6900, 77.1300, 200, 20000, 128000, 'pending', 'gov_optimized', NULL),
(119, 'Senior Citizen Home, Model Town', 28.7100, 77.1900, 95, 9500, 62000, 'pending', 'equitable', NULL),
(120, 'Public Toilet Complex, Chandni Chowk', 28.6500, 77.2300, 50, 5000, 35000, 'pending', 'gov_optimized', NULL),

-- Future (planned)
(121, 'Govt College, Kalkaji', 28.5400, 77.2500, 400, 40000, 250000, 'planned', 'gov_optimized', NULL),
(122, 'Metro Station Annex, Huda City', 28.4600, 77.0700, 150, 15000, 96000, 'planned', 'user_choice', NULL),
(123, 'District Court Complex, Sadar', 28.6400, 77.2100, 280, 28000, 175000, 'planned', 'gov_optimized', NULL),
(124, 'IT Park Office, Noida Sec 62', 28.6200, 77.3600, 320, 32000, 198000, 'planned', 'gov_optimized', NULL),
(125, 'Convention Center, Pragati Maidan', 28.6200, 77.2500, 500, 50000, 310000, 'planned', 'gov_optimized', NULL),

-- Verification pending
(126, 'Recycling Center, Ghazipur', 28.6300, 77.3200, 180, 18000, 115000, 'verification_pending', 'gov_optimized', 7),
(127, 'Industrial Training Institute, Okhla', 28.5500, 77.2800, 240, 24000, 150000, 'verification_pending', 'user_choice', 5),
(128, 'Mandi Complex, Azadpur', 28.7000, 77.1700, 300, 30000, 185000, 'verification_pending', 'equitable', 9),

-- Issues flagged
(129, 'Cold Storage Facility, Tikri Border', 28.7500, 76.9000, 450, 45000, 280000, 'issue_flagged', 'gov_optimized', 8),
(130, 'Warehouse Complex, Mundka', 28.6800, 77.0200, 380, 38000, 235000, 'issue_flagged', 'user_choice', 10)
ON CONFLICT (id) DO UPDATE SET
    status = EXCLUDED.status,
    allocation_mode = EXCLUDED.allocation_mode,
    assigned_installer_id = EXCLUDED.assigned_installer_id;

-- ============================================================
-- SAMPLE VERIFICATIONS
-- ============================================================

INSERT INTO verifications (id, job_id, installer_id, photo_url, geo_lat, geo_lng, expected_lat, expected_lng, geo_distance_m, status, fraud_risk_score) VALUES
('VER-001', 101, 1, 'https://storage.rainforge.in/ver/101_final.jpg', 28.5355, 77.3910, 28.5355, 77.3910, 5.2, 'approved', 0),
('VER-002', 102, 2, 'https://storage.rainforge.in/ver/102_final.jpg', 28.7041, 77.1025, 28.7041, 77.1025, 8.1, 'approved', 0),
('VER-003', 126, 7, 'https://storage.rainforge.in/ver/126_final.jpg', 28.6310, 77.3210, 28.6300, 77.3200, 142.5, 'pending', 35.0),
('VER-004', 127, 5, 'https://storage.rainforge.in/ver/127_final.jpg', 28.5500, 77.2800, 28.5500, 77.2800, 3.2, 'pending', 5.0),
('VER-005', 129, 8, 'https://storage.rainforge.in/ver/129_final.jpg', 28.7600, 76.8900, 28.7500, 76.9000, 1520.0, 'flagged', 85.0)
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- SAMPLE PAYMENTS
-- ============================================================

INSERT INTO payments (id, job_id, total_amount, escrow_amount, released_amount, status) VALUES
('PAY-001', 101, 96000, 0, 96000, 'released'),
('PAY-002', 102, 125000, 0, 125000, 'released'),
('PAY-003', 111, 102000, 61200, 40800, 'partial_released'),
('PAY-004', 116, 115000, 115000, 0, 'escrow')
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- SAMPLE RPI HISTORY
-- ============================================================

INSERT INTO rpi_history (installer_id, rpi_score, components) VALUES
(1, 92.5, '{"design_match": 95, "yield_accuracy": 91, "timeliness": 94, "complaint_rate": 2, "maintenance": 96}'),
(2, 85.0, '{"design_match": 88, "yield_accuracy": 84, "timeliness": 82, "complaint_rate": 5, "maintenance": 90}'),
(6, 95.0, '{"design_match": 97, "yield_accuracy": 94, "timeliness": 96, "complaint_rate": 1, "maintenance": 98}'),
(8, 65.0, '{"design_match": 70, "yield_accuracy": 62, "timeliness": 68, "complaint_rate": 12, "maintenance": 70}')
ON CONFLICT DO NOTHING;

-- Done
SELECT 'Demo data seeded: 10 installers, 30 jobs' as result;
