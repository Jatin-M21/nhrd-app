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
if 'current_tab' not in st.session_state: st.session_state.current_tab = "🏠 Home"

# --- UI STYLING ---
st.markdown("""
    <style>
    [data-testid="stHeader"] {display:none;}
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    
    /* Card Styling */
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #1A1C24 !important;
        border: 1px solid #262730 !important;
        border-radius: 15px !important;
        padding: 15px !important;
        margin-bottom: 10px;
    }
    
    /* Global Button Styling */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        border: 1px solid #FF4B4B;
        background-color: transparent;
        color: white;
    }
    .stButton>button:hover { background-color: #FF4B4B; color: white; }

    /* Nav Bar Styling */
    div[data-testid="stHorizontalBlock"] .stButton>button {
        height: 40px;
        font-size: 10px;
        padding: 0 2px;
        border-color: #262730;
        color: #9499A1;
    }
    
    /* The active tab highlight */
    .active-nav button {
        border-color: #FF4B4B !important;
        color: white !important;
        background-color: rgba(255, 75, 75, 0.1) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- TOP LEFT NAVIGATION (Home/Back) ---
nav_col1, nav_col2 = st.columns([1, 4])
with nav_col1:
    if st.session_state.view != 'main':
        if st.button("⬅️ Back"):
            st.session_state.view = 'main'
            st.rerun()
    elif st.session_state.current_tab != "🏠 Home":
        if st.button("🏠 Home"):
            st.session_state.current_tab = "🏠 Home"
            st.rerun()

# --- HEADER ---
if st.session_state.view == 'main':
    if os.path.exists("hero.png"):
        st.image("hero.png", use_container_width=True)
    st.title("NHRD SUMMIT 2026")

    # --- TAB NAVIGATION ---
    TAB_NAMES = ["🏠 Home", "📅 Agenda", "🎓 Students", "🎙️ Speakers", "🏫 SSSIHL"]
    nav_cols = st.columns(len(TAB_NAMES))
    for idx, tab_name in enumerate(TAB_NAMES):
        with nav_cols[idx]:
            # Apply active styling
            is_active = "active-nav" if st.session_state.current_tab == tab_name else ""
            st.markdown(f'<div class="{is_active}">', unsafe_allow_html=True)
            if st.button(tab_name, key=f"nav_{idx}"):
                st.session_state.current_tab = tab_name
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")

# --- MAIN CONTENT LOGIC ---
if st.session_state.view == 'main':
    active_tab = st.session_state.current_tab

    if active_tab == "🏠 Home":
        st.info("📢 **LIVE:** Summit in progress at SSSIHL Brindavan.")
        st.subheader("🕒 Happening Now")
        # Live Session Logic
        if not df_agenda.empty and 'Status' in df_agenda.columns:
            live = df_agenda[df_agenda['Status'].str.strip().str.lower() == 'live'].head(1)
            if not live.empty:
                row = live.iloc[0]
                with st.container(border=True):
                    st.markdown(f"**{row.get('Session Title')}**")
                    st.caption(f"📍 {row.get('Hall Location')} | 🕒 {row.get('Start Time')}")
            else:
                st.write("Use the navigation above to explore the Summit.")
        
        # Simple Clock
        ist_now = datetime.datetime.now() + datetime.timedelta(hours=5, minutes=30)
        st.caption(f"Local Time: {ist_now.strftime('%I:%M %p')} IST")

    elif active_tab == "📅 Agenda":
        for i, row in df_agenda.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                c1.markdown(f"**{row.get('Session Title')}**")
                c1.caption(f"🕒 {row.get('Start Time')} | 📍 {row.get('Hall Location')}")
                if c2.button("View", key=f"ag_{i}"):
                    st.session_state.selected_item = row.to_dict()
                    st.session_state.view = 'agenda_detail'
                    st.rerun()

    elif active_tab == "🎓 Students":
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
                    c1.image(row.get('photo', "https://cdn-icons-png.flaticon.com/512/149/149071.png"), width=60)
                    c2.markdown(f"**{name}**")
                    c2.caption(spec)
                    if st.button("Profile", key=f"st_{i}"):
                        st.session_state.selected_item = row.to_dict(); st.session_state.view = 'student_detail'; st.rerun()

    elif active_tab == "🎙️ Speakers":
        for i, row in df_speakers.iterrows():
            with st.container(border=True):
                cols = st.columns([1, 3])
                cols[0].image(row.get('Photo', "https://cdn-icons-png.flaticon.com/512/149/149071.png"), width=70)
                cols[1].markdown(f"**{row.get('Name')}**")
                cols[1].caption(f"{row.get('Job Title')} @ {row.get('Organization')}")
                if pd.notna(row.get('LinkedIn Profile')):
                    cols[1].link_button("LinkedIn", str(row.get('LinkedIn Profile')))

    elif active_tab == "🏫 SSSIHL":
        st.subheader("SSSIHL Brindavan Campus")
        img_path = "campus.jpg" if os.path.exists("campus.jpg") else "https://www.sssihl.edu.in/wp-content/uploads/2019/07/SSSIHL-Brindavan-Campus-1.jpg"
        st.image(img_path, use_container_width=True)
        st.write("Values-based integral education provided free of cost.")

# --- DETAIL PAGES ---
else:
    s = st.session_state.selected_item
    if st.session_state.view == 'student_detail':
        st.title(s.get('FULL Name'))
        st.caption(get_spec(s))
        st.divider()
        st.subheader("About")
        st.write(s.get('Brief Write-up (3 lines)', 'N/A'))
        if pd.notna(s.get('LinkedIn Profile Link')):
            st.link_button("🔗 LinkedIn Profile", str(s.get('LinkedIn Profile Link')))

    elif st.session_state.view == 'agenda_detail':
        st.title(s.get('Session Title'))
        st.caption(f"🕒 {s.get('Start Time')} | 📍 {s.get('Hall Location')}")
        st.divider()
        st.markdown(f"**Topic:** {s.get('Topic')}")
        st.markdown(f"**Speaker:** {s.get('Speaker Name')}")
        fb = s.get('Feedback_Link')
        if pd.notna(fb): st.link_button("⭐ Submit Feedback", str(fb), use_container_width=True)
