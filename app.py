import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Üretim Bulut v2026", layout="wide")
st.title("☁️ Bulut Tabanlı Üretim Planlama (Paylaşımlı)")

# --- GOOGLE SHEETS BAĞLANTISI ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Verileri Çekme Fonksiyonu
def verileri_yukle():
    try:
        isler_df = conn.read(worksheet="Isler")
        personel_df = conn.read(worksheet="Personeller")
        return isler_df, personel_df
    except:
        return pd.DataFrame(), pd.DataFrame()

df_isler, df_personel = verileri_yukle()

# --- VERİ YAPILARI ---
uretim_yapisi = {
    "KÖPRÜ": ["KESİM", "KİRİŞ ÇATIM", "KAYNAK (TOZ&ALIN)", "KEP ÇATIM", "KAYNAK (DİĞER)", "YÜZEY"],
    "BAŞLIK": ["KESİM (TESTERE)", "KESİM (PLAZMA)", "İŞLEME", "KAYNAK", "MONTAJ", "YÜZEY"],
    "KALDIRMA MAKİNASI": ["KESİM (TESTERE)", "KESİM (PLAZMA)", "ÇATIM", "KAYNAK", "İŞLEME", "YÜK TESTİ", "YÜZEY", "MONTAJ"],
    "ELEKTRİK": ["HAZIRLIK", "İŞLEME"],
    "FONKSİYON TESTİ": ["HAZIRLIK VE FİNAL TEST"]
}

personel_alan_yapisi = {
    "TALAŞLI İMALAT": ["FORMEN", "CNC TORNA OPERATÖRÜ", "DİK İŞLEM OPERATÖRÜ", "FREZE OPERATÖRÜ", "ÜNİVERSAL TORNA OPERATÖRÜ", "MAKİNE MONTAJ OPERATÖRÜ", "MAKİNE İMALAT OPERATÖRÜ", "YARDIMCI ELEMAN"],
    "KAYNAKLI İMALAT": ["FORMEN", "KAYNAKÇI", "TAŞLAMACI", "YARDIMCI ELEMAN"],
    "BOYAHANE": ["FORMEN", "BOYA OPERATÖRÜ", "YARDIMCI ELEMAN"],
    "ELEKTRİKHANE": ["FORMEN", "ELEKTRİK USTASI", "YARDIMCI ELEMAN"],
    "KESİM": ["FORMEN", "PLAZMA OPERATÖRÜ", "TESTERE OPERATÖRÜ", "YARDIMCI ELEMAN"],
    "KALİTE": ["KALİTE OPERATÖRÜ"]
}

# --- SOL PANEL ---
with st.sidebar:
    st.header("📋 Yeni İş Emri")
    is_no = st.text_input("İş Emri No")
    musteri = st.text_input("Müşteri Adı")
    baslik = st.selectbox("Üretim Başlığı", [""] + list(uretim_yapisi.keys()))
    surec = st.selectbox("Üretim Süreci", uretim_yapisi.get(baslik, []))
    
    personel_listesi = df_personel["Ad Soyad"].tolist() if not df_personel.empty else []
    secilen_personel = st.selectbox("Görevli Personel", ["Seçiniz"] + personel_listesi)
    
    baslangic = st.date_input("Başlangıç", value=datetime.now())
    sure = st.number_input("Süre (Gün)", min_value=1, value=1)

    if st.button("Buluta Kaydet"):
        yeni_veri = pd.DataFrame([{
            "İş No": is_no, "Müşteri": musteri, "Başlık": baslik, 
            "Süreç": surec, "Personel": secilen_personel,
            "Başlangıç": baslangic.strftime('%Y-%m-%d'),
            "Bitiş": (baslangic + timedelta(days=sure-1)).strftime('%Y-%m-%d')
        }])
        guncel_isler = pd.concat([df_isler, yeni_veri], ignore_index=True)
        conn.update(worksheet="Isler", data=guncel_isler)
        st.success("Veri Google Sheets'e gönderildi!")
        st.rerun()

# --- ANA EKRAN ---
tab1, tab2 = st.tabs(["📊 Üretim Takvimi", "👤 Personel Ekle"])

with tab1:
    if not df_isler.empty:
        df_isler["Başlangıç"] = pd.to_datetime(df_isler["Başlangıç"])
        df_isler["Bitiş"] = pd.to_datetime(df_isler["Bitiş"])
        fig = px.timeline(df_isler, x_start="Başlangıç", x_end="Bitiş", y="Personel", color="Başlık")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df_isler) # Liste hali
    else:
        st.info("Henüz kayıtlı iş yok.")

with tab2:
    st.subheader("Yeni Personel Tanımla")
    p_ad = st.text_input("Personel Ad Soyad")
    p_alan = st.selectbox("Çalışma Alanı", list(personel_alan_yapisi.keys()))
    if st.button("Personeli Kaydet"):
        yeni_p = pd.DataFrame([{"Ad Soyad": p_ad, "Alan": p_alan}])
        guncel_p = pd.concat([df_personel, yeni_p], ignore_index=True)
        conn.update(worksheet="Personeller", data=guncel_p)
        st.success("Personel listesi güncellendi!")
        st.rerun()
