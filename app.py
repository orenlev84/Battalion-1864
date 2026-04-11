import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. הגדרות דף ו-CSS
st.set_page_config(page_title='חרב שאול', page_icon="⚔️", layout="wide")
st.markdown("<style>direction: rtl; text-align: right; .stMetric {background-color: #f8f9fa; border-radius: 10px; padding: 10px;} .stButton>button {width: 100%; height: 3em; font-weight: bold; border-radius: 12px;}</style>", unsafe_allow_html=True)

# 2. אתחול נתונים
for k in ['all_data', 'personnel', 'events', 'equipment', 'comms']:
    if k not in st.session_state: st.session_state[k] = pd.DataFrame()

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# 3. מערכת כניסה
passwords = {"magad123": "מג\"ד", "yarden123": "ירדן", "gilboa123": "גלבוע", "taanach123": "תענך", "hafoola123": "עפולה", "palsam123": "פלס\"ם אג\"ם"}

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        if os.path.exists("battalion_logo.png"): st.image("battalion_logo.png", width=150)
        with st.form("login"):
            u = st.selectbox("בחר יחידה", list(passwords.values()))
            p = st.text_input("סיסמה", type="password")
            if st.form_submit_button("התחבר"):
                if p == [k for k, v in passwords.items() if v == u][0]:
                    st.session_state.logged_in, st.session_state.user_role = True, u
                    st.rerun()
                else: st.error("טעות בסיסמה")
else:
    # 4. תפריט צד
    with st.sidebar:
        st.subheader(f"שלום, {st.session_state.user_role}")
        mode = "ניהול פלוגה"
        if st.session_state.user_role == "מג\"ד":
            mode = st.radio("תפריט", ["דשבורד גדודי", "ניהול פלוגה"])
        if st.button("התנתק"):
            st.session_state.logged_in = False
            st.rerun()

    # 5. ניהול פלוגה
    if mode == "ניהול פלוגה":
        sel_co = st.session_state.user_role if st.session_state.user_role != "מג\"ד" else st.selectbox("בחר פלוגה:", ["ירדן", "גלבוע", "תענך", "עפולה", "פלס\"ם אג\"ם"])
        t1, t2, t3, t4, t5 = st.tabs(["כוח אדם", "תחמושת", "צל\"ם", "תקשוב", "אירועים"])
        
        with t1: # כ"א עם בחירה סגורה
            p_df = st.session_state.personnel
            co_p = p_df[p_df['פלוגה'] == sel_co] if not p_df.empty else pd.DataFrame(columns=['פלוגה','שם','סטטוס','מיקום'])
            ed = st.data_editor(co_p, num_rows="dynamic", use_container_width=True, column_config={"סטטוס": st.column_config.SelectboxColumn("סטטוס", options=["בבסיס", "בבית", "אחר"], required=True)})
            if st.button("שמור כוח אדם"):
                st.session_state.personnel = pd.concat([p_df[p_df['פלוגה'] != sel_co] if not p_df.empty else pd.DataFrame(), ed.assign(פלוגה=sel_co)], ignore_index=True)
                st.success("נשמר")

        with t2: # תחמושת
            with st.form("am"):
                itm = st.selectbox("סוג", ["5.56", "7.62", "רימון", "לאו"])
                qty = st.number_input("כמות", min_value=0)
                if st.form_submit_button("דווח"):
                    new = pd.DataFrame([[sel_co, "תחמושת", itm, qty, datetime.now().strftime("%H:%M")]], columns=['פלוגה','סוג','פרטים','כמות','זמן'])
                    st.session_state.all_data = pd.concat([st.session_state.all_data, new], ignore_index=True)
                    st.success("נרשם")

        with t3: # צל"ם
            eq_df = st.session_state.equipment
            co_eq = eq_df[eq_df['פלוגה'] == sel_co] if not eq_df.empty else pd.DataFrame([[sel_co, "M4", 0, 0, "תקין"]], columns=['פלוגה','פריט','נדרש','קיים','סטטוס'])
            ed_q = st.data_editor(co_eq, num_rows="dynamic", use_container_width=True)
            if st.button("שמור צל\"ם"):
                st.session_state.equipment = pd.concat([eq_df[eq_df['פלוגה'] != sel_co] if not eq_df.empty else pd.DataFrame(), ed_q.assign(פלוגה=sel_co)], ignore_index=True)
                st.success("נשמר")

        with t4: # תקשוב
            cm_df = st.session_state.comms
            co_cm = cm_df[cm_df['פלוגה'] == sel_co] if not cm_df.empty else pd.DataFrame([[sel_co, "710", 0, 0, "תקין"]], columns=['פלוגה','מכשיר','נדרש','קיים','סטטוס'])
            ed_c = st.data_editor(co_cm, num_rows="dynamic", use_container_width=True)
            if st.button("שמור תקשוב"):
                st.session_state.comms = pd.concat([cm_df[cm_df['פלוגה'] != sel_co] if not cm_df.empty else pd.DataFrame(), ed_c.assign(פלוגה=sel_co)], ignore_index=True)
                st.success("נשמר")

        with t5: # אירועים
            with st.form("ev"):
                tp = st.selectbox("סוג", ["מבצעי", "רפואי", "בטיחות"])
                tx = st.text_area("תיאור")
                if st.form_submit_button("שלח"):
                    new_e = pd.DataFrame([[datetime.now().strftime("%H:%M"), sel_co, tp, tx]], columns=['זמן','פלוגה','סוג','תיאור'])
                    st.session_state.events = pd.concat([st.session_state.events, new_e], ignore_index=True)
                    st.error("דווח")

    else: # 6. דשבורד גדודי
        st.title("🏛️ דשבורד גדוד 1864")
        p = st.session_state.personnel
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("סך חיילים", len(p) if not p.empty else 0)
        m2.metric("בבסיס", len(p[p['סטטוס'] == 'בבסיס']) if not p.empty else 0)
        m3.metric("בבית", len(p[p['סטטוס'] == 'בבית']) if not p.empty else 0)
        m4.metric("חריגים", len(st.session_state.events))
        
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📊 מצבת פלוגות")
            if not p.empty: st.bar_chart(p.groupby(['פלוגה', 'סט
