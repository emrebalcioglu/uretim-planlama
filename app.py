import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Bağlantı Testi", layout="wide")

st.title("🚀 Google Sheets Bağlantı Testi")

# Bağlantıyı kur
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Sadece 'Isler' sayfasını oku
    df = conn.read(worksheet="Isler")
    
    st.success("✅ Bağlantı Başarılı!")
    st.write("E-tablodan gelen veriler:")
    st.dataframe(df)
    
except Exception as e:
    st.error(f"❌ Bağlantı Kurulamadı! Hata: {e}")
    st.info("İpucu: Secrets kısmındaki linki ve e-tablodaki 'Isler' sekmesini kontrol edin.")
