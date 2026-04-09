import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- הגדרות תצוגה כלליות ---
st.set_page_config(
    page_title="חרב שאול - ניהול גדודי",
    page_icon="⚔️",
    layout="wide"
)

# --- עיצוב CSS מתקדם (מירכוז ויישור RTL) ---
st.markdown("""
    <style>
    /* פונט Assistant ויישור RTL כללי */
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="css"]  { font-family: 'Assistant', sans-serif; text-align: right; direction: rtl; }
    
    /* מירכוז מושלם של מסך הכניסה (הלוגו מעל הטקסט) */
    .center-column-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        width: 100%;
        margin-top: 50px; /* מרווח קטן מלמעלה */
    }
    
    /* עיצוב סמל הגדוד (ממורכז) */
    .battalion-logo { margin-bottom: 0px; }
    
    /* עיצוב כותרות (ממורכזות) */
    .app-title { color: #1e3a8a; font-weight: bold; margin-bottom: 0px; margin-top: 0px;}
    .app-subtitle { color: #666; font-size: 1.2rem; margin-top: 0px; margin-bottom: 30px;}

    /* עיצוב תיבת הטופס (ממורכזת) */
    .login-form-box { width: 100%; max-width: 400px; }
    
    /* עיצוב כפתורים גדולים */
    .stButton>button { width: 100%; height: 3.5em; border-radius: 12px; font-weight: bold; font-size: 18px;}
    
    /* עיצוב סרגל צד */
    .sidebar-title { text-align: center; color: #1e3a8a; font-weight: bold; font-size: 1.5em; }

    /* תיקון ליישור טפסים, תיבות בחירה ואינפוטים לימין */
    div[data-testid="stForm"] > label { text-align: right; width: 100%; }
    div[data-testid="stSelectbox"] > label { text-align: right; width: 100%; }
    div[data-testid="stTextInput"] > label { text-align: right; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- ניהול נתונים בזיכרון (מתאפס ברענון) ---
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

# --- מילון סיסמאות לפי תפקיד/פלוגה ---
passwords_map = {
    "מג\"ד": "magad123",
    "ירדן": "yarden123",
    "גלבוע": "gilboa123",
    "תענך": "taanach123",
    "עפולה": "hafoola123",
    "פלס\"ם אג\"ם": "palsam123"
}

# --- מסך כניסה ממוקז ומשודרג ---
def login_screen():
    # יצירת המיכל הממרכז (Flexbox Column)
    st.markdown('<div class="center-column-container">', unsafe_allow_html=True)
    
    # 1. סמל הגדוד (ממורכז)
    if os.path.exists("battalion_logo.png"):
        st.image("battalion_logo.png", width=180, caption="")
    else:
        st.warning("לא נמצא קובץ סמל. וודא שהעלת אותו ל-GitHub בשם 'battalion_logo.png'")
        
    # 2. כותרות האפליקציה (ממורכזות)
    st.markdown('<h1 class="app-title">מערכת חרב שאול</h1>', unsafe_allow_html=True)
    st.markdown('<h3 class="app-subtitle">גדוד 1864 - ניהול מבצעי</h3>', unsafe_allow_html=True)
    
    # 3. תיבת טופס הכניסה (ממורכזת)
    with st.container():
        with st.form("login_form"):
            # שימוש בתיבת בחירה (Selectbox) עבור שם המשתמש
            user_choice = st.selectbox("בחר תפקיד / פלוגה", list(passwords_map.keys()))
            pass_input = st.text_input("סיסמה", type="password")
            submit_login = st.form_submit_button("התחבר")
            
            if submit_login:
                # בדיקת התאמה בין הפלוגה שנבחרה לסיסמה
                if pass_input == passwords_map[user_choice]:
                    st.session_state.logged_in = True
                    st.session_state.user_role = user_choice
                    st.rerun()
                else:
                    st.error("סיסמה שגויה עבור הפלוגה שנבחרה")
    st.markdown('</div>', unsafe_allow_html=True) # סגירת מיכל המירכוז

# --- לוגיקה של האפליקציה ---
if not st.session_state.logged_in:
    login_screen()
else:
    # כאן ממשיך שאר הקוד המקורי של האפליקציה (סרגל צד, ניהול פלוגות וגדוד) כפי שהיה
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
            
    if view_mode == "ניהול פלוגה":
        # בחירת פלוגה (נעול עבור מ"פ, פתוח עבור מג"ד)
        if st.session_state.user_role == "מג\"ד":
            # הרשימה ללא המג"ד עצמו
            selected_company = st.selectbox("בחר פלוגה לניהול:", list(passwords_map.keys())[1:])
        else:
            selected_company = st.session_state.user_role
            
        st.title(f"📊 ניהול נתונים - פלוגת {selected_company}")
        # ... כאן יש להעתיק את הקוד המקורי של הלשוניות: תחמושת, אקסל כ"א, ואירועים חריגים ...
