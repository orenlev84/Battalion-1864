import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. הגדרות דף
st.set_page_config(page_title='חרב שאול - שו"ב גדודי', layout="wide")

# 2. CSS ליישור לימין ומניעת שגיאות תצוגה
st.markdown("""
    <style>
    direction: rtl;
    text-align: right;
    .stButton>button { width: 100%; height: 3em; font-weight: bold; border-radius: 10px; }
    div[data-testid="stForm"] { border: 1px solid #ddd; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. אתחול מאגרי נתונים (הוספת תקשוב בנפרד)
if 'all_data' not in st.session_state: st.session_state.all_data = pd.DataFrame(columns=['פלוגה','סוג','פרטים','כמות','זמן'])
if 'personnel' not in st.session_state: st.session_state.personnel = pd.DataFrame(columns=['פלוגה','שם','סטטוס','מיקום'])
if 'events' not in st.session_state: st.session_state.events = pd.DataFrame(columns=['זמן','פלוגה','סוג','תיאור'])
if 'equipment' not in st.session_state: st.session_state.equipment = pd.DataFrame(columns=['פלוגה','פריט','נדרש','קיים','סטטוס'])
if 'comms' not in st.session_state: st.session_state.comms = pd.DataFrame(columns=['פלוגה','מכשיר','נדרש','קיים','סטטוס'])
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = None

# 4. מערכת הרשאות
passwords = {
    "magad123": "מג\"ד", "yarden123": "ירדן", "gilboa123": "גלבוע",
    "taanach123": "תענך", "hafoola123": "עפולה", "palsam123": "פלס\"ם אג\"ם"
}

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        if os.path.exists("battalion_logo.png"): st.image("battalion_logo.png", width=150)
        st.title("מערכת חרב שאול")
        u_choice = st.selectbox("בחר יחידה", list(passwords.values()))
        p_input = st.text_input("סיסמה", type="password")
        if st.button("התחבר"):
            c_pass = [k for k, v in passwords.items() if v == u_choice][0]
            if p_input == c_pass:
                st.session_state.logged_in = True
                st.session_state.user_role = u_choice
                st.rerun()
            else: st.error("סיסמה שגויה")

# 5. ממשק ניהול
else:
    with st.sidebar:
        if os.path.exists("battalion_logo.png"): st.image("battalion_logo.png", width=80)
        st.write(f"שלום, {st.session_state.user_role}")
        mode = "ניהול פלוגה"
        if st.session_state.user_role == "מג\"ד":
            mode = st.radio("תפריט", ["גדודי", "ניהול פלוגה"])
        if st.button("התנתק"):
            st.session_state.logged_in = False
            st.rerun()

    if mode == "ניהול פלוגה":
        sel_co = st.session_state.user_role if st.session_state.user_role != "מג\"ד" else st.selectbox("בחר פלוגה", ["ירדן", "גלבוע", "תענך", "עפולה", "פלס\"ם אג\"ם"])
        st.header(f"ניהול פלוגת {sel_co}")
        
        # הפרדת לשוניות: צל"ם ותקשוב בנפרד
        tabs = st.tabs(["תחמושת", "כוח אדם", "צל\"ם", "תקשוב", "אירועים"])
        
        with tabs[0]: # תחמושת
            with st.form("f_am"):
                a_type = st.selectbox("סוג תחמושת", ["5.56", "7.62", "רימון", "לאו"])
                a_num = st.number_input("כמות", min_value=0, step=1)
                if st.form_submit_button("דווח"):
                    new_a = pd.DataFrame([[sel_co, "תחמושת", a_type, a_num, datetime.now().strftime("%H:%M")]], columns=st.session_state.all_data.columns)
                    st.session_state.all_data = pd.concat([st.session_state.all_data, new_a], ignore_index=True)
                    st.success("נשמר")

        with tabs[1]: # כוח אדם
            f = st.file_uploader("טען אקסל כוח אדם", type=['xlsx'])
            if f:
                d = pd.read_excel(f)
                d['פלוגה'] = sel_co
                st.session_state.personnel = pd.concat([st.session_state.personnel, d], ignore_index=True).drop_duplicates(subset=['שם'])
            co_per = st.session_state.personnel[st.session_state.personnel['פלוגה'] == sel_co]
            ed_per = st.data_editor(co_per, num_rows="dynamic", use_container_width=True, key="per_edit")
            if st.button("שמור כוח אדם"):
                others = st.session_state.personnel[st.session_state.personnel['פלוגה'] != sel_co]
                st.session_state.personnel = pd.concat([others, ed_per], ignore_index=True)
                st.success("עודכן")

        with tabs[2]: # צל"ם (נשק)
            st.subheader("ניהול צל\"ם ונשק")
            co_eq = st.session_state.equipment[st.session_state.equipment['פלוגה'] == sel_co]
            if co_eq.empty:
                co_eq = pd.DataFrame([[sel_co, "M4", 0, 0, "תקין"], [sel_co, "מאג", 0, 0, "תקין"]], columns=st.session_state.equipment.columns)
            ed_eq = st.data_editor(co_eq, num_rows="dynamic", use_container_width=True, key="eq_edit")
            if st.button("שמור צל\"ם"):
                st.session_state.equipment = pd.concat([st.session_state.equipment[st.session_state.equipment['פלוגה'] != sel_co], ed_eq], ignore_index=True)
                st.success("צל\"ם עודכן")

        with tabs[3]: # תקשוב
            st.subheader("ניהול ציוד תקשוב")
            co_cm = st.session_state.comms[st.session_state.comms['פלוגה'] == sel_co]
            if co_cm.empty:
                co_cm = pd.DataFrame([[sel_co, "710", 0, 0, "תקין"], [sel_co, "624", 0, 0, "תקין"]], columns=st.session_state.comms.columns)
            ed_cm = st.data_editor(co_cm, num_rows="dynamic", use_container_width=True, key="cm_edit")
            if st.button("שמור תקשוב"):
                st.session_state.comms = pd.concat([st.session_state.comms[st.session_state.comms['פלוגה'] != sel_co], ed_cm], ignore_index=True)
                st.success("תקשוב עודכן")

        with tabs[4]: # אירועים
            with st.form("f_ev"):
                e_opt = ["מבצעי", "רפואי", "בטיחות", "אחר"]
                e_type = st.selectbox("סוג אירוע", options=e_opt)
                e_txt = st.text_area("תיאור")
                if st.form_submit_button("שלח"):
                    new_e = pd.DataFrame([[datetime.now().strftime("%H:%M"), sel_co, e_type, e_txt]], columns=st.session_state.events.columns)
                    st.session_state.events = pd.concat([st.session_state.events, new_e], ignore_index=True)
                    st.error("דווח למפקדה")

    else: # תצוגה גדודית
        st.title("תמונת מצב גדודית")
        st.subheader("חריגים")
        st.dataframe(st.session_state.events.iloc[::-1], use_container_width=True)
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("ריכוז צל\"ם")
            st.dataframe(st.session_state.equipment, use_container_width=True)
        with c2:
            st.subheader("ריכוז תקשוב")
            st.dataframe(st.session_state.comms, use_container_width=True)
