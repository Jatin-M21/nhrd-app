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
    .stTabs [data-baseweb="tab-list"] { gap: 8px; justify-content: center; }
    .stTabs [data-baseweb="tab"] {
        height: 45px; background-color: #111; border-radius: 8px; color: white; padding: 0 15px;
    }
    .stButton>button { border-radius: 10px; }
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
    # Updated to include the 5th tab
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Home", "📅 Agenda", "🎓 Students", "🎙️ Speakers", "🏫 About SSSIHL"])

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
                c1.caption(f"🕒 {row.get('Start Time', 'TBD')} | 📍 {row.get('Hall Location', 'TBD')}")
                if c2.button("View", key=f"ag_{i}"):
                    st.session_state.selected_item = row.to_dict()
                    st.session_state.view = 'agenda_detail'
                    st.rerun()

    with tab3: # Students
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

    with tab4: # Speakers
        for i, row in df_speakers.iterrows():
            with st.container(border=True):
                cols = st.columns([1, 3])
                cols[0].image(row.get('Photo', "https://cdn-icons-png.flaticon.com/512/149/149071.png"), width=80)
                cols[1].markdown(f"**{row.get('Name', 'Speaker')}**")
                cols[1].caption(f"{row.get('Job Title', '')} at {row.get('Organization', '')}")
                if pd.notna(row.get('LinkedIn Profile')):
                    cols[1].link_button("LinkedIn", str(row.get('LinkedIn Profile')))

    with tab5: # About SSSIHL
        st.subheader("Sri Sathya Sai Institute of Higher Learning")
        st.write("""
        **Integral Education for a Better World**
        
        SSSIHL is a unique university founded on the principle of providing values-based education. 
        It offers high-quality education free of cost, focusing on character building along with 
Character Excellence.
        
        **Brindavan Campus:**
        Located in Whitefield, Bengaluru, this campus is home to the Faculty of Management 
        and Commerce. It fosters an environment where students combine modern business skills 
        with human values.
        """)
        
        if os.path.exists("campus.png"):
            st.image("campus.png", caption="SSSIHL Brindavan Campus", use_container_width=True)
        
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
        st.subheader("🎙️ Speaker")
        st.write(s.get('Speaker Name', 'Various'))
        st.subheader("📖 Topic")
        st.write(s.get('Topic', 'Join us for this session.'))
