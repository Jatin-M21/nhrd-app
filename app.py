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
if 'active_tab' not in st.session_state: st.session_state.active_tab = "🏠 Home"

# --- UI STYLING ---
st.markdown("""
    <style>
    [data-testid="stHeader"] {display:none;}
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; justify-content: center; background-color: #1A1C24; padding: 5px; border-radius: 12px; }
    .stTabs [data-baseweb="tab"] { height: 42px; background-color: transparent; border-radius: 8px; color: #9499A1; padding: 0 10px; font-size: 12px; border: none !important; }
    .stTabs [aria-selected="true"] { background-color: #FF4B4B !important; color: white !important; box-shadow: 0px 4px 10px rgba(255, 75, 75, 0.3); }
    div[data-testid="stVerticalBlockBorderWrapper"] > div { background-color: #1A1C24 !important; border: 1px solid #262730 !important; border-radius: 15px !important; padding: 15px !important; margin-bottom: 10px; }
    .stButton>button { width: 100%; border-radius: 8px; border: 1px solid #FF4B4B; background-color: transparent; color: white; font-weight: 500; }
    .stButton>button:hover { background-color: #FF4B4B; color: white; }
    .stCaption { color: #808495 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- TOP NAVIGATION BUTTONS (HOME / BACK) ---
top_col1, top_col2 = st.columns([1, 4])
with top_col1:
    if st.session_state.view != 'main':
        if st.button("⬅️ Back"):
            st.session_state.view = 'main'
            st.session_state.selected_item = None
            st.rerun()
    elif st.session_state.active_tab != "🏠 Home":
        if st.button("🏠 Home"):
            st.session_state.active_tab = "🏠 Home"
            st.rerun()

# --- HERO & TITLE ---
if st.session_state.view == 'main':
    if os.path.exists("hero.png"):
        st.image("hero.png", use_container_width=True)
    st.title("NHRD SUMMIT 2026")

# --- MAIN VIEWS ---
if st.session_state.view == 'main':
    tabs = ["🏠 Home", "📅 Agenda", "🎓 Students", "🎙️ Speakers", "🏫 About SSSIHL"]
    # We use session state to control the active tab index
    active_idx = tabs.index(st.session_state.active_tab)
    
    t1, t2, t3, t4, t5 = st.tabs(tabs)
    
    # Update active tab in session state when user clicks manually
    # Note: Streamlit tabs don't perfectly sync back to index without a rerun, but this handles the Home button logic
    
    with t1:
        st.session_state.active_tab = "🏠 Home"
        st.info("📢 **LIVE:** Summit in progress at SSSIHL Brindavan.")
        st.subheader("🕒 Happening Now")
        if not df_agenda.empty and 'Status' in df_agenda.columns:
            live_session = df_agenda[df_agenda['Status'].str.strip().str.lower() == 'live'].head(1)
            if not live_session.empty:
                row = live_session.iloc[0]
                with st.container(border=True):
                    st.markdown(f"**{row.get('Session Title')}**")
                    st.caption(f"📍 {row.get('Hall Location')} | 🕒 {row.get('Start Time')}")
            else:
                st.write("Browse the tabs to explore the agenda and our MBA talent pool.")
        
        utc_now = datetime.datetime.now()
        ist_now = utc_now + datetime.timedelta(hours=5, minutes=30)
        st.caption(f"Last Data Sync: {ist_now.strftime('%I:%M %p')} (IST)")

    with t2:
        st.session_state.active_tab = "📅 Agenda"
        for i, row in df_agenda.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([4, 1.2])
                c1.markdown(f"**{row.get('Session Title', 'Session')}**")
                c1.caption(f"🕒 {row.get('Start Time', 'TBD')} | 📍 {row.get('Hall Location', 'TBD')}")
                if pd.notna(row.get('Topic')): c1.markdown(f"*{row.get('Topic')}*")
                if c2.button("View", key=f"ag_{i}"):
                    st.session_state.selected_item = row.to_dict()
                    st.session_state.view = 'agenda_detail'
                    st.rerun()

    with t3:
        st.session_state.active_tab = "🎓 Students"
        batch_filter = st.radio("Select Batch:", ["All", "2nd Years (Finals)", "1st Years (Juniors)"], horizontal=True)
        search = st.text_input("🔍 Search Talent...")
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

    with t4:
        st.session_state.active_tab = "🎙️ Speakers"
        for i, row in df_speakers.iterrows():
            with st.container(border=True):
                cols = st.columns([1, 3])
                cols[0].image(row.get('Photo', "https://cdn-icons-png.flaticon.com/512/149/149071.png"), width=80)
                cols[1].markdown(f"**{row.get('Name', 'Speaker')}**")
                cols[1].caption(f"{row.get('Job Title', '')} at {row.get('Organization', '')}")
                ln_link = row.get('LinkedIn Profile')
                if pd.notna(ln_link) and str(ln_link).strip() != "":
                    cols[1].link_button("LinkedIn", str(ln_link))

    with t5:
        st.session_state.active_tab = "🏫 About SSSIHL"
        st.subheader("Sri Sathya Sai Institute of Higher Learning")
        st.write("Values-based education provided free of cost.")
        st.markdown("### **Brindavan Campus**")
        st.write("Located in Whitefield, Bengaluru.")
        st.image("https://www.sssihl.edu.in/wp-content/uploads/2019/07/SSSIHL-Brindavan-Campus-1.jpg", use_container_width=True)

# --- DETAIL PAGES ---
else:
    s = st.session_state.selected_item
    if st.session_state.view == 'student_detail':
        st.title(s.get('FULL Name', 'Profile'))
        st.markdown(f"#### {get_spec(s)}")
        st.divider()
        st.subheader("📝 About")
        st.write(str(s.get('Brief Write-up (3 lines)', 'N/A')))
        if pd.notna(s.get('LinkedIn Profile Link')):
            st.link_button("🔗 LinkedIn Profile", str(s.get('LinkedIn Profile Link')))

    elif st.session_state.view == 'agenda_detail':
        st.title(s.get('Session Title', 'Event Session'))
        st.caption(f"🕒 {s.get('Start Time', 'TBD')} | 📍 {s.get('Hall Location', 'TBD')}")
        st.divider()
        st.subheader("📖 Topic")
        st.write(s.get('Topic', 'Join us for this session.'))
        st.subheader("🎙️ Speaker")
        st.write(s.get('Speaker Name', 'Various'))
        
        feedback_url = s.get('Feedback_Link')
        if pd.notna(feedback_url) and str(feedback_url).startswith("http"):
            st.link_button("⭐ Submit Session Feedback", str(feedback_url), use_container_width=True)
