import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="NHRD Summit 2026", layout="centered")

# --- DATA LOADING (GitHub & KeyError Proof) ---
@st.cache_data(ttl=60) # Auto-refresh every 60 seconds
def load_data(file_path):
    try: 
        # utf-8-sig handles the 'hidden characters' that block GitHub editing
        df = pd.read_csv(file_path, skip_blank_lines=True, encoding='utf-8-sig')
        df = df.dropna(how='all') # Remove empty rows added by GitHub/Excel
        df.columns = df.columns.str.strip() 
        return df
    except:
        return pd.DataFrame()

df_agenda = load_data("agenda.csv")
df_students = load_data("students.csv")
df_speakers = load_data("speakers.csv")

# --- HELPER: Specialization Logic (Standalone vs Major/Minor) ---
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

# --- SESSION STATE & NAVIGATION ---
if 'view' not in st.session_state: st.session_state.view = 'main'
if 'selected_item' not in st.session_state: st.session_state.selected_item = None
if 'active_tab' not in st.session_state: st.session_state.active_tab = "🏠 Home"

# --- UI STYLING (The Custom CSS) ---
st.markdown("""
    <style>
    [data-testid="stHeader"] {display:none;}
    
    /* Center and Style Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; justify-content: center; }
    .stTabs [data-baseweb="tab"] {
        height: 45px; background-color: #111; border-radius: 8px; color: white; padding: 0 15px;
    }
    
    /* Glide-style Home Buttons */
    .home-btn-container div.stButton > button {
        height: 120px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 15px;
        border: 1px solid #333;
        background-color: #1a1a1a;
        white-space: pre-line; /* Allows emojis on top of text */
    }
    div.stButton > button:hover { border-color: #ff4b4b; background-color: #262626; }
    
    /* Standard Card Styling */
    .stContainer { border-radius: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION HELPER ---
def switch_tab(tab_name):
    st.session_state.active_tab = tab_name
    st.rerun()

# --- MAIN APP FLOW ---
if st.session_state.view == 'main':
    # Hero Image
    if os.path.exists("hero.png"):
        st.image("hero.png", use_container_width=True)
    
    st.title("NHRD SUMMIT 2026")
    
    # Render Tabs
    tab_list = ["🏠 Home", "📅 Agenda", "🎓 Students", "🎙️ Speakers"]
    tab_idx = tab_list.index(st.session_state.active_tab)
    tab1, tab2, tab3, tab4 = st.tabs(tab_list)

    # --- TAB 1: HOME (With Action Buttons) ---
    with tab1:
        st.markdown('<div class="home-btn-container">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        if col1.button("📅\n\nView\nAgenda", key="home_btn_ag"):
            switch_tab("📅 Agenda")
            
        if col2.button("🎓\n\nMBA\nTalent", key="home_btn_st"):
            switch_tab("🎓 Students")
            
        if col3.button("🎙️\n\nEvent\nSpeakers", key="home_btn_sp"):
            switch_tab("🎙️ Speakers")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        st.info("📍 **Venue:** SSSIHL, Brindavan Campus. \n\nWelcome to the NHRD HR Summit. Use the buttons above to navigate the event details.")
        st.caption(f"Last data sync from GitHub: {datetime.now().strftime('%H:%M:%S')}")

    # --- TAB 2: AGENDA ---
    with tab2:
        if not df_agenda.empty:
            for i, row in df_agenda.iterrows():
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    c1.markdown(f"**{row.get('Session Title', 'Session')}**")
                    c1.caption(f"🕒 {row.get('Start Time', 'TBD')} | 📍 {row.get('Hall Location', 'TBD')}")
                    if c2.button("View", key=f"ag_btn_{i}"):
                        st.session_state.selected_item = row.to_dict()
                        st.session_state.view = 'agenda_detail'
                        st.rerun()
        else:
            st.warning("Agenda data not found. Check agenda.csv on GitHub.")

    # --- TAB 3: STUDENTS (With 1st/2nd Year Filter) ---
    with tab3:
        if not df_students.empty:
            # Batch Filter
            batch_filter = st.radio("Filter Batch:", ["All", "2nd Years", "1st Years"], horizontal=True)
            search = st.text_input("🔍 Search Student Name...")
            
            filtered_df = df_students.copy()
            # Logic: Using 'nn' column prefix (24 for seniors, 25 for juniors)
            if batch_filter == "2nd Years":
                filtered_df = filtered_df[filtered_df['nn'].astype(str).str.startswith('24')]
            elif batch_filter == "1st Years":
                filtered_df = filtered_df[filtered_df['nn'].astype(str).str.startswith('25')]

            for i, row in filtered_df.iterrows():
                name = str(row.get('FULL Name', 'Student'))
                current_spec = get_spec(row)
                
                if search.lower() in name.lower() or search.lower() in current_spec.lower():
                    with st.container(border=True):
                        c1, c2 = st.columns([1, 4])
                        # Use default icon if photo link is empty
                        photo_url = row.get('photo') if pd.notna(row.get('photo')) else "https://cdn-icons-png.flaticon.com/512/149/149071.png"
                        c1.image(photo_url, width=65)
                        c2.markdown(f"**{name}**")
                        c2.caption(current_spec)
                        if st.button("View Profile", key=f"st_btn_{i}"):
                            st.session_state.selected_item = row.to_dict()
                            st.session_state.view = 'student_detail'
                            st.rerun()
        else:
            st.warning("Student data not found. Check students.csv.")

    # --- TAB 4: SPEAKERS ---
    with tab4:
        if not df_speakers.empty:
            for i, row in df_speakers.iterrows():
                with st.container(border=True):
                    sc1, sc2 = st.columns([1, 3])
                    sc1.image(row.get('Photo', "https://cdn-icons-png.flaticon.com/512/149/149071.png"), width=80)
                    sc2.markdown(f"**{row.get('Name', 'Speaker')}**")
                    sc2.caption(f"{row.get('Job Title', '')} at {row.get('Organization', '')}")
                    if pd.notna(row.get('LinkedIn Profile')):
                        sc2.link_button("LinkedIn", str(row.get('LinkedIn Profile')))
        else:
            st.warning("Speaker data not found. Check speakers.csv.")

# --- DETAIL PAGES ---
else:
    s = st.session_state.selected_item
    
    if st.button("⬅️ Back to List"):
        st.session_state.view = 'main'
        st.rerun()
    st.divider()

    if st.session_state.view == 'student_detail':
        detail_spec = get_spec(s)
        st.title(s.get('FULL Name', 'Profile'))
        st.markdown(f"#### {detail_spec}")
        
        col_a, col_b = st.columns(2)
        col_a.subheader("📝 About")
        col_a.write(s.get('Brief Write-up (3 lines)', 'N/A'))
        col_b.subheader("💼 Internship")
        col_b.write(f"**{s.get('Internship Company', 'N/A')}**\n{s.get('InternshipRole', 'N/A')}")
        
        st.subheader("🎓 Education")
        st.write(s.get('Education (Bachelors Degree)', 'N/A'))
        
        if pd.notna(s.get('LinkedIn Profile Link')):
            st.link_button("🔗 Connect on LinkedIn", str(s.get('LinkedIn Profile Link')))

    elif st.session_state.view == 'agenda_detail':
        st.title(s.get('Session Title', 'Event Session'))
        st.caption(f"🕒 {s.get('Start Time', 'TBD')} - {s.get('End Time', 'TBD')} | 📍 {s.get('Hall Location', 'TBD')}")
        st.divider()
        st.subheader("🎙️ Speaker")
        st.write(s.get('Speaker Name', 'Various Speakers'))
        st.subheader("📖 Topic")
        st.write(s.get('Topic', 'Join us for this insightful session.'))
