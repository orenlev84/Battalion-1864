import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- הגדרות תצוגה ---
st.set_page_config(
    page_title="חרב שאול - ניהול גדודי",
    page_icon="⚔️",
    layout="wide"
)

# --- עיצוב CSS משופר למירכוז ויישור לימין ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="css"]  { font-family: 'Assistant', sans-serif; text-align: right; direction: rtl; }
    
    /* מירכוז מוחלט של הסמל והכותרות */
    .center-all {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        width: 100%;
    }
    
    .stButton>button { width: 100%; height: 3em; border-radius: 12px; font-weight: bold; }
    .sidebar-title { text-align: center; color: #1e3a8a; font-weight: bold; font-size: 1.5em; }
    .event-card { background-color: #fef2f2; border: 2px solid #ef4444; border-radius: 10px; padding: 10px; margin-bottom: 10px; }
    
    /* תיקון יישור טפסים ותיבות בחירה לימין */
    div[data-testid="stSelectbox"] > label { text-align: right; width: 100%; }
    div[data-testid="stTextInput"] > label { text-align: right; width: 100%; }
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

# --- מילון סיסמאות מותאם לתפקידים ---
passwords_map = {
    "מג\"ד": "magad123",
    "ירדן": "yarden123",
    "גלבוע": "gilboa123",
    "תענך": "taanach123",
    "עפולה": "hafoola123",
    "פלס\"ם אג\"ם": "palsam123"
}

# --- מסך כניסה ממוקד ---
def login_screen():
    # יצירת מרווח מלמעלה
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # שימוש במיכל ממרכז
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # עטיפת הסמל במערך ממרכז
        st.markdown('<div class="center-all">', unsafe_allow_html=True)
        if os.path.exists("battalion_logo.png"):
            st.image("battalion_logo.png", width=200)
        st.markdown('<h1 style="margin-bottom:0;">מערכת חרב שאול</h1>', unsafe_allow_html=True)
        st.markdown('<h3 style="color: #666; margin-top:0;">גדוד 1864</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            # בחירה מרשימה במקום הקלדה
            user_choice = st.selectbox("בחר תפקיד/פלוגה", list(passwords_map.keys()))
            pass_input = st.text_input("סיסמה", type="password")
            submit_login = st.form_submit_button("התחבר למערכת")
            
            if submit_login:
                # בדיקה אם הסיסמה מתאימה לתפקיד שנבחר
                if pass_input == passwords_map[user_choice]:
                    st.session_state.logged_in = True
                    st.session_state.user_role = user_choice
                    st.rerun()
                else:
                    st.error("סיסמה שגויה עבור התפקיד שנבחר")

# --- הרצת המערכת ---
if not st.session_state.logged_in:
    login_screen()
else:
    # כאן ממשיך שאר הקוד של האפליקציה (סרגל צד, ניהול פלוגה/גדוד) כפי שהיה
    with st.sidebar:
        if os.path.exists("battalion_logo.png"):
            st.image("battalion_logo.png", width=100)
        st.markdown(f'<div class="sidebar-title">שלום, {st.session_state.user_role}</div>', unsafe_allow_html=True)
        
        if st.session_state.user_role == "מג\"ד":
            view_mode = st.radio("בחר תצוגה:", ["ניהול פלוגה", "תמונת מצב גדודית"], index=1)
        else:
            view_mode = "ניהול פלוגה"
        
        if st.button("התנתק"):
            st.session_state.logged_in = False
            st.rerun()

    # לוגיקה פלוגתית / גדודית (נשמרת מהגרסאות הקודמות)
    if view_mode == "ניהול פלוגה":
        selected_company = st.session_state.user_role if st.session_state.user_role != "מג\"ד" else st.selectbox("בחר פלוגה:", list(passwords_map.keys())[1:])
        st.title(f"📊 ניהול - פלוגת {selected_company}")
        # ... המשך הקוד (תחמושת, אקסל כ"א, אירועים חריגים) ...
        # (שים לב להעתיק את הלשוניות מהגרסה הקודמת לתוך הבלוק הזה)
