import streamlit as st
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="NHRD Summit 2026", page_icon="🏢", layout="centered")

# Custom CSS for a mobile-app feel
st.markdown("""
    <style>
    [data-testid="stHeader"] {display:none;}
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: #1e1e1e;
        border-radius: 5px;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data(file):
    try:
        return pd.read_csv(file)
    except:
        return pd.DataFrame()

df_agenda = load_data("agenda.csv")
df_students = load_data("students.csv")
df_speakers = load_data("speakers.csv")

# --- HEADER ---
st.title("NHRD HR Summit 2026")
st.markdown("#### *Balancing Act of AI & EI*")
st.caption("SSSIHL Brindavan Campus | March 13, 2026")

tab1, tab2, tab3, tab4 = st.tabs(["🏠 Home", "📅 Agenda", "🎓 Students", "🎙️ Speakers"])

# --- HOME ---
with tab1:
    st.info("🔴 **Live Update:** Inauguration Ceremony starting soon.")
    st.write("Welcome to the SSSIHL Brindavan Campus. Use the tabs above to navigate.")
    st.divider()
    st.button("📍 View Campus Map", use_container_width=True)

# --- AGENDA ---
with tab2:
    st.subheader("Schedule")
    if not df_agenda.empty:
        st.dataframe(df_agenda, use_container_width=True, hide_index=True)
    else:
        st.warning("agenda.csv not found or empty.")

# --- STUDENTS ---
with tab3:
    st.subheader("MBA Talent")
    if not df_students.empty:
        # This part is now 'safe' - it looks for the name column regardless of what you named it
        name_col = next((c for c in df_students.columns if 'name' in c.lower()), df_students.columns[0])
        spec_col = next((c for c in df_students.columns if 'spec' in c.lower()), df_students.columns[1] if len(df_students.columns)>1 else df_students.columns[0])
        
        for _, row in df_students.iterrows():
            with st.container(border=True):
                st.write(f"**{row[name_col]}**")
                st.caption(f"Area: {row[spec_col]}")
                # Only show buttons if the columns exist
                if 'Resume' in df_students.columns:
                    st.link_button("View Resume", str(row['Resume']))
    else:
        st.error("students.csv is missing.")

# --- SPEAKERS ---
with tab4:
    st.subheader("Speakers")
    if not df_speakers.empty:
        # Safe column detection
        spk_name = next((c for c in df_speakers.columns if 'name' in c.lower()), df_speakers.columns[0])
        
        for _, row in df_speakers.iterrows():
            with st.expander(f"{row[spk_name]}"):
                if 'Bio' in row: st.write(row['Bio'])
                if 'Designation' in row: st.caption(row['Designation'])
    else:
        st.error("speakers.csv is missing.")
