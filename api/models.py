# api/models.py

from pydantic import BaseModel
from typing import List, Optional, Dict

class Building(BaseModel):
    name: str
    category: str # "Higher Villa", "Multi-Story Building", "Fuel Station", etc.
    
    # Fields for standard buildings
    length: Optional[float] = None
    width: Optional[float] = None
    num_floors: Optional[int] = None
    selected_materials: Optional[Dict[str, str]] = None
    confirmed_grade: Optional[str] = None
    is_under_construction: Optional[bool] = False
    incomplete_components: Optional[List[str]] = []

    # Fields for specialized buildings
    specialized_components: Optional[Dict[str, float]] = None

class OtherCosts(BaseModel):
    fence_percent: int
    septic_percent: int
    external_works_percent: int
    consultancy_percent: int
    water_tank_cost: float

class PropertyDetails(BaseModel):
    plot_area: float
    prop_town: str
    gen_use: str
    plot_grade: str

class ValuationRequest(BaseModel):
    buildings: List[Building]
    property_details: PropertyDetails
    other_costs: OtherCosts

class ValuationResponse(BaseModel):
    total_building_cost: float
    total_other_costs: float
    calculated_location_value: float
    location_value_limit: float
    final_applied_location_value: float
    estimated_market_value: float
    estimated_forced_value: float
    suggested_grades: Dict[str, str]
