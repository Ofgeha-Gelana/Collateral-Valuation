# core/calculation_engine.py

from .data_loader import (
    get_building_rates_data, get_component_percentages, 
    get_mapping_by_category, get_fuel_station_rates, get_coffee_site_rates
)

# Load data at the module level
building_rates_data = get_building_rates_data()
component_percentages = get_component_percentages()
fuel_station_rates = get_fuel_station_rates()
coffee_site_rates = get_coffee_site_rates()

# --- NEW: Specialized Calculation Functions ---
def calculate_fuel_station_value(components: dict) -> float:
    """Calculates value based on Fuel Station components."""
    total_value = 0
    total_value += components.get("site_preparation_area", 0) * fuel_station_rates["site_preparation"]
    total_value += components.get("forecourt_area", 0) * fuel_station_rates["reinforced_concrete_forecourt"]
    total_value += components.get("canopy_area", 0) * fuel_station_rates["steel_canopy"]
    total_value += components.get("num_pump_islands", 0) * fuel_station_rates["pump_island"]
    total_value += components.get("num_ugt_30m3", 0) * fuel_station_rates["ugt_30m3"]
    total_value += components.get("num_ugt_50m3", 0) * fuel_station_rates["ugt_50m3"]
    return total_value

def calculate_coffee_site_value(components: dict) -> float:
    """Calculates value based on Coffee Washing Site components."""
    total_value = 0
    total_value += components.get("cherry_hopper_area", 0) * coffee_site_rates["cherry_hopper"]
    total_value += components.get("fermentation_tanks_area", 0) * coffee_site_rates["fermentation_tanks"]
    total_value += components.get("washing_channels_length", 0) * coffee_site_rates["washing_channels"]
    total_value += components.get("coffee_drier_area", 0) * coffee_site_rates["coffee_drier"]
    return total_value

# --- Existing Helper Functions (some are collapsed for brevity) ---
def get_building_grade_rate(building_type: str, grade: str) -> float:
    # ... (function is unchanged)
    for item in building_rates_data:
        if item['Building Type'] == building_type:
            try:
                rate = (item[f'{grade}_Min'] + item[f'{grade}_Max']) / 2
                return rate
            except KeyError:
                return (item['Average_Min'] + item['Average_Max']) / 2
    return 0

def suggest_grade_from_materials(selected_materials: dict, category: str) -> str:
    # ... (function is unchanged)
    quality_scores = {'Excellent': 4, 'Good': 3, 'Average': 2, 'Economy': 1, 'Minimum': 0}
    material_grade_mapping = get_mapping_by_category(category)
    total_score = 0
    count = 0
    for component, material in selected_materials.items():
        if component in material_grade_mapping:
            for material_substring, grade in material_grade_mapping[component].items():
                if material_substring in material:
                    total_score += quality_scores.get(grade, 2)
                    count += 1
                    break
    if count == 0: return "Average"
    avg_score = total_score / count
    if avg_score >= 3.5: return "Excellent"
    if avg_score >= 2.5: return "Good"
    if avg_score >= 1.5: return "Average"
    if avg_score >= 0.5: return "Economy"
    return "Minimum"

def calculate_under_construction_value(full_value: float, building_type: str, grade: str, incomplete_components: list) -> float:
    # ... (function is unchanged)
    total_deduction_percent = 0
    grade_map = {'Excellent': 'Best', 'Good': 'Best', 'Average': 'Avg', 'Economy': 'Poor', 'Minimum': 'Poor'}
    if "Single Story" in building_type: type_key = "Single_Storey"
    elif "G+1" in building_type or "G+2" in building_type: type_key = "G1_G2"
    elif "G+3" in building_type or "G+4" in building_type: type_key = "G3_G4"
    else: type_key = "G1_G2"
    column_key = f"{type_key}_{grade_map.get(grade, 'Avg')}"
    for component in incomplete_components:
        if component in component_percentages.index:
            try:
                deduction = component_percentages.loc[component, column_key]
                total_deduction_percent += deduction
            except KeyError: pass
    completed_percent = 1.0 - total_deduction_percent
    return full_value * completed_percent

def calculate_location_value(town_category: str, use_type: str, plot_grade: str, plot_area: float) -> float:
    # ... (function is unchanged)
    mock_rate_per_m2 = 3000 
    if "Finfinne" in town_category: mock_rate_per_m2 = 15000
    elif "Major Cities" in town_category: mock_rate_per_m2 = 8000
    return mock_rate_per_m2 * plot_area

def calculate_location_value_limit(ccw: float, plot_area: float) -> float:
    # ... (function is unchanged)
    if ccw == 0: return 0
    if plot_area <= 2000:
        return 3.0 * ccw
    elif 2001 <= plot_area <= 10000:
        return (3.5 * ccw) - (ccw * plot_area / 4000)
    else:
        return 1.0 * ccw

# --- Main Valuation Function (Revised) ---
def run_full_valuation(valuation_data: dict) -> dict:
    """
    The main valuation function. Now handles both standard and specialized buildings.
    """
    total_building_cost = 0
    all_suggested_grades = {}
    
    for i, building in enumerate(valuation_data.get('buildings', [])):
        category = building.get('category', 'Multi-Story Building')
        building_cost = 0

        if category in ["Higher Villa", "Multi-Story Building", "MPH & Factory Building"]:
            area = building.get('length', 0) * building.get('width', 0)
            num_floors = building.get('num_floors', 0)
            
            if category == "Higher Villa":
                building_type_for_rate = "Single Story Building (higher Villa)"
            else:
                if 1 <= num_floors <= 2: building_type_for_rate = "G+1 and G+2"
                elif 3 <= num_floors <= 4: building_type_for_rate = "G+3 and G+4"
                else: building_type_for_rate = "G+7 and Above"
            
            suggested_grade = suggest_grade_from_materials(building.get('selected_materials', {}), category)
            all_suggested_grades[f"Building {i+1} ({building.get('name')})"] = suggested_grade
            grade = building.get('confirmed_grade') or suggested_grade
            
            rate = get_building_grade_rate(building_type_for_rate, grade)
            full_replacement_cost = area * (num_floors + 1) * rate
            
            if building.get('is_under_construction', False):
                building_cost = calculate_under_construction_value(full_replacement_cost, building_type_for_rate, grade, building.get('incomplete_components', []))
            else:
                building_cost = full_replacement_cost
        
        elif category == "Fuel Station":
            building_cost = calculate_fuel_station_value(building.get('specialized_components', {}))
        
        elif category == "Coffee Washing Site":
            building_cost = calculate_coffee_site_value(building.get('specialized_components', {}))

        total_building_cost += building_cost

    ccw = total_building_cost
    
    # ... (rest of the function remains the same) ...
    other_costs_details = valuation_data.get('other_costs', {})
    fence_cost = ccw * (other_costs_details.get('fence_percent', 0) / 100)
    septic_cost = ccw * (other_costs_details.get('septic_percent', 0) / 100)
    external_cost = ccw * (other_costs_details.get('external_works_percent', 0) / 100)
    consultancy_fee = ccw * (other_costs_details.get('consultancy_percent', 0) / 100)
    water_tank_cost = other_costs_details.get('water_tank_cost', 0)
    total_other_costs = fence_cost + septic_cost + external_cost + consultancy_fee + water_tank_cost

    property_details = valuation_data.get('property_details', {})
    calculated_lv = calculate_location_value(property_details.get('prop_town', ''), property_details.get('gen_use', ''), property_details.get('plot_grade', ''), property_details.get('plot_area', 0))
    lv_limit = calculate_location_value_limit(ccw, property_details.get('plot_area', 0))
    final_location_value = min(calculated_lv, lv_limit)

    total_market_value = ccw + total_other_costs + final_location_value
    forced_value = total_market_value * 0.8

    return {
        "total_building_cost": ccw,
        "total_other_costs": total_other_costs,
        "calculated_location_value": calculated_lv,
        "location_value_limit": lv_limit,
        "final_applied_location_value": final_location_value,
        "estimated_market_value": total_market_value,
        "estimated_forced_value": forced_value,
        "suggested_grades": all_suggested_grades
    }
