import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- הגדרות תצוגה ---
st.set_page_config(
    page_title="חרב שאול - כניסה למערכת",
    page_icon="⚔️",
    layout="wide"
)

# --- עיצוב CSS (כולל מסך כניסה) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="css"]  { font-family: 'Assistant', sans-serif; text-align: right; }
    .stButton>button { width: 100%; height: 3em; border-radius: 12px; font-weight: bold; }
    .login-box { background-color: #f0f2f6; padding: 20px; border-radius: 15px; border: 1px solid #d1d5db; }
    .sidebar-title { text-align: center; color: #1e3a8a; font-weight: bold; font-size: 1.5em; }
    .event-card { background-color: #fef2f2; border: 2px solid #ef4444; border-radius: 10px; padding: 10px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- ניהול נתונים בזיכרון ---
if 'all_data' not in st.session_state:
    st.session_state.all_data = pd.DataFrame(columns=['פלוגה', 'סוג_דיווח', 'פרטים', 'כמות', 'זמן'])
if 'personnel' not in st.session_state:
    st.session_state.personnel = pd.DataFrame(columns=['פלוגה', 'שם', 'סטטוס_גיוס', 'מיקום'])
if 'events' not in st.session_state:
    st.session_state.events = pd.DataFrame(columns=['זמן', 'פלוגה', 'סוג_אירוע', 'תיאור'])
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

# --- מילון סיסמאות והרשאות ---
passwords = {
    "magad123": "מג\"ד",
    "yarden123": "ירדן",
    "gilboa123": "גלבוע",
    "taanach123": "תענך",
    "hafoola123": "עפולה",
    "palsam123": "פלס\"ם אג\"ם"
}

# --- מסך כניסה ---
def login_screen():
    st.container()
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if os.path.exists("battalion_logo.png"):
            st.image("battalion_logo.png", width=150)
        st.title("כניסה למערכת חרב שאול")
        
        with st.form("login_form"):
            user_input = st.text_input("שם משתמש (תפקיד/מחלקה)")
            pass_input = st.text_input("סיסמה", type="password")
            submit_login = st.form_submit_button("התחבר")
            
            if submit_login:
                if pass_input in passwords:
                    st.session_state.logged_in = True
                    st.session_state.user_role = passwords[pass_input]
                    st.rerun()
                else:
                    st.error("סיסמה שגויה. נסה שוב.")

# --- תצוגת האפליקציה לאחר התחברות ---
if not st.session_state.logged_in:
    login_screen()
else:
    # סרגל צד מעוצב
    with st.sidebar:
        if os.path.exists("battalion_logo.png"):
            st.image("battalion_logo.png", width=100)
        st.markdown(f'<div class="sidebar-title">שלום, {st.session_state.user_role}</div>', unsafe_allow_html=True)
        
        if st.session_state.user_role == "מג\"ד":
            view_mode = st.radio("בחר תצוגה:", ["ניהול פלוגה", "תמונת מצב גדודית"], index=1)
        else:
            view_mode = "ניהול פלוגה"
            st.info(f"מחובר למערכת פלוגת {st.session_state.user_role}")
        
        if st.button("התנתק"):
            st.session_state.logged_in = False
            st.rerun()

    # לוגיקה לפי תפקיד
    if view_mode == "ניהול פלוגה":
        # אם זה מג"ד הוא בוחר פלוגה, אם זה מ"פ זה נעול על הפלוגה שלו
        if st.session_state.user_role == "מג\"ד":
            selected_company = st.selectbox("בחר פלוגה לניהול:", ["ירדן", "גלבוע", "תענך", "עפולה", "פלס\"ם אג\"ם"])
        else:
            selected_company = st.session_state.user_role
            
        st.title(f"📊 ניהול - פלוגת {selected_company}")
        
        tab1, tab2, tab3 = st.tabs(["💣 תחמושת", "👥 כוח אדם", "⚠️ אירועים"])
        
        with tab1:
            st.subheader("דיווח צריכה")
            col1, col2 = st.columns(2)
            with col1: item = st.selectbox("סוג", ["5.56", "7.62", "רימון", "לאו", "מטול"])
            with col2: amount = st.number_input("כמות", min_value=1, step=1)
            if st.button("שלח דיווח"):
                new_report = pd.DataFrame([[selected_company, "תחמושת", item, amount, datetime.now().strftime("%H:%M")]], columns=['פלוגה', 'סוג_דיווח', 'פרטים', 'כמות', 'זמן'])
                st.session_state.all_data = pd.concat([st.session_state.all_data, new_report], ignore_index=True)
                st.success("נרשם.")

        with tab2:
            st.subheader("עדכון כוח אדם")
            with st.form("p_form"):
                p_name = st.text_input("שם החייל")
                p_status = st.selectbox("סטטוס", ["מגוייס", "משוחרר/מילואים", "בצוו 8"])
                p_loc = st.selectbox("מיקום", ["ביחידה", "בבית", "אחר"])
                if st.form_submit_button("עדכן"):
                    st.session_state.personnel = st.session_state.personnel[st.session_state.personnel['שם'] != p_name]
                    new_p = pd.DataFrame([[selected_company, p_name, p_status, p_loc]], columns=['פלוגה', 'שם', 'סטטוס_גיוס', 'מיקום'])
                    st.session_state.personnel = pd.concat([st.session_state.personnel, new_p], ignore_index=True)
                    st.success("עודכן.")

        with tab3:
            st.subheader("דיווח חריג")
            with st.form("e_form"):
                e_type = st.selectbox("סוג", ["בטיחות", "רפואי", "מבצעי", "משמעת"])
                e_desc = st.text_area("פירוט")
                if st.form_submit_button("שלח דחוף"):
                    new_event = pd.DataFrame([[datetime.now().strftime("%H:%M"), selected_company, e_type, e_desc]], columns=['זמן', 'פלוגה', 'סוג_אירוע', 'תיאור'])
                    st.session_state.events = pd.concat([st.session_state.events, new_event], ignore_index=True)
                    st.error("הדיווח נשלח למג\"ד")

    else:
        # תצוגת מג"ד
        st.title("🏛️ חמ\"ל גדודי - חרב שאול")
        st.markdown("### ⚠️ אירועים חריגים")
        if not st.session_state.events.empty:
            for i, row in st.session_state.events.iloc[::-1].head(5).iterrows():
                st.markdown(f'<div class="event-card"><b>{row["זמן"]} | פלוגת {row["פלוגה"]}</b><br>{row["תיאור"]}</div>', unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### 👥 מצב כוח אדם גדודי")
        if not st.session_state.personnel.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("מגוייסים", len(st.session_state.personnel[st.session_state.personnel['סטטוס_גיוס'] == "מגוייס"]))
            c2.metric("ביחידה", len(st.session_state.personnel[st.session_state.personnel['מיקום'] == "ביחידה"]))
            c3.metric("בבית", len(st.session_state.personnel[st.session_state.personnel['מיקום'] == "בבית"]))
            st.dataframe(st.session_state.personnel.groupby(['פלוגה', 'מיקום']).size().unstack(fill_value=0), use_container_width=True)
