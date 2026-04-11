import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. הגדרות בסיס
st.set_page_config(page_title="חרב שאול - ניהול גדודי", layout="wide")

# 2. CSS מינימליסטי ליישור לימין ומירכוז
st.markdown("""
    <style>
    direction: rtl;
    text-align: right;
    font-family: sans-serif;
    .stButton>button { width: 100%; height: 3em; font-weight: bold; border-radius: 10px; }
    div[data-testid="stForm"] { border: 1px solid #ddd; padding: 10px; border-radius: 10px; }
    /* מירכוז כותרת וסמל במסך כניסה */
    .login-box { display: flex; flex-direction: column; align-items: center; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 3. אתחול מאגרי נתונים (כולל צל"ם)
if 'all_data' not in st.session_state: st.session_state.all_data = pd.DataFrame(columns=['פלוגה','סוג','פרטים','כמות','זמן'])
if 'personnel' not in st.session_state: st.session_state.personnel = pd.DataFrame(columns=['פלוגה','שם','סטטוס','מיקום'])
if 'events' not in st.session_state: st.session_state.events = pd.DataFrame(columns=['זמן','פלוגה','סוג','תיאור'])
if 'equipment' not in st.session_state: st.session_state.equipment = pd.DataFrame(columns=['פלוגה','סוג_ציוד','שם_פריט','כמות_נדרשת','כמות_קיימת','סטטוס'])
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = None

# 4. ניהול כניסה
passwords = {
    "magad123": "מג\"ד", "yarden123": "ירדן", "gilboa123": "גלבוע",
    "taanach123": "תענך", "hafoola123": "עפולה", "palsam123": "פלס\"ם אג\"ם"
}

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        if os.path.exists("battalion_logo.png"): st.image("battalion_logo.png", width=150)
        st.title("מערכת חרב שאול")
        st.markdown('</div>', unsafe_allow_html=True)
        
        user_choice = st.selectbox("בחר יחידה", list(passwords.values()))
        pass_input = st.text_input("סיסמה", type="password")
        if st.button("התחבר"):
            correct_pass = [k for k, v in passwords.items() if v == user_choice][0]
            if pass_input == correct_pass:
                st.session_state.logged_in = True
                st.session_state.user_role = user_choice
                st.rerun()
            else: st.error("סיסמה לא נכונה")

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
        
        # הוספת הלשונית החדשה: צל"ם ותקשוב
        tab_ammo, tab_per, tab_equip, tab_ev = st.tabs(["💣 תחמושת", "👥 כוח אדם", "📦 צל\"ם ותקשוב", "⚠️ אירועים"])
        
        with tab_ammo:
            with st.form("f_ammo"):
                itm = st.selectbox("סוג", ["5.56", "7.62", "רימון", "לאו", "מטול"])
                num = st.number_input("כמות", min_value=0)
                if st.form_submit_button("דווח"):
                    new_a = pd.DataFrame([[sel_co, "תחמושת", itm, num, datetime.now().strftime("%H:%M")]], columns=st.session_state.all_data.columns)
                    st.session_state.all_data = pd.concat([st.session_state.all_data, new_a], ignore_index=True)
                    st.success("דיווח נשמר")

        with tab_per:
            f = st.file_uploader("טען אקסל כוח אדם", type=['xlsx'])
            if f:
                d = pd.read_excel(f)
                d['פלוגה'] = sel_co
                st.session_state.personnel = pd.concat([st.session_state.personnel, d], ignore_index=True).drop_duplicates(subset=['שם'])
                st.success("נטען בהצלחה")
            
            co_per = st.session_state.personnel[st.session_state.personnel['פלוגה'] == sel_co]
            edited_per = st.data_editor(co_per, num_rows="dynamic", use_container_width=True)
            if st.button("שמור שינויים בכוח אדם"):
                others = st.session_state.personnel[st.session_state.personnel['פלוגה'] != sel_co]
                st.session_state.personnel = pd.concat([others, edited_per], ignore_index=True)
                st.success("המצבה עודכנה")

        with tab_equip:
            st.subheader("מעקב צל\"ם, נשק ותקשוב")
            st.info("ניתן להוסיף שורות חדשות עבור פריטים נוספים (נשקים, מכשירי קשר וכו')")
            
            # סינון ציוד לפי פלוגה
            co_equip = st.session_state.equipment[st.session_state.equipment['פלוגה'] == sel_co]
            
            # אם הרשימה ריקה, ניצור פריטי בסיס כברירת מחדל
            if co_equip.empty:
                default_items = [
                    [sel_co, "נשק", "M4/M16", 0, 0, "תקין"],
                    [sel_co, "נשק", "מאג", 0, 0, "תקין"],
                    [sel_co, "תקשוב", "מכשיר קשר 710", 0, 0, "תקין"],
                    [sel_co, "תקשוב", "מכשיר קשר 624", 0, 0, "תקין"]
                ]
                co_equip = pd.DataFrame(default_items, columns=st.session_state.equipment.columns)

            edited_equip = st.data_editor(
                co_equip, 
                column_order=("סוג_ציוד", "שם_פריט", "כמות_נדרשת", "כמות_קיימת", "סטטוס"),
                num_rows="dynamic", 
                use_container_width=True
            )
            
            if st.button("שמור דוח צל\"ם"):
                edited_equip['פלוגה'] = sel_co # לוודא ששם הפלוגה נשמר
                others_eq = st.session_state.equipment[st.session_state.equipment['פלוגה'] != sel_co]
                st.session_state.equipment = pd.concat([others_eq, edited_equip], ignore_index=True)
                st.success("דוח צל\"ם ותקשוב עודכן!")

        with tab_ev:
            with st.form("f_ev"):
                tp = st.selectbox("סוג", ["בטיחות", "רפואי", "מבצע
