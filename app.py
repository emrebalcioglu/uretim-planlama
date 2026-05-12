import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Sayfa Yapılandırması
st.set_page_config(page_title="Üretim Planlama v1.0", layout="wide", initial_sidebar_state="expanded")

st.title("🏭 Üretim Planlama ve Takip Sistemi")

# --- BAĞLANTI ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # ttl=0 verinin her seferinde güncel gelmesini sağlar
    df = conn.read(ttl=0)
    
    # Eğer tablo boşsa veya kolonlar yoksa başlıkları oluştur
    if df.empty:
        df = pd.DataFrame(columns=["İş No", "Müşteri", "İş Başlığı", "Süreç", "Sorumlu", "Başlangıç", "Bitiş"])

    # --- SIDEBAR: YENİ İŞ GİRİŞİ ---
    with st.sidebar:
        st.header("📌 Yeni İş Ekle")
        with st.form("yeni_is_formu", clear_on_submit=True):
            is_no = st.text_input("İş No")
            musteri = st.text_input("Müşteri")
            baslik = st.text_input("Yapılacak İş")
            
            # Personel listesi (Bunu manuel ekledik, ileride Sheets'ten de çekebiliriz)
            personel_listesi = ["Emre Balcıoğlu", "Ahmet", "Mehmet", "Dış Tedarik"]
            sorumlu = st.selectbox("Sorumlu Personel", personel_listesi)
            
            surec_listesi = ["Beklemede", "Tasarım", "Kesim/Büküm", "Kaynak", "Boya", "Montaj", "Tamamlandı"]
            surec = st.selectbox("Mevcut Süreç", surec_listesi)
            
            tarih = st.date_input("Başlangıç Tarihi")
            
            submit = st.form_submit_button("Sisteme Kaydet")

            if submit:
                if is_no and musteri:
                    yeni_veri = pd.DataFrame([{
                        "İş No": is_no,
                        "Müşteri": musteri,
                        "İş Başlığı": baslik,
                        "Süreç": surec,
                        "Sorumlu": sorumlu,
                        "Başlangıç": tarih.strftime("%d.%m.%Y"),
                        "Bitiş": "-"
                    }])
                    
                    # Veriyi mevcut tabloya ekle ve Google Sheets'i güncelle
                    updated_df = pd.concat([df, yeni_veri], ignore_index=True)
                    conn.update(data=updated_df)
                    st.toast("İş başarıyla kaydedildi!", icon="✅")
                    st.rerun()
                else:
                    st.error("Lütfen İş No ve Müşteri alanlarını doldurun.")

    # --- ANA PANEL: ÖZET VE TABLO ---
    # Üst Bilgi Kartları
    toplam_is = len(df)
    devam_eden = len(df[df["Süreç"] != "Tamamlandı"])
    tamamlanan = len(df[df["Süreç"] == "Tamamlandı"])
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam İş", toplam_is)
    c2.metric("Devam Eden", devam_eden)
    c3.metric("Tamamlanan", tamamlanan)

    st.divider()

    # Filtreleme Seçenekleri
    st.subheader("📋 Üretim Çizelgesi")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        f_personel = st.multiselect("Personele Göre Filtrele", options=df["Sorumlu"].unique())
    with col_f2:
        f_surec = st.multiselect("Sürece Göre Filtrele", options=df["Süreç"].unique())

    # Filtreleri Uygula
    filtered_df = df.copy()
    if f_personel:
        filtered_df = filtered_df[filtered_df["Sorumlu"].isin(f_personel)]
    if f_surec:
        filtered_df = filtered_df[filtered_df["Süreç"].isin(f_surec)]

    # Tabloyu Göster
    st.dataframe(
        filtered_df, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Süreç": st.column_config.SelectboxColumn(
                "Süreç",
                options=surec_listesi,
                required=True,
            )
        }
    )

except Exception as e:
    st.error(f"Bağlantı hatası: {e}")
    st.info("Eğer 'Bağlantı başarılı' yazısını gördüysen ama bu hatayı alıyorsan, Google Sheets'teki sütun isimlerini kontrol et.")
