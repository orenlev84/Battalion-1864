import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. הגדרות דף בסיסיות ---
st.set_page_config(page_title="חרב שאול - שו\"ב גדודי", layout="wide")

# --- 2. CSS יציב ליישור לימין ועיצוב דשבורד ---
st.markdown("""
    <style>
    direction: rtl;
    text-align: right;
    .stMetric { background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 10px; padding: 10px; }
    .stButton>button { width: 100%; height: 3em; font-weight: bold; border-radius: 10px; }
    .event-card { background-color: #fff5f5; border-right: 5px solid #ff4b4b; padding: 10px; margin-bottom: 5px; border-radius: 5px; }
    div[data-testid="stForm"] { border: 1px solid #ddd; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. אתחול מאגרי נתונים ב-Session State ---
keys = ['all_data', 'personnel', 'events', 'equipment', 'comms']
for key in keys:
    if key not in st.session_state:
        st.session_state[key] = pd.DataFrame()

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = None

# --- 4. מערכת הרשאות וסיסמאות ---
passwords_map = {
    "magad123": "מג\"ד",
    "yarden123": "ירדן",
    "gilboa123": "גלבוע",
    "taanach123": "תענך",
    "hafoola123": "עפולה",
    "palsam123": "פלס\"ם אג\"ם"
}

# --- 5. לוגיקה של מסך כניסה ---
if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        if os.path.exists("battalion_logo.png"): st.image("battalion_logo.png", width=150)
        st.title("מערכת חרב שאול")
        u_labels = list(passwords_map.values())
        u_choice = st.selectbox("בחר יחידה", options=u_labels)
        p_input = st.text_input("סיסמה", type="password")
        if st.button("התחבר"):
            # מציאת הסיסמה הנכונה עבור הבחירה
            correct_pass = [k for k, v in passwords_map.items() if v == u_choice][0]
            if p_input == correct_pass:
                st.session_state.logged_in = True
                st.session_state.user_role = u_choice
                st.rerun()
            else:
                st.error("סיסמה שגויה")

# --- 6. ממשק לאחר התחברות ---
else:
    with st.sidebar:
        if os.path.exists("battalion_logo.png"): st.image("battalion_logo.png", width=80)
        st.subheader(f"שלום, {st.session_state.user_role}")
        view_mode = "ניהול פלוגה"
        if st.session_state.user_role == "מג\"ד":
            view_mode = st.radio("תפריט", ["דשבורד גדודי", "ניהול פלוגה"])
        if st.button("התנתק"):
            st.session_state.logged_in = False
            st.rerun()

    # --- א. ממשק ניהול פלוגתי ---
    if view_mode == "ניהול פלוגה":
        all_companies = ["ירדן", "גלבוע", "תענך", "עפולה", "פלס\"ם אג\"ם"]
        if st.session_state.user_role == "מג\"ד":
            sel_co = st.selectbox("בחר פלוגה לניהול:", all_companies)
        else:
            sel_co = st.session_state.user_role
            
        st.header(f"ניהול נתונים - פלוגת {sel_co}")
        tabs = st.tabs(["תחמושת", "כוח אדם", "צל\"ם", "תקשוב", "אירועים"])
        
        with tabs[0]: # תחמושת
            with st.form("ammo_f"):
                a_type = st.selectbox("סוג", ["5.56", "7.62", "רימון", "לאו", "מטול"])
                a_num = st.number_input("כמות", min_value=0, step=1)
                if st.form_submit_button("דווח"):
                    new_a = pd.DataFrame([[sel_co, "תחמושת", a_type, a_num, datetime.now().strftime("%H:%M")]], columns=['פלוגה','סוג','פרטים','כמות','זמן'])
                    st.session_state.all_data = pd.concat([st.session_state.all_data, new_a], ignore_index=True)
                    st.success("דיווח נשמר")

        with tabs[1]: # כוח אדם
            f = st.file_uploader("טען אקסל כוח אדם", type=['xlsx'])
            if f:
                d = pd.read_excel(f)
                d['פלוגה'] = sel_co
                st.session_state.personnel = pd.concat([st.session_state.personnel, d], ignore_index=True).drop_duplicates(subset=['שם'])
            co_per = st.session_state.personnel[st.session_state.personnel['פלוגה'] == sel_co] if not st.session_state.personnel.empty else pd.DataFrame(columns=['פלוגה','שם','סטטוס','מיקום'])
            ed_per = st.data_editor(co_per, num_rows="dynamic", use_container_width=True, key="per_ed")
            if st.button("שמור כוח אדם"):
                others = st.session_state.personnel[st.session_state.personnel['פלוגה'] != sel_co] if not st.session_state.personnel.empty else pd.DataFrame()
                st.session_state.personnel = pd.concat([others, ed_per], ignore_index=True)
                st.success("עודכן")

        with tabs[2]: # צל"ם
            co_eq = st.session_state.equipment[st.session_state.equipment['פלוגה'] == sel_co] if not st.session_state.equipment.empty else pd.DataFrame(columns=['פלוגה','פריט','נדרש','קיים','סטטוס'])
            if co_eq.empty:
                co_eq = pd.DataFrame([[sel_co, "M4", 0, 0, "תקין"], [sel_co, "מאג", 0, 0, "תקין"]], columns=['פלוגה','פריט','נדרש','קיים','סטטוס'])
            ed_eq = st.data_editor(co_eq, num_rows="dynamic", use_container_width=True, key="eq_ed")
            if st.button("שמור צל\"ם"):
                others_eq = st.session_state.equipment[st.session_state.equipment['פלוגה'] != sel_co] if not st.session_state.equipment.empty else pd.DataFrame()
                st.session_state.equipment = pd.concat([others_eq, ed_eq], ignore_index=True)
                st.success("עודכן")

        with tabs[3]: # תקשוב
            co_cm = st.session_state.comms[st.session_state.comms['פלוגה'] == sel_co] if not st.session_state.comms.empty else pd.DataFrame(columns=['פלוגה','מכשיר','נדרש','קיים','סטטוס'])
            if co_cm.empty:
                co_cm = pd.DataFrame([[sel_co, "710", 0, 0, "תקין"], [sel_co, "624", 0, 0, "תקין"]], columns=['פלוגה','מכשיר','נדרש','קיים','סטטוס'])
            ed_cm = st.data_editor(co_cm, num_rows="dynamic", use_container_width=True, key="cm_ed")
            if st.button("שמור תקשוב"):
                others_cm = st.session_state.comms[st.session_state.comms['פלוגה'] != sel_co] if not st.session_state.comms.empty else pd.DataFrame()
                st.session_state.comms = pd.concat([others_cm, ed_cm], ignore_index=True)
                st.success("עודכן")

        with tabs[4]: # אירועים
            with st.form("ev_f"):
                e_type = st.selectbox("סוג אירוע", ["מבצעי", "רפואי", "בטיחות", "אחר"])
                e_txt = st.text_area("תיאור")
                if st.form_submit_button("שלח"):
                    new_e = pd.DataFrame([[datetime.now().strftime("%H:%M"), sel_co, e_type, e_txt]], columns=['זמן','פלוגה','סוג','תיאור'])
                    st.session_state.events = pd.concat([st.session_state.events, new_e], ignore_index=True)
                    st.error("דווח למפקדה")

    # --- ב. דשבורד גדודי אטרקטיבי ---
    else:
        st.title("🏛️ דשבורד פיקודי - גדוד 1864")
        m1, m2, m3, m4 = st
