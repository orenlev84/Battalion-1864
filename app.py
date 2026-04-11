import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. הגדרות דף ---
st.set_page_config(page_title='חרב שאול - שו"ב גדודי', page_icon="⚔️", layout="wide")

# --- 2. עיצוב CSS יציב (יישור לימין ומראה דשבורד) ---
st.markdown("""
    <style>
    direction: rtl; text-align: right;
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; }
    .stMetric { background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 10px; padding: 10px; }
    .stButton>button { width: 100%; height: 3em; font-weight: bold; border-radius: 12px; }
    .event-card { background-color: #fff5f5; border-right: 5px solid #ff4b4b; padding: 10px; margin-bottom: 5px; border-radius: 5px; }
    div[data-testid="stForm"] { border: 1px solid #ddd; padding: 15px; border-radius: 15px; }
    .login-header { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. אתחול מאגרי נתונים (Session State) ---
keys = ['all_data', 'personnel', 'events', 'equipment', 'comms']
for key in keys:
    if key not in st.session_state:
        st.session_state[key] = pd.DataFrame()

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = None

# --- 4. מערכת סיסמאות ---
passwords_map = {
    "magad123": "מג\"ד", "yarden123": "ירדן", "gilboa123": "גלבוע",
    "taanach123": "תענך", "hafoola123": "עפולה", "palsam123": "פלס\"ם אג\"ם"
}

# --- 5. מסך כניסה ממוקרז ---
if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown('<div class="login-header">', unsafe_allow_html=True)
        if os.path.exists("battalion_logo.png"): st.image("battalion_logo.png", width=180)
        st.markdown('<h1>מערכת חרב שאול</h1><h3 style="color:gray;">גדוד 1864</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        with st.form("login_form"):
            u_choice = st.selectbox("בחר יחידה", list(passwords_map.values()))
            p_input = st.text_input("סיסמה", type="password")
            if st.form_submit_button("התחבר"):
                correct_pass = [k for k, v in passwords_map.items() if v == u_choice][0]
                if p_input == correct_pass:
                    st.session_state.logged_in = True
                    st.session_state.user_role = u_choice
                    st.rerun()
                else: st.error("סיסמה שגויה")

# --- 6. ממשק מערכת לאחר כניסה ---
else:
    with st.sidebar:
        if os.path.exists("battalion_logo.png"): st.image("battalion_logo.png", width=100)
        st.subheader(f"שלום, {st.session_state.user_role}")
        mode = "ניהול פלוגה"
        if st.session_state.user_role == "מג\"ד":
            mode = st.radio("תפריט", ["דשבורד גדודי", "ניהול פלוגה"])
        if st.button("התנתק"):
            st.session_state.logged_in = False
            st.rerun()

    # --- א. ממשק ניהול פלוגתי ---
    if mode == "ניהול פלוגה":
        sel_co = st.session_state.user_role if st.session_state.user_role != "מג\"ד" else st.selectbox("בחר פלוגה:", ["ירדן", "גלבוע", "תענך", "עפולה", "פלס\"ם אג\"ם"])
        st.title(f"📊 ניהול - פלוגת {sel_co}")
        tabs = st.tabs(["💣 תחמושת", "👥 כוח אדם", "⚔️ צל\"ם", "📡 תקשוב", "⚠️ אירועים"])
        
        with tabs[0]: # תחמושת
            with st.form("am_f"):
                itm = st.selectbox("סוג", ["5.56", "7.62", "רימון", "לאו", "מטול"])
                qty = st.number_input("כמות", min_value=0, step=1)
                if st.form_submit_button("דווח"):
                    new_a = pd.DataFrame([[sel_co, "תחמושת", itm, qty, datetime.now().strftime("%H:%M")]], columns=['פלוגה','סוג','פרטים','כמות','זמן'])
                    st.session_state.all_data = pd.concat([st.session_state.all_data, new_a], ignore_index=True)
                    st.success("נרשם")

        with tabs[1]: # כוח אדם
            f = st.file_uploader("טען אקסל כוח אדם", type=['xlsx'])
            if f:
                d = pd.read_excel(f)
                d['פלוגה'] = sel_co
                st.session_state.personnel = pd.concat([st.session_state.personnel, d], ignore_index=True).drop_duplicates(subset=['שם'])
            co_per = st.session_state
