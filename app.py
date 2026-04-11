import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. הגדרות ועיצוב
st.set_page_config(page_title="חרב שאול", layout="wide")
st.markdown("<style>direction:rtl;text-align:right;* {font-family:'Assistant',sans-serif;}</style>", unsafe_allow_html=True)

# 2. אתחול מאגרים
keys = ['all_data', 'personnel', 'events', 'equipment', 'comms']
for k in keys:
    if k not in st.session_state: st.session_state[k] = pd.DataFrame()

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# 3. ניהול כניסה
pwd = {"magad123":"מג\"ד","yarden123":"ירדן","gilboa123":"גלבוע","taanach123":"תענך","hafoola123":"עפולה","palsam123":"פלס\"ם אג\"ם"}

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        if os.path.exists("battalion_logo.png"): st.image("battalion_logo.png", width=120)
        with st.form("L"):
            u = st.selectbox("יחידה", list(pwd.values()))
            p = st.text_input("סיסמה", type="password")
            if st.form_submit_button("כניסה"):
                role_key = [k for k, v in pwd.items() if v == u][0]
                if p == role_key:
                    st.session_state.logged_in, st.session_state.role = True, u
                    st.rerun()
                else: st.error("שגוי")
else:
    # 4. תפריט צד
    with st.sidebar:
        st.write(f"שלום {st.session_state.role}")
        view = "פלוגה"
        if st.session_state.role == "מג\"ד":
            view = st.radio("תפריט", ["גדודי", "פלוגה"])
        if st.button("התנתקות"):
            st.session_state.logged_in = False
            st.rerun()

    # 5. ניהול פלוגה
    if view == "פלוגה":
        co_list = ["ירדן","גלבוע","תענך","עפולה","פלס\"ם אג\"ם"]
        co = st.session_state.role if st.session_state.role != "מג\"ד" else st.selectbox("פלוגה", co_list)
        t_labels = ["כ\"א", "תחמושת", "צל\"ם", "תקשוב", "חריגים"]
        t1, t2, t3, t4, t5 = st.tabs(t_labels)
        
        with t1:
            df_p = st.session_state.personnel
            curr_p = df_p[df_p['פלוגה']==co] if not df_p.empty else pd.DataFrame(columns=['פלוגה','שם','סטטוס','מיקום'])
            st_opts = ["בבסיס","בבית","אחר"]
            ed_p = st.data_editor(curr_p, num_rows="dynamic", use_container_width=True, column_config={"סטטוס": st.column_config.SelectboxColumn("סטטוס", options=st_opts)})
            if st.button("שמור כ\"א"):
                st.session_state.personnel = pd.concat([df_p[df_p['פלוגה']!=co] if not df_p.empty else pd.DataFrame(), ed_p.assign(פלוגה=co)], ignore_index=True)
                st.success("נשמר")

        with t2:
            with st.form("A"):
                am_opts = ["5.56","7.62","לאו","מטול"]
                i = st.selectbox("סוג", am_opts)
                n = st.number_input("כמות", 0)
                if st.form_submit_button("דווח"):
                    new_a = pd.DataFrame([[co,"תחמושת",i,n,datetime.now().strftime("%H:%M")]], columns=['פלוגה','סוג','פרטים','כמות','זמן'])
                    st.session_state.all_data = pd.concat([st.session_state.all_data, new_a], ignore_index=True)
                    st.success("נשלח")

        with t3:
            df_q = st.session_state.equipment
            curr_q = df_q[df_q['פלוגה']==co] if not df_q.empty else pd.DataFrame([[co,"M4
