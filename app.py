import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. הגדרות דף
st.set_page_config(page_title='חרב שאול - שו"ב גדודי', layout="wide")

# 2. CSS מתקדם לדשבורד
st.markdown("""
    <style>
    direction: rtl;
    text-align: right;
    .stMetric { background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 10px; padding: 10px; }
    .stButton>button { width: 100%; height: 3em; font-weight: bold; border-radius: 10px; }
    .event-card { background-color: #fff5f5; border-right: 5px solid #ff4b4b; padding: 10px; margin-bottom: 5px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 3. אתחול מאגרי נתונים (אם לא קיימים)
for key in ['all_data', 'personnel', 'events', 'equipment', 'comms']:
    if key not in st.session_state:
        st.session_state[key] = pd.DataFrame()

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# 4. מערכת הרשאות וסיסמאות
passwords = {
    "magad123": "מג\"ד", "yarden123": "ירדן", "gilboa123": "גלבוע",
    "taanach123": "תענך", "hafoola123": "עפולה", "palsam123": "פלס\"ם אג\"ם"
}

# --- מסך כניסה (קוצר לצורך הדוגמה) ---
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
        # (הקוד של ניהול פלוגה נשאר זהה לגרסה הקודמת עם הטאבים)
        st.info("כאן מופיע ממשק הניהול הפלוגתי כפי שהיה")
        
    else: # --- דשבורד גדודי אטרקטיבי ---
        st.title("🏛️ דשבורד פיקודי - גדוד 1864")
        
        # שורת מדדים עליונה (KPIs)
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            count_ev = len(st.session_state.events)
            st.metric("אירועים חריגים", count_ev, delta=count_ev, delta_color="inverse")
        with m2:
            total_per = len(st.session_state.personnel[st.session_state.personnel['סטטוס'] == 'מגוייס'])
            st.metric("סך מגוייסים", total_per)
        with m3:
            total_ammo = st.session_state.all_data['כמות'].sum() if not st.session_state.all_data.empty else 0
            st.metric("תחמושת שנורתה", int(total_ammo))
        with m4:
            st.metric("סטטוס גדוד", "מבצעי", delta="תקין")

        st.divider()

        # חלוקה לטורים: אירועים מול תחמושת
        col_right, col_left = st.columns([1, 1])

        with col_right:
            st.subheader("⚠️ אירועים חריגים אחרונים")
            if not st.session_state.events.empty:
                for _, row in st.session_state.events.iloc[::-1].head(5).iterrows():
                    st.markdown(f"""
                    <div class="event-card">
                        <strong>{row['זמן']} | פלוגת {row['פלוגה']}</strong><br>
                        {row['סוג']}: {row['תיאור']}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.write("אין אירועים לדווח")

        with col_left:
            st.subheader("💣 צריכת תחמושת לפי פלוגה")
            if not st.session
