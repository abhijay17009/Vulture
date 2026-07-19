import streamlit as st
import json
import os

# --- ADMIN FRONTEND ENVIRONMENT ONLY ---
st.set_page_config(page_title="Vulture Internal Ops", page_icon="⚙️", layout="wide")

DB_TARGET_PATH = "database.json"
STAGE_MAP = {1: "Ordered", 2: "Shipped", 3: "In Transit", 4: "Delivered"}

def pull_raw_json():
    """Reads directly from disk into admin scope."""
    if os.path.exists(DB_TARGET_PATH):
        try:
            with open(DB_TARGET_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def commit_to_json(data_payload):
    """Overwrites persistent database file layer."""
    with open(DB_TARGET_PATH, "w") as f:
        json.dump(data_payload, f, indent=4)

st.title("🛡️ Vulture Internal Ops Control Panel")
st.caption("Isolated Operational Node — Synchronizations overwrite persistent production JSON variables directly.")
st.markdown("---")

# --- INITIALIZE COHERENT SESSION MEMORY LAYER ---
# Loads disk arrays ONCE into session state so intermediate interactions don't overwrite them
if "admin_db" not in st.session_state:
    st.session_state.admin_db = pull_raw_json()

manipulator_tab, matrix_tab = st.tabs(["🎛️ Pipeline Step Manipulator", "📝 Interactive Data Grid"])

with manipulator_tab:
    st.subheader("Live Order Pipelines")
    if not st.session_state.admin_db:
        st.info("The production JSON file target is currently blank.")
    
    col1, col2 = st.columns(2)
    # Loop through the persistently updating session state memory
    for idx, (oid, details) in enumerate(list(st.session_state.admin_db.items())):
        target_col = col1 if idx % 2 == 0 else col2
        with target_col:
            with st.container(border=True):
                st.markdown(f"### 📦 Admin Control Card: **#{oid}**")
                
                current_step = int(details.get("step", 1))
                
                # Write changes DIRECTLY into session state as soon as interactive components change
                selected_step = st.slider(f"Force Milestone Phase Location", 1, 4, current_step, key=f"slide_{oid}")
                input_loc = st.text_input("Assign Target Facility Location", value=details.get("location", ""), key=f"loc_{oid}")
                input_date = st.text_input("Set Promised Arrival Deadline", value=details.get("delivery_date", ""), key=f"date_{oid}")
                input_carrier = st.text_input("Reroute Strategic Logistics Carrier", value=details.get("carrier", ""), key=f"carr_{oid}")
                
                # Instantly capture and commit structural changes to session state memory block
                st.session_state.admin_db[oid]["step"] = selected_step
                st.session_state.admin_db[oid]["status"] = STAGE_MAP[selected_step]
                st.session_state.admin_db[oid]["location"] = input_loc
                st.session_state.admin_db[oid]["delivery_date"] = input_date
                st.session_state.admin_db[oid]["carrier"] = input_carrier

with matrix_tab:
    st.subheader("Raw Storage Cluster Matrix")
    data_frame_source = []
    for k, v in st.session_state.admin_db.items():
        data_frame_source.append({
            "Order ID": k, "Status": v["status"], "Pipeline Step": v["step"], 
            "Location": v["location"], "Delivery Window": v["delivery_date"], "Logistics Carrier": v["carrier"]
        })
        
    grid_editor_output = st.data_editor(data_frame_source, num_rows="dynamic", key="external_matrix_editor", use_container_width=True)
    
    if st.button("🔄 Format Grid Array to Staging Cache", use_container_width=True):
        rebuilt_staging_map = {}
        for row in grid_editor_output:
            if row.get("Order ID"):
                oid_key = str(row["Order ID"])
                step_idx = int(row.get("Pipeline Step", 1))
                rebuilt_staging_map[oid_key] = {
                    "status": STAGE_MAP.get(step_idx, "Ordered"),
                    "step": step_idx,
                    "location": row.get("Location", "Warehouse Central"),
                    "delivery_date": row.get("Delivery Window", "Pending"),
                    "carrier": row.get("Logistics Carrier", "Internal Fleet")
                }
        # Commit grid configurations instantly to session state
        st.session_state.admin_db = rebuilt_staging_map
        st.toast("Grid adjustments mapped to session memory storage!", icon="🔄")

st.markdown("---")

# Left and right functional system layout triggers
save_col, reload_col = st.columns(2)

with save_col:
    # --- EXECUTE DISK OVERWRITE FUNCTION ---
    if st.button("💾 Broadcast Updates to Production Client (Commit to JSON)", type="primary", use_container_width=True):
        commit_to_json(st.session_state.admin_db)
        st.success("📡 Disk commit operation successful. Shared state pipeline completely synchronized!")
        st.balloons()

with reload_col:
    # --- RESET MECHANICS FOR SAFETY ---
    if st.button("🔄 Discard Cache & Fetch Fresh Production Data", use_container_width=True):
        st.session_state.admin_db = pull_raw_json()
        st.toast("Admin cache refetched clean from production database file!", icon="💾")
        st.rerun()