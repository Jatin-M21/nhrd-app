import streamlit as st
import pandas as pd

# --- APP CONFIG ---
st.set_page_config(page_title="NHRD Summit 2026", layout="centered")

# Custom CSS for the "Mobile App" look
st.markdown("""
    <style>
    [data-testid="stHeader"] {display:none;}
    .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: #111; border-radius: 10px; color: white; padding: 0 20px;
    }
    .card {
        background-color: #1a1a1a; border-radius: 15px; padding: 15px; margin-bottom: 10px; border: 1px solid #333;
    }
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

# Navigation State: This tracks if we are looking at a specific "Detail Page"
if 'view' not in st.session_state: st.session_state.view = 'list'
if 'item_data' not in st.session_state: st.session_state.item_data = None

# --- NAVIGATION HEADER ---
if st.session_state.view != 'list':
    if st.button("⬅️ Back"):
        st.session_state.view = 'list'
        st.rerun()
else:
    st.title("NHRD SUMMIT 2026")
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 Home", "📅 Agenda", "🎓 Students", "🎙️ Speakers"])

# --- TAB 1: HOME ---
if st.session_state.view == 'list':
    with tab1:
        st.error("📢 **LIVE UPDATE:** Assemble in the Auditorium for the Keynote.")
        st.subheader("🕒 HAPPENING NOW")
        with st.container(border=True):
            st.image("https://images.unsplash.com/photo-1475721027785-f74dea0f779f?w=800")
            st.markdown("### Welcome Note")
            st.caption("📍 Auditorium")

# --- TAB 2: AGENDA (List) ---
    with tab2:
        if not df_agenda.empty:
            for i, row in df_agenda.iterrows():
                with st.container(border=True):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**{row['Session Title']}**")
                        st.caption(f"🕒 {row['Start Time']} | 📍 {row['Hall Location']}")
                    with col2:
                        if st.button("View", key=f"ag_{i}"):
                            st.session_state.view = 'agenda_detail'
                            st.session_state.item_data = row
                            st.rerun()

# --- TAB 3: STUDENTS (List) ---
    with tab3:
        if not df_students.empty:
            search = st.text_input("🔍 Search Student Talent...")
            for i, row in df_students.iterrows():
                if search.lower() in str(row['FULL Name']).lower():
                    with st.container(border=True):
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"**{row['FULL Name']}**")
                            st.caption(f"🎯 {row['MBA Specialization (Select) (Standalone)']}")
                        with col2:
                            if st.button("Info", key=f"st_{i}"):
                                st.session_state.view = 'student_detail'
                                st.session_state.item_data = row
                                st.rerun()

# --- TAB 4: SPEAKERS (List) ---
    with tab4:
        if not df_speakers.empty:
            for i, row in df_speakers.iterrows():
                with st.container(border=True):
                    st.image(row['Photo'], width=100)
                    st.markdown(f"### {row['Name']}")
                    st.caption(f"{row['Job Title']} @ {row['Organization']}")
                    st.link_button("LinkedIn Profile", row['LinkedIn Profile'])

# --- DETAIL PAGES ---
elif st.session_state.view == 'student_detail':
    data = st.session_state.item_data
    st.image("https://cdn-icons-png.flaticon.com/512/149/149071.png", width=150)
    st.title(data['FULL Name'])
    st.markdown(f"**Specialization:** {data['MBA Specialization (Select) (Standalone)']}")
    st.divider()
    st.subheader("About")
    st.write(data['Brief Write-up (3 lines)'])
    st.subheader("Experience")
    st.write(f"**Internship:** {data['Internship Company']} ({data['InternshipRole']})")
    st.link_button("🔗 View LinkedIn Profile", str(data['LinkedIn Profile Link']))

elif st.session_state.view == 'agenda_detail':
    data = st.session_state.item_data
    if pd.notna(data['Session Image']): st.image(data['Session Image'])
    st.title(data['Session Title'])
    st.caption(f"📅 {data['Date']} | 🕒 {data['Start Time']} - {data['End Time']}")
    st.divider()
    st.subheader("Speaker")
    st.write(data['Speaker Name'])
    st.subheader("Topic")
    st.write(data['Topic'])
