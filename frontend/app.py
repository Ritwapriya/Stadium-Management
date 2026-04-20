import streamlit as st
import asyncio
import websockets
import json
import requests
import pandas as pd
import altair as alt
import threading
from queue import Queue
import time

import os

# Configuration
API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
WS_URL = os.getenv("WS_URL", API_URL.replace("http", "ws") + "/ws/live")

st.set_page_config(page_title="Smart Stadium AI", layout="wide", page_icon="🏟️")

# --- Custom CSS for Styling ---
st.markdown("""
<style>
    .metric-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #4CAF50;
    }
    .metric-label {
        color: #888;
        text-transform: uppercase;
        font-size: 0.8rem;
    }
    .alert-banner {
        background-color: #FF5252;
        color: white;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
        font-weight: bold;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- State Management ---
if 'live_data' not in st.session_state:
    st.session_state.live_data = {
        'crowd': {},
        'queue': {},
        'recommendations': {},
        'plan': {}
    }

# Sync fetching context for initial load/fallback
def fetch_full_context():
    try:
        response = requests.get(f"{API_URL}/context/")
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return {}

# WebSocket thread payload queue
ws_queue = Queue()

def start_websocket_sync():
    async def run_ws():
        while True:
            try:
                async with websockets.connect(WS_URL) as ws:
                    while True:
                        msg = await ws.recv()
                        ws_queue.put(json.loads(msg))
            except Exception as e:
                # Reconnect after error
                await asyncio.sleep(2)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_ws())

if 'ws_thread_started' not in st.session_state:
    thread = threading.Thread(target=start_websocket_sync, daemon=True)
    thread.start()
    st.session_state.ws_thread_started = True

# Process queued messages
while not ws_queue.empty():
    msg = ws_queue.get()
    topic = msg.get("topic")
    data = msg.get("data")
    
    if topic == "crowd.density":
        st.session_state.live_data['crowd'] = data
    elif topic == "queue.predictions":
        st.session_state.live_data['queue'] = data
    elif topic == "recommendations":
        st.session_state.live_data['recommendations'] = data
    elif topic == "plan.update":
        st.session_state.live_data['plan'] = data


# Layout
st.title("🏟️ Smart Stadium Live Dashboard")

context = fetch_full_context()
match_phase = context.get("match_phase", "UNKNOWN")

st.markdown(f"### Current Phase: `{match_phase}`")

# 1. Staff Alerts
recommendations = st.session_state.live_data.get('recommendations', {})
staff_alert = recommendations.get('staff_alert')
if staff_alert:
    st.markdown(f'<div class="alert-banner">🚨 ACTION REQUIRED: {staff_alert}</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("👥 Crowd Density Hotspots")
    crowd_data = st.session_state.live_data.get('crowd', {})
    densities = crowd_data.get('zone_densities', {})
    
    if densities:
        df = pd.DataFrame(densities.items(), columns=['Zone', 'Density'])
        chart = alt.Chart(df).mark_bar().encode(
            x='Zone',
            y='Density',
            color=alt.Color('Density', scale=alt.Scale(scheme='redyellowgreen', reverse=True))
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("Waiting for crowd sensor data...")

with col2:
    st.subheader("⏱️ Live Queue Wait Times")
    queue_data = st.session_state.live_data.get('queue', {})
    wait_times = queue_data.get('wait_times', {})
    
    if wait_times:
        for stall, wait in wait_times.items():
            color = "green" if wait <= 5 else "orange" if wait <= 10 else "red"
            st.markdown(f"""
            <div style="background-color: #262730; padding: 10px; border-radius: 5px; margin-bottom: 5px; display: flex; justify-content: space-between;">
                <span>{stall}</span>
                <span style="color: {color}; font-weight: bold;">{wait} min</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Waiting for queue data...")

st.markdown("---")

col3, col4 = st.columns([1, 1])

with col3:
    st.subheader("🎯 Intelligence & Recommendations")
    
    if recommendations:
        conf = int(recommendations.get('confidence', 0) * 100)
        st.markdown(f"""
        <div class="metric-card">
            <h4>{recommendations.get('action', 'Waiting for events...')}</h4>
            <br/>
            <p><strong>Reason:</strong> {recommendations.get('reason', 'N/A')}</p>
            <p><strong>Confidence:</strong> {conf}%</p>
            <progress value="{recommendations.get('confidence', 0)}" max="1" style="width:100%;"></progress>
        </div>
        """, unsafe_allow_html=True)
    else:
         st.info("Waiting for recommendations...")
    
    st.markdown("##### Manual Event Trigger")
    pref = st.selectbox("Preference", ["food", "wc", "none"])
    if st.button("Trigger Recommendation Event"):
        requests.post(f"{API_URL}/recommend/", json={"user_id": "demo_user", "preference": pref, "location": "demo_zone"})
        st.success(f"Dispatched '{pref}' event")

with col4:
    st.subheader("💬 Ask Smart Stadium AI")
    query = st.text_input("Ask about the current situation:")
    if st.button("Query AI"):
        with st.spinner("AI is thinking..."):
            try:
                res = requests.post(f"{API_URL}/chat/ask", json={"query": query})
                if res.status_code == 200:
                    st.write(res.json().get('response'))
                else:
                    st.error("Chat Agent unavailable")
            except Exception:
                st.error("Error connecting to Chat Agent")

# Auto-refresh
time.sleep(2)
st.rerun()
