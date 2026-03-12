import streamlit as st
import pandas as pd
import os
from streamlit_option_menu import option_menu

# --- PAGE CONFIG ---
st.set_page_config(page_title="NHRD Summit 2026", layout="centered", initial_sidebar_state="collapsed")

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

# --- SESSION STATE ---
if 'nav' not in st.session_state: st.session_state.nav = 'Home'
if 'view' not in st.session_state: st.session_state.view = 'main'
if 'selected_item' not in st.session_state: st.session_state.selected_item = None

# --- UI STYLING ---
st.markdown("""
    <style>
    [data-testid="stHeader"] {display:none;}
    .stApp { background-color: #0E1117; color: white; }
    
    iframe[title="streamlit_option_menu.option_menu"] {
        position: fixed; top: 0; left: 0; width: 100%; z-index: 9999;
        background-color: #1A1C24; border-bottom: 1px solid #262730;
    }

    .main-content { margin-top: 100px; padding-bottom: 80px; }

    /* Card Styling */
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #1A1C24 !important;
        border: 1px solid #262730 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        margin-bottom: 15px !important;
    }
    
    .section-label { font-size: 20px; font-weight: 700; margin-bottom: 15px; color: #FF4B4B; text-transform: uppercase; }
    .br-title { font-size: 24px; font-weight: 800; color: #FF4B4B; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- TOP NAVIGATION ---
nav_options = ["Home", "Agenda", "Students", "Speakers", "SSSIHL"]
selected = option_menu(
    menu_title=None, options=nav_options,
    icons=["house", "calendar", "mortarboard", "mic", "building"],
    default_index=nav_options.index(st.session_state.nav),
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#1A1C24"},
        "nav-link": {"font-size": "11px", "color": "#9499A1", "padding": "12px 0px"},
        "nav-link-selected": {"background-color": "transparent", "color": "#FF4B4B"}
    }
)

if selected != st.session_state.nav:
    st.session_state.nav = selected
    st.session_state.view = 'main'
    st.rerun()

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# --- HELPERS ---
def get_spec(row_data):
    standalone = row_data.get('MBA Specialization (Select) (Standalone)')
    major = row_data.get('MBA Specialization (Major)')
    minor = row_data.get('MBA Specialization (Minor)')
    if pd.notna(standalone) and str(standalone).strip(): return str(standalone)
    if pd.notna(major) and str(major).strip():
        return f"{major} + {minor}" if pd.notna(minor) and str(minor).strip() else str(major)
    return "MBA Student"

# --- RENDER LOGIC ---
if st.session_state.view == 'main':
    
    if st.session_state.nav == 'Home':
        if os.path.exists("hero.png"): st.image("hero.png", use_container_width=True)
        st.markdown('<h1 style="margin-bottom:0;">NHRD SUMMIT 2026</h1>', unsafe_allow_html=True)
        st.caption("13th March 2026 | SSSIHL Brindavan Campus")
        
        st.markdown('<div class="section-label">🕒 HAPPENING NOW</div>', unsafe_allow_html=True)
        if not df_agenda.empty and 'Status' in df_agenda.columns:
            live = df_agenda[df_agenda['Status'].str.lower() == 'live'].head(1)
            if not live.empty:
                row = live.iloc[0]
                with st.container(border=True):
                    st.markdown(f"### {row.get('Session Title')}")
                    st.caption(f"📍 {row.get('Hall Location')} | {row.get('Start Time')}")

    elif st.session_state.nav == 'Agenda':
        st.markdown('<div class="section-label">📅 SUMMIT AGENDA</div>', unsafe_allow_html=True)
        for i, row in df_agenda.iterrows():
            with st.container(border=True):
                st.markdown(f"### {row.get('Session Title')}")
                st.caption(f"🕒 {row.get('Start Time')} | 📍 {row.get('Hall Location')}")
                if pd.notna(row.get('Topic')): st.info(f"**Topic:** {row.get('Topic')}")
                
                # PER-SESSION FEEDBACK BUTTON
                col1, col2 = st.columns(2)
                if col1.button("View Details", key=f"det_{i}"):
                    st.session_state.selected_item = row.to_dict(); st.session_state.view = 'agenda_detail'; st.rerun()
                if col2.link_button("⭐ Feedback", f"https://your-form-url.com?session={row.get('Session Title')}"):
                    pass

    elif st.session_state.nav == 'Speakers':
        st.markdown('<div class="section-label">🎙️ FEATURED SPEAKERS</div>', unsafe_allow_html=True)
        for i, row in df_speakers.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([1, 3])
                img = row.get('Photo') if pd.notna(row.get('Photo')) else "https://cdn-icons-png.flaticon.com/512/149/149071.png"
                c1.image(img, width=100)
                c2.markdown(f"### {row.get('Name')}")
                c2.write(f"**{row.get('Job Title')}**")
                c2.caption(row.get('Organization'))
                # LinkedIn Logic
                if pd.notna(row.get('LinkedIn')):
                    c2.link_button("🔗 LinkedIn Profile", str(row.get('LinkedIn')))

    elif st.session_state.nav == 'SSSIHL':
        # FIXED: Info and Image for Brindavan Campus
        st.markdown('<div class="br-title">🏛️ SSSIHL BRINDAVAN</div>', unsafe_allow_html=True)
        st.image("https://www.sssihl.edu.in/wp-content/uploads/2019/07/SSSIHL-Brindavan-Campus-1.jpg", caption="SSSIHL Brindavan Campus", use_container_width=True)
        st.markdown("""
        **Sri Sathya Sai Institute of Higher Learning** provides quality education free of cost, focusing on character building along with Academic Excellence.

        **Brindavan Campus:** Located in Whitefield, Bengaluru, this campus is home to the Faculty of Management and Commerce. It fosters an environment where students combine modern business skills with human values.
        """)

    elif st.session_state.nav == 'Students':
        st.markdown('<div class="section-label">🎓 MBA TALENT</div>', unsafe_allow_html=True)
        for i, row in df_students.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([1, 4])
                img = row.get('photo') if pd.notna(row.get('photo')) else "https://cdn-icons-png.flaticon.com/512/149/149071.png"
                c1.image(img, width=70)
                c2.markdown(f"**{row.get('FULL Name')}**")
                c2.caption(get_spec(row))
                if st.button("View Resume", key=f"st_{i}"):
                    st.session_state.selected_item = row.to_dict(); st.session_state.view = 'student_detail'; st.rerun()

# --- DETAIL VIEWS ---
elif st.session_state.view == 'agenda_detail':
    if st.button("⬅️ Back"): st.session_state.view = 'main'; st.rerun()
    s = st.session_state.selected_item
    st.title(s.get('Session Title'))
    st.info(f"📍 {s.get('Hall Location')} | 🕒 {s.get('Start Time')}")
    if pd.notna(s.get('Topic')): st.subheader(f"Topic: {s.get('Topic')}")
    st.write(f"**Speaker:** {s.get('Speaker Name')}")
    st.markdown(f"**Summary:** {s.get('Event Summary')}")
