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
    .stTabs { display: none; }

    /* Pinned Top Navigation Bar */
    iframe[title="streamlit_option_menu.option_menu"] {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        z-index: 9999;
        background-color: #1A1C24;
        border-bottom: 1px solid #262730;
    }

    /* Padding to prevent content from hiding under navbar */
    .main-content {
        margin-top: 100px;
        padding-bottom: 50px;
    }

    /* Card Styling */
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #1A1C24 !important;
        border: 1px solid #262730 !important;
        border-radius: 16px !important;
        padding: 15px !important;
        margin-bottom: 12px !important;
    }
    
    .summit-title { font-size: 30px; font-weight: 800; margin-bottom: 0px; line-height: 1.2;}
    .summit-subtitle { color: #808495; font-size: 15px; margin-bottom: 20px; }
    .section-header { font-size: 20px; font-weight: 700; margin: 20px 0px 10px 0px; text-transform: uppercase; }
    
    .live-banner {
        background: linear-gradient(90deg, #1E3A5F 0%, #2D5A88 100%);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- TOP NAVIGATION ---
nav_options = ["Home", "Agenda", "Students", "Speakers", "SSSIHL"]
current_idx = nav_options.index(st.session_state.nav) if st.session_state.nav in nav_options else 0

selected = option_menu(
    menu_title=None,
    options=nav_options,
    icons=["house", "calendar", "mortarboard", "mic", "building"],
    default_index=current_idx,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#1A1C24", "border-radius": "0"},
        "icon": {"color": "#9499A1", "font-size": "18px"},
        "nav-link": {"font-size": "11px", "text-align": "center", "margin": "0px", "color": "#9499A1", "padding": "10px 0px"},
        "nav-link-selected": {"background-color": "transparent", "color": "#FF4B4B", "font-weight": "700"}
    }
)

if selected != st.session_state.nav:
    st.session_state.nav = selected
    st.session_state.view = 'main'
    st.rerun()

# --- CONTENT WRAPPER ---
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def get_spec(row_data):
    standalone = row_data.get('MBA Specialization (Select) (Standalone)')
    major = row_data.get('MBA Specialization (Major)')
    minor = row_data.get('MBA Specialization (Minor)')
    if pd.notna(standalone) and str(standalone).strip() and str(standalone).lower() != "nan":
        return str(standalone)
    elif pd.notna(major) and str(major).strip() and str(major).lower() != "nan":
        return f"{major} + {minor}" if pd.notna(minor) and str(minor).strip() else str(major)
    return "MBA Student"

# --- MAIN NAVIGATION LOGIC ---
if st.session_state.view == 'main':
    
    if st.session_state.nav == 'Home':
        st.markdown('<div class="live-banner"><b>📢 LIVE UPDATE</b><br>The event is starting at 9:00 AM. Please assemble in the Auditorium.</div>', unsafe_allow_html=True)
        # Using the hero image from your design
        if os.path.exists("hero.png"):
            st.image("hero.png", use_container_width=True)
        st.markdown('<div class="summit-title">NHRD SUMMIT 2026</div>', unsafe_allow_html=True)
        st.markdown('<div class="summit-subtitle">13th March 2026 | SSSIHL Brindavan Campus</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-header">🕒 HAPPENING NOW</div>', unsafe_allow_html=True)
        with st.container(border=True):
            c1, c2 = st.columns([1, 3])
            c1.image("https://cdn-icons-png.flaticon.com/512/3652/3652191.png", width=60)
            c2.markdown("**Welcome Note**")
            c2.caption("Auditorium")

    elif st.session_state.nav == 'Agenda':
        st.markdown('<div class="section-header">📅 SUMMIT AGENDA</div>', unsafe_allow_html=True)
        if df_agenda.empty: st.info("Agenda details will appear here.")
        for i, row in df_agenda.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                c1.markdown(f"**{row.get('Session Title', 'Session')}**")
                c1.caption(f"🕒 {row.get('Start Time', 'TBD')} | 📍 {row.get('Hall Location', 'TBD')}")
                if c2.button("View", key=f"ag_{i}"):
                    st.session_state.selected_item = row.to_dict()
                    st.session_state.view = 'agenda_detail'
                    st.rerun()

    elif st.session_state.nav == 'Students':
        st.markdown('<div class="section-header">🎓 STUDENT TALENT</div>', unsafe_allow_html=True)
        search = st.text_input("🔍 Search by Name or Specialization...")
        for i, row in df_students.iterrows():
            name, spec = str(row.get('FULL Name', 'Student')), get_spec(row)
            if search.lower() in name.lower() or search.lower() in spec.lower():
                with st.container(border=True):
                    c1, c2 = st.columns([1, 4])
                    img = row.get('photo') if pd.notna(row.get('photo')) else "https://cdn-icons-png.flaticon.com/512/149/149071.png"
                    c1.image(img, width=60)
                    c2.markdown(f"**{name}**")
                    c2.caption(spec)
                    if st.button("View Profile", key=f"st_{i}"):
                        st.session_state.selected_item = row.to_dict()
                        st.session_state.view = 'student_detail'
                        st.rerun()

    elif st.session_state.nav == 'Speakers':
        st.markdown('<div class="section-header">🎙️ FEATURED SPEAKERS</div>', unsafe_allow_html=True)
        if df_speakers.empty:
            st.warning("Speaker list is being updated. Please check back later.")
        else:
            for i, row in df_speakers.iterrows():
                with st.container(border=True):
                    c1, c2 = st.columns([1, 3])
                    img = row.get('Photo') if pd.notna(row.get('Photo')) else "https://cdn-icons-png.flaticon.com/512/149/149071.png"
                    c1.image(img, width=80)
                    c2.markdown(f"**{row.get('Name', 'Speaker')}**")
                    c2.caption(f"{row.get('Job Title', '')} \n\n {row.get('Organization', '')}")

    elif st.session_state.nav == 'SSSIHL':
        st.markdown('<div class="section-header">🏛️ ABOUT THE INSTITUTE</div>', unsafe_allow_html=True)
        # Using Brindavan campus image
        st.image("https://www.sssihl.edu.in/wp-content/uploads/2019/07/SSSIHL-Brindavan-Campus-1.jpg", use_container_width=True)
        st.markdown("""
        **Sri Sathya Sai Institute of Higher Learning (SSSIHL)** is a unique institution that provides quality education free of cost, focusing on character building along with Academic Excellence.
        
        **Brindavan Campus:**
        Located in Whitefield, Bengaluru, this campus is home to the Faculty of Management and Commerce. It fosters an environment where students combine modern business skills with human values.
        """)

# --- DETAIL VIEWS ---
elif st.session_state.view == 'student_detail':
    if st.button("⬅️ Back to List"):
        st.session_state.view = 'main'
        st.rerun()
    s = st.session_state.selected_item
    st.title(s.get('FULL Name', 'Profile'))
    st.write(f"**Specialization:** {get_spec(s)}")
    st.divider()
    st.write(str(s.get('Brief Write-up (3 lines)', 'No bio available.')))
    if pd.notna(s.get('LinkedIn Profile Link')):
        st.link_button("🔗 Connect on LinkedIn", str(s.get('LinkedIn Profile Link')))

elif st.session_state.view == 'agenda_detail':
    if st.button("⬅️ Back to Agenda"):
        st.session_state.view = 'main'
        st.rerun()
    s = st.session_state.selected_item
    st.title(s.get('Session Title'))
    st.info(f"📍 {s.get('Hall Location')} | 🕒 {s.get('Start Time')}")
    st.write(str(s.get('Event Summary', 'No additional details provided.')))

st.markdown('</div>', unsafe_allow_html=True)
