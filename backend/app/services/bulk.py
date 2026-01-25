"""
RainForge Bulk Assessment Service
Batch processing for city-scale RWH deployment.
"""

from typing import List, Dict, Optional
import uuid
from datetime import datetime
from app.services.hydrology import HydrologyEngine, ScenarioMode
from app.services.weather import WeatherService


class BulkAssessmentService:
    """
    Service for batch processing multiple RWH assessments.
    Designed for municipal/government-scale deployments.
    """
    
    @staticmethod
    def process_batch(
        sites: List[Dict],
        scenario: ScenarioMode = ScenarioMode.COST_OPTIMIZED,
        batch_name: str = "Unnamed Batch"
    ) -> Dict:
        """
        Process multiple sites in batch.
        
        Args:
            sites: List of dicts with {site_id, address, roof_area_sqm, roof_material, lat, lng}
            scenario: Assessment scenario mode
            batch_name: Name for this batch
        
        Returns:
            Batch results with aggregates and per-site data
        """
        batch_id = str(uuid.uuid4())[:8]
        results = []
        failed = []
        
        total_yield = 0
        total_cost = 0
        total_payback = 0
        
        for site in sites:
            try:
                # Get location-based rainfall
                lat = site.get("lat", 28.6)  # Default Delhi
                lng = site.get("lng", 77.2)
                weather = WeatherService.get_historical_rainfall(lat, lng)
                
                # Calculate yield
                area = site.get("roof_area_sqm", 100)
                material = site.get("roof_material", "concrete")
                
                simulation = HydrologyEngine.simulate_yearly_yield(
                    area_sqm=area,
                    monthly_rainfall=weather["monthly_mm"],
                    surface_type=material,
                    scenario=scenario
                )
                
                storage = HydrologyEngine.calculate_storage_requirement(
                    monthly_yield=simulation["monthly_yield_liters"],
                    daily_demand_liters=500,
                    scenario=scenario
                )
                
                result = {
                    "site_id": site.get("site_id", str(len(results))),
                    "address": site.get("address", "Unknown"),
                    "status": "success",
                    "annual_yield_liters": simulation["total_yield_liters"],
                    "tank_size_liters": storage["recommended_capacity_liters"],
                    "cost_inr": storage["estimated_cost_inr"],
                    "payback_years": storage["payback_years"],
                    "lat": lat,
                    "lng": lng
                }
                
                results.append(result)
                total_yield += simulation["total_yield_liters"]
                total_cost += storage["estimated_cost_inr"]
                total_payback += storage["payback_years"]
                
            except Exception as e:
                failed.append({
                    "site_id": site.get("site_id", "unknown"),
                    "error": str(e)
                })
        
        # Calculate aggregates
        num_success = len(results)
        avg_payback = total_payback / num_success if num_success > 0 else 0
        
        # Generate heatmap data (for visualization)
        heatmap_data = [
            {
                "lat": r["lat"],
                "lng": r["lng"],
                "value": r["annual_yield_liters"],
                "address": r["address"]
            }
            for r in results if r.get("lat") and r.get("lng")
        ]
        
        return {
            "batch_id": batch_id,
            "batch_name": batch_name,
            "created_at": datetime.utcnow().isoformat(),
            "scenario": scenario.value,
            "total_sites": len(sites),
            "processed_sites": num_success,
            "failed_sites": len(failed),
            "total_capture_liters": round(total_yield, 0),
            "total_cost_inr": round(total_cost, 0),
            "avg_payback_years": round(avg_payback, 1),
            "total_beneficiaries": num_success * 4,  # Assume 4 people per site
            "site_results": results,
            "failed_results": failed,
            "heatmap_data": heatmap_data,
            "summary": {
                "water_saved_million_liters": round(total_yield / 1_000_000, 2),
                "investment_lakhs": round(total_cost / 100_000, 2),
                "co2_offset_tons": round(total_yield * 0.0007 / 1000, 2),  # 0.7g CO2 per liter
            }
        }
    
    @staticmethod
    def parse_csv(csv_content: str) -> List[Dict]:
        """
        Parse CSV content into site list.
        Expected columns: site_id, address, roof_area_sqm, roof_material, lat, lng
        """
        lines = csv_content.strip().split("\n")
        if len(lines) < 2:
            return []
        
        headers = [h.strip().lower() for h in lines[0].split(",")]
        sites = []
        
        for line in lines[1:]:
            values = [v.strip() for v in line.split(",")]
            if len(values) >= len(headers):
                site = {}
                for i, header in enumerate(headers):
                    site[header] = values[i]
                
                # Convert numeric fields
                if "roof_area_sqm" in site:
                    try:
                        site["roof_area_sqm"] = float(site["roof_area_sqm"])
                    except:
                        site["roof_area_sqm"] = 100.0
                
                if "lat" in site:
                    try:
                        site["lat"] = float(site["lat"])
                    except:
                        site["lat"] = 28.6
                
                if "lng" in site:
                    try:
                        site["lng"] = float(site["lng"])
                    except:
                        site["lng"] = 77.2
                
                sites.append(site)
        
        return sites
    
    @staticmethod
    def generate_sample_csv() -> str:
        """
        Generate sample CSV template for bulk upload.
        """
        return """site_id,address,roof_area_sqm,roof_material,lat,lng
SITE001,Municipal School Sector 5,250,concrete,28.6139,77.2090
SITE002,Community Hall Block A,180,tiles,28.6150,77.2100
SITE003,Primary Health Center,120,metal,28.6120,77.2080
SITE004,Govt Office Complex,400,concrete,28.6145,77.2095
SITE005,Anganwadi Center,80,tiles,28.6135,77.2075"""
