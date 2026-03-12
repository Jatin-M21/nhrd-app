import streamlit as st
import pandas as pd
import os
import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="NHRD Summit 2026", layout="centered")

# --- DATA LOADING ---
@st.cache_data(ttl=60)
def load_data(file):
    try: 
        df = pd.read_csv(file, encoding='utf-8-sig')
        df.columns = df.columns.str.strip() 
        return df
    except: 
        return pd.DataFrame()

df_agenda = load_data("agenda.csv")
df_students = load_data("students.csv")
df_speakers = load_data("speakers.csv")

# --- HELPER: Smart Specialization Logic ---
def get_spec(row_data):
    standalone = row_data.get('MBA Specialization (Select) (Standalone)')
    major = row_data.get('MBA Specialization (Major)')
    minor = row_data.get('MBA Specialization (Minor)')
    if pd.notna(standalone) and str(standalone).strip() != "" and str(standalone).lower() != "nan":
        return str(standalone)
    elif pd.notna(major) and str(major).strip() != "" and str(major).lower() != "nan":
        if pd.notna(minor) and str(minor).strip() != "" and str(minor).lower() != "nan":
            return f"{major} + {minor}"
        return str(major)
    return "MBA Student"

# --- SESSION STATE ---
if 'view' not in st.session_state: st.session_state.view = 'main'
if 'selected_item' not in st.session_state: st.session_state.selected_item = None

# --- UI STYLING ---
st.markdown("""
    <style>
    [data-testid="stHeader"] {display:none;}
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    
    /* Ensure Navigation Buttons are prominent */
    .nav-button-container {
        padding: 10px 0px;
    }

    .stTabs [data-baseweb="tab-list"] { gap: 4px; justify-content: center; background-color: #1A1C24; padding: 5px; border-radius: 12px; }
    .stTabs [data-baseweb="tab"] { height: 42px; background-color: transparent; border-radius: 8px; color: #9499A1; padding: 0 10px; font-size: 11px; border: none !important; }
    .stTabs [aria-selected="true"] { background-color: #FF4B4B !important; color: white !important; box-shadow: 0px 4px 10px rgba(255, 75, 75, 0.3); }
    
    div[data-testid="stVerticalBlockBorderWrapper"] > div { background-color: #1A1C24 !important; border: 1px solid #262730 !important; border-radius: 15px !important; padding: 15px !important; margin-bottom: 10px; }
    
    .stButton>button { width: 100%; border-radius: 8px; border: 1px solid #FF4B4B; background-color: transparent; color: white; font-weight: 500; }
    .stButton>button:hover { background-color: #FF4B4B; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- TOP NAVIGATION (BACK / HOME) ---
# Check if we need a button at the very top
if st.session_state.view != 'main':
    if st.button("⬅️ Back to List"):
        st.session_state.view = 'main'
        st.session_state.selected_item = None
        st.rerun()
else:
    # On main view, we only show "Go to Home Tab" if the user might be lost
    # Since tabs are always visible, a "Home" button at top is often redundant, 
    # but I'm adding it here as a clear 'Reset' button as requested.
    c1, c2 = st.columns([1, 3])
    with c1:
        if st.button("🏠 Reset"):
            st.rerun()

# --- CONTENT ---
if st.session_state.view == 'main':
    if os.path.exists("hero.png"):
        st.image("hero.png", use_container_width=True)
    st.title("NHRD SUMMIT 2026")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Home", "📅 Agenda", "🎓 Students", "🎙️ Speakers", "🏫 SSSIHL"])

    with tab1:
        st.info("📢 **LIVE:** Summit in progress at SSSIHL Brindavan.")
        st.subheader("🕒 Happening Now")
        if not df_agenda.empty and 'Status' in df_agenda.columns:
            live = df_agenda[df_agenda['Status'].str.strip().str.lower() == 'live'].head(1)
            if not live.empty:
                row = live.iloc[0]
                with st.container(border=True):
                    st.markdown(f"**{row.get('Session Title')}**")
                    st.caption(f"📍 {row.get('Hall Location')} | 🕒 {row.get('Start Time')}")
            else:
                st.write("Welcome! Use the tabs to navigate the summit.")

    with tab2: # Agenda
        for i, row in df_agenda.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([4, 1.2])
                c1.markdown(f"**{row.get('Session Title', 'Session')}**")
                c1.caption(f"🕒 {row.get('Start Time')} | 📍 {row.get('Hall Location')}")
                if pd.notna(row.get('Topic')): c1.markdown(f"*{row.get('Topic')}*")
                if c2.button("View", key=f"ag_{i}"):
                    st.session_state.selected_item = row.to_dict()
                    st.session_state.view = 'agenda_detail'
                    st.rerun()

    with tab3: # Students
        batch = st.radio("Batch:", ["All", "2nd Years", "1st Years"], horizontal=True)
        search = st.text_input("🔍 Search...")
        f_df = df_students.copy()
        if batch == "2nd Years": f_df = f_df[f_df['nn'].astype(str).str.startswith('24')]
        elif batch == "1st Years": f_df = f_df[f_df['nn'].astype(str).str.startswith('25')]

        for i, row in f_df.iterrows():
            name, spec = str(row.get('FULL Name')), get_spec(row)
            if search.lower() in name.lower() or search.lower() in spec.lower():
                with st.container(border=True):
                    c1, c2 = st.columns([1, 4])
                    img = row.get('photo') if pd.notna(row.get('photo')) else "https://cdn-icons-png.flaticon.com/512/149/149071.png"
                    c1.image(img, width=60)
                    c2.markdown(f"**{name}**")
                    c2.caption(spec)
                    if st.button("Profile", key=f"st_{i}"):
                        st.session_state.selected_item = row.to_dict(); st.session_state.view = 'student_detail'; st.rerun()

    with tab4: # Speakers
        for i, row in df_speakers.iterrows():
            with st.container(border=True):
                cols = st.columns([1, 3])
                cols[0].image(row.get('Photo', "https://cdn-icons-png.flaticon.com/512/149/149071.png"), width=80)
                cols[1].markdown(f"**{row.get('Name')}**")
                cols[1].caption(f"{row.get('Job Title')} at {row.get('Organization')}")
                ln = row.get('LinkedIn Profile')
                if pd.notna(ln): cols[1].link_button("LinkedIn", str(ln))

    with tab5: # SSSIHL
        st.subheader("SSSIHL Brindavan Campus")
        st.image("https://www.sssihl.edu.in/wp-content/uploads/2019/07/SSSIHL-Brindavan-Campus-1.jpg", use_container_width=True)
        st.write("Values-based integral education provided free of cost.")

# --- DETAIL PAGES ---
else:
    s = st.session_state.selected_item
    if st.session_state.view == 'student_detail':
        st.title(s.get('FULL Name'))
        st.markdown(f"#### {get_spec(s)}")
        st.divider()
        st.write(str(s.get('Brief Write-up (3 lines)', 'N/A')))
        if pd.notna(s.get('LinkedIn Profile Link')):
            st.link_button("🔗 LinkedIn", str(s.get('LinkedIn Profile Link')))

    elif st.session_state.view == 'agenda_detail':
        st.title(s.get('Session Title'))
        st.caption(f"🕒 {s.get('Start Time')} | 📍 {s.get('Hall Location')}")
        st.divider()
        st.subheader("📖 Topic")
        st.write(s.get('Topic'))
        st.subheader("🎙️ Speaker")
        st.write(s.get('Speaker Name'))
        fb = s.get('Feedback_Link')
        if pd.notna(fb): st.link_button("⭐ Feedback", str(fb), use_container_width=True)
