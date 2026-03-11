import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="NHRD Summit 2026", layout="centered")

# --- DATA LOADING (GitHub-Proof) ---
@st.cache_data(ttl=60) 
def load_data(file_path):
    try: 
        df = pd.read_csv(file_path, skip_blank_lines=True, encoding='utf-8-sig')
        df = df.dropna(how='all') 
        df.columns = df.columns.str.strip() 
        return df
    except:
        return pd.DataFrame()

df_agenda = load_data("agenda.csv")
df_students = load_data("students.csv")
df_speakers = load_data("speakers.csv")

# --- HELPER: Specialization Logic ---
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
    .stTabs [data-baseweb="tab-list"] { gap: 5px; justify-content: center; }
    .stTabs [data-baseweb="tab"] {
        height: 45px; background-color: #111; border-radius: 8px; color: white; padding: 0 10px;
        font-size: 14px;
    }
    div.stButton > button { border-radius: 10px; width: 100%; background-color: #1a1a1a; border: 1px solid #333; }
    div.stButton > button:hover { border-color: #ff4b4b; }
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
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Home", "📅 Agenda", "🎓 Students", "🎙️ Speakers", "🏫 About SSSIHL"])

    with tab1:
        st.subheader("Welcome")
        st.info("📍 **Venue:** SSSIHL, Brindavan Campus.")
        st.write("Welcome to the NHRD HR Summit. Explore the tabs to navigate the event details.")
        st.divider()
        st.caption(f"App synced with GitHub at {datetime.now().strftime('%H:%M:%S')}")

    with tab2:
        if not df_agenda.empty:
            for i, row in df_agenda.iterrows():
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    c1.markdown(f"**{row.get('Session Title', 'Session')}**")
                    c1.caption(f"🕒 {row.get('Start Time', 'TBD')} | 📍 {row.get('Hall Location', 'TBD')}")
                    if c2.button("View", key=f"ag_{i}"):
                        st.session_state.selected_item = row.to_dict()
                        st.session_state.view = 'agenda_detail'
                        st.rerun()

    with tab3:
        if not df_students.empty:
            batch_filter = st.radio("Batch:", ["All", "2nd Years", "1st Years"], horizontal=True)
            search = st.text_input("🔍 Search Students...")
            
            filtered_df = df_students.copy()
            if batch_filter == "2nd Years":
                filtered_df = filtered_df[filtered_df['nn'].astype(str).str.startswith('24')]
            elif batch_filter == "1st Years":
                filtered_df = filtered_df[filtered_df['nn'].astype(str).str.startswith('25')]

            for i, row in filtered_df.iterrows():
                name = str(row.get('FULL Name', 'Student'))
                spec = get_spec(row)
                if search.lower() in name.lower() or search.lower() in spec.lower():
                    with st.container(border=True):
                        sc1, sc2 = st.columns([1, 4])
                        # Safety check for photo
                        photo = row.get('photo')
                        photo_url = str(photo) if pd.notna(photo) else "https://cdn-icons-png.flaticon.com/512/149/149071.png"
                        sc1.image(photo_url, width=65)
                        sc2.markdown(f"**{name}**")
                        sc2.caption(spec)
                        if st.button("View Profile", key=f"st_{i}"):
                            st.session_state.selected_item = row.to_dict()
                            st.session_state.view = 'student_detail'
                            st.rerun()

    with tab4:
        if not df_speakers.empty:
            for i, row in df_speakers.iterrows():
                with st.container(border=True):
                    sc1, sc2 = st.columns([1, 3])
                    s_photo = row.get('Photo')
                    s_photo_url = str(s_photo) if pd.notna(s_photo) else "https://cdn-icons-png.flaticon.com/512/149/149071.png"
                    sc1.image(s_photo_url, width=80)
                    sc2.markdown(f"**{row.get('Name', 'Speaker')}**")
                    sc2.caption(f"{row.get('Job Title', '')} at {row.get('Organization', '')}")
                    if pd.notna(row.get('LinkedIn Profile')):
                        sc2.link_button("LinkedIn", str(row.get('LinkedIn Profile')))

    with tab5:
        st.subheader("Sri Sathya Sai Institute of Higher Learning")
        st.write("SSSIHL provides values-based integral education at the Brindavan Campus.")
        if os.path.exists("campus.png"):
            st.image("campus.png", caption="SSSIHL Brindavan Campus", use_container_width=True)
        st.divider()
        st.link_button("🌐 Visit Official Website", "https://www.sssihl.edu.in")

# --- DETAIL PAGES (WHERE THE ERRORS WERE) ---
else:
    s = st.session_state.selected_item
    
    if st.session_state.view == 'student_detail':
        current_spec = get_spec(s)
        # Fix for AttributeError: wrap photo in str()
        st.title(str(s.get('FULL Name', 'Profile')))
        st.markdown(f"#### {current_spec}")
        st.divider()
        st.subheader("📝 About")
        st.write(str(s.get('Brief Write-up (3 lines)', 'N/A')))
        st.subheader("💼 Internship")
        st.write(f"**{str(s.get('Internship Company', 'N/A'))}** - {str(s.get('InternshipRole', 'N/A'))}")
        if pd.notna(s.get('LinkedIn Profile Link')):
            st.link_button("🔗 LinkedIn Profile", str(s.get('LinkedIn Profile Link')))

    elif st.session_state.view == 'agenda_detail':
        if os.path.exists("hero.png"): st.image("hero.png", use_container_width=True)
        st.title(str(s.get('Session Title', 'Event Session')))
        st.caption(f"🕒 {str(s.get('Start Time', 'TBD'))} | 📍 {str(s.get('Hall Location', 'TBD'))}")
        st.divider()
        st.subheader("🎙️ Speaker")
        st.write(str(s.get('Speaker Name', 'Various Speakers')))
        st.subheader("📖 Topic")
        st.write(str(s.get('Topic', 'Join us for this session.')))
