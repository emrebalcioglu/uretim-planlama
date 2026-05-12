import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Sayfa Ayarları
st.set_page_config(page_title="Üretim Planlama", layout="wide")

st.title("🏭 Akıllı Üretim Planlama Sistemi")

# --- BAĞLANTI (Çalışan yöntem) ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Veriyi oku (Cache'i temizlemesi için ttl=0 ekledik, anlık güncellenir)
    df = conn.read(ttl=0)
    
    st.success("✅ Google Sheets Bağlantısı Aktif")

    # --- SOL PANEL: YENİ İŞ EKLEME ---
    with st.sidebar:
        st.header("📌 Yeni İş Kaydı")
        with st.form("kayit_formu", clear_on_submit=True):
            is_no = st.text_input("İş No (Örn: 2024-001)")
            musteri = st.text_input("Müşteri Adı")
            baslik = st.text_input("İşin Başlığı")
            surec = st.selectbox("Süreç", ["Beklemede", "Tasarım", "Üretim", "Montaj", "Tamamlandı"])
            personel = st.text_input("Sorumlu Personel")
            
            submit = st.form_submit_button("Sisteme Kaydet")

            if submit:
                if is_no and musteri:
                    # Yeni veriyi hazırla
                    yeni_satir = pd.DataFrame([{
                        "İş No": is_no,
                        "Müşteri": musteri,
                        "Başlık": baslik,
                        "Süreç": surec,
                        "Personel": personel,
                        "Başlangıç": pd.Timestamp.now().strftime("%d/%m/%Y"),
                        "Bitiş": "-"
                    }])
                    
                    # Mevcut veriye ekle ve güncelle
                    guncel_df = pd.concat([df, yeni_satir], ignore_index=True)
                    conn.update(data=guncel_df)
                    st.toast("İş başarıyla eklendi!")
                    st.rerun()
                else:
                    st.error("Lütfen İş No ve Müşteri alanlarını doldurun.")

    # --- ANA EKRAN: TABLO VE FİLTRELEME ---
    if not df.empty:
        st.subheader("📋 Güncel İş Planı")
        
        # Basit bir arama kutusu
        arama = st.text_input("Tabloda ara (Müşteri veya İş No)...")
        if arama:
            df = df[df.apply(lambda row: arama.lower() in row.astype(str).str.lower().values, axis=1)]
            
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Henüz eklenmiş bir iş yok. Sol panelden ilk işi ekleyerek başlayabilirsiniz.")

except Exception as e:
    st.error(f"Bağlantı sırasında bir hata oluştu: {e}")
    st.info("İpucu: Sayfayı yenilemeyi veya Secrets ayarlarını kontrol etmeyi deneyin.")
