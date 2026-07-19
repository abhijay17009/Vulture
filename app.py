import streamlit as st
import base64
import json
import os
import io
from google import genai
from google.genai import types

# 1. Page Configuration
st.set_page_config(
    page_title="Vulture CommandCenter", 
    page_icon="🦅", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Theme-Aware & Speed-Optimised CSS Stylesheets
st.markdown("""
<style>
    /* 1. Header & Deploy Button Resets */
    [data-testid="stHeader"] { 
        background-color: transparent !important;
        background: transparent !important;
    }
    .stAppDeployButton { display: none !important; }
    
    /* 2. Sidebar Component Styling */
    [data-testid="stSidebarCollapseButton"] {
        background-color: var(--background-color) !important;
        border: 1px solid var(--secondary-background-color) !important;
        color: var(--text-color) !important;
        border-radius: 4px !important;
        margin-top: 4px !important;
    }
    
    /* 3. Operational Telemetry Cards */
    .metric-card {
        background-color: var(--secondary-background-color);
        border: 1px solid var(--secondary-background-color);
        border-left: 4px solid #1f6feb;
        border-radius: 6px;
        padding: 12px 14px;
        margin-bottom: 12px;
    }
    .metric-label { font-size: 11px; color: var(--text-color); opacity: 0.7; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-value { font-size: 20px; font-weight: bold; color: #1f6feb; margin-top: 2px; }
    .metric-delta { font-size: 11px; color: #3fb950; margin-top: 2px; }
    
    /* 4. Active Logistics Tracking Framework */
    .status-box { 
        padding: 14px; 
        border-radius: 8px; 
        background-color: var(--secondary-background-color); 
        color: var(--text-color);
        border-left: 5px solid #1f6feb; 
        margin: 10px 0; 
    }

    .progress-track {
        background-color: #30363d;
        border-radius: 10px;
        position: relative;
        margin: 15px 0 5px 0;
        height: 8px;
        width: 100%;
    }
    .progress-fill {
        background-color: #1f6feb;
        height: 100%;
        border-radius: 10px;
        transition: width 0.4s ease-in-out;
    }

    /* =====================================================================
       THE GLOBAL CATCH-ALL NUKE: OBLITERATE RED BORDERS EVERYWHERE IN INPUT
       ===================================================================== */
    
    /* Target the chat input block container and EVERY single thing inside it */
    section[data-testid="stChatInputContainer"],
    section[data-testid="stChatInputContainer"] div,
    section[data-testid="stChatInputContainer"] textarea,
    .stChatInput,
    .stChatInput div,
    .stChatInput textarea {
        border-color: #30363d !important;
        box-shadow: none !important;
        outline: none !important;
    }

    /* Keep the layout background matched to your clean dark theme layout */
    [data-testid="stChatInputHoverArea"],
    section[data-testid="stChatInputContainer"] > div {
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        background-color: #0d1117 !important;
    }

    /* Apply a sharp blue ring ONLY when clicking/typing in the box */
    section[data-testid="stChatInputContainer"] div:focus-within,
    section[data-testid="stChatInputContainer"] textarea:focus,
    [data-testid="stChatInputHoverArea"]:focus-within {
        border-color: #1f6feb !important;
        box-shadow: 0 0 0 1px #1f6feb !important;
    }

    .stChatInput {
        padding-bottom: 20px !important;
    }
</style>
""", unsafe_allow_html=True)

# Securely initialize Gemini Client — REPLACE WITH YOUR ACTUAL API KEY
client = genai.Client(api_key="")

# Shared JSON Database File Path Integration
DB_FILE = "database.json"

def read_live_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

# Initialize Local App Session States
if "messages" not in st.session_state: st.session_state.messages = []
if "api_history" not in st.session_state: st.session_state.api_history = []
if "escalated" not in st.session_state: st.session_state.escalated = False
if "analytics_runs" not in st.session_state: st.session_state.analytics_runs = 43
if "faq_click" not in st.session_state: st.session_state.faq_click = None

def check_order_status(order_id: str) -> str:
    order_id = str(order_id).strip()
    live_db = read_live_db()
    if order_id in live_db:
        order = live_db[order_id]
        return f"ORDER_FOUND|{order_id}|{order['status']}|{order['step']}|{order['location']}|{order['delivery_date']}|{order['carrier']}"
    return f"ORDER_NOT_FOUND|{order_id}"

def transfer_to_human(reason: str) -> str:
    return f"PERCH_PROTOCOL_TRIGGERED: {reason}"

system_instruction = (
    "You are Vulture, an advanced AI automated routing node for an enterprise e-commerce platform. "
    "Use cool bird-themed words like 'swoop' and 'perch' subtly, but maintain an elite, efficient tone. "
    "CRITICAL: When searching for an order, use the check_order_status tool. If the tool returns data starting with 'ORDER_FOUND', "
    "extract the details and summarize it naturally for the user. Explicitly mention which carrier is shipping it. "
    "CRITICAL RULE: If the user expresses frustration, anger, or asks for a person, manager, or human, you MUST IMMEDIATELY "
    "call the 'transfer_to_human' tool without trying to resolve it yourself."
)

# 2. Sidebar Panel UI
with st.sidebar:
    st.title("🦅 Vulture Ops Node")
    st.caption("Enterprise AI Router & Automated Helpdesk")
    st.markdown("---")
    
    st.subheader("📊 System Telemetry")
    st.markdown(f'<div class="metric-card" style="border-left: 4px solid #58a6ff;"><div class="metric-label">System API Handshakes</div><div class="metric-value">{st.session_state.analytics_runs} Requests</div><div class="metric-delta">↑ 12.4% Latency Save</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-card" style="border-left: 4px solid #1f6feb;"><div class="metric-label">Autonomous Resolution Rate</div><div class="metric-value">94.2% Ratio</div></div>', unsafe_allow_html=True)
    
    if st.session_state.escalated:
        st.markdown('<div class="metric-card" style="border-left: 4px solid #f85149;"><div class="metric-label">Node Core State</div><div class="metric-value" style="color: #f85149;">ESCALATED</div><div class="metric-delta" style="color: #f85149;">🛡️ Live Specialist Active</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="metric-card" style="border-left: 4px solid #3fb950;"><div class="metric-label">Node Core State</div><div class="metric-value" style="color: #3fb950;">HEALTHY</div><div class="metric-delta">🟢 AI Autonomous Active</div></div>', unsafe_allow_html=True)
        
    st.markdown("---")
    st.subheader("📦 Live Transit Material View")
    st.caption("Read-only view streaming fresh from production JSON core:")
    
    for oid, details in read_live_db().items():
        with st.expander(f"🔹 Order Reference #{oid}"):
            pct = int(details.get('step', 1)) * 25
            st.markdown(f"* **Current Status:** `{details.get('status', 'Ordered')}`")
            st.markdown(f"* **Assigned Carrier:** {details.get('carrier', 'Pending')}")
            st.markdown(f"* **Last Seen At:** {details.get('location', 'Distribution Hub')}")
            st.markdown(f"* **Expected Delivery:** {details.get('delivery_date', 'Calculating...')}")
            st.markdown(f'<div class="progress-track"><div class="progress-fill" style="width: {pct}%;"></div></div><small style="opacity:0.6;">Pipeline Milestone Stage {details.get("step", 1)}/4</small>', unsafe_allow_html=True)
            
    st.markdown("---")
    st.subheader("📬 Submit Console Review")
    with st.expander("Submit Telemetry Overview"):
        fb_user = st.text_input("Name/Email", value="Developer Hub")
        fb_text = st.text_area("Observations Matrix")
        fb_score = st.slider("System Rating Cluster", 1, 5, 5)
        
        if st.button("🚀 Dispatch Telemetry Package", use_container_width=True):
            if fb_text:
                payload = {"client": fb_user, "feedback": fb_text, "rating": fb_score, "system_handshakes": st.session_state.analytics_runs}
                feedback_file = "user_feedback.json"
                existing_entries = []
                if os.path.exists(feedback_file):
                    try:
                        with open(feedback_file, "r") as f:
                            existing_entries = json.load(f)
                    except Exception: pass
                existing_entries.append(payload)
                with open(feedback_file, "w") as f:
                    json.dump(existing_entries, f, indent=4)
                st.success("Telemetry package appended to user_feedback.json!")

# 3. Header Setup
title_col, btn_col = st.columns([3.8, 1.2], gap="medium")
with title_col:
    svg_raw = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path d="M10 35 L25 38 L30 30 L45 35 L50 20 L55 35 L70 30 L75 38 L90 35 L80 55 L70 60 L50 90 L30 60 L20 55 Z" fill="none" stroke="#1f6feb" stroke-width="5" stroke-linejoin="round"/><path d="M42 45 L50 35 L58 45 L50 52 Z" fill="#1f6feb"/></svg>'
    b64_logo = base64.b64encode(svg_raw.encode('utf-8')).decode('utf-8')
    st.markdown(f'<div style="display: flex; align-items: center; gap: 16px; margin-top: 10px;"><img src="data:image/svg+xml;base64,{b64_logo}" width="48" height="48" style="flex-shrink:0;"/><h1 style="margin:0; padding:0; font-size:34px; font-weight:700; letter-spacing:-0.5px;">The Vulture Aviary Control Deck</h1></div>', unsafe_allow_html=True)

with btn_col:
    st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)
    if st.button("🧹 Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.api_history = []
        st.session_state.escalated = False
        st.session_state.faq_click = None
        st.rerun()

st.markdown("---")

# Pre-population sandbox buttons
if not st.session_state.messages:
    st.markdown("### 💡 Welcome to the Sandbox Environment")
    faq_col1, faq_col2 = st.columns(2)
    with faq_col1:
        if st.button("🔍 Check Status: Order #12345", use_container_width=True):
            st.session_state.faq_click = "Check status for order #12345"
        if st.button("📦 Check Status: Order #11122", use_container_width=True):
            st.session_state.faq_click = "Check status for order #11122"
    with faq_col2:
        if st.button("⚡ Test System Human Escalation Protocol", use_container_width=True):
            st.session_state.faq_click = "I'm very upset, transfer me to a real person right now!"
        if st.button("🌐 General Platform Capability Query", use_container_width=True):
            st.session_state.faq_click = "Please outline your core algorithmic processing routing capabilities."
            
    if st.session_state.faq_click:
        user_input_preset = st.session_state.faq_click
        st.session_state.faq_click = None
    else: user_input_preset = None
else: user_input_preset = None

# =====================================================================
# 4 & 5. SPLIT CONSOLE RENDERING VIEW
# =====================================================================

if st.session_state.escalated:
    st.markdown("### 🛠️ Vulture Live Specialist Console")
    st.caption("Internal administrative node override. Customer input channel is locked.")
    st.markdown("---")
    
    for idx, msg in enumerate(st.session_state.messages):
        avatar_choice = "👥" if msg["role"] == "user" else "🦅"
        with st.chat_message(msg["role"], avatar=avatar_choice):
            st.write(msg["text"].split("<button")[0].strip())

    st.markdown("<br>", unsafe_allow_html=True)
    st.error("🛡️ **AUTOMATED ROADSIDE NODE LOCKED:** Session state escalated to Human Override Specialists.")
    
    with st.container(border=True):
        st.subheader("📟 Live Agent Workspace Terminal Connection Active")
        st.info("💡 Use the main communication input field at the bottom of the screen to send specialist directives.")
        
        if st.button("🛡️ Resolve Conflict & Re-engage AI Node", use_container_width=True, type="primary"):
            st.session_state.escalated = False
            st.session_state.messages.append({"role": "assistant", "text": "🔄 [SYSTEM NOTE]: Live specialist cleared the deadlock. Vulture autonomous AI routing matrix online."})
            st.rerun()
else:
    for idx, msg in enumerate(st.session_state.messages):
        avatar_choice = "👥" if msg["role"] == "user" else "🦅"
        with st.chat_message(msg["role"], avatar=avatar_choice):
            display_text = msg["text"].split("<button")[0].strip()
            st.write(display_text)
            
            if "payload" in msg and msg["payload"]["type"] == "order_card":
                live_snap = read_live_db()
                target_id = msg["payload"]["order_id"]
                p = live_snap.get(target_id, {"status": "Unknown", "step": 1, "location": "N/A", "delivery_date": "N/A", "carrier": "N/A"})
                pct_fill = int(p["step"]) * 25
                st.markdown(f'<div class="status-box"><b>📍 Logistics Routing Details — Carrier: {p["carrier"]}</b><br>• Current Status: <b>{p["status"]}</b><br>• Last Seen At: {p["location"]}<br>• Expected Delivery: {p["delivery_date"]}<br><div class="progress-track"><div class="progress-fill" style="width: {pct_fill}%;"></div></div></div>', unsafe_allow_html=True)

# =====================================================================
# 6. UNIVERSAL DYNAMIC ROUTING CHAT INPUT
# =====================================================================
input_placeholder = "Type Specialist Directive Response..." if st.session_state.escalated else "Enter customer prompt..."

user_input = st.chat_input(input_placeholder)
if user_input_preset:
    user_input = user_input_preset

if user_input:
    if st.session_state.escalated:
        st.session_state.messages.append({"role": "assistant", "text": f"👤 [LIVE SPECIALIST]: {user_input}"})
        st.session_state.api_history.append(types.Content(role="model", parts=[types.Part.from_text(text=f"[HUMAN INTERVENTION NOTE]: {user_input}")]))
        st.rerun()
    else:
        st.session_state.analytics_runs += 1
        st.session_state.messages.append({"role": "user", "text": user_input})
        st.session_state.api_history.append(types.Content(role="user", parts=[types.Part.from_text(text=user_input)]))
        
        with st.spinner("Processing through Gemini Neural Engine..."):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=st.session_state.api_history,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        response_modalities=["TEXT"], # FIXED: Force text output modality to prevent the 400 error
                        tools=[
                            types.Tool(
                                function_declarations=[
                                    types.FunctionDeclaration(
                                        name="check_order_status",
                                        description="Queries database for order tracker details.",
                                        parameters=types.Schema(
                                            type="OBJECT",
                                            properties={"order_id": types.Schema(type="STRING", description="The order ID")},
                                            required=["order_id"]
                                        )
                                    ),
                                    types.FunctionDeclaration(
                                        name="transfer_to_human",
                                        description="Triggers live agent escalation.",
                                        parameters=types.Schema(
                                            type="OBJECT",
                                            properties={"reason": types.Schema(type="STRING", description="Reason text")},
                                            required=["reason"]
                                        )
                                    )
                                ]
                            )
                        ]
                    )
                )
                
                if response.function_calls:
                    for function_call in response.function_calls:
                        name = function_call.name
                        args = function_call.args
                        
                        if name == "check_order_status":
                            raw_result = check_order_status(order_id=args["order_id"])
                            st.session_state.api_history.append(response.candidates[0].content)
                            
                            if raw_result.startswith("ORDER_FOUND"):
                                _, oid, status, step, loc, ddate, carrier = raw_result.split("|")
                                vulture_text = f"🦅 Swooping into our aviary logs... I have successfully located material shipment #{oid}.\n\nYour package is currently **{status}** at the **{loc}** hub and is being handled via **{carrier}**. Delivery is expected **{ddate}**."
                                
                                st.session_state.api_history.append(types.Content(role="tool", parts=[types.Part.from_function_response(name=name, response={"result": raw_result})]))
                                st.session_state.api_history.append(types.Content(role="model", parts=[types.Part.from_text(text=vulture_text)]))
                                
                                msg_payload = {"type": "order_card", "order_id": oid}
                                st.session_state.messages.append({"role": "assistant", "text": vulture_text, "payload": msg_payload})
                            else:
                                st.session_state.api_history.append(types.Content(role="tool", parts=[types.Part.from_function_response(name=name, response={"result": "Order not found."})]))
                                vulture_text = "🦅 I have combed through our transit tracking database, but it looks like that order number hasn't landed in our system yet."
                                st.session_state.api_history.append(types.Content(role="model", parts=[types.Part.from_text(text=vulture_text)]))
                                st.session_state.messages.append({"role": "assistant", "text": vulture_text})
                                
                        elif name == "transfer_to_human":
                            escalation_reason = args.get("reason", "Customer requested direct support.")
                            handover_text = f"🚨 **System Escalation Protocol Active:** *{escalation_reason}*\n\nReassigning terminal context to a Live Support Specialist..."
                            
                            st.session_state.api_history.append(response.candidates[0].content)
                            st.session_state.api_history.append(types.Content(role="tool", parts=[types.Part.from_function_response(name=name, response={"result": "Transfer initialization success."})]))
                            st.session_state.messages.append({"role": "assistant", "text": handover_text})
                            st.session_state.escalated = True
                    st.rerun()
                else:
                    st.session_state.api_history.append(response.candidates[0].content)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "text": response.text if response.text else ""
                    })
                    st.rerun()
                    
            except Exception as e:
                if "503" in str(e) or "UNAVAILABLE" in str(e):
                    st.warning("⚠️ Neural Engine Busy. Tap Enter to resubmit.")
                else:
                    st.error(f"Pipeline error: {e}")