import streamlit as st
import random
from datetime import datetime

# --------------------------------------------------
# PAGE CONFIGURATION (must be first Streamlit call)
# --------------------------------------------------
st.set_page_config(
    page_title="Timetable Generator",
    page_icon="📅",
    layout="wide"
)

# --------------------------------------------------
# THEME DETECTION & STYLING
# --------------------------------------------------
theme_base = st.get_option("theme.base")

if theme_base == "dark":
    bg_card = "#1e1e1e"
    bg_soft = "#262730"
    border_color = "#3a3a3a"
    text_muted = "#b0b0b0"
else:
    bg_card = "#ffffff"
    bg_soft = "#f6f7f9"
    border_color = "#e0e0e0"
    text_muted = "#555555"

st.markdown(
    f"""
    <style>
    .card {{
        background-color: {bg_card};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
    }}
    .soft-card {{
        background-color: {bg_soft};
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 12px;
    }}
    .muted {{
        color: {text_muted};
        font-size: 0.9rem;
    }}
    .event {{
        padding: 10px 12px;
        border-radius: 8px;
        margin-bottom: 8px;
        border-left: 4px solid;
    }}
    .event-activity {{ border-color: #1f77b4; }}
    .event-compulsory {{ border-color: #d62728; }}
    .event-break {{ border-color: #9e9e9e; }}
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# CONSTANTS & STATE
# --------------------------------------------------
DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
break_time = 2  # hours

if "timetable" not in st.session_state:
    st.session_state.timetable = {day: [] for day in DAY_NAMES}
if "list_of_activities" not in st.session_state:
    st.session_state.list_of_activities = []
if "list_of_compulsory_events" not in st.session_state:
    st.session_state.list_of_compulsory_events = []

# --------------------------------------------------
# TIME HELPERS (unchanged logic)
# --------------------------------------------------
def time_str_to_minutes(t):
    h, m = t.split(":")
    return int(h) * 60 + int(m)

def minutes_to_time_str(m):
    return f"{m // 60:02d}:{m % 60:02d}"

def add_minutes(t, mins):
    return minutes_to_time_str(min(1439, time_str_to_minutes(t) + mins))

def is_time_slot_free(day, start, end):
    s, e = time_str_to_minutes(start), time_str_to_minutes(end)
    for ev in st.session_state.timetable[day]:
        es, ee = time_str_to_minutes(ev["start"]), time_str_to_minutes(ev["end"])
        if not (e <= es or s >= ee):
            return False
    return True

def add_event(day, start, end, name, etype):
    st.session_state.timetable[day].append(
        {"start": start, "end": end, "name": name, "type": etype}
    )
    st.session_state.timetable[day].sort(key=lambda x: time_str_to_minutes(x["start"]))

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title("Smart Timetable Generator")
st.markdown(
    "<p class='muted'>Generate a structured weekly timetable based on priorities, deadlines, and fixed commitments.</p>",
    unsafe_allow_html=True
)

# --------------------------------------------------
# SIDEBAR – CONFIGURATION
# --------------------------------------------------
with st.sidebar:
    st.header("Configuration")

    tabs = st.tabs(["Add Activity", "Add Compulsory Event"])

    with tabs[0]:
        with st.form("activity_form"):
            name = st.text_input("Activity name")
            priority = st.slider("Priority", 1, 5, 3)
            deadline = st.date_input("Deadline", min_value=datetime.now().date())
            hours = st.number_input("Total hours required", 1, 24, 1)

            if st.form_submit_button("Add activity"):
                if name:
                    days_left = (deadline - datetime.now().date()).days
                    st.session_state.list_of_activities.append(
                        {
                            "activity": name,
                            "priority": priority,
                            "deadline": days_left,
                            "timing": hours,
                        }
                    )
                    st.success("Activity added")
                else:
                    st.error("Activity name is required")

    with tabs[1]:
        with st.form("event_form"):
            name = st.text_input("Event name")
            day = st.selectbox("Day", DAY_NAMES)
            c1, c2 = st.columns(2)
            with c1:
                start = st.time_input("Start time")
            with c2:
                end = st.time_input("End time")

            if st.form_submit_button("Add event"):
                if name and end > start:
                    st.session_state.list_of_compulsory_events.append(
                        {
                            "event": name,
                            "day": day,
                            "start_time": start.strftime("%H:%M"),
                            "end_time": end.strftime("%H:%M"),
                        }
                    )
                    st.success("Event added")
                else:
                    st.error("Invalid event details")

# --------------------------------------------------
# DASHBOARD METRICS
# --------------------------------------------------
m1, m2, m3 = st.columns(3)
m1.metric("Activities", len(st.session_state.list_of_activities))
m2.metric("Compulsory events", len(st.session_state.list_of_compulsory_events))
m3.metric("Days scheduled", sum(bool(v) for v in st.session_state.timetable.values()))

# --------------------------------------------------
# TIMETABLE DISPLAY
# --------------------------------------------------
st.header("Weekly Timetable")

for day in DAY_NAMES:
    with st.expander(day, expanded=True):
        if not st.session_state.timetable[day]:
            st.markdown("<div class='soft-card muted'>No events scheduled</div>", unsafe_allow_html=True)
        else:
            for ev in st.session_state.timetable[day]:
                css = {
                    "ACTIVITY": "event event-activity",
                    "COMPULSORY": "event event-compulsory",
                    "BREAK": "event event-break",
                }[ev["type"]]

                st.markdown(
                    f"""
                    <div class="{css}">
                        <strong>{ev['start']} – {ev['end']}</strong><br/>
                        {ev['name']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
