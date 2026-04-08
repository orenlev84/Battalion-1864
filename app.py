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
    .exception-box { padding: 10px; border: 1px solid #ff4b4b; border-radius: 5px; background-color: #fff1f1; }
    </style>
    """, unsafe_allow_html=True)

# --- ניהול נתונים בזיכרון ---
if 'all_data' not in st.session_state:
    st.session_state.all_data = pd.DataFrame(columns=['פלוגה', 'סוג_דיווח', 'פרטים', 'כמות', 'זמן'])
if 'personnel' not in st.session_state:
    st.session_state.personnel = pd.DataFrame(columns=['פלוגה', 'שם', 'סטטוס_גיוס', 'מיקום'])
if 'events' not in st.session_state:
    st.session_state.events = pd.DataFrame(columns=['זמן', 'פלוגה', 'סוג_אירוע', 'תיאור'])

# --- סרגל צד לניווט ---
st.sidebar.title("תפריט שליטה")
view_mode = st.sidebar.radio("בחר תצוגה:", ["ניהול פלוגה", "תמונת מצב גדודית"])

list_of_companies = ["ירדן", "גלבוע", "תענך", "עפולה", "פלס\"ם אג\"ם"]

if view_mode == "ניהול פלוגה":
    selected_company = st.sidebar.selectbox("בחר את הפלוגה שלך:", list_of_companies)
    st.title(f"ניהול נתונים - {selected_company}")
    
    tab1, tab2, tab3 = st.tabs(["דיווח תחמושת", "ניהול כוח אדם", "אירועים חריגים"])
    
    with tab1:
        st.subheader("דיווח צריכת תחמושת")
        col1, col2 = st.columns(2)
        with col1:
            item = st.selectbox("סוג תחמושת", ["5.56", "7.62", "רימון", "לאו", "מטול"])
        with col2:
            amount = st.number_input("כמות", min_value=1, step=1)
        
        if st.button(f"שלח דיווח פלוגת {selected_company}"):
            new_report = pd.DataFrame([[selected_company, "תחמושת", item, amount, datetime.now().strftime("%H:%M")]], 
                                      columns=['פלוגה', 'סוג_דיווח', 'פרטים', 'כמות', 'זמן'])
            st.session_state.all_data = pd.concat([st.session_state.all_data, new_report], ignore_index=True)
            st.success(f"הדיווח נשמר במערכת")

    with tab2:
        st.subheader("עדכון סטטוס חייל")
        with st.form("personnel_form"):
            p_name = st.text_input("שם החייל / מספר")
            p_status = st.selectbox("סטטוס גיוס", ["מגוייס", "משוחרר/מילואים", "בצוו 8"])
            p_loc = st.selectbox("מיקום נוכחי", ["ביחידה (בפעילות)", "בבית (אפטר)", 'במקום אחר (קורס/בי"ח)'])
            submit_p = st.form_submit_button("עדכן חייל")
            
            if submit_p:
                st.session_state.personnel = st.session_state.personnel[st.session_state.personnel['שם'] != p_name]
                new_p = pd.DataFrame([[selected_company, p_name, p_status, p_loc]], 
                                     columns=['פלוגה', 'שם', 'סטטוס_גיוס', 'מיקום'])
                st.session_state.personnel = pd.concat([st.session_state.personnel, new_p], ignore_index=True)
                st.success(f"הסטטוס של {p_name} עודכן")

    with tab3:
        st.subheader("דיווח אירוע חריג")
        with st.form("event_form"):
            event_type = st.selectbox("סוג אירוע", ["בטיחות", "רפואי", "מבצעי", "משמעת", "אחר"])
            event_desc = st.text_area("פירוט האירוע")
            submit_event = st.form_submit_button("שלח דיווח חריג")
            
            if submit_event:
                new_event = pd.DataFrame([[datetime.now().strftime("%d/%m %H:%M"), selected_company, event_type, event_desc]], 
                                         columns=['זמן', 'פלוגה', 'סוג_אירוע', 'תיאור'])
                st.session_state.events = pd.concat([st.session_state.events, new_event], ignore_index=True)
                st.error("הדיווח נשלח לרמת הגדוד!") # צבע אדום להדגשת חריג

# --- תצוגת גדוד (מבט מג"ד) ---
else:
    st.title("תמונת מצב גדודית - גדוד 1864")
    
    # --- אירועים חריגים למעלה (כי זה הכי דחוף) ---
    st.header("⚠️ אירועים חריגים אחרונים")
    if not st.session_state.events.empty:
        # הצגת האירועים האחרונים קודם
        st.table(st.session_state.events.iloc[::-1])
    else:
        st.info("אין אירועים חריגים מדווחים")
    
    st.divider()

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
    
    st.divider()
    
    st.header("💣 צריכת תחמושת גדודית")
    if not st.session_state.all_data.empty:
        ammo_df = st.session_state.all_data[st.session_state.all_data['סוג_דיווח'] == "תחמושת"]
        ammo_summary = ammo_df.groupby(['פלוגה', 'פרטים'])['כמות'].sum().unstack(fill_value=0)
        st.bar_chart(ammo_summary)
    else:
        st.info("טרם התקבלו דיווחי תחמושת")
