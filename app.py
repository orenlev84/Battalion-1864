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

# --- עיצוב CSS (כולל מירכוז מסך כניסה) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="css"]  { font-family: 'Assistant', sans-serif; text-align: right; direction: rtl; }
    
    /* מירכוז אלמנטים במסך הכניסה */
    .centered-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    
    .stButton>button { width: 100%; height: 3em; border-radius: 12px; font-weight: bold; }
    .sidebar-title { text-align: center; color: #1e3a8a; font-weight: bold; font-size: 1.5em; }
    .event-card { background-color: #fef2f2; border: 2px solid #ef4444; border-radius: 10px; padding: 10px; margin-bottom: 10px; }
    
    /* תיקון ליישור טפסים לימין */
    [data-testid="stForm"] { text-align: right; direction: rtl; }
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

# --- מילון סיסמאות ---
passwords = {
    "magad123": "מג\"ד",
    "yarden123": "ירדן",
    "gilboa123": "גלבוע",
    "taanach123": "תענך",
    "hafoola123": "עפולה",
    "palsam123": "פלס\"ם אג\"ם"
}

# --- מסך כניסה ממוקז ---
def login_screen():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="centered-container">', unsafe_allow_html=True)
        if os.path.exists("battalion_logo.png"):
            st.image("battalion_logo.png", width=180)
        st.markdown('<h1 style="text-align: center;">מערכת חרב שאול</h1>', unsafe_allow_html=True)
        st.markdown('<h3 style="text-align: center; color: #666;">גדוד 1864</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            user_input = st.text_input("שם משתמש")
            pass_input = st.text_input("סיסמה", type="password")
            submit_login = st.form_submit_button("התחבר")
            
            if submit_login:
                if pass_input in passwords:
                    st.session_state.logged_in = True
                    st.session_state.user_role = passwords[pass_input]
                    st.rerun()
                else:
                    st.error("סיסמה שגויה")

# --- תצוגת האפליקציה ---
if not st.session_state.logged_in:
    login_screen()
else:
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
        selected_company = st.session_state.user_role if st.session_state.user_role != "מג\"ד" else st.selectbox("בחר פלוגה:", ["ירדן", "גלבוע", "תענך", "עפולה", "פלס\"ם אג\"ם"])
        
        st.title(f"📊 ניהול - פלוגת {selected_company}")
        tab1, tab2, tab3 = st.tabs(["💣 תחמושת", "👥 כוח אדם", "⚠️ אירועים"])
        
        with tab1:
            st.subheader("דיווח צריכה")
            # קוד תחמושת... (נשאר זהה)
            
        with tab2:
            st.subheader("ניהול מצבת כוח אדם")
            
            # אפשרות העלאת אקסל
            st.markdown("---")
            st.markdown("#### 📂 העלאת מצבה מאקסל")
            uploaded_file = st.file_uploader("בחר קובץ אקסל (עמודות נדרשות: שם, סטטוס_גיוס, מיקום)", type=["xlsx", "xls"])
            
            if uploaded_file:
                try:
                    df_excel = pd.read_excel(uploaded_file)
                    # וידוא עמודות קיימות
                    required_columns = ['שם', 'סטטוס_גיוס', 'מיקום']
                    if all(col in df_excel.columns for col in required_columns):
                        df_excel['פלוגה'] = selected_company
                        # הסרת כפילויות ישנות והוספת החדשות
                        names_to_remove = df_excel['שם'].tolist()
                        st.session_state.personnel = st.session_state.personnel[~st.session_state.personnel['שם'].isin(names_to_remove)]
                        st.session_state.personnel = pd.concat([st.session_state.personnel, df_excel[required_columns + ['פלוגה']]], ignore_index=True)
                        st.success(f"נטענו {len(df_excel)} חיילים בהצלחה!")
                    else:
                        st.error("מבנה הקובץ לא תקין. וודא שיש עמודות: שם, סטטוס_גיוס, מיקום")
                except Exception as e:
                    st.error(f"שגיאה בקריאת הקובץ: {e}")

            st.markdown("---")
            st.markdown("#### ✍️ עדכון ידני")
            with st.form("p_manual"):
                p_name = st.text_input("שם החייל")
                p_status = st.selectbox("סטטוס", ["מגוייס", "משוחרר/מילואים", "בצוו 8"])
                p_loc = st.selectbox("מיקום", ["ביחידה", "בבית", "אחר"])
                if st.form_submit_button("עדכן ידנית"):
                    st.session_state.personnel = st.session_state.personnel[st.session_state.personnel['שם'] != p_name]
                    new_p = pd.DataFrame([[selected_company, p_name, p_status, p_loc]], columns=['פלוגה', 'שם', 'סטטוס_גיוס', 'מיקום'])
                    st.session_state.personnel = pd.concat([st.session_state.personnel, new_p], ignore_index=True)
                    st.success("עודכן")

        with tab3:
            # קוד אירועים חריגים... (נשאר זהה)
            st.subheader("דיווח חריג")
            with st.form("e_form"):
                e_type = st.selectbox("סוג", ["בטיחות", "רפואי", "מבצעי", "משמעת"])
                e_desc = st.text_area("פירוט")
                if st.form_submit_button("שלח דחוף"):
                    new_event = pd.DataFrame([[datetime.now().strftime("%H:%M"), selected_company, e_type, e_desc]], columns=['זמן', 'פלוגה', 'סוג_אירוע', 'תיאור'])
                    st.session_state.events = pd.concat([st.session_state.events, new_event], ignore_index=True)
                    st.error("הדיווח נשלח למג\"ד")

    else:
        # תצוגת מג"ד (נשארת זהה)
        st.title("🏛️ חמ\"ל גדודי - חרב שאול")
        # ... (שאר קוד הדאשבורד)
