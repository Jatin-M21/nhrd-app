#update
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
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #1A1C24 !important;
        border: 1px solid #262730 !important;
        border-radius: 15px !important;
        padding: 15px !important;
        transition: transform 0.2s ease-in-out;
        margin-bottom: 10px;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] > div:hover {
        border-color: #FF4B4B !important;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        border: 1px solid #FF4B4B;
        background-color: transparent;
        color: white;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: #FF4B4B;
        color: white;
    }
    .stCaption {
        color: #808495 !important;
    }

    /* Custom nav bar styling */
    div[data-testid="stHorizontalBlock"] .stButton>button {
        height: 42px;
        font-size: 11px;
        padding: 0 4px;
        border-color: #262730;
        color: #9499A1;
        border-radius: 8px;
    }
    div[data-testid="stHorizontalBlock"] .stButton>button:hover {
        border-color: #FF4B4B;
        color: white;
        background-color: transparent;
    }

    /* Home button - small subtle style */
    .home-row .stButton>button {
        width: auto !important;
        font-size: 12px;
        padding: 2px 10px;
        border-color: #444;
        color: #aaa;
        background-color: transparent;
    }
    .home-row .stButton>button:hover {
        background-color: #FF4B4B;
        border-color: #FF4B4B;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- REUSABLE HOME BUTTON ---
def home_button(key):
    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button("🏠 Home", key=key):
            st.session_state.current_tab = "🏠 Home"
            st.rerun()

# --- NAVIGATION ---
if st.session_state.view != 'main':
    if st.button("⬅️ Back to List"):
        st.session_state.view = 'main'
        st.session_state.selected_item = None
        st.rerun()
else:
    if os.path.exists("hero.png"):
        st.image("hero.png", use_container_width=True)
    st.title("NHRD SUMMIT 2026")

    # --- CUSTOM SESSION-STATE DRIVEN NAV BAR (replaces st.tabs) ---
    TAB_NAMES = ["🏠 Home", "📅 Agenda", "🎓 Students", "🎙️ Speakers", "🏫 About SSSIHL"]
    nav_cols = st.columns(len(TAB_NAMES))
    for idx, tab_name in enumerate(TAB_NAMES):
        with nav_cols[idx]:
            if st.button(tab_name, key=f"nav_{idx}"):
                st.session_state.current_tab = tab_name
                st.rerun()
    st.markdown("---")

    active_tab = st.session_state.current_tab

# --- MAIN VIEWS ---
if st.session_state.view == 'main':

    # ── HOME ──
    if active_tab == "🏠 Home":
        st.info("📢 **LIVE:** Summit in progress at SSSIHL Brindavan.")
        
        st.subheader("🕒 Happening Now")
        if not df_agenda.empty and 'Status' in df_agenda.columns:
            live_session = df_agenda[df_agenda['Status'].str.strip().str.lower() == 'live'].head(1)
            if not live_session.empty:
                row = live_session.iloc[0]
                with st.container(border=True):
                    st.markdown(f"**{row.get('Session Title')}**")
                    st.caption(f"📍 {row.get('Hall Location')} ")
            else:
                st.write("Browse the tabs to explore the agenda and our MBA talent pool.")
        else:
            st.write("Welcome! Explore the tabs for more information.")
        
        utc_now = datetime.datetime.now()
        ist_now = utc_now + datetime.timedelta(hours=5, minutes=30)
        current_time = ist_now.strftime("%I:%M %p")
        st.caption(f"Last Data Sync: {current_time} (IST)")

    # ── AGENDA ──
    elif active_tab == "📅 Agenda":
        home_button("home_agenda")

        for i, row in df_agenda.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                c1.markdown(f"**{row.get('Session Title', 'Session')}**")
                c1.caption(f"🕒 {row.get('Start Time', 'TBD')} | 📍 {row.get('Hall Location', 'TBD')}")
                if pd.notna(row.get('Topic')):
                    c1.markdown(f"*{row.get('Topic')}*")
                if c2.button("View", key=f"ag_{i}"):
                    st.session_state.selected_item = row.to_dict()
                    st.session_state.view = 'agenda_detail'
                    st.rerun()

    # ── STUDENTS ──
    elif active_tab == "🎓 Students":
        home_button("home_students")

        batch_filter = st.radio("Select Batch:", ["All", "2nd Years (Finals)", "1st Years (Juniors)"], horizontal=True)
        search = st.text_input("🔍 Search by Name or Specialization...")
        
        filtered_df = df_students.copy()
        
        if batch_filter == "2nd Years (Finals)":
            filtered_df = filtered_df[filtered_df['nn'].astype(str).str.startswith('24')]
        elif batch_filter == "1st Years (Juniors)":
            filtered_df = filtered_df[filtered_df['nn'].astype(str).str.startswith('25')]

        for i, row in filtered_df.iterrows():
            name = str(row.get('FULL Name', 'Student'))
            current_spec = get_spec(row)
            
            if search.lower() in name.lower() or search.lower() in current_spec.lower():
                with st.container(border=True):
                    c1, c2 = st.columns([1, 4])
                    img = row.get('photo') if pd.notna(row.get('photo')) else "https://cdn-icons-png.flaticon.com/512/149/149071.png"
                    c1.image(img, width=60)
                    c2.markdown(f"**{name}**")
                    c2.caption(current_spec)
                    if st.button("View Profile", key=f"st_{i}"):
                        st.session_state.selected_item = row.to_dict()
                        st.session_state.view = 'student_detail'
                        st.rerun()

    # ── SPEAKERS ──
    elif active_tab == "🎙️ Speakers":
        home_button("home_speakers")

        for i, row in df_speakers.iterrows():
            with st.container(border=True):
                cols = st.columns([1, 3])
                cols[0].image(row.get('Photo', "https://cdn-icons-png.flaticon.com/512/149/149071.png"), width=80)
                cols[1].markdown(f"**{row.get('Name', 'Speaker')}**")
                cols[1].caption(f"{row.get('Job Title', '')} at {row.get('Organization', '')}")
                ln_link = row.get('LinkedIn Profile')
                if pd.notna(ln_link) and str(ln_link).strip() != "":
                    cols[1].link_button("LinkedIn", str(ln_link))

    # ── ABOUT SSSIHL ──
    elif active_tab == "🏫 About SSSIHL":
        home_button("home_about")

        st.subheader("Sri Sathya Sai Institute of Higher Learning")
        st.markdown("### Integral Education for a Better World")
        st.write("SSSIHL is a unique university founded on the principle of providing values-based education. It offers high-quality education free of cost.")
       
        st.markdown("---")
        st.markdown("### **Brindavan Campus**")
        st.write("Located in Whitefield, Bengaluru, this campus fosters an environment where students combine modern business skills with human values.")
       
        if os.path.exists("campus.jpg"):
            st.image("campus.jpg", caption="SSSIHL Brindavan Campus", use_container_width=True)
        else:
            st.image("https://www.sssihl.edu.in/wp-content/uploads/2019/07/SSSIHL-Brindavan-Campus-1.jpg", caption="SSSIHL Brindavan Campus", use_container_width=True)
       
        st.divider()
        st.link_button("🌐 Visit Official Website", "https://www.sssihl.edu.in")

# --- DETAIL PAGES ---
else:
    s = st.session_state.selected_item
    if st.session_state.view == 'student_detail':
        detail_spec = get_spec(s)
        st.title(s.get('FULL Name', 'Profile'))
        st.markdown(f"#### {detail_spec}")
        st.divider()
        st.subheader("📝 About")
        st.write(str(s.get('Brief Write-up (3 lines)', 'N/A')))
        st.subheader("💼 Internship")
        st.write(f"**{str(s.get('Internship Company', 'N/A'))}** - {str(s.get('InternshipRole', 'N/A'))}")
        if pd.notna(s.get('LinkedIn Profile Link')):
            st.link_button("🔗 LinkedIn Profile", str(s.get('LinkedIn Profile Link')))

    elif st.session_state.view == 'agenda_detail':
        if os.path.exists("hero.png"): st.image("hero.png", use_container_width=True)
        st.title(s.get('Session Title', 'Event Session'))
        st.caption(f"🕒 {s.get('Start Time', 'TBD')} | 📍 {s.get('Hall Location', 'TBD')}")
        st.divider()
        
        st.subheader("📖 Topic")
        st.write(s.get('Topic', 'Join us for this session.'))
        
        st.subheader("🎙️ Speaker")
        st.write(s.get('Speaker Name', 'Various'))

        summary_text = s.get('Event Summary')
        if pd.notna(summary_text) and str(summary_text).strip() != "":
            st.subheader("📝 Session Summary")
            with st.container(border=True):
                st.write(str(summary_text))
        
        feedback_url = s.get('Feedback_Link')
        if pd.notna(feedback_url) and str(feedback_url).startswith("http"):
            st.link_button("⭐ Submit Session Feedback", str(feedback_url), use_container_width=True)
            st.info("Your feedback helps us improve the summit experience!")
