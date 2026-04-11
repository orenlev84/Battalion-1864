import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. הגדרות ועיצוב
st.set_page_config(page_title="חרב שאול", layout="wide")
st.markdown("<style>direction:rtl;text-align:right;* {font-family:'Assistant',sans-serif;}</style>", unsafe_allow_html=True)

# 2. אתחול מאגרים
for k in ['all_data', 'personnel', 'events', 'equipment', 'comms']:
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
                if p == [k for k, v in pwd.items() if v == u][0]:
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
        co = st.session_state.role if st.session_state.role != "מג\"ד" else st.selectbox("פלוגה", ["ירדן","גלבוע","תענך","עפולה","פלס\"ם אג\"ם"])
        t1, t2, t3, t4, t5 = st.tabs(["כ\"א", "תחמושת", "צל\"ם", "תקשוב", "חריגים"])
        
        with t1:
            df = st.session_state.personnel
            curr = df[df['פלוגה']==co] if not df.empty else pd.DataFrame(columns=['פלוגה','שם','סטטוס','מיקום'])
            ed = st.data_editor(curr, num_rows="dynamic", use_container_width=True, column_config={"סטטוס":{"options":["בבסיס","בבית","אחר"]}})
            if st.button("שמור כ\"א"):
                st.session_state.personnel = pd.concat([df[df['פלוגה']!=co] if not df.empty else pd.DataFrame(), ed.assign(פלוגה=co)], ignore_index=True)
                st.success("נשמר")

        with t2:
            with st.form("A"):
                i, n = st.selectbox("סוג", ["5.56","7.62","לאו"]), st.number_input("כמות", 0)
                if st.form_submit_button("דווח"):
                    new = pd.DataFrame([[co,"תחמושת",i,n,datetime.now().strftime("%H:%M")]], columns=['פלוגה','סוג','פרטים','כמות','זמן'])
                    st.session_state.all_data = pd.concat([st.session_state.all_data, new], ignore_index=True)
                    st.success("נשלח")

        with t3:
            eq = st.session_state.equipment
            curr_q = eq[eq['פלוגה']==co] if not eq.empty else pd.DataFrame([[co,"M4",0,0,"תקין"]], columns=['פלוגה','פריט','נדרש','קיים','סטטוס'])
            ed_q = st.data_editor(curr_q, num_rows="dynamic", use_container_width=True)
            if st.button("שמור צל\"ם"):
                st.session_state.equipment = pd.concat([eq[eq['פלוגה']!=co] if not eq.empty else pd.DataFrame(), ed_q.assign(פלוגה=co)], ignore_index=True)

        with t4:
            cm = st.session_state.comms
            curr_c = cm[cm['פלוגה']==co] if not cm.empty else pd.DataFrame([[co,"710",0,0,"תקין"]], columns=['פלוגה','מכשיר','נדרש','קיים','סטטוס'])
            ed_c = st.data_editor(curr_c, num_rows="dynamic", use_container_width=True)
            if st.button("שמור תקשוב"):
                st.session_state.comms = pd.concat([cm[cm['פלוגה']!=co] if not cm.empty else pd.DataFrame(), ed_c.assign(פלוגה=co)], ignore_index=True)

        with t5:
            with st.form("E"):
                tp, tx = st.selectbox("סוג", ["מבצעי","רפואי","בטיחות"]), st.text_area("תיאור")
                if st.form_submit_button("דווח חריג"):
                    st.session_state.events = pd.concat([st.session_state.events, pd.DataFrame([[datetime.now().strftime("%H:%M"),co,tp,tx]], columns=['זמן','פלוגה','סוג','תיאור'])], ignore_index=True)

    # 6. דשבורד גדודי
    else:
        st.title("🏛️ חמ\"ל חרב שאול")
        p = st.session_state.personnel
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("סד\"כ", len(p) if not p.empty else 0)
        c2.metric("בבסיס", len(p[p['סטטוס']=='בבסיס']) if not p.empty else 0)
        c3.metric("ב
