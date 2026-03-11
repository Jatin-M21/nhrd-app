import streamlit as st
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="NHRD Summit 2026", layout="centered")

# Custom CSS for the "Glide" Look
st.markdown("""
    <style>
    [data-testid="stHeader"] {display:none;}
    .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: #111; border-radius: 10px; color: white; padding: 0 20px;
    }
    .card { background-color: #1a1a1a; border-radius: 15px; padding: 15px; border: 1px solid #333; margin-bottom: 15px; }
    .back-btn { margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data(file):
    try: return pd.read_csv(file)
    except: return pd.DataFrame()

df_agenda = load_data("agenda.csv")
df_students = load_data("students.csv")
df_speakers = load_data("speakers.csv")

# Navigation State
if 'view' not in st.session_state: st.session_state.view = 'main'
if 'selected_item' not in st.session_state: st.session_state.selected_item = None

# --- TOP NAVIGATION / BACK BUTTON ---
if st.session_state.view != 'main':
    if st.button("⬅️ Back to List"):
        st.session_state.view = 'main'
        st.session_state.selected_item = None
        st.rerun()
else:
    st.title("NHRD SUMMIT 2026")
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 Home", "📅 Agenda", "🎓 Students", "🎙️ Speakers"])

# --- MAIN LIST VIEWS ---
if st.session_state.view == 'main':
    
    # TAB 1: HOME
    with tab1:
        st.info("📢 **LIVE:** Join us in the Auditorium for the Inaugural Ceremony.")
        with st.container(border=True):
            st.image("w=800")
            st.subheader("Welcome to Brindavan")
            st.write("Sri Sathya Sai Institute of Higher Learning")

    # TAB 2: AGENDA
    with tab2:
        if not df_agenda.empty:
            for i, row in df_agenda.iterrows():
                with st.container(border=True):
                    col1, col2 = st.columns([4, 1])
                    col1.markdown(f"**{row['Session Title']}**")
                    col1.caption(f"🕒 {row['Start Time']} | 📍 {row['Hall Location']}")
                    if col2.button("View", key=f"ag_{i}"):
                        st.session_state.view = 'agenda_detail'
                        st.session_state.selected_item = row
                        st.rerun()

    # TAB 3: STUDENTS (Detail View logic included)
    with tab3:
        search = st.text_input("🔍 Search Students...")
        if not df_students.empty:
            # Clean column names to handle the "FULL Name " space issue
            df_students.columns = df_students.columns.str.strip() 
            
            for i, row in df_students.iterrows():
                name = str(row.get('FULL Name', 'Student'))
                if search.lower() in name.lower():
                    with st.container(border=True):
                        c1, c2 = st.columns([1, 4])
                        # Check for lowercase 'photo' column
                        photo_url = row.get('photo') if pd.notna(row.get('photo')) else "https://cdn-icons-png.flaticon.com/512/149/149071.png"
                        c1.image(photo_url, width=60)
                        c2.markdown(f"**{name}**")
                        c2.caption(row.get('MBA Specialization (Select) (Standalone)', 'MBA Student'))
                        if st.button(f"View Profile", key=f"st_{i}"):
                            st.session_state.view = 'student_detail'
                            st.session_state.selected_item = row
                            st.rerun()

    # TAB 4: SPEAKERS
    with tab4:
        if not df_speakers.empty:
            for i, row in df_speakers.iterrows():
                with st.container(border=True):
                    cols = st.columns([1, 3])
                    # Speaker CSV uses 'Photo' with Capital P
                    spk_photo = row.get('Photo') if pd.notna(row.get('Photo')) else "https://cdn-icons-png.flaticon.com/512/149/149071.png"
                    cols[0].image(spk_photo, width=80)
                    cols[1].markdown(f"**{row['Name']}**")
                    cols[1].caption(f"{row.get('Job Title')} at {row.get('Organization')}")
                    cols[1].link_button("LinkedIn", str(row.get('LinkedIn Profile')))

# --- DETAIL PAGES ---

elif st.session_state.view == 'student_detail':
    s = st.session_state.selected_item
    # Header Info
    photo_url = s.get('photo') if pd.notna(s.get('photo')) else "https://cdn-icons-png.flaticon.com/512/149/149071.png"
    st.image(photo_url, width=150)
    st.title(s.get('FULL Name', 'Student Profile'))
    st.markdown(f"### {s.get('MBA Specialization (Select) (Standalone)')}")
    
    st.divider()
    
    # Content sections matching your Glide screenshot
    st.subheader("📝 About")
    st.write(s.get('Brief Write-up (3 lines)', 'No bio provided.'))
    
    st.subheader("🎓 Education")
    st.write(s.get('Education (Bachelors Degree)', 'N/A'))
    
    st.subheader("💼 Experience")
    st.write(f"**{s.get('Internship Company', 'N/A')}**")
    st.caption(f"Role: {s.get('InternshipRole', 'N/A')}")
    
    st.divider()
    if pd.notna(s.get('LinkedIn Profile Link')):
        st.link_button("🔗 View LinkedIn Profile", str(s.get('LinkedIn Profile Link')))

elif st.session_state.view == 'agenda_detail':
    a = st.session_state.selected_item
    if pd.notna(a.get('Session Image')):
        st.image(a['Session Image'], use_container_width=True)
    
    st.title(a['Session Title'])
    st.caption(f"🕒 {a['Start Time']} - {a['End Time']} | 📍 {a['Hall Location']}")
    
    st.divider()
    st.subheader("🎙️ Speaker")
    st.write(a.get('Speaker Name', 'To be announced'))
    
    st.subheader("📖 Topic & Description")
    st.write(a.get('Topic', 'No additional details available for this session.'))
