-- RainForge Seed Database Script
-- Run after docker-compose up to populate demo data

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- =====================================================
-- INSTALLERS
-- =====================================================

INSERT INTO installers (id, name, company, lat, lng, rpi_score, capacity_available, capacity_max, avg_cost_factor, sla_compliance_pct, jobs_completed, is_blacklisted, cert_level, service_areas, warranty_months, specialization, created_at)
VALUES
  (1, 'Ramesh Kumar', 'AquaTech Solutions', 28.6139, 77.2090, 92.5, 5, 10, 1.0, 96.0, 145, false, 'premium', 'Delhi,Noida,Gurgaon', 24, 'residential', NOW()),
  (2, 'Priya Sharma', 'GreenWater Systems', 28.4595, 77.0266, 78.3, 3, 8, 1.15, 88.5, 67, false, 'certified', 'Gurgaon,Faridabad', 18, 'commercial', NOW()),
  (3, 'Mohammed Ali', 'EcoRain Pvt Ltd', 19.0760, 72.8777, 85.1, 7, 15, 0.95, 92.0, 203, false, 'premium', 'Mumbai,Thane,Navi Mumbai', 24, 'all', NOW()),
  (4, 'Suresh Reddy', 'JalSeva Enterprises', 12.9716, 77.5946, 61.2, 2, 5, 1.25, 75.0, 28, false, 'basic', 'Bangalore,Mysore', 12, 'residential', NOW()),
  (5, 'Lakshmi Devi', 'RainHarvest Co', 17.3850, 78.4867, 88.7, 4, 10, 1.05, 94.5, 112, false, 'certified', 'Hyderabad,Secunderabad', 18, 'all', NOW()),
  (6, 'Vikram Singh', 'AquaSave India', 13.0827, 80.2707, 45.8, 1, 3, 1.40, 65.0, 12, false, 'basic', 'Chennai,Kanchipuram', 12, 'residential', NOW())
ON CONFLICT (id) DO UPDATE SET 
  rpi_score = EXCLUDED.rpi_score,
  capacity_available = EXCLUDED.capacity_available;

-- =====================================================
-- SUBSIDY RULES
-- =====================================================

INSERT INTO subsidy_rules (id, state, scheme_name, subsidy_pct, max_subsidy_inr, eligible_building_types, min_roof_sqm, max_roof_sqm, valid_from, valid_until, source_url)
VALUES
  (1, 'Delhi', 'Delhi Jal Board RWH Scheme', 50, 50000, 'residential,commercial,government', 50, 5000, '2024-01-01', '2025-12-31', 'https://delhijalboard.nic.in'),
  (2, 'Maharashtra', 'Maharashtra RWH Rebate', 35, 75000, 'residential,commercial', 100, 10000, '2024-04-01', '2025-03-31', 'https://mahawater.gov.in'),
  (3, 'Karnataka', 'Bangaluru Jalasiri', 40, 40000, 'residential', 50, 2000, '2024-01-01', '2025-12-31', 'https://bwssb.gov.in'),
  (4, 'Tamil Nadu', 'TN RWH Mandate', 30, 35000, 'residential,commercial,government', 100, 5000, '2024-01-01', '2025-12-31', 'https://tnpwd.gov.in'),
  (5, 'Telangana', 'HMWSSB Green Building', 45, 60000, 'residential,commercial', 75, 3000, '2024-01-01', '2025-12-31', 'https://hyderabadwater.gov.in'),
  (6, 'Rajasthan', 'Mukhyamantri Jal Swavlamban', 60, 100000, 'residential,government', 50, 10000, '2024-01-01', '2025-12-31', 'https://water.rajasthan.gov.in'),
  (7, 'Uttar Pradesh', 'UP RWH Incentive', 25, 25000, 'residential', 100, 2000, '2024-01-01', '2025-12-31', 'https://upjn.org'),
  (8, 'Gujarat', 'Gujarat RWH Policy', 40, 50000, 'residential,commercial,industrial', 100, 5000, '2024-01-01', '2025-12-31', 'https://gwssb.gujarat.gov.in'),
  (9, 'West Bengal', 'WB Jaldapara Scheme', 30, 30000, 'residential', 50, 1500, '2024-01-01', '2025-12-31', 'https://wbphed.gov.in'),
  (10, 'Kerala', 'Kerala RWH Mission', 50, 75000, 'residential,commercial', 50, 5000, '2024-01-01', '2025-12-31', 'https://kwa.kerala.gov.in')
ON CONFLICT (id) DO UPDATE SET 
  subsidy_pct = EXCLUDED.subsidy_pct,
  max_subsidy_inr = EXCLUDED.max_subsidy_inr;

-- =====================================================
-- SAMPLE PROJECTS (Verified, Pending, Fraud cases)
-- =====================================================

INSERT INTO projects (id, site_id, address, lat, lng, roof_area_sqm, roof_material, floors, people, state, city, status, verification_status, installer_id, annual_capture_liters, tank_capacity_liters, total_cost_inr, created_at)
VALUES
  -- Verified projects
  (1, 'SITE-V001', '15 Janpath Road', 28.6139, 77.2090, 150, 'concrete', 2, 5, 'Delhi', 'New Delhi', 'completed', 'verified', 1, 89250, 5000, 42000, '2025-08-15'),
  (2, 'SITE-V002', '22 MG Road Sector 5', 28.4595, 77.0266, 220, 'metal', 3, 8, 'Delhi', 'Gurugram', 'completed', 'verified', 2, 130900, 10000, 68000, '2025-09-01'),
  (3, 'SITE-V003', 'Government School Block A', 28.7041, 77.1025, 500, 'concrete', 2, 100, 'Delhi', 'New Delhi', 'completed', 'verified', 1, 297500, 20000, 125000, '2025-07-20'),
  (4, 'SITE-V004', 'Rajiv Nagar House 12', 28.6280, 77.2197, 100, 'tiles', 1, 4, 'Delhi', 'New Delhi', 'completed', 'verified', 1, 51000, 3000, 28000, '2025-10-10'),
  (5, 'SITE-V005', 'Industrial Estate Unit 7', 28.4089, 77.3178, 800, 'metal', 1, 20, 'Delhi', 'Faridabad', 'completed', 'verified', 2, 408000, 30000, 185000, '2025-06-15'),
  
  -- Pending projects
  (11, 'SITE-P011', 'IT Park Electronic City', 12.8456, 77.6603, 1500, 'metal', 4, 300, 'Karnataka', 'Bangalore', 'in_progress', 'pending', 4, 990000, 50000, 285000, '2026-01-15'),
  (12, 'SITE-P012', 'Government Hospital Wing C', 12.9352, 77.5389, 750, 'concrete', 3, 150, 'Karnataka', 'Bangalore', 'in_progress', 'pending', 4, 495000, 30000, 165000, '2026-01-20'),
  (13, 'SITE-P013', 'Apartment Complex Tower B', 13.0827, 80.2707, 400, 'concrete', 8, 120, 'Tamil Nadu', 'Chennai', 'in_progress', 'pending', 6, 228000, 15000, 98000, '2026-01-18'),
  
  -- Fraud cases
  (16, 'SITE-F016', 'Residential Colony Plot 23', 17.3850, 78.4867, 120, 'concrete', 2, 5, 'Telangana', 'Hyderabad', 'completed', 'rejected', 5, 69600, 5000, 35000, '2025-11-05'),
  (17, 'SITE-F017', 'Software Park Tower A', 17.4300, 78.4512, 900, 'metal', 6, 200, 'Telangana', 'Hyderabad', 'completed', 'rejected', 5, 522000, 35000, 195000, '2025-10-28'),
  (18, 'SITE-F018', 'Municipal School Secunderabad', 17.4399, 78.4983, 350, 'tiles', 2, 150, 'Telangana', 'Hyderabad', 'completed', 'flagged', 5, 203000, 15000, 85000, '2025-12-01'),
  (19, 'SITE-F019', 'Warehouse District 5', 28.5355, 77.3910, 1200, 'metal', 1, 15, 'Delhi', 'Noida', 'completed', 'rejected', 1, 714000, 40000, 210000, '2025-09-22')
ON CONFLICT (id) DO UPDATE SET 
  status = EXCLUDED.status,
  verification_status = EXCLUDED.verification_status;

-- =====================================================
-- FRAUD FLAGS
-- =====================================================

INSERT INTO verification_flags (project_id, flag_type, description, fraud_score, created_at)
VALUES
  (16, 'location_mismatch', 'GPS 600m from project site', 0.8, '2025-11-05'),
  (16, 'photo_reuse', 'Photo hash matches SITE-F019', 1.0, '2025-11-05'),
  (17, 'exif_stripped', 'No EXIF metadata in photos', 0.7, '2025-10-28'),
  (17, 'timestamp_invalid', 'Photo timestamp 72 hours before upload', 0.5, '2025-10-28'),
  (18, 'distance_warning', 'GPS 180m from project site', 0.35, '2025-12-01'),
  (19, 'photo_reuse', 'Photo hash matches SITE-F016', 1.0, '2025-09-22'),
  (19, 'software_edited', 'Photoshop detected in EXIF Software field', 0.6, '2025-09-22')
ON CONFLICT DO NOTHING;

-- =====================================================
-- WARDS (for public dashboard)
-- =====================================================

INSERT INTO wards (id, ward_id, ward_name, city, state, population, area_sqkm, geom, created_at)
VALUES
  (1, 'WARD-001', 'Connaught Place', 'New Delhi', 'Delhi', 45000, 2.8, 
   ST_GeomFromGeoJSON('{"type":"Polygon","coordinates":[[[77.2090,28.6200],[77.2250,28.6200],[77.2250,28.6050],[77.2090,28.6050],[77.2090,28.6200]]]}'), 
   NOW()),
  (2, 'WARD-002', 'Sector 5 Gurugram', 'Gurugram', 'Delhi', 32000, 4.2,
   ST_GeomFromGeoJSON('{"type":"Polygon","coordinates":[[[77.0200,28.4650],[77.0400,28.4650],[77.0400,28.4500],[77.0200,28.4500],[77.0200,28.4650]]]}'),
   NOW()),
  (3, 'WARD-003', 'Koramangala', 'Bangalore', 'Karnataka', 68000, 5.1,
   ST_GeomFromGeoJSON('{"type":"Polygon","coordinates":[[[77.6150,12.9350],[77.6400,12.9350],[77.6400,12.9100],[77.6150,12.9100],[77.6150,12.9350]]]}'),
   NOW())
ON CONFLICT DO NOTHING;

-- =====================================================
-- DEMO USERS
-- =====================================================

INSERT INTO users (id, email, hashed_password, full_name, role, is_active, created_at)
VALUES
  (1, 'admin@rainforge.in', '$2b$12$demo_hashed_password_admin', 'Admin User', 'admin', true, NOW()),
  (2, 'verifier@rainforge.in', '$2b$12$demo_hashed_password_verifier', 'Verifier User', 'verifier', true, NOW()),
  (3, 'installer@rainforge.in', '$2b$12$demo_hashed_password_installer', 'Installer User', 'installer', true, NOW()),
  (4, 'govuser@rainforge.in', '$2b$12$demo_hashed_password_gov', 'Government User', 'gov_user', true, NOW())
ON CONFLICT (email) DO UPDATE SET 
  role = EXCLUDED.role;

-- =====================================================
-- PRINT SUMMARY
-- =====================================================

SELECT 'Seed data loaded successfully!' as message;
SELECT 'Installers:' as entity, COUNT(*) as count FROM installers;
SELECT 'Subsidy Rules:' as entity, COUNT(*) as count FROM subsidy_rules;
SELECT 'Projects:' as entity, COUNT(*) as count FROM projects;
SELECT 'Wards:' as entity, COUNT(*) as count FROM wards;
SELECT 'Users:' as entity, COUNT(*) as count FROM users;
