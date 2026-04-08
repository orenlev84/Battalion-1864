import streamlit as st
import pandas as pd
from datetime import datetime

# הגדרות תצוגה
st.set_page_config(page_title='מערכת שו"ב גדודית', layout="wide")

# עיצוב מותאם למובייל
st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 3em; font-size: 18px; font-weight: bold; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- ניהול נתונים (זמני בזיכרון) ---
if 'all_data' not in st.session_state:
    st.session_state.all_data = pd.DataFrame(columns=['פלוגה', 'סוג_דיווח', 'פרטים', 'כמות', 'זמן'])
if 'personnel' not in st.session_state:
    st.session_state.personnel = pd.DataFrame(columns=['פלוגה', 'שם', 'סטטוס_גיוס', 'מיקום'])

# --- סרגל צד לניווט ---
st.sidebar.title("תפריט שליטה")
view_mode = st.sidebar.radio("בחר תצוגה:", ["ניהול פלוגה", "תמונת מצב גדודית"])

list_of_companies = ["פלוגה א'", "פלוגה ב'", "פלוגה ג'", "פלוגת סיוע"]

if view_mode == "ניהול פלוגה":
    selected_company = st.sidebar.selectbox("בחר את הפלוגה שלך:", list_of_companies)
    st.title(f"ניהול נתונים - {selected_company}")
    
    tab1, tab2 = st.tabs(["דיווח תחמושת", "ניהול כוח אדם"])
    
    with tab1:
        st.subheader("דיווח צריכה")
        col1, col2 = st.columns(2)
        with col1:
            item = st.selectbox("סוג תחמושת", ["5.56", "7.62", "רימון", "לאו", "מטול"])
        with col2:
            amount = st.number_input("כמות", min_value=1, step=1)
        
        if st.button(f"שלח דיווח {selected_company}"):
            new_report = pd.DataFrame([[selected_company, "תחמושת", item, amount, datetime.now().strftime("%H:%M")]], 
                                      columns=['פלוגה', 'סוג_דיווח', 'פרטים', 'כמות', 'זמן'])
            st.session_state.all_data = pd.concat([st.session_state.all_data, new_report], ignore_index=True)
            st.success("הדיווח נשמר במערכת הגדודית")

    with tab2:
        st.subheader("עדכון סטטוס חייל (כ\"א)")
        with st.form("personnel_form"):
            p_name = st.text_input("שם החייל (או קוד/מספר)")
            p_status = st.selectbox("סטטוס גיוס", ["מגוייס", "משוחרר/מילואים", "בצוו 8"])
            # שים לב לשימוש במירכאות בודדות כדי לפתור את בעיית הבי"ח
            p_loc = st.selectbox("מיקום נוכחי", ["ביחידה (בפעילות)", "בבית (אפטר)", 'במקום אחר (קורס/בי"ח)'])
            submit_p = st.form_submit_button("עדכן חייל")
            
            if submit_p:
                st.session_state.personnel = st.session_state.personnel[st.session_state.personnel['שם'] != p_name]
