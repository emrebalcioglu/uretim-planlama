import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Bağlantı Testi", layout="wide")
st.title("Google Sheets Bağlantı Testi")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)

    df = conn.read()

    st.success("Bağlantı başarılı")
    st.dataframe(df)

except Exception as e:
    st.error(f"Hata: {e}")
