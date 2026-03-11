import streamlit as st
import pandas as pd
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="NHRD Summit 2026", layout="centered")

# Custom UI Styling
st.markdown("""
    <style>
    [data-testid="stHeader"] {display:none;}
    .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: #111; border-radius: 10px; color: white; padding: 0 20px;
    }
    .card { background-color: #1a1a1a; border-radius: 15px; padding: 15px; border: 1px solid #333; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

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

# --- SESSION STATE INITIALIZATION ---
if 'view' not in st.session_state: st.session_state.view = 'main'
if 'selected_item' not in st.session_state: st.session_state.selected_item = None

# --- TOP NAVIGATION ---
if st.session_state.view != 'main':
    if st.button("⬅️ Back to List"):
        st.session_state.view = 'main'
        st.session_state.selected_item = None
        st.rerun()
else:
    # Hero Section
    if os.path.exists("hero.png"):
        st.image("hero.png", use_container_width=True)
    
    st.title("NHRD SUMMIT 2026")
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 Home", "📅 Agenda", "🎓 Students", "🎙️ Speakers"])

# --- MAIN LIST VIEWS ---
if st.session_state.view == 'main':
    
    with tab1:
        st.info("📢 **LIVE:** Session starting in the Main Auditorium.")
        st.subheader("Welcome to SSSIHL")
        st.write("Brindavan Campus, March 13th, 2026.")

    with tab2:
        if not df_agenda.empty:
            for i, row in df_agenda.iterrows():
                with st.container(border=True):
                    col1, col2 = st.columns([4, 1])
                    col1.markdown(f"**{row.get('Session Title', 'Session')}**")
                    col1.caption(f"🕒 {row.get('Start Time')} | 📍 {row.get('Hall Location')}")
                    if col2.button("View", key=f"ag_{i}"):
                        st.session_state.selected_item = row.to_dict() # Force to Dictionary
                        st.session_state.view = 'agenda_detail'
                        st.rerun()

    with tab3:
        search = st.text_input("🔍 Search Students...")
        if not df_students.empty:
            for i, row in df_students.iterrows():
                name = str(row.get('FULL Name', 'Student'))
                if search.lower() in name.lower():
                    with st.container(border=True):
                        c1, c2 = st.columns([1, 4])
                        p_url = row.get('photo') if pd.notna(row.get('photo')) else "https://cdn-icons-png.flaticon.com/512/149/149071.png"
                        c1.image(p_url, width=60)
                        c2.markdown(f"**{name}**")
                        c2.caption(row.get('MBA Specialization (Select) (Standalone)', 'MBA Student'))
                        if st.button("View Profile", key=f"st_{i}"):
                            st.session_state.selected_item = row.to_dict() # Force to Dictionary
                            st.session_state.view = 'student_detail'
                            st.rerun()

    with tab4:
        if not df_speakers.empty:
            for i, row in df_speakers.iterrows():
                with st.container(border=True):
                    cols = st.columns([1, 3])
                    spk_photo = row.get('Photo') if pd.notna(row.get('Photo')) else "https://cdn-icons-png.flaticon.com/512/149/149071.png"
                    cols[0].image(spk_photo, width=80)
                    cols[1].markdown(f"**{row.get('Name')}**")
                    cols[1].caption(f"{row.get('Job Title')} at {row.get('Organization')}")
                    cols[1].link_button("LinkedIn", str(row.get('LinkedIn Profile')))

# --- DETAIL PAGES ---
else:
    s = st.session_state.selected_item
    
    # Validation check to prevent the 'str' object error
    if not isinstance(s, dict):
        st.session_state.view = 'main'
        st.rerun()

    if st.session_state.view == 'student_detail':
        p_url = s.get('photo') if pd.notna(s.get('photo')) else "https://cdn-icons-png.flaticon.com/512/149/149071.png"
        st.image(p_url, width=150)
        st.title(s.get('FULL Name', 'Profile'))
        st.markdown(f"#### {s.get('MBA Specialization (Select) (Standalone)')}")
        st.divider()
        st.subheader("📝 About")
        st.write(s.get('Brief Write-up (3 lines)', 'N/A'))
        st.subheader("🎓 Education")
        st.write(s.get('Education (Bachelors Degree)', 'N/A'))
        st.subheader("💼 Internship")
        st.write(f"**{s.get('Internship Company', 'N/A')}**")
        if pd.notna(s.get('LinkedIn Profile Link')):
            st.link_button("🔗 View LinkedIn", str(s.get('LinkedIn Profile Link')))

    elif st.session_state.view == 'agenda_detail':
        if pd.notna(s.get('Session Image')):
            st.image(s['Session Image'], use_container_width=True)
        st.title(s.get('Session Title'))
        st.caption(f"🕒 {s.get('Start Time')} - {s.get('End Time')} | 📍 {s.get('Hall Location')}")
        st.divider()
        st.subheader("🎙️ Speaker")
        st.write(s.get('Speaker Name', 'Various'))
        st.subheader("📖 Topic")
        st.write(s.get('Topic', 'No further details.'))
