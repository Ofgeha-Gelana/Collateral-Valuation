import streamlit as st
import requests
import pandas as pd

# --- Configuration ---
API_URL = "http://127.0.0.1:8000/estimate"

# --- Data for UI ---
# In a real app, this would be fetched from an API endpoint
def get_materials_by_category(category: str):
    villa_and_multi_story = {
        "Foundation": ["RC, Best workmanship", "RC, Good workmanship", "RC, Stone Masonry", "Stone Masonry"],
        "Roofing": ["Decra, RC, EGA & similar tiles", "CIS G 28, CIS G 32, GQ", "CIS G32", "CIS G 32 & 35"],
        "Metal Work": ["Aluminum profile", "Aluminum imitation", "LTZ"],
        "Floor": ["Granite, Marble, ceramic, parquet, porcelain", "Parquet, Ceramic, All GQ", "PVC, Terrazzo, Cement tiles", "Cement tiles, Sc."],
        "Ceiling": ["Gypsum, PVC, Parquet", "Good quality gypsum, PVC", "Chip wood, Hard Board, Ply wood", "Abujidi"],
        "Sanitary": ["Jacuzzi, Steam, Sauna", "Good quality HWB, WC etc.", "Shower, HWB, WC (all MQ)", "Dry latrine, Turkish seat"]
    }
    mph_factory = {
        "Foundation": ["RC, Best workmanship", "RC, Good workmanship", "RC, Stone Masonry", "Stone Masonry"],
        "Structure": ["RC, Steel Structure, Best workmanship", "RC, Steel Structure, Good workmanship", "RC, (Average)", "RC, Wooden structure"],
        "Roofing": ["EGA on steel, RC Slab", "CIS G 28, CIS G 32, on steel GQ", "CIS G32 on wood (Average)", "CIS G 32 & 35 on wood"],
        "Metal Work": ["Al. Pro, Al imitation", "Al imitation LTZ", "LTZ"],
        "Floor": ["Best quality, Epoxy, Ceramic, PVC, marble, granite", "Good quality Cement Tiles/Screed, PVC, Terrazzo", "Cement screed Average)", "Sc."],
    }
    if category == "Higher Villa" or category == "Multi-Story Building":
        return villa_and_multi_story
    elif category == "MPH & Factory Building":
        return mph_factory
    return {}

COMPONENT_PERCENTAGES_LIST = ['Sub Structure', 'Super Structure', 'Block work- Internal', 'Block work- External', 'Roofing', 'Joinery', 'Metal Work', 'Floor finish', 'Wall finish - Internal', 'Wall finish - External', 'Ceiling works', 'Hand rail and Balustrade', 'Sanitary Work', 'Electrical Work']

# --- UI Functions for Forms ---
def standard_building_form(building_number, category):
    building_key = f"building_{building_number}"
    col1, col2 = st.columns(2)
    with col1:
        st.number_input("Length (m)", min_value=0.0, format="%.2f", key=f"length_{building_key}")
        st.number_input("Width (m)", min_value=0.0, format="%.2f", key=f"width_{building_key}")
        st.number_input("Number of Floors (G+)", min_value=0, key=f"floors_{building_key}")
    with col2:
        material_options = get_materials_by_category(category)
        with st.expander(f"Select Materials for: {category}"):
            for component, options in material_options.items():
                st.selectbox(component, options, key=f"mat_{component.replace(' ', '_')}_{building_key}")

def fuel_station_form(building_number):
    building_key = f"building_{building_number}"
    st.info("Enter the quantities for each component of the Fuel Station.")
    c1, c2 = st.columns(2)
    with c1:
        st.number_input("Site Preparation Area (m²)", min_value=0.0, key=f"fs_site_preparation_area_{building_key}")
        st.number_input("Reinforced Concrete Forecourt Area (m²)", min_value=0.0, key=f"fs_forecourt_area_{building_key}")
        st.number_input("Steel Canopy Area (m²)", min_value=0.0, key=f"fs_canopy_area_{building_key}")
    with c2:
        st.number_input("Number of Pump Islands", min_value=0, step=1, key=f"fs_num_pump_islands_{building_key}")
        st.number_input("Number of UGTs (30.0 m³)", min_value=0, step=1, key=f"fs_num_ugt_30m3_{building_key}")
        st.number_input("Number of UGTs (50.0 m³)", min_value=0, step=1, key=f"fs_num_ugt_50m3_{building_key}")

def coffee_site_form(building_number):
    building_key = f"building_{building_number}"
    st.info("Enter the quantities for each component of the Coffee Washing Site.")
    c1, c2 = st.columns(2)
    with c1:
        st.number_input("Cherry Hopper Area (m²)", min_value=0.0, key=f"cs_cherry_hopper_area_{building_key}")
        st.number_input("Fermentation & Soak Tanks Area (m²)", min_value=0.0, key=f"cs_fermentation_tanks_area_{building_key}")
    with c2:
        st.number_input("Washing & Grading Channels Length (ml)", min_value=0.0, key=f"cs_washing_channels_length_{building_key}")
        st.number_input("Coffee Drier Area (m²)", min_value=0.0, key=f"cs_coffee_drier_area_{building_key}")

# --- Main App UI ---
st.set_page_config(page_title="Professional Valuation App", layout="wide")
st.title("Professional Property Valuation System")

with st.form("valuation_form"):
    # ... (Property details and other costs sections remain the same) ...
    st.header("Property & Building Details")
    st.subheader("Property Location & Neighborhood")
    col1, col2, col3 = st.columns(3)
    with col1:
        plot_area = st.number_input("Plot Area (m2)", min_value=0.0, format="%.2f", value=200.0)
    with col2:
        prop_town = st.selectbox("Property Town/Area:", ['Finfinne Border A1', 'Surrounding Finfinne B1', 'Major Cities C1', 'Major Cities C2'])
        plot_grade = st.selectbox("Plot Grade:", ['1st', '2nd', '3rd', '4th'])
    with col3:
        gen_use = st.selectbox("General Use:", ["Residential", "Commercial", "Industrial"])

    st.subheader("Other Costs (as per manual)")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        fence_percent = st.slider("Fence & Compound Work %", 0, 10, 5)
    with c2:
        septic_percent = st.slider("Septic Tank %", 0, 3, 2)
    with c3:
        external_works_percent = st.slider("External Works %", 0, 3, 2)
    with c4:
        consultancy_percent = st.slider("Consultancy Fee %", 0, 3, 3)
    water_tank_cost = st.number_input("Water Tank Cost (Birr)", min_value=0.0, format="%.2f", value=15508.0)
    
    st.markdown("---")
    st.subheader("Building Details")
    num_buildings = st.number_input("How many buildings are on the property?", min_value=1, value=1, step=1, key="num_buildings")
    for i in range(num_buildings):
        i_key = i + 1
        st.markdown(f"---")
        st.text_input("Building Name/Description", f"Building {i_key}", key=f"name_building_{i_key}")
        category = st.selectbox("Building Category", ["Higher Villa", "Multi-Story Building", "MPH & Factory Building", "Fuel Station", "Coffee Washing Site"], key=f"category_building_{i_key}")

        if category in ["Higher Villa", "Multi-Story Building", "MPH & Factory Building"]:
            standard_building_form(i_key, category)
            st.selectbox("Confirm or Override Suggested Grade:", ["Excellent", "Good", "Average", "Economy", "Minimum"], key=f"confirmed_grade_building_{i_key}")
        elif category == "Fuel Station":
            fuel_station_form(i_key)
        elif category == "Coffee Washing Site":
            coffee_site_form(i_key)
        
    submitted = st.form_submit_button("Calculate Valuation")

if submitted:
    buildings_payload = []
    for i in range(num_buildings):
        i_key = i + 1
        category = st.session_state[f"category_building_{i_key}"]
        building_data = {"name": st.session_state[f"name_building_{i_key}"], "category": category}

        if category in ["Higher Villa", "Multi-Story Building", "MPH & Factory Building"]:
            material_options = get_materials_by_category(category)
            selected_mats = {}
            for component in material_options.keys():
                selected_mats[component] = st.session_state[f"mat_{component.replace(' ', '_')}_building_{i_key}"]
            
            building_data.update({
                "length": st.session_state[f"length_building_{i_key}"],
                "width": st.session_state[f"width_building_{i_key}"],
                "num_floors": st.session_state[f"floors_building_{i_key}"],
                "selected_materials": selected_mats,
                "confirmed_grade": st.session_state[f"confirmed_grade_building_{i_key}"],
                "is_under_construction": st.session_state.get(f"uc_building_{i_key}", False),
                "incomplete_components": st.session_state.get(f"incomplete_building_{i_key}", [])
            })
        elif category == "Fuel Station":
            building_data["specialized_components"] = {
                "site_preparation_area": st.session_state[f"fs_site_preparation_area_building_{i_key}"],
                "forecourt_area": st.session_state[f"fs_forecourt_area_building_{i_key}"],
                "canopy_area": st.session_state[f"fs_canopy_area_building_{i_key}"],
                "num_pump_islands": st.session_state[f"fs_num_pump_islands_building_{i_key}"],
                "num_ugt_30m3": st.session_state[f"fs_num_ugt_30m3_building_{i_key}"],
                "num_ugt_50m3": st.session_state[f"fs_num_ugt_50m3_building_{i_key}"]
            }
        elif category == "Coffee Washing Site":
            building_data["specialized_components"] = {
                "cherry_hopper_area": st.session_state[f"cs_cherry_hopper_area_building_{i_key}"],
                "fermentation_tanks_area": st.session_state[f"cs_fermentation_tanks_area_building_{i_key}"],
                "washing_channels_length": st.session_state[f"cs_washing_channels_length_building_{i_key}"],
                "coffee_drier_area": st.session_state[f"cs_coffee_drier_area_building_{i_key}"]
            }
        buildings_payload.append(building_data)

    request_payload = {
        "buildings": buildings_payload,
        "property_details": { "plot_area": plot_area, "prop_town": prop_town, "gen_use": gen_use, "plot_grade": plot_grade },
        "other_costs": { "fence_percent": fence_percent, "septic_percent": septic_percent, "external_works_percent": external_works_percent, "consultancy_percent": consultancy_percent, "water_tank_cost": water_tank_cost }
    }

    try:
        with st.spinner("Calculating..."):
            response = requests.post(API_URL, json=request_payload)
            response.raise_for_status()
            results = response.json()

            st.header("Valuation Summary & Report")
            for building_name, grade in results['suggested_grades'].items():
                st.info(f"System Suggested Grade for **{building_name}**: **{grade}**")
            
            # ... (Display logic remains the same) ...

    except requests.exceptions.RequestException as e:
        st.error(f"Could not connect to the Valuation API. Please ensure the API is running. Error: {e}")
