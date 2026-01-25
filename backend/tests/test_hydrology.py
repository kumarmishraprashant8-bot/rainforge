import pytest
from app.services.hydrology import HydrologyEngine

def test_runoff_calculation_simple():
    """
    Test Case 1: Simple 100sqm concrete roof, 10mm rain.
    Q = 0.90 (efficiency) * 0.85 (concrete C) * 10 (mm) * 100 (sqm)
    Q = 765 Liters
    """
    area = 100.0
    rain = 10.0
    surface = "concrete"
    
    # Expected: 100 * 10 * 0.85 * 0.90 = 765
    expected = 765.0
    result = HydrologyEngine.calculate_runoff(area, rain, surface)
    
    assert result == expected

def test_runoff_calculation_metal():
    """
    Test Case 2: 50sqm metal roof, 25mm rain.
    Q = 0.90 * 0.90 (metal C) * 25 * 50
    Q = 1012.5 Liters
    """
    result = HydrologyEngine.calculate_runoff(50.0, 25.0, "metal")
    # 50 * 25 * 0.9 * 0.9 = 1012.5
    assert result == 1012.5

def test_yearly_yield_simulation():
    """
    Test Case 3: Yearly yield summing correct months.
    """
    area = 100
    # 12 months of 10mm rain
    monthly_rain = [10.0] * 12
    surface = "concrete"
    
    result = HydrologyEngine.simulate_yearly_yield(area, monthly_rain, surface)
    
    # Each month 765L
    assert len(result["monthly_yield_liters"]) == 12
    assert result["monthly_yield_liters"][0] == 765.0
    assert result["total_yield_liters"] == 765.0 * 12
