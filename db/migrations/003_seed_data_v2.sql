-- RainForge Seed Data - Subsidy Rules for Demo
-- 3 Sample States: Delhi, Maharashtra, Karnataka

INSERT INTO subsidy_rules (state, scheme_name, scheme_code, subsidy_type, subsidy_percent, max_amount, min_roof_area_sqm, eligibility_json, valid_from, valid_to, is_active, source_url) VALUES
-- Delhi
('Delhi', 'Delhi Jal Board RWH Subsidy', 'DJB-RWH-2024', 'percentage', 50.00, 50000.00, 50, 
 '{"building_types": ["residential", "commercial"], "min_tank_size_l": 1000, "requires_borewell": false}',
 '2024-01-01', '2026-12-31', TRUE, 'https://delhijalboard.gov.in/rwh'),

('Delhi', 'Delhi Development Authority Green Building', 'DDA-GREEN', 'percentage', 30.00, 100000.00, 100,
 '{"building_types": ["commercial", "industrial"], "requires_green_cert": true}',
 '2024-04-01', '2025-12-31', TRUE, 'https://dda.org.in/green-building'),

-- Maharashtra
('Maharashtra', 'Jalyukta Shivar Abhiyan', 'MH-JSA', 'percentage', 60.00, 75000.00, 30,
 '{"building_types": ["residential", "government"], "districts": ["Pune", "Mumbai", "Nagpur", "Nashik"]}',
 '2024-01-01', '2026-03-31', TRUE, 'https://water.maharashtra.gov.in/jsa'),

('Maharashtra', 'MHADA Housing RWH', 'MHADA-RWH', 'fixed', NULL, 25000.00, 25,
 '{"building_types": ["residential"], "requires_society_registration": true}',
 '2024-06-01', '2025-12-31', TRUE, 'https://mhada.gov.in/rwh'),

-- Karnataka
('Karnataka', 'Jal Jeevan Mission - Karnataka', 'KA-JJM', 'percentage', 75.00, 100000.00, 20,
 '{"building_types": ["residential", "government"], "priority_districts": ["Bangalore Urban", "Mysore", "Belgaum"]}',
 '2024-01-01', '2027-03-31', TRUE, 'https://jalshakti-dowr.gov.in/jjm-karnataka'),

('Karnataka', 'BWSSB Rainwater Harvesting', 'BWSSB-RWH', 'tiered', 40.00, 60000.00, 40,
 '{"building_types": ["residential", "commercial"], "city": "Bangalore", "tiered_rates": [{"max_area": 100, "subsidy_pct": 50}, {"max_area": 500, "subsidy_pct": 40}, {"max_area": 99999, "subsidy_pct": 30}]}',
 '2024-01-01', '2025-12-31', TRUE, 'https://bwssb.gov.in/rwh')
ON CONFLICT DO NOTHING;

-- Sample Material Prices
INSERT INTO material_prices (category, item_name, unit, price_per_unit, vendor, state) VALUES
('Tank', 'PVC Tank 1000L', 'unit', 8500.00, 'Sintex', 'All India'),
('Tank', 'PVC Tank 2000L', 'unit', 14000.00, 'Sintex', 'All India'),
('Tank', 'PVC Tank 5000L', 'unit', 28000.00, 'Sintex', 'All India'),
('Tank', 'RCC Tank 5000L', 'unit', 45000.00, 'Local', 'All India'),
('Tank', 'RCC Tank 10000L', 'unit', 75000.00, 'Local', 'All India'),
('Pipes', 'PVC Pipe 4" (per meter)', 'meter', 180.00, 'Supreme', 'All India'),
('Pipes', 'PVC Pipe 6" (per meter)', 'meter', 320.00, 'Supreme', 'All India'),
('Filter', 'First Flush Diverter', 'unit', 2500.00, 'RainMan', 'All India'),
('Filter', 'Sand-Gravel Filter', 'unit', 5500.00, 'Local', 'All India'),
('Filter', 'Commercial Multi-stage Filter', 'unit', 18000.00, 'AquaSafe', 'All India'),
('Gutter', 'PVC Gutter (per meter)', 'meter', 150.00, 'Local', 'All India'),
('Gutter', 'Metal Gutter (per meter)', 'meter', 280.00, 'Local', 'All India'),
('Labour', 'Installation Labour (per day)', 'day', 800.00, 'Local', 'All India'),
('Labour', 'Plumber (per day)', 'day', 600.00, 'Local', 'All India'),
('Recharge', 'Recharge Pit (standard)', 'unit', 15000.00, 'Local', 'All India'),
('Recharge', 'Recharge Well (borewell)', 'unit', 35000.00, 'Local', 'All India')
ON CONFLICT DO NOTHING;

-- Sample Organizations
INSERT INTO organizations (name, type, contact_email, state, city) VALUES
('Delhi Jal Board', 'government', 'contact@djb.gov.in', 'Delhi', 'New Delhi'),
('BWSSB Bangalore', 'government', 'info@bwssb.gov.in', 'Karnataka', 'Bangalore'),
('Maharashtra Water Authority', 'government', 'mwa@maharashtra.gov.in', 'Maharashtra', 'Mumbai'),
('Green Homes Pvt Ltd', 'commercial', 'info@greenhomes.in', 'Karnataka', 'Bangalore'),
('Demo User Org', 'residential', 'demo@rainforge.app', 'Delhi', 'New Delhi')
ON CONFLICT DO NOTHING;

-- Sample Rainfall Data (Delhi - 10 years monthly normals)
INSERT INTO rainfall_data (lat, lng, grid_cell, year, month, rainfall_mm, source) VALUES
-- Delhi coordinates (28.6139, 77.2090)
(28.61, 77.21, 'DELHI_CENTRAL', 2024, 1, 18.5, 'imd'),
(28.61, 77.21, 'DELHI_CENTRAL', 2024, 2, 22.0, 'imd'),
(28.61, 77.21, 'DELHI_CENTRAL', 2024, 3, 15.0, 'imd'),
(28.61, 77.21, 'DELHI_CENTRAL', 2024, 4, 10.0, 'imd'),
(28.61, 77.21, 'DELHI_CENTRAL', 2024, 5, 25.0, 'imd'),
(28.61, 77.21, 'DELHI_CENTRAL', 2024, 6, 85.0, 'imd'),
(28.61, 77.21, 'DELHI_CENTRAL', 2024, 7, 210.0, 'imd'),
(28.61, 77.21, 'DELHI_CENTRAL', 2024, 8, 250.0, 'imd'),
(28.61, 77.21, 'DELHI_CENTRAL', 2024, 9, 125.0, 'imd'),
(28.61, 77.21, 'DELHI_CENTRAL', 2024, 10, 15.0, 'imd'),
(28.61, 77.21, 'DELHI_CENTRAL', 2024, 11, 5.0, 'imd'),
(28.61, 77.21, 'DELHI_CENTRAL', 2024, 12, 10.0, 'imd'),
-- Mumbai coordinates (19.0760, 72.8777)
(19.08, 72.88, 'MUMBAI_CENTRAL', 2024, 1, 2.0, 'imd'),
(19.08, 72.88, 'MUMBAI_CENTRAL', 2024, 2, 1.0, 'imd'),
(19.08, 72.88, 'MUMBAI_CENTRAL', 2024, 3, 0.5, 'imd'),
(19.08, 72.88, 'MUMBAI_CENTRAL', 2024, 4, 2.0, 'imd'),
(19.08, 72.88, 'MUMBAI_CENTRAL', 2024, 5, 20.0, 'imd'),
(19.08, 72.88, 'MUMBAI_CENTRAL', 2024, 6, 520.0, 'imd'),
(19.08, 72.88, 'MUMBAI_CENTRAL', 2024, 7, 840.0, 'imd'),
(19.08, 72.88, 'MUMBAI_CENTRAL', 2024, 8, 550.0, 'imd'),
(19.08, 72.88, 'MUMBAI_CENTRAL', 2024, 9, 320.0, 'imd'),
(19.08, 72.88, 'MUMBAI_CENTRAL', 2024, 10, 75.0, 'imd'),
(19.08, 72.88, 'MUMBAI_CENTRAL', 2024, 11, 15.0, 'imd'),
(19.08, 72.88, 'MUMBAI_CENTRAL', 2024, 12, 3.0, 'imd'),
-- Bangalore coordinates (12.9716, 77.5946)
(12.97, 77.59, 'BANGALORE_CENTRAL', 2024, 1, 5.0, 'imd'),
(12.97, 77.59, 'BANGALORE_CENTRAL', 2024, 2, 8.0, 'imd'),
(12.97, 77.59, 'BANGALORE_CENTRAL', 2024, 3, 12.0, 'imd'),
(12.97, 77.59, 'BANGALORE_CENTRAL', 2024, 4, 45.0, 'imd'),
(12.97, 77.59, 'BANGALORE_CENTRAL', 2024, 5, 115.0, 'imd'),
(12.97, 77.59, 'BANGALORE_CENTRAL', 2024, 6, 85.0, 'imd'),
(12.97, 77.59, 'BANGALORE_CENTRAL', 2024, 7, 110.0, 'imd'),
(12.97, 77.59, 'BANGALORE_CENTRAL', 2024, 8, 140.0, 'imd'),
(12.97, 77.59, 'BANGALORE_CENTRAL', 2024, 9, 195.0, 'imd'),
(12.97, 77.59, 'BANGALORE_CENTRAL', 2024, 10, 175.0, 'imd'),
(12.97, 77.59, 'BANGALORE_CENTRAL', 2024, 11, 60.0, 'imd'),
(12.97, 77.59, 'BANGALORE_CENTRAL', 2024, 12, 15.0, 'imd')
ON CONFLICT DO NOTHING;

SELECT 'Seed data V2 inserted successfully' as result;
