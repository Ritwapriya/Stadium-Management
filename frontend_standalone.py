import streamlit as st
import random
import time
import pandas as pd
import altair as alt

st.set_page_config(page_title="Smart Stadium AI", layout="wide", page_icon="🏟️")

# CSS
st.markdown("""
<style>
.metric-card { background-color: #1E1E1E; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
.metric-value { font-size: 2rem; font-weight: bold; color: #4CAF50; }
.alert-banner { background-color: #FF5252; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; font-weight: bold; text-align: center; }
.recommendation-box { background-color: #262730; padding: 15px; border-radius: 10px; border-left: 4px solid #4CAF50; }
.queue-item { background-color: #262730; padding: 10px; border-radius: 5px; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# Generate fake data
zones = ['North Gate', 'South Gate', 'East Stand', 'West Stand', 'Food Court']
stalls = ['Food Stall A', 'Food Stall B', 'Food Stall C', 'Merchandise', 'Restroom North', 'Restroom South']
phases = ['PRE', 'LIVE', 'HALFTIME', 'POST']

@st.cache_data(ttl=2)
def generate_data():
    densities = {zone: round(random.uniform(0.3, 0.95), 2) for zone in zones}
    queues = {stall: random.randint(2, 18) for stall in stalls}
    phase = random.choice(phases)
    
    busy_zone = max(densities, key=densities.get)
    less_busy = min(densities, key=densities.get)
    
    return {
        'densities': densities,
        'queues': queues,
        'phase': phase,
        'hotspot': busy_zone,
        'recommendation': f'Go to {less_busy} - Less crowded!',
        'reason': f'{busy_zone} is at {int(densities[busy_zone]*100)}% capacity',
        'confidence': round(random.uniform(0.75, 0.95), 2),
        'alert': 'Long queues at Food Court!' if densities['Food Court'] > 0.8 else None
    }

data = generate_data()

# Header
st.title("🏟️ Smart Stadium Live Dashboard")
st.markdown(f"### Current Phase: `{data['phase']}`")

# Alert
if data['alert']:
    st.markdown(f'<div class="alert-banner">🚨 {data["alert"]}</div>', unsafe_allow_html=True)

# Columns
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("👥 Crowd Density Hotspots")
    df = pd.DataFrame(data['densities'].items(), columns=['Zone', 'Density'])
    chart = alt.Chart(df).mark_bar().encode(
        x='Zone',
        y=alt.Y('Density', scale=alt.Scale(domain=[0, 1])),
        color=alt.Color('Density', scale=alt.Scale(scheme='redyellowgreen', reverse=True, domain=[0, 1]))
    ).properties(height=300)
    st.altair_chart(chart, use_container_width=True)

with col2:
    st.subheader("⏱️ Live Queue Wait Times")
    for stall, wait in data['queues'].items():
        color = "#4CAF50" if wait <= 5 else "#FF9800" if wait <= 10 else "#FF5252"
        st.markdown(f'<div class="queue-item"><span>{stall}</span><span style="float:right;color:{color};font-weight:bold;">{wait} min</span></div>', unsafe_allow_html=True)

st.markdown("---")

col3, col4 = st.columns([1, 1])

with col3:
    st.subheader("🎯 Intelligence & Recommendations")
    st.markdown(f'''
    <div class="recommendation-box">
        <h4>{data["recommendation"]}</h4>
        <p><strong>Reason:</strong> {data["reason"]}</p>
        <p><strong>Confidence:</strong> {int(data["confidence"]*100)}%</p>
        <div style="background:#333;height:10px;border-radius:5px;">
            <div style="background:#4CAF50;width:{int(data["confidence"]*100)}%;height:100%;border-radius:5px;"></div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown("##### Manual Event Trigger")
    pref = st.selectbox("Preference", ["food", "wc", "none"])
    if st.button("Trigger Event"):
        st.success(f"Event triggered: {pref}")

with col4:
    st.subheader("💬 Ask Smart Stadium AI")
    query = st.text_input("Ask about the stadium:")
    if st.button("Ask AI"):
        responses = [
            f"The {data['hotspot']} is currently the busiest area. I recommend going to {min(data['densities'], key=data['densities'].get)} instead.",
            f"Current match phase is {data['phase']}. Average queue time is {sum(data['queues'].values())//len(data['queues'])} minutes.",
            "Based on current crowd density, I suggest entering through South Gate for faster access.",
            f"Food Court has {data['queues']['Food Stall A'] + data['queues']['Food Stall B']} min total wait. Try Food Stall C for shorter lines!"
        ]
        st.write(random.choice(responses))

# Auto refresh
time.sleep(2)
st.rerun()
