import streamlit as st
import pandas as pd
from datetime import datetime

# הגדרות תצוגה למובייל
st.set_page_config(page_title="חמ"ל פלוגתי", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 3em; font-size: 20px; }
    </style>
    """, unsafe_allow_metas=True)

st.title("📲 שליטה ובקרה פלוגתית")

# אתחול נתונים בזיכרון (כאן כדאי בהמשך לחבר ל-Google Sheets)
if 'logs' not in st.session_state:
    st.session_state.logs = []

tab1, tab2, tab3 = st.tabs(["דיווח", "מצב מלאי", "ניהול כ"א"])

with tab1:
    st.subheader("דיווח צריכת תחמושת")
    ammo_type = st.selectbox("סוג תחמושת", ["5.56", "7.62 (מאג)", "רימון", "מטול"], key="ammo")
    amount = st.number_input("כמות שנורתה", min_value=1, step=1)
    
    if st.button("שלח דיווח"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.logs.append({"זמן": timestamp, "סוג": ammo_type, "כמות": amount})
        st.success("הדיווח נקלט!")

with tab2:
    st.subheader("תמונת מצב מלאי")
    if st.session_state.logs:
        df = pd.DataFrame(st.session_state.logs)
        st.table(df)
        
        # אפשרות להוריד את הנתונים לאקסל בטלפון
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("הורד דו"ח למכשיר (CSV)", data=csv, file_name="ammo_report.csv")
    else:
        st.info("אין דיווחים עדיין")

with tab3:
    st.subheader("סטטוס מחלקות")
    # כאן אפשר להוסיף צ'ק-בוקסים מהירים למצבת בוקר
    st.checkbox("מחלקה 1 - כשירה")
    st.checkbox("מחלקה 2 - כשירה")
    st.checkbox("מחלקה 3 - כשירה")
