import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Sayfa Konfigürasyonu
st.set_page_config(page_title="Üretim İş Emri Sistemi", layout="wide")

st.title("🏭 Üretim İş Emri ve Planlama")

# --- BAĞLANTI (Test ettiğimiz ve çalışan yöntem) ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0)
    
    # E-tablo boşsa başlıkları hazırla
    if df.empty:
        df = pd.DataFrame(columns=["İş Emri No", "Müşteri", "İş Tanımı", "Miktar", "Süreç", "Sorumlu", "Teslim Tarihi"])

    # --- SOL PANEL: İŞ EMRİ GİRİŞİ ---
    with st.sidebar:
        st.header("📝 Yeni İş Emri Oluştur")
        with st.form("is_emri_formu", clear_on_submit=True):
            ie_no = st.text_input("İş Emri No", placeholder="Örn: IE-001")
            musteri = st.text_input("Müşteri / Proje")
            is_tanimi = st.text_area("İşin Detaylı Tanımı")
            miktar = st.number_input("Adet / Miktar", min_value=1, step=1)
            
            st.divider()
            
            # Operasyonel Detaylar
            personel_listesi = ["Emre Balcıoğlu", "Ahmet", "Mehmet", "Dış Tedarik"]
            sorumlu = st.selectbox("İşten Sorumlu Personel", personel_listesi)
            
            surec_listesi = ["Beklemede", "Tasarım/Onay", "Ham Malzeme", "Üretim", "Boya/Kaplama", "Montaj", "Sevkiyata Hazır"]
            surec = st.selectbox("İşin Mevcut Durumu", surec_listesi)
            
            teslim_tarihi = st.date_input("Planlanan Teslim Tarihi")
            
            submit = st.form_submit_button("İş Emrini Kaydet")

            if submit:
                if ie_no and musteri:
                    yeni_kayit = pd.DataFrame([{
                        "İş Emri No": ie_no,
                        "Müşteri": musteri,
                        "İş Tanımı": is_tanimi,
                        "Miktar": miktar,
                        "Süreç": surec,
                        "Sorumlu": sorumlu,
                        "Teslim Tarihi": teslim_tarihi.strftime("%d.%m.%Y")
                    }])
                    
                    # Veriyi ekle ve Google Sheets'i güncelle
                    guncel_df = pd.concat([df, yeni_kayit], ignore_index=True)
                    conn.update(data=guncel_df)
                    st.toast(f"{ie_no} Nolu İş Emri Kaydedildi!", icon="🚀")
                    st.rerun()
                else:
                    st.error("Lütfen 'İş Emri No' ve 'Müşteri' alanlarını boş bırakmayın.")

    # --- ANA EKRAN: OPERASYONEL TAKİP ---
    
    # Üst Özet Kartları
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Aktif İş Emirleri", len(df[df["Süreç"] != "Sevkiyata Hazır"]))
    c2.metric("Üretim Aşamasında", len(df[df["Süreç"] == "Üretim"]))
    c3.metric("Bekleyen İşler", len(df[df["Süreç"] == "Beklemede"]))
    c4.metric("Tamamlanan", len(df[df["Süreç"] == "Sevkiyata Hazır"]))

    st.subheader("📋 Üretim Çizelgesi ve İş Takibi")
    
    # Tablo Filtreleme
    col_search, col_filter = st.columns([2, 1])
    with col_search:
        search_query = st.text_input("🔍 İş Emri veya Müşteri Ara...")
    with col_filter:
        filter_status = st.multiselect("Duruma Göre Filtrele", options=surec_listesi)

    # Veriyi Filtrele
    view_df = df.copy()
    if search_query:
        view_df = view_df[view_df.apply(lambda row: search_query.lower() in row.astype(str).str.lower().values, axis=1)]
    if filter_status:
        view_df = view_df[view_df["Süreç"].isin(filter_status)]

    # Tabloyu şık bir şekilde göster
    st.dataframe(
        view_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "İş Emri No": st.column_config.TextColumn("İş Emri No", help="Benzersiz iş emri numarası"),
            "Süreç": st.column_config.SelectboxColumn("Süreç", options=surec_listesi),
            "Miktar": st.column_config.NumberColumn("Miktar", format="%d Adet"),
            "Teslim Tarihi": st.column_config.TextColumn("📅 Teslim Tarihi")
        }
    )

except Exception as e:
    st.error(f"Sistem Hatası: {e}")
    st.info("Bağlantı sağlandı ancak veri okuma/yazma hatası oluştu. Lütfen Google Sheets yapısını kontrol et.")
