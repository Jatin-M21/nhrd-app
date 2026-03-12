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
    
    /* Pinned Top Navigation */
    iframe[title="streamlit_option_menu.option_menu"] {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        z-index: 9999;
        background-color: #1A1C24;
        border-bottom: 1px solid #262730;
    }

    /* Padding to ensure content starts below the navbar */
    .main-content {
        margin-top: 85px;
        padding-bottom: 60px;
    }

    /* Card Layouts */
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #1A1C24 !important;
        border: 1px solid #262730 !important;
        border-radius: 12px !important;
        padding: 18px !important;
        margin-bottom: 10px !important;
    }
    
    .summit-header { font-size: 28px; font-weight: 800; margin-bottom: 5px; color: white; }
    .summit-sub { color: #808495; font-size: 14px; margin-bottom: 20px; }
    .section-label { font-size: 18px; font-weight: 700; margin: 15px 0px 10px 0px; color: #FF4B4B; }
    
    .live-alert {
        background: #1E3A5F;
        padding: 12px;
        border-radius: 10px;
        border-left: 5px solid #3498db;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- TOP NAVIGATION MENU ---
nav_options = ["Home", "Agenda", "Students", "Speakers", "SSSIHL"]
current_idx = nav_options.index(st.session_state.nav) if st.session_state.nav in nav_options else 0

selected = option_menu(
    menu_title=None,
    options=nav_options,
    icons=["house", "calendar", "mortarboard", "mic", "building"],
    default_index=current_idx,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#1A1C24"},
        "icon": {"color": "#9499A1", "font-size": "16px"},
        "nav-link": {"font-size": "11px", "color": "#9499A1", "padding": "12px 0px"},
        "nav-link-selected": {"background-color": "transparent", "color": "#FF4B4B"}
    }
)

if selected != st.session_state.nav:
    st.session_state.nav = selected
    st.session_state.view = 'main'
    st.rerun()

# --- CONTENT WRAPPER ---
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# --- HELPER: Student Specialization ---
def get_spec(row_data):
    standalone = row_data.get('MBA Specialization (Select) (Standalone)')
    major = row_data.get('MBA Specialization (Major)')
    minor = row_data.get('MBA Specialization (Minor)')
    if pd.notna(standalone) and str(standalone).strip() and str(standalone).lower() != "nan":
        return str(standalone)
    elif pd.notna(major) and str(major).strip() and str(major).lower() != "nan":
        return f"{major} + {minor}" if pd.notna(minor) and str(minor).strip() else str(major)
    return "MBA Student"

# --- RENDER LOGIC ---
if st.session_state.view == 'main':
    
    if st.session_state.nav == 'Home':
        st.markdown('<div class="live-alert"><b>📢 LIVE UPDATE</b><br>Summit in progress at SSSIHL Brindavan.</div>', unsafe_allow_html=True)
        if os.path.exists("hero.png"):
            st.image("hero.png", use_container_width=True)
        st.markdown('<div class="summit-header">NHRD SUMMIT 2026</div>', unsafe_allow_html=True)
        st.markdown('<div class="summit-sub">13th March 2026 | SSSIHL Brindavan Campus</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-label">🕒 HAPPENING NOW</div>', unsafe_allow_html=True)
        with st.container(border=True):
            c1, c2 = st.columns([1, 4])
            c1.image("https://cdn-icons-png.flaticon.com/512/3652/3652191.png", width=50)
            c2.markdown("**Welcome & Keynote**")
            c2.caption("Auditorium | Starting Now")

    elif st.session_state.nav == 'Agenda':
        st.markdown('<div class="section-label">📅 SUMMIT AGENDA</div>', unsafe_allow_html=True)
        if df_agenda.empty:
            st.info("Agenda details are being finalized.")
        else:
            for i, row in df_agenda.iterrows():
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1.2])
                    # Ensure columns match your agenda.csv
                    c1.markdown(f"**{row.get('Session Title', 'Unnamed Session')}**")
                    c1.caption(f"🕒 {row.get('Start Time', 'TBD')} | 📍 {row.get('Hall Location', 'Auditorium')}")
                    c1.markdown(f"*{row.get('Speaker Name', 'Guest Speaker')}*")
                    if c2.button("Details", key=f"ag_{i}"):
                        st.session_state.selected_item = row.to_dict()
                        st.session_state.view = 'agenda_detail'
                        st.rerun()

    elif st.session_state.nav == 'Students':
        st.markdown('<div class="section-label">🎓 MBA TALENT POOL</div>', unsafe_allow_html=True)
        search = st.text_input("🔍 Search by Name or Major...")
        for i, row in df_students.iterrows():
            name, spec = str(row.get('FULL Name', 'Student')), get_spec(row)
            if search.lower() in name.lower() or search.lower() in spec.lower():
                with st.container(border=True):
                    c1, c2 = st.columns([1, 4])
                    img = row.get('photo') if pd.notna(row.get('photo')) else "https://cdn-icons-png.flaticon.com/512/149/149071.png"
                    c1.image(img, width=60)
                    c2.markdown(f"**{name}**")
                    c2.caption(spec)
                    if st.button("View Resume", key=f"st_{i}"):
                        st.session_state.selected_item = row.to_dict()
                        st.session_state.view = 'student_detail'
                        st.rerun()

    elif st.session_state.nav == 'Speakers':
        st.markdown('<div class="section-label">🎙️ FEATURED SPEAKERS</div>', unsafe_allow_html=True)
        if df_speakers.empty:
            st.warning("Speaker details coming soon!")
        else:
            for i, row in df_speakers.iterrows():
                with st.container(border=True):
                    c1, c2 = st.columns([1, 3])
                    img = row.get('Photo') if pd.notna(row.get('Photo')) else "https://cdn-icons-png.flaticon.com/512/149/149071.png"
                    c1.image(img, width=80)
                    c2.markdown(f"**{row.get('Name', 'Speaker')}**")
                    c2.caption(f"{row.get('Job Title', '')} at {row.get('Organization', '')}")

    elif st.session_state.nav == 'SSSIHL':
        st.markdown('<div class="section-label">🏛️ SSSIHL BRINDAVAN</div>', unsafe_allow_html=True)
        st.image("https://www.sssihl.edu.in/wp-content/uploads/2019/07/SSSIHL-Brindavan-Campus-1.jpg", use_container_width=True)
        st.markdown("""
        **Sri Sathya Sai Institute of Higher Learning** provides quality education free of cost, 
        focusing on character building and excellence.
        
        **Brindavan Campus:** Home to the Faculty of Management and Commerce, blending 
        modern skills with human values.
        """)

# --- DETAIL VIEWS ---
elif st.session_state.view == 'student_detail':
    if st.button("⬅️ Back to List"):
        st.session_state.view = 'main'; st.rerun()
    s = st.session_state.selected_item
    st.title(s.get('FULL Name', 'Student Profile'))
    st.markdown(f"**Specialization:** {get_spec(s)}")
    st.divider()
    st.write(str(s.get('Brief Write-up (3 lines)', 'No bio provided.')))
    if pd.notna(s.get('LinkedIn Profile Link')):
        st.link_button("🔗 LinkedIn", str(s.get('LinkedIn Profile Link')))

elif st.session_state.view == 'agenda_detail':
    if st.button("⬅️ Back to Agenda"):
        st.session_state.view = 'main'; st.rerun()
    s = st.session_state.selected_item
    st.title(s.get('Session Title'))
    st.info(f"📍 {s.get('Hall Location')} | 🕒 {s.get('Start Time')}")
    st.write(f"**Speaker:** {s.get('Speaker Name', 'Guest')}")
    st.markdown(f"> {s.get('Event Summary', 'No additional description available.')}")

st.markdown('</div>', unsafe_allow_html=True)
