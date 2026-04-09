import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- הגדרות תצוגה מתקדמות ---
st.set_page_config(
    page_title="חרב שאול - שו\"ב גדודי",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- עיצוב CSS מותאם אישית למובייל (ידידותי למשתמש) ---
st.markdown("""
    <style>
    /* עיצוב כללי ופונטים */
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="css"]  { font-family: 'Assistant', sans-serif; }

    /* עיצוב סרגל הצד */
    .css-1d391kg { background-color: #f0f2f6; }
    .sidebar-logo { display: block; margin-left: auto; margin-right: auto; width: 80px; }
    .sidebar-title { text-align: center; color: #1e3a8a; font-weight: bold; margin-top: -10px; margin-bottom: 20px; }

    /* עיצוב כפתורים גדולים למובייל */
    .stButton>button { 
        width: 100%; height: 3.5em; font-size: 18px; font-weight: bold; 
        border-radius: 12px; transition: all 0.3s;
    }
    .stButton>button:hover { background-color: #1e3a8a; color: white; transform: scale(1.02); }

    /* עיצוב מדדים (Metrics) - קוביות נתונים */
    [data-testid="stMetricValue"] { font-size: 2.5rem; font-weight: bold; color: #1e3a8a; }
    [data-testid="stMetricLabel"] { font-size: 1.1rem; color: #4b5563; }
    .stMetric { 
        background-color: white; padding: 15px; border-radius: 15px; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); 
        border: 1px solid #e5e7eb;
    }

    /* עיצוב כרטיסי אירועים חריגים */
    .event-card { 
        background-color: #fef2f2; border: 2px solid #ef4444; border-radius: 10px; 
        padding: 10px; margin-bottom: 10px; 
    }
    .event-time { color: #991b1b; font-weight: bold; font-size: 0.9em; }
    .event-co { color: #b91c1c; font-weight: bold; }
    .event-desc { color: #000; margin-top: 5px; }

    /* עיצוב כרטיסיות (Tabs) */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #f3f4f6; border-radius: 10px; padding: 10px 20px; 
        color: #4b5563; font-weight: bold; 
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #1e3a8a; color: white; }

    </style>
    """, unsafe_allow_html=True)

# --- טעינת נתונים בזיכרון (יימחק ברענון) ---
if 'all_data' not in st.session_state:
    st.session_state.all_data = pd.DataFrame(columns=['פלוגה', 'סוג_דיווח', 'פרטים', 'כמות', 'זמן'])
if 'personnel' not in st.session_state:
    st.session_state.personnel = pd.DataFrame(columns=['פלוגה', 'שם', 'סטטוס_גיוס', 'מיקום'])
if 'events' not in st.session_state:
    st.session_state.events = pd.DataFrame(columns=['זמן', 'פלוגה', 'סוג_אירוע', 'תיאור'])

# --- סרגל צד (Sidebar) מעוצב ---
with st.sidebar:
    # 1. הוספת לוגו וכותרת "חרב שאול"
    logo_path = "battalion_logo.png" # שם הקובץ שנעלה ל-GitHub
    if os.path.exists(logo_path):
        st.image(logo_path, width=100)
    
    st.markdown('<div class="sidebar-title">חרב שאול</div>', unsafe_allow_html=True)
    st.title("🗺️ תפריט")
    view_mode = st.radio("בחר תצוגה:", ["ניהול פלוגה", "תמונת מצב גדודית"], index=1)
    
    st.divider()
    
    list_of_companies = ["ירדן", "גלבוע", "תענך", "עפולה", "פלס\"ם אג\"ם"]

# --- תצוגת פלוגה (למ"פ/סמ"פ) ---
if view_mode == "ניהול פלוגה":
    selected_company = st.sidebar.selectbox("בחר את הפלוגה שלך:", list_of_companies)
    st.title(f"📊 ניהול נתונים - {selected_company}")
    
    tab1, tab2, tab3 = st.tabs(["💣 תחמושת", "👥 כוח אדם", "⚠️ אירועים"])
    
    with tab1:
        st.subheader("📝 דיווח צריכה")
        col1, col2 = st.columns(2)
        with col1:
            item = st.selectbox("סוג תחמושת", ["5.56", "7.62", "רימון", "לאו", "מטול"])
        with col2:
            amount = st.number_input("כמות שנורתה", min_value=1, step=1)
        
        if st.button(f"שלח דיווח ({selected_company})"):
            new_report = pd.DataFrame([[selected_company, "תחמושת", item, amount, datetime.now().strftime("%H:%M")]], 
                                      columns=['פלוגה', 'סוג_דיווח', 'פרטים', 'כמות', 'זמן'])
            st.session_state.all_data = pd.concat([st.session_state.all_data, new_report], ignore_index=True)
            st.success(f"הדיווח נשמר 👍")

    with tab2:
        st.subheader("📝 עדכון סטטוס חייל")
        with st.form("personnel_form"):
            p_name = st.text_input("שם החייל / מספר")
            p_status = st.selectbox("סטטוס גיוס", ["מגוייס", "משוחרר/מילואים", "בצוו 8"])
            p_loc = st.selectbox("מיקום נוכחי", ["ביחידה (בפעילות)", "בבית (אפטר)", 'במקום אחר (קורס/בי"ח)'])
            submit_p = st.form_submit_button("עדכן סטטוס حייאל")
            
            if submit_p:
                st.session_state.personnel = st.session_state.personnel[st.session_state.personnel['שם'] != p_name]
                new_p = pd.DataFrame([[selected_company, p_name, p_status, p_loc]], 
                                     columns=['פלוגה', 'שם', 'סטטוס_גיוס', 'מיקום'])
                st.session_state.personnel = pd.concat([st.session_state.personnel, new_p], ignore_index=True)
                st.success(f"הסטטוס של {p_name} עודכן")

    with tab3:
        st.subheader("📝 דיווח אירוע חריג")
        with st.form("event_form"):
            event_type = st.selectbox("סוג אירוע", ["🚒 בטיחות", "🚑 רפואי", "⚔️ מבצעי", "⚖️ משמעת", "❓ אחר"])
            event_desc = st.text_area("פירוט האירוע")
            submit_event = st.form_submit_button("🚀 שלח דיווח דחוף לגדוד")
            
            if submit_event:
                new_event = pd.DataFrame([[datetime.now().strftime("%d/%m %H:%M"), selected_company, event_type, event_desc]], 
                                         columns=['זמן', 'פלוגה', 'סוג_אירוע', 'תיאור'])
                st.session_state.events = pd.concat([st.session_state.events, new_event], ignore_index=True)
                st.error("הדיווח נשלח למג\"ד!")

# --- תצוגת גדוד (למג"ד - ה-Dashboard הידידותי) ---
else:
    st.title("🏛️ חמ\"ל גדודי - גדוד 1864")
    
    # --- 1. אירועים חריגים ככרטיסים (Cards) ---
    st.markdown("### ⚠️ אירועים חריגים אחרונים")
    if not st.session_state.events.empty:
        # הצגת 3 אירועים אחרונים ככרטיסים מעוצבים
        latest_events = st.session_state.events.iloc[::-1].head(3)
        for index, row in latest_events.iterrows():
            st.markdown(f"""
                <div class="event-card">
                    <span class="event-time">{row['זמן']}</span> - 
                    <span class="event-co">פלוגת {row['פלוגה']}</span> | 
                    <strong>{row['סוג_אירוע']}</strong>
                    <div class="event-desc">{row['תיאור']}</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("אין אירועים חריגים מדווחים ✅")
    
    st.divider()

    # --- 2. סיכום כוח אדם כקוביות נתונים (Metrics) ---
    st.markdown("### 👥 מצב כוח אדם גדודי")
    if not st.session_state.personnel.empty:
        col_a, col_b, col_c = st.columns(3)
        
        # חישוב נתונים
        total_deployed = len(st.session_state.personnel[st.session_state.personnel['סטטוס_גיוס'] == "מגוייס"])
        in_unit = len(st.session_state.personnel[st.session_state.personnel['מיקום'] == "ביחידה (בפעילות)"])
        at_home = len(st.session_state.personnel[st.session_state.personnel['מיקום'] == "בבית (אפטר)"])
        
        # הצגה כקוביות
        with col_a: st.metric("סך מגוייסים", total_deployed, help="חיילים בסטטוס 'מגוייס'")
        with col_b: st.metric("נמצאים ביחידה", in_unit, delta=f"{in_unit} ח'")
        with col_c: st.metric("נמצאים בבית", at_home, delta=f"-{at_home} ח'", delta_color="inverse")
        
        st.markdown("#### פירוט לפי פלוגות")
        # טבלה מעוצבת יותר (use_container_width)
        summary_table = st.session_state.personnel.groupby(['פלוגה', 'מיקום']).size().unstack(fill_value=0)
        st.dataframe(summary_table, use_container_width=True)
    else:
        st.info("אין נתוני כוח אדם")
    
    st.divider()
    
    # --- 3. סיכום תחמושת כגרף מעוצב ---
    st.markdown("### 💣 צריכת תחמושת גדודית")
    if not st.session_state.all_data.empty:
        ammo_df = st.session_state.all_data[st.session_state.all_data['סוג_דיווח'] == "תחמושת"]
        ammo_summary = ammo_df.groupby(['פלוגה', 'פרטים'])['כמות'].sum().unstack(fill_value=0)
        
        # גרף ברים צבעוני
        st.bar_chart(ammo_summary)
    else:
        st.info("טרם התקבלו דיווחי תחמושת")
