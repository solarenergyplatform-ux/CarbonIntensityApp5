import streamlit as st
import requests
import pandas as pd
import altair as alt
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

BASE_URL = "https://api.carbonintensity.org.uk"
headers = {"Accept": "application/json"}

# ----------- API Calls -----------
def get_today_intensity():
    """Fetch today's half-hourly carbon intensity data."""
    resp = requests.get(f"{BASE_URL}/intensity/date", headers=headers)
    return resp.json()

def get_generation_mix():
    """Fetch current generation mix (fuel types)."""
    resp = requests.get(f"{BASE_URL}/generation", headers=headers)
    return resp.json()

# ----------- Streamlit UI -----------
st.set_page_config(page_title="UK Carbon Intensity Tracker", page_icon="🌍", layout="wide")

# 🔄 Auto-refresh every 31 minutes
st_autorefresh(interval=31 * 60 * 1000, key="data_refresh")

# ---- Top Section with Centered Logo ----
st.markdown(
    '<div style="text-align:center">'
    '<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Globe_icon.svg/200px-Globe_icon.svg.png" width="100">'
    '</div>',
    unsafe_allow_html=True
)

st.title("🌍 UK Carbon Intensity Tracker")
st.markdown("""
Welcome! This dashboard tracks the carbon intensity of Great Britain's electricity grid in real-time.  
Use the sidebar to select which data you want to see.
""")
st.caption("🔄 Auto-refreshes every 31 minutes to match National Grid updates.")
st.write("")  # spacing

# ---- Last Updated ----
st.write(f"🕒 Last updated at: **{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**")
st.write("")  # spacing

# ---- Sidebar ----
st.sidebar.header("Navigation")
view = st.sidebar.radio("Select view:", ["Today's Intensity", "Generation Mix"])

# ---- Main Content ----
if view == "Today's Intensity":
    data = get_today_intensity()["data"]

    # Convert JSON → DataFrame
    df = pd.DataFrame([{
        "from": entry["from"],
        "to": entry["to"],
        "forecast": entry["intensity"]["forecast"],
        "actual": entry["intensity"].get("actual"),
        "index": entry["intensity"]["index"]
    } for entry in data])

    # Parse datetime
    df["from"] = pd.to_datetime(df["from"])
    df["to"] = pd.to_datetime(df["to"])

    # ---- Chart + Table Layout ----
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📈 Today's Carbon Intensity (gCO₂/kWh)")
        chart = (
            alt.Chart(df)
            .mark_line(point=True)
            .encode(
                x="from:T",
                y="forecast:Q",
                tooltip=["from:T", "to:T", "forecast:Q", "actual:Q", "index:N"]
            )
            .properties(width=800, height=400)
        )
        st.altair_chart(chart, use_container_width=True)

    with col2:
        st.subheader("ℹ️ Info")
        st.write("This chart shows the **forecasted carbon intensity** in gCO₂/kWh for each half-hour block today.")
        st.write("Color-coded index: very low, low, moderate, high, very high.")

    st.write("")  # spacing
    st.dataframe(df)

elif view == "Generation Mix":
    mix = get_generation_mix()["data"]["generationmix"]
    df = pd.DataFrame(mix)

    st.subheader("⚡ Current Electricity Generation Mix")
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x="perc:Q",
            y=alt.Y("fuel:N", sort="-x"),
            tooltip=["fuel", "perc"]
        )
        .properties(width=700, height=400)
    )
    st.altair_chart(chart, use_container_width=True)

    st.write("")  # spacing
    st.dataframe(df)
