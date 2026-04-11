import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. הגדרות דף ---
st.set_page_config(page_title='חרב שאול - שו"ב גדודי', page_icon="⚔️", layout="wide")

# --- 2. CSS יציב ---
st.markdown("""
    <style>
    direction: rtl; text-align: right;
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; }
    .stMetric { background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 10px; padding: 10px; }
    .stButton>button { width: 100%; height: 3em; font-weight: bold; border-radius: 12px; }
    .event-card { background-color: #fff5f5; border-right: 5px solid #ff4b4b; padding: 10px; margin-bottom: 5px; border-radius: 5px; }
    div[data-testid="stForm"] { border: 1px solid #ddd; padding: 15px; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. אתחול מאגרי נתונים - חובה לאתחל עם עמודות נכונות ---
if 'all_data' not in st.session_state:
    st.session_state.all_data = pd.DataFrame(columns=['פלוגה','סוג','פרטים','כמות','זמן'])
if 'personnel' not in st.session_state:
    st.session_state.personnel = pd.DataFrame(columns=['פלוגה','שם','סטטוס','מיקום'])
if 'events' not in st.session_state:
    st.session_state.events = pd.DataFrame(columns=['זמן','פלוגה','סוג','תיאור'])
if 'equipment' not in st.session_state:
    st.session_state.equipment = pd.DataFrame(columns=['פלוגה','פריט','נדרש','קיים','סטטוס'])
if 'comms' not in st.session_state:
    st.session_state.comms = pd.DataFrame(columns=['פלוגה','מכשיר','נדרש','קיים','סטטוס'])

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = None

passwords_map = {
    "magad123": "מג\"ד", "yarden123": "ירדן", "gilboa123": "גלבוע",
    "taanach123": "תענך", "hafoola123": "עפולה", "palsam123": "פלס\"ם אג\"ם"
}

# --- 4. מסך כניסה ---
if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        if os.path.exists("battalion_logo.png"): st.image("battalion_logo.png", width=180)
        st.markdown('<h1 style="text-align:center;">מערכת חרב שאול</h1>', unsafe_allow_html=True)
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

# --- 5. ממשק מערכת ---
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

    if mode == "ניהול פלוגה":
        sel_co = st.session_state.user_role if st.session_state.user_role != "מג\"ד" else st.selectbox("בחר פלוגה:", ["ירדן", "גלבוע", "תענך", "עפולה", "פלס\"ם אג\"ם"])
        st.title(f"📊 ניהול - פלוגת {sel_co}")
        tabs = st.tabs(["💣 תחמושת", "👥 כוח אדם", "⚔️ צל\"ם", "📡 תקשוב", "⚠️ אירועים"])
        
        with tabs[0]: # תחמושת
            with st.form("am_f"):
                itm = st.selectbox("סוג", ["5.56", "7.62", "רימון", "לאו", "מטול"])
                qty = st.number_input("כמות", min_value=0, step=1)
                if st.form_submit_button("דווח"):
                    new_a = pd.DataFrame([[sel_co, "תחמושת", itm, qty, datetime.now().strftime("%H:%M")]], columns=st.session_state.all_data.columns)
                    st.session_state.all_data = pd.concat([st.session_state.all_data, new_a], ignore_index=True)
                    st.success("נרשם")

        with tabs[1]: # כוח אדם
            f = st.file_uploader("טען אקסל כוח אדם", type=['xlsx'])
            if f:
                d = pd.read_excel(f)
                d['פלוגה'] = sel_co
                st.session_state.personnel = pd.concat([st.session_state.personnel, d], ignore_index=True).drop_duplicates(subset=['שם'])
            co_per = st.session_state.personnel[st.session_state.personnel['פלוגה'] == sel_co]
            ed_per = st.data_editor(co_per, num_rows="dynamic", use_container_width=True, key=f"p_ed_{sel_co}")
            if st.button("שמור כוח אדם"):
                st.session_state.personnel = pd.concat([st.session_state.personnel[st.session_state.personnel['פלוגה'] != sel_co], ed_per], ignore_index=True)
                st.success("נשמר")

        with tabs[2]: # צל"ם
            co_eq = st.session_state.equipment[st.session_state.equipment['פלוגה'] == sel_co]
            if co_eq.empty: co_eq = pd.DataFrame([[sel_co, "M4", 0, 0, "תקין"], [sel_co, "מאג", 0, 0, "תקין"]], columns=st.session_state.equipment.columns)
            ed_eq = st.data_editor(co_eq, num_rows="dynamic", use_container_width=True, key=f"q_ed_{sel_co}")
            if st.button("שמור צל\"ם"):
                st.session_state.equipment = pd.concat([st.session_state.equipment[st.session_state.equipment['פלוגה'] != sel_co], ed_eq], ignore_index=True)
                st.success("נשמר")

        with tabs[3]: # תקשוב
            co_cm = st.session_state.comms[st.session_state.comms['פלוגה'] == sel_co]
            if co_cm.empty: co_cm = pd.DataFrame([[sel_co, "710", 0, 0, "תקין"], [sel_co, "624", 0, 0, "תקין"]], columns=st.session_state.comms.columns)
            ed_cm = st.data_editor(co_cm, num_rows="dynamic", use_container_width=True, key=f"c_ed_{sel_co}")
            if st.button("שמור תקשוב"):
                st.session_state.comms = pd.concat([st.session_state.comms[st.session_state.comms['פלוגה'] != sel_co], ed_cm], ignore_index=True)
                st.success("נשמר")

        with tabs[4]: # אירועים
            with st.form("ev_f"):
                tp = st.selectbox("סוג", ["מבצעי", "רפואי", "בטיחות", "אחר"])
                txt = st.text_area("תיאור")
                if st.form_submit_button("שלח"):
                    new_e = pd.DataFrame([[datetime.now().strftime("%H:%M"), sel_co, tp, txt]], columns=st.session_state.events.columns)
                    st.session_state.events = pd.concat([st.session_state.events, new_e], ignore_index=True)
                    st.error("נשלח")

    else: # --- דשבורד גדודי ---
        st.title("🏛️ דשבורד פיקודי - חרב שאול")
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("חריגים", len(st.session_state.events))
        with m2: 
            p = st.session_state.personnel
            count_m = len(p[p['סטטוס'] == 'מגוייס']) if not p.empty else 0
            st.metric("מגוייסים", count_m)
        with m3: 
            a = st.session_state.all_data
            ammo_tot = a['כמות'].sum() if not a.empty else 0
            st.metric("תחמושת", int(ammo_tot))
        with m4: st.metric("כשירות", "מבצעית")

        st.divider()
        cl, cr = st.columns(2)
        with cl:
            st.subheader("⚠️ חריגים")
            if not st.session_state.events.empty:
                for _, r in st.session_state.events.iloc[::-1].head(5).iterrows():
                    st.markdown(f"<div class='event-card'><b>{r['זמן']} | {r['פלוגה']}</b><br>{r['תיאור']}</div>", unsafe_allow_html=True)
            else: st.write("אין אירועים")
        with cr:
            st.subheader("💣 תחמושת")
            if not st.session_state.all_data.empty:
                st.bar_chart(st.session_state.all_data.groupby(['פלוגה', 'פרטים'])['כמות'].sum().unstack(fill_value=0))
            else: st.info("ממתין לנתונים")
        
        st.divider()
        st.subheader("📦 צל\"ם ותקשוב")
        c_eq, c_cm = st.columns(2)
        with c_eq:
            if not st.session_state.equipment.empty:
                st.bar_chart(st.session_state.equipment.groupby('פלוגה')[['נדרש', 'קיים']].sum())
        with c_cm:
            if not st.session_state.comms.empty:
                st.bar_chart(st.session_state.comms.groupby('פלוגה')[['נדרש', 'קיים']].sum())
