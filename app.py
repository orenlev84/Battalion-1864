import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- הגדרות דף ---
st.set_page_config(page_title='חרב שאול - שו"ב גדודי', page_icon="⚔️", layout="wide")

# --- CSS למירכוז ויישור לימין ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; text-align: right; direction: rtl; }
    .login-header { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; width: 100%; }
    .stButton>button { width: 100%; height: 3em; border-radius: 12px; font-weight: bold; }
    div[data-testid="stForm"] { direction: rtl !important; text-align: right !important; }
    [data-testid="stDataEditor"] { direction: rtl !important; }
    .event-card { background-color: #fef2f2; border: 2px solid #ef4444; border-radius: 10px; padding: 10px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- ניהול נתונים בזיכרון ---
if 'all_data' not in st.session_state: st.session_state.all_data = pd.DataFrame(columns=['פלוגה','סוג_דיווח','פרטים','כמות','זמן'])
if 'personnel' not in st.session_state: st.session_state.personnel = pd.DataFrame(columns=['פלוגה','שם','סטטוס_גיוס','מיקום'])
if 'events' not in st.session_state: st.session_state.events = pd.DataFrame(columns=['זמן','פלוגה','סוג_אירוע','תיאור'])
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = None

passwords_map = {
    "מג\"ד": "magad123", "ירדן": "yarden123", "גלבוע": "gilboa123",
    "תענך": "taanach123", "עפולה": "hafoola123", "פלס\"ם אג\"ם": "palsam123"
}

# --- מסך כניסה ---
def login_screen():
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown('<div class="login-header">', unsafe_allow_html=True)
        if os.path.exists("battalion_logo.png"): st.image("battalion_logo.png", width=180)
        st.markdown('<h1>מערכת חרב שאול</h1><h3 style="color:gray;">גדוד 1864</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        with st.form("login_form"):
            user_choice = st.selectbox("בחר תפקיד / פלוגה", list(passwords_map.keys()))
            pass_input = st.text_input("סיסמה", type="password")
            if st.form_submit_button("התחבר"):
                if pass_input == passwords_map[user_choice]:
                    st.session_state.logged_in = True
                    st.session_state.user_role = user_choice
                    st.rerun()
                else: st.error("סיסמה שגויה")

if not st.session_state.logged_in:
    login_screen()
else:
    with st.sidebar:
        if os.path.exists("battalion_logo.png"): st.image("battalion_logo.png", width=100)
        st.subheader(f"שלום, {st.session_state.user_role}")
        view_mode = "ניהול פלוגה"
        if st.session_state.user_role == "מג\"ד":
            view_mode = st.radio("תפריט:", ["תמונת מצב גדודית", "ניהול פלוגה"])
        if st.button("התנתק"):
            st.session_state.logged_in = False
            st.rerun()

    if view_mode == "ניהול פלוגה":
        selected_company = st.session_state.user_role if st.session_state.user_role != "מג\"ד" else st.selectbox("בחר פלוגה:", list(passwords_map.keys())[1:])
        st.title(f"📊 ניהול - פלוגת {selected_company}")
        
        t1, t2, t3 = st.tabs(["💣 תחמושת", "👥 כוח אדם", "⚠️ אירועים"])
        
        with t1:
            st.subheader("דיווח תחמושת")
            c1, c2 = st.columns(2)
            with c1: itm = st.selectbox("סוג", ["5.56", "7.62", "רימון", "לאו", "מטול"])
            with c2: qty = st.number_input("כמות", min_value=1, step=1)
            if st.button("שלח"):
                new_row = pd.DataFrame([[selected_company, "תחמושת", itm, qty, datetime.now().strftime("%H:%M")]], columns=['פלוגה','סוג_דיווח','פרטים','כמות','זמן'])
                st.session_state.all_data = pd.concat([st.session_state.all_data, new_row], ignore_index=True)
                st.success("דיווח נשמר")

        with t2:
            st.subheader("ניהול מצבת כוח אדם")
            uploaded_file = st.file_uploader("טען מצבה מאקסל (עמודות: שם, סטטוס_גיוס, מיקום)", type=['xlsx'])
            if uploaded_file:
                try:
                    df_excel = pd.read_excel(uploaded_file)
                    df_excel['פלוגה'] = selected_company
                    st.session_state.personnel = pd.concat([st.session_state.personnel, df_excel[['פלוגה','שם','סטטוס_גיוס','מיקום']]], ignore_index=True).drop_duplicates(subset=['שם'], keep='last')
                    st.success("נטענו נתונים בהצלחה")
                except Exception as e: st.error(f"שגיאה: {e}")

            st.divider()
            st.markdown("#### ✏️ עריכה והסרת חיילים")
            company_personnel = st.session_state.personnel[st.session_state.personnel['פלוגה'] == selected_company]
            edited_df = st.data_editor(company_personnel, column_order=("שם", "סטטוס_גיוס", "מיקום"), num_rows="dynamic", use_container_width=True)
            if st.button("שמור שינויים במצבה"):
                other_companies = st.session_state.personnel[st.session_state.personnel['פלוגה'] != selected_company]
                st.session_state.personnel = pd.concat([other_companies, edited_df], ignore_index=True)
                st.success("המצבה עודכנה!")

        with t3:
            st.subheader("אירוע חריג")
            with st.form("ev"):
                tp = st.selectbox("סוג", ["בטיחות", "רפואי", "מבצעי", "משמעת"])
                ds = st.text_area("תיאור")
                if st.form_submit_button("דיווח דחוף"):
                    new_e = pd.DataFrame([[datetime.now().strftime("%H:%M"), selected_company, tp, ds]], columns=['זמן','פלוגה','סוג_אירוע','תיאור'])
                    st.session_state.events = pd.concat([st.session_state.events, new_e], ignore_index=True)
                    st.error("דיווח נשלח למג\"ד")

    else:
        st.title("🏛️ חמ\"ל גדודי - חרב שאול")
        st.markdown("### ⚠️ חריגים אחרונים")
        if not st.session_state.events.empty:
            for i, row in st.session_state.events.iloc[::-1].iterrows():
                st.markdown(f'<div class="event-card"><b>{row["זמן"]} | {row["פלוגה"]}</b><br>{row["תיאור"]}</div>', unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### 👥 מצבת כ\"א גדודית")
        if not st.session_state.personnel.empty:
            st.dataframe(st.session_state.personnel, use_container_width=True)
