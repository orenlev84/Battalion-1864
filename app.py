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

# עדכון שמות הפלוגות לפי בקשתך
list_of_companies = ["ירדן", "גלבוע", "תענך", "עפולה", "פלס\"ם אג\"ם"]

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
        
        if st.button(f"שלח דיווח פלוגת {selected_company}"):
            new_report = pd.DataFrame([[selected_company, "תחמושת", item, amount, datetime.now().strftime("%H:%M")]], 
                                      columns=['פלוגה', 'סוג_דיווח', 'פרטים', 'כמות', 'זמן'])
            st.session_state.all_data = pd.concat([st.session_state.all_data, new_report], ignore_index=True)
            st.success(f"הדיווח נשמר במערכת עבור פלוגת {selected_company}")

    with tab2:
        st.subheader("עדכון סטטוס חייל (כ\"א)")
        with st.form("personnel_form"):
            p_name = st.text_input("שם החייל (או קוד/מספר)")
            p_status = st.selectbox("סטטוס גיוס", ["מגוייס", "משוחרר/מילואים", "בצוו 8"])
            p_loc = st.selectbox("מיקום נוכחי", ["ביחידה (בפעילות)", "בבית (אפטר)", 'במקום אחר (קורס/בי"ח)'])
            submit_p = st.form_submit_button("עדכן חייל")
            
            if submit_p:
                st.session_state.personnel = st.session_state.personnel[st.session_state.personnel['שם'] != p_name]
                new_p = pd.DataFrame([[selected_company, p_name, p_status, p_loc]], 
                                     columns=['פלוגה', 'שם', 'סטטוס_גיוס', 'מיקום'])
                st.session_state.personnel = pd.concat([st.session_state.personnel, new_p], ignore_index=True)
                st.success(f"הסטטוס של {p_name} עודכן")

# --- תצוגת גדוד (מבט מג"ד) ---
else:
    st.title("תמונת מצב גדודית - גדוד 1864")
    
    st.header("📊 סיכום כוח אדם גדודי")
    if not st.session_state.personnel.empty:
        col_a, col_b, col_c = st.columns(3)
        total_deployed = len(st.session_state.personnel[st.session_state.personnel['סטטוס_גיוס'] == "מגוייס"])
        in_unit = len(st.session_state.personnel[st.session_state.personnel['מיקום'] == "ביחידה (בפעילות)"])
        at_home = len(st.session_state.personnel[st.session_state.personnel['מיקום'] == "בבית (אפטר)"])
        
        col_a.metric("סך מגוייסים", total_deployed)
        col_b.metric("ביחידה", in_unit)
        col_c.metric("בבית", at_home)
        
        st.subheader("פירוט סטטוס לפי פלוגות")
        summary_table = st.session_state.personnel.groupby(['פלוגה', 'מיקום']).size().unstack(fill_value=0)
        st.dataframe(summary_table, use_container_width=True)
    else:
        st.info("אין נתוני כוח אדם להצגה")
    
    st.divider()
    
    st.header("💣 צריכת תחמושת גדודית")
    if not st.session_state.all_data.empty:
        ammo_df = st.session_state.all_data[st.session_state.all_data['סוג_דיווח'] == "תחמושת"]
        ammo_summary = ammo_df.groupby(['פלוגה', 'פרטים'])['כמות'].sum().unstack(fill_value=0)
        st.bar_chart(ammo_summary)
        st.dataframe(ammo_summary, use_container_width=True)
    else:
        st.info("טרם התקבלו דיווחי תחמושת מהפלוגות")
