import streamlit as st
import pandas as pd
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="NHRD Summit 2026", layout="centered")

# --- DATA LOADING ---
@st.cache_data
def load_data(file):
    try: 
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip() 
        return df
    except: 
        return pd.DataFrame()

df_agenda = load_data("agenda.csv")
df_students = load_data("students.csv")
df_speakers = load_data("speakers.csv")

# --- HELPER: Smart Specialization Logic ---
def get_spec(row):
    # This function is now the single source of truth for both List and Detail views
    standalone = row.get('MBA Specialization (Select) (Standalone)')
    major = row.get('MBA Specialization (Major)')
    minor = row.get('MBA Specialization (Minor)')
    
    if pd.notna(standalone) and str(standalone).strip() != "":
        return str(standalone)
    elif pd.notna(major) and str(major).strip() != "":
        if pd.notna(minor) and str(minor).strip() != "":
            return f"{major} + {minor}"
        return str(major)
    return "MBA Student"

# --- SESSION STATE & NAVIGATION ---
if 'view' not in st.session_state: st.session_state.view = 'main'
if 'selected_item' not in st.session_state: st.session_state.selected_item = None

# Safety check: Force dictionary format
if st.session_state.selected_item and not isinstance(st.session_state.selected_item, dict):
    st.session_state.selected_item = None
    st.session_state.view = 'main'

# --- UI STYLING ---
st.markdown("""
    <style>
    [data-testid="stHeader"] {display:none;}
    .stTabs [data-baseweb="tab-list"] { gap: 8px; justify-content: center; }
    .stTabs [data-baseweb="tab"] {
        height: 45px; background-color: #111; border-radius: 8px; color: white; padding: 0 15px;
    }
    .card { background-color: #1a1a1a; border-radius: 12px; padding: 15px; border: 1px solid #333; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

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
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 Home", "📅 Agenda", "🎓 Students", "🎙️ Speakers"])

# --- MAIN VIEWS ---
if st.session_state.view == 'main':
    with tab1:
        st.info("📢 **LIVE:** Summit in progress at SSSIHL Brindavan.")
        st.subheader("Welcome")
        st.write("Browse the tabs to explore the agenda and our MBA talent pool.")

    with tab2: # Agenda
        for i, row in df_agenda.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                c1.markdown(f"**{row.get('Session Title', 'Session')}**")
                c1.caption(f"🕒 {row.get('Start Time')} | 📍 {row.get('Hall Location')}")
                if c2.button("View", key=f"ag_{i}"):
                    st.session_state.selected_item = row.to_dict()
                    st.session_state.view = 'agenda_detail'
                    st.rerun()

    with tab3: # Students
        search = st.text_input("🔍 Search Students...")
        for i, row in df_students.iterrows():
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

    with tab4: # Speakers
        for i, row in df_speakers.iterrows():
            with st.container(border=True):
                cols = st.columns([1, 3])
                cols[0].image(row.get('Photo', "https://cdn-icons-png.flaticon.com/512/149/149071.png"), width=80)
                cols[1].markdown(f"**{row.get('Name')}**")
                cols[1].caption(f"{row.get('Job Title')} at {row.get('Organization')}")
                cols[1].link_button("LinkedIn", str(row.get('LinkedIn Profile')))

# --- DETAIL PAGES ---
else:
    s = st.session_state.selected_item
    
    if st.session_state.view == 'student_detail':
        # Re-calculate the spec here so we don't need 'computed_spec' in the dict
        detail_spec = get_spec(s)
        
        st.image(s.get('photo', "https://cdn-icons-png.flaticon.com/512/149/149071.png"), width=120)
        st.title(s.get('FULL Name', 'Profile'))
        st.markdown(f"#### {detail_spec}")
        st.divider()
        st.subheader("📝 About")
        st.write(s.get('Brief Write-up (3 lines)', 'N/A'))
        st.subheader("🎓 Education")
        st.write(s.get('Education (Bachelors Degree)', 'N/A'))
        st.subheader("💼 Internship")
        st.write(f"**{s.get('Internship Company', 'N/A')}** - {s.get('InternshipRole', 'N/A')}")
        if pd.notna(s.get('LinkedIn Profile Link')):
            st.link_button("🔗 LinkedIn Profile", str(s.get('LinkedIn Profile Link')))

    elif st.session_state.view == 'agenda_detail':
        if pd.notna(s.get('Session Image')): st.image(s['Session Image'])
        st.title(s.get('Session Title'))
        st.caption(f"🕒 {s.get('Start Time')} | 📍 {s.get('Hall Location')}")
        st.divider()
        st.subheader("Speaker")
        st.write(s.get('Speaker Name', 'Various'))
        st.subheader("Topic")
        st.write(s.get('Topic', 'No details available.'))
