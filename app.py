import os
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

API_BASE = "https://api.openf1.org/v1"
REFRESH_SECONDS = 60
DEFAULT_TIMEZONE = "America/New_York"

st.set_page_config(
    page_title="OpenPit | Race Engineer Dashboard",
    page_icon="🏎️",
    layout="wide",
)

CUSTOM_CSS = """
<style>
:root {
  --bg: #0a0f14;
  --surface: #111826;
  --surface-2: #172131;
  --border: #263246;
  --text: #edf2f7;
  --muted: #9fb0c7;
  --accent: #ff5a36;
  --accent-2: #22c55e;
  --yellow: #facc15;
}
.main {
  background: radial-gradient(circle at top right, rgba(255,90,54,0.10), transparent 25%), var(--bg);
}
.block-container {
  padding-top: 1.4rem;
  padding-bottom: 2rem;
}
.metric-card {
  background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 16px 18px;
  min-height: 120px;
}
.panel {
  background: rgba(17,24,38,0.85);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 14px 16px 4px 16px;
}
.kicker {
  color: var(--accent);
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-weight: 700;
}
.hero-title {
  font-size: 2.1rem;
  font-weight: 800;
  line-height: 1.05;
  margin-bottom: 0.25rem;
}
.hero-sub {
  color: var(--muted);
  font-size: 0.98rem;
  margin-bottom: 0;
}
.small-note {
  color: var(--muted);
  font-size: 0.86rem;
}
.badge {
  display: inline-block;
  border: 1px solid rgba(255,90,54,0.35);
  color: #ffd3ca;
  background: rgba(255,90,54,0.12);
  border-radius: 999px;
  padding: 0.2rem 0.65rem;
  font-size: 0.78rem;
  font-weight: 700;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def fetch_openf1(endpoint: str, **params):
    clean = {k: v for k, v in params.items() if v is not None and v != ""}
    response = requests.get(f"{API_BASE}/{endpoint}", params=clean, timeout=30)
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=REFRESH_SECONDS, show_spinner=False)
def get_sessions(year: int):
    data = fetch_openf1("sessions", year=year)
    df = pd.DataFrame(data)
    if df.empty:
        return df
    df["date_start"] = pd.to_datetime(df["date_start"], utc=True)
    df["date_end"] = pd.to_datetime(df["date_end"], utc=True)
    return df.sort_values("date_start", ascending=False)


@st.cache_data(ttl=REFRESH_SECONDS, show_spinner=False)
def get_meetings(year: int):
    data = fetch_openf1("meetings", year=year)
    df = pd.DataFrame(data)
    if df.empty:
        return df
    df["date_start"] = pd.to_datetime(df["date_start"], utc=True)
    df["date_end"] = pd.to_datetime(df["date_end"], utc=True)
    return df.sort_values("date_start", ascending=False)


@st.cache_data(ttl=REFRESH_SECONDS, show_spinner=False)
def get_drivers(session_key: int):
    df = pd.DataFrame(fetch_openf1("drivers", session_key=session_key))
    if df.empty:
        return df
    df["team_colour"] = df["team_colour"].fillna("FFFFFF")
    return df.sort_values(["team_name", "driver_number"])


@st.cache_data(ttl=REFRESH_SECONDS, show_spinner=False)
def get_laps(session_key: int):
    df = pd.DataFrame(fetch_openf1("laps", session_key=session_key))
    if df.empty:
        return df
    if "date_start" in df.columns:
        df["date_start"] = pd.to_datetime(df["date_start"], utc=True, errors="coerce")
    numeric_cols = [
        "lap_duration",
        "duration_sector_1",
        "duration_sector_2",
        "duration_sector_3",
        "i1_speed",
        "i2_speed",
        "st_speed",
        "lap_number",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


@st.cache_data(ttl=REFRESH_SECONDS, show_spinner=False)
def get_weather(session_key: int):
    df = pd.DataFrame(fetch_openf1("weather", session_key=session_key))
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce")
    return df.sort_values("date")


@st.cache_data(ttl=REFRESH_SECONDS, show_spinner=False)
def get_race_control(session_key: int):
    df = pd.DataFrame(fetch_openf1("race_control", session_key=session_key))
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce")
    return df.sort_values("date", ascending=False)


@st.cache_data(ttl=REFRESH_SECONDS, show_spinner=False)
def get_position(session_key: int):
    df = pd.DataFrame(fetch_openf1("position", session_key=session_key))
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce")
    df["position"] = pd.to_numeric(df["position"], errors="coerce")
    return df.sort_values("date")


@st.cache_data(ttl=REFRESH_SECONDS, show_spinner=False)
def get_intervals(session_key: int):
    df = pd.DataFrame(fetch_openf1("intervals", session_key=session_key))
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce")
    return df.sort_values("date")


@st.cache_data(ttl=REFRESH_SECONDS, show_spinner=False)
def get_stints(session_key: int):
    df = pd.DataFrame(fetch_openf1("stints", session_key=session_key))
    if df.empty:
        return df
    return df.sort_values(["driver_number", "stint_number"])


@st.cache_data(ttl=REFRESH_SECONDS, show_spinner=False)
def get_car_data(session_key: int, driver_number: int):
    df = pd.DataFrame(fetch_openf1("car_data", session_key=session_key, driver_number=driver_number))
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce")
    for col in ["speed", "throttle", "brake", "rpm", "n_gear"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.sort_values("date")


@st.cache_data(ttl=REFRESH_SECONDS, show_spinner=False)
def get_location(session_key: int, driver_number: int):
    df = pd.DataFrame(fetch_openf1("location", session_key=session_key, driver_number=driver_number))
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce")
    return df.sort_values("date")


@st.cache_data(ttl=REFRESH_SECONDS, show_spinner=False)
def get_team_radio(session_key: int, driver_number: int):
    df = pd.DataFrame(fetch_openf1("team_radio", session_key=session_key, driver_number=driver_number))
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce")
    return df.sort_values("date", ascending=False)


def fmt_lap_time(seconds):
    if pd.isna(seconds):
        return "—"
    minutes = int(seconds // 60)
    rem = seconds - minutes * 60
    return f"{minutes}:{rem:06.3f}"


def fmt_dt(ts, tz_name=DEFAULT_TIMEZONE):
    if pd.isna(ts):
        return "—"
    return ts.tz_convert(ZoneInfo(tz_name)).strftime("%b %d, %I:%M %p")


def card(title: str, value: str, extra: str):
    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='small-note'>{title}</div>
            <div style='font-size:1.9rem;font-weight:800;margin-top:0.35rem'>{value}</div>
            <div class='small-note' style='margin-top:0.4rem'>{extra}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.markdown("## OpenPit")
    st.caption("Race engineer style dashboard built on OpenF1.")
    year = st.selectbox("Season", options=list(range(datetime.now().year, 2022, -1)), index=0)
    meetings_df = get_meetings(year)
    sessions_df = get_sessions(year)

    if meetings_df.empty or sessions_df.empty:
        st.error("No OpenF1 data available for this year right now.")
        st.stop()

    meeting_options = meetings_df[["meeting_key", "meeting_name", "location", "country_name"]].drop_duplicates()
    meeting_labels = {
        row.meeting_key: f"{row.meeting_name} · {row.location}, {row.country_name}"
        for row in meeting_options.itertuples()
    }

    selected_meeting_key = st.selectbox(
        "Grand Prix weekend",
        options=meeting_options["meeting_key"].tolist(),
        format_func=lambda k: meeting_labels.get(k, str(k)),
        index=0,
    )

    available_sessions = sessions_df[sessions_df["meeting_key"] == selected_meeting_key].copy()
    available_sessions = available_sessions.sort_values("date_start")
    if available_sessions.empty:
        st.error("This meeting has no sessions loaded.")
        st.stop()

    session_labels = {
        row.session_key: f"{row.session_name} · {row.date_start.strftime('%b %d %H:%M UTC')}"
        for row in available_sessions.itertuples()
    }

    selected_session_key = st.selectbox(
        "Session",
        options=available_sessions["session_key"].tolist(),
        format_func=lambda k: session_labels.get(k, str(k)),
        index=len(available_sessions) - 1,
    )

    tz_choice = st.selectbox(
        "Display timezone",
        options=["America/New_York", "UTC", "Europe/London"],
        index=0,
    )

    auto_refresh = st.toggle("Auto refresh every 60s", value=True)

    if st.button("Refresh now", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

session_row = available_sessions[available_sessions["session_key"] == selected_session_key].iloc[0]
drivers_df = get_drivers(int(selected_session_key))
laps_df = get_laps(int(selected_session_key))
weather_df = get_weather(int(selected_session_key))
race_control_df = get_race_control(int(selected_session_key))
position_df = get_position(int(selected_session_key))
intervals_df = get_intervals(int(selected_session_key))
stints_df = get_stints(int(selected_session_key))

if auto_refresh:
    st.autorefresh(interval=REFRESH_SECONDS * 1000, key="openpit-refresh")

meeting_name = session_row["session_name"]
meeting_location = f"{session_row['location']}, {session_row['country_name']}"

st.markdown(
    f"""
    <div class='kicker'>Race Engineer Dashboard</div>
    <div class='hero-title'>{meeting_name}</div>
    <p class='hero-sub'>{session_row['circuit_short_name']} · {meeting_location} · <span class='badge'>Session key {selected_session_key}</span></p>
    """,
    unsafe_allow_html=True,
)

left, mid, right, far = st.columns(4)

with left:
    card("Session window", f"{fmt_dt(session_row['date_start'], tz_choice)}", f"Ends {fmt_dt(session_row['date_end'], tz_choice)}")

with mid:
    if not laps_df.empty and "lap_duration" in laps_df.columns:
        fastest = laps_df.dropna(subset=["lap_duration"]).sort_values("lap_duration").head(1)
        if not fastest.empty:
            fast_driver = int(fastest.iloc[0]["driver_number"])
            if not drivers_df.empty and fast_driver in drivers_df["driver_number"].values:
                fast_name = drivers_df.loc[drivers_df["driver_number"] == fast_driver, "name_acronym"].iloc[0]
            else:
                fast_name = str(fast_driver)
            card("Fastest lap", fmt_lap_time(fastest.iloc[0]["lap_duration"]), f"Driver {fast_name} · Lap {int(fastest.iloc[0]['lap_number'])}")
        else:
            card("Fastest lap", "—", "No lap data yet")
    else:
        card("Fastest lap", "—", "No lap data yet")

with right:
    if not weather_df.empty:
        latest_weather = weather_df.iloc[-1]
        card("Track temp", f"{latest_weather['track_temperature']:.1f}°C", f"Air {latest_weather['air_temperature']:.1f}°C · Wind {latest_weather['wind_speed']:.1f} m/s")
    else:
        card("Track temp", "—", "Weather feed unavailable")

with far:
    rc_count = 0 if race_control_df.empty else len(race_control_df)
    last_rc = "No messages"
    if not race_control_df.empty:
        last_rc = str(race_control_df.iloc[0].get("category", "Update"))
    card("Race control", str(rc_count), f"Latest: {last_rc}")

st.markdown("### Session command view")
col1, col2 = st.columns([1.25, 1])

with col1:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader("Lap pace by driver")
    if laps_df.empty:
        st.info("Lap data has not arrived for this session yet.")
    else:
        laps_plot = laps_df.dropna(subset=["lap_duration"]).copy()
        if not drivers_df.empty:
            laps_plot = laps_plot.merge(drivers_df[["driver_number", "name_acronym", "team_colour"]], on="driver_number", how="left")
            laps_plot["driver"] = laps_plot["name_acronym"].fillna(laps_plot["driver_number"].astype(str))
            color_map = {
                row.name_acronym: f"#{row.team_colour}"
                for row in drivers_df.itertuples()
                if pd.notna(row.name_acronym)
            }
        else:
            laps_plot["driver"] = laps_plot["driver_number"].astype(str)
            color_map = None

        fig_laps = px.line(
            laps_plot,
            x="lap_number",
            y="lap_duration",
            color="driver",
            color_discrete_map=color_map,
            markers=True,
            labels={"lap_number": "Lap", "lap_duration": "Lap time (s)", "driver": "Driver"},
        )
        fig_laps.update_layout(
            height=420,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            legend_orientation="h",
            legend_y=1.08,
        )
        st.plotly_chart(fig_laps, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader("Weather trend")
    if weather_df.empty:
        st.info("Weather feed unavailable for this session.")
    else:
        weather_long = weather_df[["date", "track_temperature", "air_temperature", "wind_speed"]].melt(
            "date", var_name="metric", value_name="value"
        )
        fig_weather = px.line(
            weather_long,
            x="date",
            y="value",
            color="metric",
            labels={"date": "Time", "value": "Value", "metric": "Metric"},
        )
        fig_weather.update_layout(
            height=420,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig_weather, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("### Driver drilldown")

if drivers_df.empty:
    st.warning("Driver list is unavailable for this session.")
else:
    driver_options = drivers_df.sort_values("driver_number")["driver_number"].tolist()
    selected_driver = st.selectbox(
        "Choose a driver",
        options=driver_options,
        format_func=lambda n: f"{drivers_df.loc[drivers_df['driver_number'] == n, 'name_acronym'].iloc[0]} · #{n} · {drivers_df.loc[drivers_df['driver_number'] == n, 'team_name'].iloc[0]}",
    )

    car_df = get_car_data(int(selected_session_key), int(selected_driver))
    loc_df = get_location(int(selected_session_key), int(selected_driver))
    radio_df = get_team_radio(int(selected_session_key), int(selected_driver))

    top_left, top_mid, top_right = st.columns([1, 1.2, 1])

    with top_left:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader("Sector summary")
        driver_laps = laps_df[laps_df["driver_number"] == selected_driver].dropna(subset=["lap_duration"]).copy()
        if driver_laps.empty:
            st.info("No completed laps yet for this driver.")
        else:
            best_row = driver_laps.sort_values("lap_duration").iloc[0]
            sector_table = pd.DataFrame(
                {
                    "Metric": ["Best lap", "Sector 1", "Sector 2", "Sector 3", "Speed trap"],
                    "Value": [
                        fmt_lap_time(best_row.get("lap_duration")),
                        f"{best_row.get('duration_sector_1', float('nan')):.3f}s" if pd.notna(best_row.get("duration_sector_1")) else "—",
                        f"{best_row.get('duration_sector_2', float('nan')):.3f}s" if pd.notna(best_row.get("duration_sector_2")) else "—",
                        f"{best_row.get('duration_sector_3', float('nan')):.3f}s" if pd.notna(best_row.get("duration_sector_3")) else "—",
                        f"{int(best_row.get('st_speed'))} km/h" if pd.notna(best_row.get("st_speed")) else "—",
                    ],
                }
            )
            st.dataframe(sector_table, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with top_mid:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader("Speed, throttle, brake")
        if car_df.empty:
            st.info("Car telemetry is unavailable for this driver/session combination.")
        else:
            telemetry = car_df[["date", "speed", "throttle", "brake"]].melt(
                "date", var_name="channel", value_name="value"
            )
            fig_tel = px.line(telemetry, x="date", y="value", color="channel")
            fig_tel.update_layout(
                height=340,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10),
            )
            st.plotly_chart(fig_tel, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with top_right:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader("Track trace")
        if loc_df.empty:
            st.info("Location feed unavailable.")
        else:
            fig_loc = px.line(loc_df.tail(800), x="x", y="y")
            fig_loc.update_yaxes(scaleanchor="x", scaleratio=1, visible=False)
            fig_loc.update_xaxes(visible=False)
            fig_loc.update_layout(
                height=340,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=0),
                showlegend=False,
            )
            st.plotly_chart(fig_loc, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    lower_left, lower_right = st.columns([1.25, 1])

    with lower_left:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader("Position or interval history")
        driver_position = position_df[position_df["driver_number"] == selected_driver].copy()
        if not driver_position.empty:
            fig_pos = px.line(driver_position, x="date", y="position", markers=True)
            fig_pos.update_yaxes(autorange="reversed")
            fig_pos.update_layout(
                height=320,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10),
                showlegend=False,
            )
            st.plotly_chart(fig_pos, use_container_width=True)
        else:
            driver_intervals = intervals_df[intervals_df["driver_number"] == selected_driver].copy()
            if driver_intervals.empty:
                st.info("No live position or interval history yet.")
            else:
                for col in ["gap_to_leader", "interval"]:
                    driver_intervals[col] = pd.to_numeric(driver_intervals[col], errors="coerce")
                fig_gap = px.line(driver_intervals, x="date", y=["gap_to_leader", "interval"])
                fig_gap.update_layout(
                    height=320,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=10, r=10, t=10, b=10),
                )
                st.plotly_chart(fig_gap, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with lower_right:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader("Stints and team radio")
        driver_stints = stints_df[stints_df["driver_number"] == selected_driver].copy() if not stints_df.empty else pd.DataFrame()
        if driver_stints.empty:
            st.caption("No stint data yet.")
        else:
            st.dataframe(
                driver_stints[["stint_number", "compound", "lap_start", "lap_end", "tyre_age_at_start"]],
                use_container_width=True,
                hide_index=True,
            )

        if radio_df.empty:
            st.caption("No radio clips available from OpenF1 for this driver/session.")
        else:
            for row in radio_df.head(3).itertuples():
                st.markdown(f"**{fmt_dt(row.date, tz_choice)}**")
                st.audio(row.recording_url, format="audio/mp3")
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("### Race control feed")
feed_col, standings_col = st.columns([1.1, 0.9])

with feed_col:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    if race_control_df.empty:
        st.info("No race control messages available.")
    else:
        feed = race_control_df[["date", "category", "flag", "message", "driver_number", "scope"]].fillna("—").head(20).copy()
        feed["date"] = feed["date"].apply(lambda x: fmt_dt(x, tz_choice))
        st.dataframe(feed, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

with standings_col:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader("Latest driver snapshot")
    if laps_df.empty:
        st.info("No live snapshot available.")
    else:
        latest_laps = laps_df.sort_values("lap_number").groupby("driver_number", as_index=False).tail(1)
        snapshot = latest_laps[
            ["driver_number", "lap_number", "lap_duration", "duration_sector_1", "duration_sector_2", "duration_sector_3"]
        ].copy()

        if not drivers_df.empty:
            snapshot = snapshot.merge(
                drivers_df[["driver_number", "name_acronym", "team_name"]],
                on="driver_number",
                how="left",
            )
            snapshot = snapshot[
                ["name_acronym", "team_name", "lap_number", "lap_duration", "duration_sector_1", "duration_sector_2", "duration_sector_3"]
            ]
            snapshot.columns = ["Driver", "Team", "Lap", "Lap time", "S1", "S2", "S3"]

        snapshot = snapshot.sort_values("Lap", ascending=False)
        st.dataframe(snapshot.head(20), use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.caption(
    "OpenPit uses OpenF1 historical and session data. Historical data from 2023 onward is freely accessible, while real-time access may depend on OpenF1 subscription limits."
)
