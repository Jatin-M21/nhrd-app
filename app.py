import streamlit as st
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="NHRD Summit 2026", page_icon="🏢", layout="centered")

# Custom CSS to make it look like a mobile app
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 5px;
        gap: 1px;
        padding-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOAD DATA FROM LOCAL CSVs ---
@st.cache_data
def load_local_data(file_name):
    try:
        return pd.read_csv(file_name)
    except:
        return pd.DataFrame()

df_agenda = load_local_data("agenda.csv")
df_students = load_local_data("students.csv")
df_speakers = load_local_data("speakers.csv")

# --- HEADER ---
st.title("NHRD HR Summit 2026")
st.markdown("### *Balancing Act of AI & EI*")
st.caption("SSSIHL Brindavan Campus | March 13, 2026")

# --- TABS NAVIGATION ---
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Home", "📅 Agenda", "🎓 Students", "🎙️ Speakers"])

# HOME TAB
with tab1:
    st.info("🔴 **Live Update:** Inauguration Ceremony starting in the Auditorium.")
    st.markdown("""
    Welcome to the SSSIHL Brindavan Campus. This app provides real-time access to the summit schedule, 
    speaker profiles, and our MBA talent directory.
    """)
    st.divider()
    st.button("📍 View Campus Map", use_container_width=True)

# AGENDA TAB
with tab2:
    st.subheader("Event Schedule")
    if not df_agenda.empty:
        st.dataframe(df_agenda, use_container_width=True, hide_index=True)
    else:
        st.error("Agenda file (agenda.csv) not found.")

# STUDENTS TAB
with tab3:
    st.subheader("MBA Talent Directory")
    search = st.text_input("Search students by name or skill...")
    if not df_students.empty:
        # Simple search logic
        filtered_students = df_students[df_students.apply(lambda row: search.lower() in row.astype(str).str.lower().values, axis=1)] if search else df_students
        for _, row in filtered_students.iterrows():
            with st.container(border=True):
                st.write(f"**{row['Name']}**")
                st.caption(f"Specialization: {row['Specialization']}")
                st.link_button("View Resume", row['Resume_Link'])
    else:
        st.error("Student database (students.csv) not found.")

# SPEAKERS TAB
with tab4:
    st.subheader("Our Esteemed Speakers")
    if not df_speakers.empty:
        for _, row in df_speakers.iterrows():
            with st.expander(f"{row['Name']} - {row['Designation']}"):
                st.write(row['Bio'])
    else:
        st.error("Speaker file (speakers.csv) not found.")
