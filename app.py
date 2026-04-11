import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. הגדרות דף ---
st.set_page_config(page_title="Herev Shaul", layout="wide")
st.markdown("<style>direction:rtl; text-align:right; * {font-family:'Assistant',sans-serif;}</style>", unsafe_allow_html=True)

# --- 2. אתחול מאגרי נתונים (חובה שיופיעו בהתחלה) ---
for k in ['all_data', 'personnel', 'events', 'equipment', 'comms']:
    if k not in st.session_state:
        st.session_state[k] = pd.DataFrame()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'role' not in st.session_state:
    st.session_state.role = None

# --- 3. מערכת כניסה ---
passwords = {"magad123":"מג\"ד","yarden123":"ירדן","gilboa123":"גלבוע","taanach123":"תענך","hafoola123":"עפולה","palsam123":"פלס\"ם אג\"ם"}

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        if os.path.exists("battalion_logo.png"): st.image("battalion_logo.png", width=120)
        with st.form("login_form"):
            u = st.selectbox("בחר יחידה", list(passwords.values()))
            p = st.text_input("סיסמה", type="password")
            if st.form_submit_button("כניסה"):
                correct_pass = [k for k, v in passwords.items() if v == u][0]
                if p == correct_pass:
                    st.session_state.role = u
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("סיסמה שגויה")
else:
    # --- 4. תפריט צד (מוצג רק אחרי התחברות) ---
    with st.sidebar:
        st.write(f"שלום {st.session_state.role}")
        view = "פלוגה"
        if st.session_state.role == "מג\"ד":
            view = st.radio("תפריט", ["גדודי", "פלוגה"])
        if st.button("התנתקות"):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.rerun()

    # --- 5. ניהול פלוגה ---
    if view == "פלוגה":
        co = st.session_state.role if st.session_state.role != "מג\"ד" else st.selectbox("פלוגה", ["ירדן","גלבוע","תענך","עפולה","פלס\"ם אג\"ם"])
        t1, t2, t3, t4, t5 = st.tabs(["כוח אדם", "תחמושת", "צל\"ם", "תקשוב", "חריגים"])
        
        with t1: # כוח אדם
            df_p = st.session_state.personnel
            curr_p = df_p[df_p['company']==co] if not df_p.empty else pd.DataFrame(columns=['company','name','status','location'])
            ed_p = st.data_editor(curr_p, num_rows="dynamic", use_container_width=True, column_config={"status": st.column_config.SelectboxColumn("סטטוס", options=["בבסיס","בבית","אחר"])})
            if st.button("שמור כוח אדם"):
                st.session_state.personnel = pd.concat([df_p[df_p['company']!=co] if not df_p.empty else pd.DataFrame(), ed_p.assign(company=co)], ignore_index=True)
                st.success("נשמר")

        with t2: # תחמושת
            with st.form("ammo_form"):
                i = st.selectbox("סוג", ["5.56","7.62","לאו","מטול"])
                n = st.number_input("כמות", 0)
                if st.form_submit_button("דווח"):
                    new_a = pd.DataFrame([[co,"תחמושת",i,n,datetime.now().strftime("%H:%M")]], columns=['company','type','item','qty','time'])
                    st.session_state.all_data = pd.concat([st.session_state.all_data, new_a], ignore_index=True)
                    st.success("דיווח נשלח")

        with t3: # צל"ם
            df_q = st.session_state.equipment
            curr_q = df_q[df_q['company']==co] if not df_q.empty else pd.DataFrame([[co,"M4",0,0,"תקין"]], columns=['company','item','req','has','status'])
            ed_q = st.data_editor(curr_q, num_rows="dynamic", use_container_width=True, key="eq_editor")
            if st.button("שמור צל\"ם"):
                st.session_state.equipment = pd.concat([df_q[df_q['company']!=co] if not df_q.empty else pd.DataFrame(), ed_q.assign(company=co)], ignore_index=True)
                st.success("עודכן")

        with t4: # תקשוב
            df_c = st.session_state.comms
            curr_c = df_c[df_c['company']==co] if not df_c.empty else pd.DataFrame([[co,"710",0,0,"תקין"]], columns=['company','item','req','has','status'])
            ed_c = st.data_editor(curr_c, num_rows="dynamic", use_container_width=True, key="cm_editor")
            if st.button("שמור תקשוב"):
                st.session_state.comms = pd.concat([df_c[df_c['company']!=co] if not df_c.empty else pd.DataFrame(), ed_c.assign(company=co)], ignore_index=True)
                st.success("עודכן")

        with t5: # חריגים
            with st.form("event_form"):
                tp = st.selectbox("סוג", ["מבצעי","רפואי","בטיחות"])
                tx = st.text_area("תיאור")
                if st.form_submit_button("דווח חריג"):
                    new_e = pd.DataFrame([[datetime.now().strftime("%H:%M"),co,tp,tx]], columns=['time','company','type','desc'])
                    st.session_state.events = pd.concat([st.session_state.events, new_e], ignore_index=True)
                    st.error("דיווח נשלח")

    # --- 6. דשבורד גדודי ---
    else:
        st.title("🏛️ דשבורד פיקודי - חרב שאול")
        p = st.session_state.personnel
        e = st.session_state.events
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("סד\"כ", len(p) if not p.empty else 0)
        c2.metric("בבסיס", len(p[p['status']=="בבסיס"]) if not p.empty else 0)
        c3.metric("בבית", len(p[p['status']=="בבית"]) if not p.empty else 0)
        c4.metric("חריגים", len(e) if not e.empty else 0)
        
        st.divider()
        col_r, col_l = st.columns(2)
        with col_r:
            st.subheader("📊 מצבת פלוגות")
            if not p.empty:
                chart_data = p.groupby(['company', 'status']).size().unstack(fill_value=0)
                st.bar_chart(chart_data)
        with col_l:
            st.subheader("💣 תחמושת")
            if not st.session_state.all_data.empty:
                st.bar_chart(st.session_state.all_data.groupby('company')['qty'].sum())
