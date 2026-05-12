# import streamlit as st
# import pandas as pd
# import requests
# import plotly.express as px
# #https://datascienceprojects-usccygvvktsatu5mzrzcyf.streamlit.app/
# API_BASE = "https://datascienceprojects-production.up.railway.app"

# API_KEY = st.secrets["API_KEY"]

# HEADERS = {
#     "X-API-Key": API_KEY
# }
# st.set_page_config(
#     page_title="Helldivers Analytics Dashboard",
#     layout="wide"
# )

# st.title("Helldivers 2 Analytics Dashboard")

# # =====================================
# # HEALTH
# # =====================================
# st.header("Server Health")

# health = requests.get(f"{API_BASE}/health").json()

# col1, col2, col3 = st.columns(3)

# col1.metric("API", health["api"])
# col2.metric("Database", health["database"])
# col3.metric("Model Loaded", health["model_loaded"])

# st.write("Latest Data Timestamp:")
# st.write(health["latest_data_timestamp"])

# # =====================================
# # MAJOR ORDER STATUS
# # =====================================
# st.header("Current Major Order")

# mo = requests.get(f"{API_BASE}/major-order-status").json()

# st.subheader("Server Health")

# st.json(mo["server_health"])

# st.subheader("Major Order Data")

# mo_data = mo["major_order_data"]

# col1, col2, col3 = st.columns(3)

# col1.metric(
#     "Players In MO",
#     f"{mo_data['players_in_major_order']:,}"
# )

# col2.metric(
#     "Players Outside MO",
#     f"{mo_data['players_outside_major_order']:,}"
# )

# col3.metric(
#     "MO Ratio",
#     mo_data["major_order_ratio"]
# )

# st.write("Major Order Dispatch:")
# st.write(mo_data["major_order_dispatch"])

# # =====================================
# # FORECAST
# # =====================================
# st.header("24 Hour Forecast")

# #forecast = requests.get(f"{API_BASE}/forecast-24h").json()

# forecast = requests.get(
#     f"{API_BASE}/forecast-24h",
#     headers=HEADERS
# ).json()

# if "forecast" in forecast:

#     forecast_df = pd.DataFrame(forecast["forecast"])

#     fig = px.line(
#         forecast_df,
#         x="timestamp",
#         y="predicted_players",
#         title="Predicted Players Next 24 Hours"
#     )

#     st.plotly_chart(fig, width="stretch")

# else:
#     st.error(forecast)

# # =====================================
# # HISTORICAL MAJOR ORDER
# # =====================================
# st.header("Historical Major Order Analytics")

# days_ago = st.slider(
#     "Major Order From How Many Days Ago?",
#     min_value=1,
#     max_value=30,
#     value=5
# )

# history = requests.get(
#     f"{API_BASE}/major-order-history-by-day?days_ago={days_ago}"
# ).json()

# if "major_order_history" in history:

#     hist_df = pd.DataFrame(history["major_order_history"])

#     # =====================================
#     # BAR CHART
#     # =====================================

#     fig_bar = px.bar(
#         hist_df,
#         x="timestamp",
#         y=[
#             "players_in_major_order",
#             "players_outside_major_order"
#         ],
#         barmode="group",
#         title="Major Order vs Non-Major Order Players"
#     )

#     st.plotly_chart(fig_bar, width="stretch")

#     # =====================================
#     # AREA CHART
#     # =====================================

#     fig_area = px.area(
#         hist_df,
#         x="timestamp",
#         y=[
#             "players_in_major_order",
#             "players_outside_major_order"
#         ],
#         title="Player Distribution Over Time"
#     )

#     st.plotly_chart(fig_area, width="stretch")

#     # =====================================
#     # DIFFERENCE CHART
#     # =====================================

#     hist_df["difference"] = (
#         hist_df["players_in_major_order"]
#         - hist_df["players_outside_major_order"]
#     )

#     fig_diff = px.bar(
#         hist_df,
#         x="timestamp",
#         y="difference",
#         title="Major Order Player Advantage"
#     )

#     st.plotly_chart(fig_diff, width="stretch")
#     # =====================================
#     # MO RATIO %
#     # =====================================

#     hist_df["mo_ratio_percent"] = (
#         hist_df["players_in_major_order"]
#         / hist_df["total_players"]
#     ) * 100

#     fig_ratio = px.line(
#         hist_df,
#         x="timestamp",
#         y="mo_ratio_percent",
#         title="Major Order Participation Percentage"
#     )

#     st.plotly_chart(fig_ratio, width="stretch")

#     # =====================================
#     # KPI METRICS
#     # =====================================

#     latest = hist_df.iloc[-1]

#     players_in = latest["players_in_major_order"]
#     players_out = latest["players_outside_major_order"]

#     difference = players_in - players_out

#     ratio = (
#         players_in / players_out
#         if players_out > 0 else None
#     )

#     pct_more = (
#         ((players_in - players_out) / players_out) * 100
#         if players_out > 0 else None
#     )

#     st.subheader("Current Major Order Engagement")

#     col1, col2, col3, col4 = st.columns(4)

#     col1.metric(
#         "Players In MO",
#         f"{int(players_in):,}"
#     )

#     col2.metric(
#         "Players Outside MO",
#         f"{int(players_out):,}"
#     )

#     col3.metric(
#         "Difference",
#         f"{int(difference):,}"
#     )

#     col4.metric(
#         "% More In MO",
#         f"{pct_more:.1f}%"
#     )

#     # =====================================
#     # PEAK ENGAGEMENT
#     # =====================================

#     peak_idx = hist_df["players_in_major_order"].idxmax()

#     peak_row = hist_df.loc[peak_idx]

#     st.subheader("Peak Engagement")

#     col1, col2 = st.columns(2)

#     col1.metric(
#         "Peak MO Players",
#         f"{int(peak_row['players_in_major_order']):,}"
#     )

#     col2.metric(
#         "Peak MO %",
#         f"{peak_row['mo_ratio_percent']:.1f}%"
#     )

#     st.write("Peak Timestamp:")
#     st.write(peak_row["timestamp"])

#     # =====================================
#     # MAJOR ORDER DESCRIPTION
#     # =====================================

#     st.subheader("Major Order Dispatch")

#     st.write(history["major_order_dispatch"])

# else:
#     st.error(history)
    
    
    
# # =====================================
# # FACTION SUMMARY
# # =====================================

# st.header("Current Faction Player Distribution")
# #below is when the data was pulled
# st.caption(
#     f"Live snapshot from latest available data pull: "
#     f"{health['latest_data_timestamp']}"
# )
# faction_data = requests.get(
#     f"{API_BASE}/faction-summary"
# ).json()

# faction_df = pd.DataFrame(
#     faction_data["factions"]
# )

# col1, col2 = st.columns(2)

# # PIE CHART
# with col1:

#     fig_pie = px.pie(
#         faction_df,
#         names="enemy_faction",
#         values="players_fighting",
#         title="Players Fighting Each Enemy Faction"
#     )

#     st.plotly_chart(fig_pie, use_container_width=True)

# # BAR CHART
# with col2:

#     fig_bar = px.bar(
#         faction_df,
#         x="enemy_faction",
#         y="players_fighting",
#         title="Players Fighting Each Enemy Faction"
#     )

#     st.plotly_chart(fig_bar, use_container_width=True)
    
    
# # =====================================
# # TOP PLANETS
# # =====================================

# st.header("Top Active Planets")

# top_planets = requests.get(
#     f"{API_BASE}/top-planets?limit=15"
# ).json()

# # SERVER HEALTH WARNING
# if top_planets["server_health"]["status"] != "ok":

#     st.warning(
#         f"Planet data may be unreliable: "
#         f"{top_planets['server_health']['status']}"
#     )

# top_df = pd.DataFrame(
#     top_planets["top_planets"]
# )

# # CLEAN COLUMN NAMES
# # top_df.columns = [
# #     "Planet",
# #     "Players",
# #     "Owner",
# #     "In Major Order",
# #     "Strategic Opportunity",
# #     "Possible Paths To MO",
# #     "Sector"
# # ]

# top_df = top_df.rename(columns={
#     "planet": "Planet",
#     "players": "Players",
#     "owner": "Owner",
#     "in_major_order": "In Major Order",
#     "sector": "Sector",
#     "strategic_opportunity": "Strategic Opportunity",
#     "possible_paths_to_major_order": "Possible Paths To MO"
# })
# #st.write(top_df.columns.tolist())
# # SORT
# top_df = top_df.sort_values(
#     by="Players",
#     ascending=False
# )

# # TABLE
# st.dataframe(
#     top_df,
#     use_container_width=True,
#     hide_index=True
# )

# # =====================================
# # TOP PLANETS BAR CHART
# # =====================================

# fig_top = px.bar(
#     top_df,
#     x="Planet",
#     y="Players",
#     color="Owner",
#     title="Top Populated Planets"
# )

# st.plotly_chart(
#     fig_top,
#     use_container_width=True
# )





#copy and paste below


import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import requests
import uuid

# =====================================
# CONFIG
# =====================================

API_BASE = "https://datascienceprojects-production.up.railway.app"

#API_KEY = st.secrets["API_KEY"]
import os

API_KEY = os.getenv("API_KEY")

HEADERS = {
    "X-API-Key": API_KEY
}

API_BASE_URL = "https://datascienceprojects-production.up.railway.app"

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

def track_event(event_type, element):

    payload = {
        "session_id": st.session_state.session_id,
        "event_type": event_type,
        "element": element
    }

    try:
        requests.post(
            f"{API_BASE_URL}/track-event",
            json=payload,
            timeout=5
        )

    except Exception as e:
        print(f"Tracking failed: {e}")


track_event(
    event_type="impression",
    element="dashboard_loaded"
)
st.set_page_config(
    page_title="Helldivers Analytics Dashboard",
    layout="wide"
)
st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

div[data-testid="metric-container"] {
    background-color: #111827;
    padding: 15px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

#st.autorefresh(interval=300000, key="refresh")

st.title("Helldivers 2 Analytics Dashboard")

st.caption(
    "Live Helldivers 2 analytics platform with forecasting, "
    "major order tracking, and real-time faction engagement metrics."
)

st.markdown("""
This project collects live Helldivers 2 API data,
stores historical snapshots in PostgreSQL,
serves analytics through FastAPI,
and visualizes player behavior trends in Streamlit.
""")

st.divider()

# =====================================
# CACHED API HELPERS
# =====================================

@st.cache_data(ttl=300)
def get_health():
    response = requests.get(
        f"{API_BASE}/health",
        headers=HEADERS,
        timeout=20
    )

    response.raise_for_status()

    return response.json()


@st.cache_data(ttl=300)
def get_major_order():
    response = requests.get(
        f"{API_BASE}/major-order-status",
        headers=HEADERS,
        timeout=20
    )

    response.raise_for_status()

    return response.json()


@st.cache_data(ttl=300)
def get_forecast():
    response = requests.get(
        f"{API_BASE}/forecast-24h",
        headers=HEADERS,
        timeout=20
    )

    response.raise_for_status()

    return response.json()


@st.cache_data(ttl=300)
def get_faction_summary():
    response = requests.get(
        f"{API_BASE}/faction-summary",
        headers=HEADERS,
        timeout=20
    )

    response.raise_for_status()

    return response.json()


@st.cache_data(ttl=120)
def get_top_planets(limit=15):
    response = requests.get(
        f"{API_BASE}/top-planets?limit={limit}",
        headers=HEADERS,
        timeout=20
    )

    response.raise_for_status()

    return response.json()


@st.cache_data(ttl=300)
def get_major_order_history(days_ago):
    response = requests.get(
        f"{API_BASE}/major-order-history-by-day?days_ago={days_ago}",
        headers=HEADERS,
        timeout=20
    )

    response.raise_for_status()

    return response.json()


# =====================================
# HEALTH
# =====================================

try:
    health = get_health()
except Exception as e:
    st.error(f"Health endpoint failed: {e}")
    st.stop()

st.caption(
    "Infrastructure status for the live analytics platform."
)
st.header("Server Health")

col1, col2, col3 = st.columns(3)

col1.metric("API", health["api"])
col2.metric("Database", health["database"])
col3.metric("Model Loaded", health["model_loaded"])

st.write("Latest Data Timestamp:")
st.write(health["latest_data_timestamp"])
st.divider()
# =====================================
# MAJOR ORDER STATUS
# =====================================

try:
    mo = get_major_order()
except Exception as e:
    st.error(f"Major order endpoint failed: {e}")
    st.stop()
st.caption(
    "Real-time snapshot of current major order engagement."
)
st.header("Current Major Order")

st.subheader("Server Health")

st.json(mo["server_health"])

st.subheader("Major Order Data")

mo_data = mo["major_order_data"]

col1, col2, col3 = st.columns(3)

col1.metric(
    "Players On Major Order Planets",
    f"{mo_data['players_in_major_order']:,}"
)

col2.metric(
    "Players Outside Major Order Planets",
    f"{mo_data['players_outside_major_order']:,}"
)

col3.metric(
    "MO Participation %",
    f"{mo_data['major_order_ratio']:.1%}"
)

st.subheader("Major Order Dispatch")

st.info(mo_data["major_order_dispatch"])
st.divider()
# =====================================
# FORECAST
# =====================================

try:
    forecast = get_forecast()
except Exception as e:
    st.error(f"Forecast endpoint failed: {e}")
    forecast = {}
st.caption(
    "Machine learning forecast of total active Helldivers players over the next 24 hours."
)
st.header("24 Hour Forecast")

if "forecast" in forecast:

    forecast_df = pd.DataFrame(forecast["forecast"])

    fig = px.line(
        forecast_df,
        x="timestamp",
        y="predicted_players",
        title="Predicted Players Next 24 Hours",
        template="plotly_dark"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:
    st.error(forecast)
    
st.divider()
# =====================================
# HISTORICAL MAJOR ORDER
# =====================================
st.caption(
    "Historical trends showing how player participation changes during major orders."
)
st.header("Historical Major Order Analytics")

days_ago = st.slider(
    "Major Order From How Many Days Ago?",
    min_value=1,
    max_value=30,
    value=5
)

try:
    history = get_major_order_history(days_ago)
except Exception as e:
    st.error(f"Historical endpoint failed: {e}")
    st.stop()

if "major_order_history" in history:

    hist_df = pd.DataFrame(history["major_order_history"])

    # =====================================
    # BAR CHART
    # =====================================

    fig_bar = px.bar(
        hist_df,
        x="timestamp",
        y=[
            "players_in_major_order",
            "players_outside_major_order"
        ],
        barmode="group",
        title="Major Order vs Non-Major Order Players",
        template="plotly_dark"
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

    # =====================================
    # AREA CHART
    # =====================================

    fig_area = px.area(
        hist_df,
        x="timestamp",
        y=[
            "players_in_major_order",
            "players_outside_major_order"
        ],
        title="Player Distribution Over Time",
        template="plotly_dark"
    )

    st.plotly_chart(
        fig_area,
        use_container_width=True
    )

    # =====================================
    # DIFFERENCE CHART
    # =====================================

    hist_df["difference"] = (
        hist_df["players_in_major_order"]
        - hist_df["players_outside_major_order"]
    )

    fig_diff = px.bar(
        hist_df,
        x="timestamp",
        y="difference",
        title="Major Order Player Advantage",
        template="plotly_dark"
    )

    st.plotly_chart(
        fig_diff,
        use_container_width=True
    )

    # =====================================
    # MO RATIO %
    # =====================================

    hist_df["mo_ratio_percent"] = (
        hist_df["players_in_major_order"]
        / hist_df["total_players"]
    ) * 100

    fig_ratio = px.line(
        hist_df,
        x="timestamp",
        y="mo_ratio_percent",
        title="Major Order Participation Percentage historical from slider above",
        template="plotly_dark"
    )

    st.plotly_chart(
        fig_ratio,
        use_container_width=True
    )

    # =====================================
    # KPI METRICS
    # =====================================

    latest = hist_df.iloc[-1]

    players_in = latest["players_in_major_order"]
    players_out = latest["players_outside_major_order"]

    total_players = players_in + players_out

    mo_share = (
        (players_in / total_players) * 100
        if total_players > 0 else 0
    )

    st.subheader(
        "Historical Major Order Participation Snapshot"
    )

    st.caption(
        "Metrics below reflect the most recent timestamp from the selected historical window."
    )
    # st.subheader(
    #     "Major Order Participation Percentage historical from slider above"
    # )

    col1, col2, col3, col4 = st.columns(4)
    
    st.caption(
        "Snapshot from the latest available game data."
    )
    col1.metric(
        "Players On Major Order Planets",
        f"{int(players_in):,}"
    )

    col2.metric(
        "Players Outside MO",
        f"{int(players_out):,}"
    )

    col3.metric(
        "Total Active Players",
        f"{int(total_players):,}"
    )

    percent_in_mo = (
        latest["mo_ratio_percent"]
    )

    col4.metric(
        "% Of Players In Major Order",
        f"{percent_in_mo:.1f}%"
    )
    # col4.metric(
    #     "Share Participating In MO",
    #     f"{mo_share:.1f}%"
    # )

    # =====================================
    # PEAK ENGAGEMENT
    # =====================================

    peak_idx = hist_df["players_in_major_order"].idxmax()

    peak_row = hist_df.loc[peak_idx]
    st.caption(
        "Highest recorded player participation within the selected historical window."
    )
    st.subheader("Peak Engagement")

    col1, col2 = st.columns(2)

    col1.metric(
        "Peak MO Players",
        f"{int(peak_row['players_in_major_order']):,}"
    )

    col2.metric(
        "Highest Major Order Participation %",
        f"{peak_row['mo_ratio_percent']:.1f}%"
    )

    st.write("Peak Timestamp:")
    st.write(peak_row["timestamp"])

else:
    st.error(history)
    
st.divider()
# =====================================
# FACTION SUMMARY
# =====================================

try:
    faction_data = get_faction_summary()
except Exception as e:
    st.error(f"Faction endpoint failed: {e}")
    st.stop()
st.caption(
    "Distribution of active players currently fighting each enemy faction."
)
st.header("Current Faction Player Distribution")

st.caption(
    f"Live snapshot from latest available data pull: "
    f"{health['latest_data_timestamp']}"
)

faction_df = pd.DataFrame(
    faction_data["factions"]
)

col1, col2 = st.columns(2)

# PIE CHART
with col1:

    fig_pie = px.pie(
        faction_df,
        names="enemy_faction",
        values="players_fighting",
        title="Players Fighting Each Enemy Faction",
        template="plotly_dark"
    )

    st.plotly_chart(
        fig_pie,
        use_container_width=True
    )

# BAR CHART
with col2:

    fig_bar = px.bar(
        faction_df,
        x="enemy_faction",
        y="players_fighting",
        title="Players Fighting Each Enemy Faction",
        template="plotly_dark"
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

# =====================================
# TOP PLANETS
# =====================================

try:
    top_planets = get_top_planets(15)
except Exception as e:
    st.error(f"Top planets endpoint failed: {e}")
    st.stop()

st.caption(
    "Most populated planets from the latest live data snapshot."
)
st.header("Top Active Planets")

if top_planets["server_health"]["status"] != "ok":

    st.warning(
        f"Planet data may be unreliable: "
        f"{top_planets['server_health']['status']}"
    )

top_df = pd.DataFrame(
    top_planets["top_planets"]
)

top_df = top_df.rename(columns={
    "planet": "Planet",
    "players": "Players",
    "owner": "Owner",
    "in_major_order": "In Major Order",
    "sector": "Sector",
    "strategic_opportunity": "Strategic Opportunity",
    "possible_paths_to_major_order": "Possible Paths To MO"
})

top_df = top_df.sort_values(
    by="Players",
    ascending=False
)

st.dataframe(
    top_df,
    use_container_width=True,
    hide_index=True
)

# =====================================
# TOP PLANETS BAR CHART
# =====================================

fig_top = px.bar(
    top_df,
    x="Planet",
    y="Players",
    color="Owner",
    title="Top Populated Planets",
    template="plotly_dark"
)

st.plotly_chart(
    fig_top,
    use_container_width=True
)

st.divider()

st.caption("""
Built with:
FastAPI • PostgreSQL • Streamlit • Railway • XGBoost

Data collected hourly from public Helldivers 2 APIs.
""")