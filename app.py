import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. הגדרות בסיס - ללא עיצובים מורכבים שעלולים להישבר
st.set_page_config(page_title="חרב שאול", layout="wide")

# 2. CSS מינימליסטי וקריא למובייל
st.markdown("""
    <style>
    direction: rtl;
    text-align: right;
    font-family: sans-serif;
    .stButton>button { width: 100%; height: 3em; font-weight: bold; border-radius: 10px; }
    div[data-testid="stForm"] { border: 1px solid #ddd; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. אתחול מאגרי נתונים
if 'all_data' not in st.session_state: st.session_state.all_data = pd.DataFrame(columns=['פלוגה','סוג','פרטים','כמות','זמן'])
if 'personnel' not in st.session_state: st.session_state.personnel = pd.DataFrame(columns=['פלוגה','שם','סטטוס','מיקום'])
if 'events' not in st.session_state: st.session_state.events = pd.DataFrame(columns=['זמן','פלוגה','סוג','תיאור'])
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = None

# 4. ניהול כניסה
passwords = {
    "magad123": "מג\"ד", "yarden123": "ירדן", "gilboa123": "גלבוע",
    "taanach123": "תענך", "hafoola123": "עפולה", "palsam123": "פלס\"ם אג\"ם"
}

if not st.session_state.logged_in:
    st.title("כניסה - חרב שאול")
    user_choice = st.selectbox("בחר יחידה", list(passwords.values()))
    pass_input = st.text_input("סיסמה", type="password")
    if st.button("התחבר"):
        # בדיקה אם הסיסמה מתאימה לתפקיד
        correct_pass = [k for k, v in passwords.items() if v == user_choice][0]
        if pass_input == correct_pass:
            st.session_state.logged_in = True
            st.session_state.user_role = user_choice
            st.rerun()
        else:
            st.error("סיסמה לא נכונה")

# 5. ממשק פוסט-כניסה
else:
    with st.sidebar:
        st.write(f"שלום, {st.session_state.user_role}")
        mode = "ניהול פלוגה"
        if st.session_state.user_role == "מג\"ד":
            mode = st.radio("תפריט", ["גדודי", "פלוגתי"])
        if st.button("התנתק"):
            st.session_state.logged_in = False
            st.rerun()

    if mode == "פלוגתי":
        sel_co = st.session_state.user_role if st.session_state.user_role != "מג\"ד" else st.selectbox("בחר פלוגה", ["ירדן", "גלבוע", "תענך", "עפולה", "פלס\"ם אג\"ם"])
        st.header(f"ניהול פלוגת {sel_co}")
        
        tab_ammo, tab_per, tab_ev = st.tabs(["תחמושת", "כוח אדם", "אירועים"])
        
        with tab_ammo:
            with st.form("f_ammo"):
                itm = st.selectbox("סוג", ["5.56", "7.62", "רימון", "לאו"])
                num = st.number_input("כמות", min_value=1)
                if st.form_submit_button("דווח"):
                    new_a = pd.DataFrame([[sel_co, "תחמושת", itm, num, datetime.now().strftime("%H:%M")]], columns=st.session_state.all_data.columns)
                    st.session_state.all_data = pd.concat([st.session_state.all_data, new_a], ignore_index=True)
                    st.success("נשמר")

        with tab_per:
            f = st.file_uploader("טען אקסל (שם, סטטוס, מיקום)", type=['xlsx'])
            if f:
                d = pd.read_excel(f)
                d['פלוגה'] = sel_co
                st.session_state.personnel = pd.concat([st.session_state.personnel, d], ignore_index=True).drop_duplicates(subset=['שם'])
                st.success("נטען")
            
            st.write("עריכת מצבה:")
            co_per = st.session_state.personnel[st.session_state.personnel['פלוגה'] == sel_co]
            edited = st.data_editor(co_per, num_rows="dynamic")
            if st.button("שמור מצבה"):
                others = st.session_state.personnel[st.session_state.personnel['פלוגה'] != sel_co]
                st.session_state.personnel = pd.concat([others, edited], ignore_index=True)
                st.success("עודכן")

        with tab_ev:
            with st.form("f_ev"):
                tp = st.selectbox("סוג", ["בטיחות", "רפואי", "מבצעי"])
                txt = st.text_area("תיאור")
                if st.form_submit_button("שלח חריג"):
                    new_e = pd.DataFrame([[datetime.now().strftime("%H:%M"), sel_co, tp, txt]], columns=st.session_state.events.columns)
                    st.session_state.events = pd.concat([st.session_state.events, new_e], ignore_index=True)
                    st.error("נשלח")

    else: # מצב גדודי
        st.header("חמ\"ל חרב שאול")
        st.subheader("אירועים")
        st.table(st.session_state.events.iloc[::-1])
        st.subheader("מצבת כ\"א")
        st.dataframe(st.session_state.personnel, use_container_width=True)
