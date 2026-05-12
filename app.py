import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Üretim Planlama v2026", layout="wide")
st.title("🏗️ Üretim Planlama ve Personel Atama Sistemi (2026)")

# --- VERİ YAPILARI (Senin Belirlediğin Mantık) ---
uretim_yapisi = {
    "KÖPRÜ": ["KESİM", "KİRİŞ ÇATIM", "KAYNAK (TOZ&ALIN)", "KEP ÇATIM", "KAYNAK (DİĞER)", "YÜZEY"],
    "BAŞLIK": ["KESİM (TESTERE)", "KESİM (PLAZMA)", "İŞLEME", "KAYNAK", "MONTAJ", "YÜZEY"],
    "KALDIRMA MAKİNASI": ["KESİM (TESTERE)", "KESİM (PLAZMA)", "ÇATIM", "KAYNAK", "İŞLEME", "YÜK TESTİ", "YÜZEY", "MONTAJ"],
    "ELEKTRİK": ["HAZIRLIK", "İŞLEME"],
    "FONKSİYON TESTİ": ["HAZIRLIK VE FİNAL TEST"]
}

renkler = {
    "KÖPRÜ": "#3498db", # Mavi
    "BAŞLIK": "#e67e22", # Turuncu
    "KALDIRMA MAKİNASI": "#2ecc71", # Yeşil
    "ELEKTRİK": "#f1c40f", # Sarı
    "FONKSİYON TESTİ": "#9b59b6" # Mor
}

# Personel Listesi (Her bölüme 3 kişi)
if 'personel_listesi' not in st.session_state:
    st.session_state.personel_listesi = [
        {"ad": "Ahmet Y.", "alan": "TALAŞLI İMALAT", "gorev": "CNC TORNA OPERATÖRÜ"},
        {"ad": "Mehmet A.", "alan": "TALAŞLI İMALAT", "gorev": "DİK İŞLEM OPERATÖRÜ"},
        {"ad": "Caner T.", "alan": "TALAŞLI İMALAT", "gorev": "MAKİNE MONTAJ OPERATÖRÜ"},
        {"ad": "Hüseyin K.", "alan": "KAYNAKLI İMALAT", "gorev": "KAYNAKÇI"},
        {"ad": "Murat G.", "alan": "KAYNAKLI İMALAT", "gorev": "TAŞLAMACI"},
        {"ad": "Salih B.", "alan": "KAYNAKLI İMALAT", "gorev": "FORMEN"},
        {"ad": "Mustafa Ö.", "alan": "ELEKTRİKHANE", "gorev": "ELEKTRİK USTASI"},
        {"ad": "Selim Y.", "alan": "ELEKTRİKHANE", "gorev": "YARDIMCI ELEMAN"},
        {"ad": "Onur A.", "alan": "ELEKTRİKHANE", "gorev": "FORMEN"},
        {"ad": "Sinan G.", "alan": "KALİTE", "gorev": "KALİTE OPERATÖRÜ"}
    ]

if 'planlanan_isler' not in st.session_state:
    st.session_state.planlanan_isler = []

# --- SOL PANEL: GİRİŞ VE SEÇİMLER ---
with st.sidebar:
    st.header("📋 İş Emri Girişi")
    is_no = st.text_input("İş Emri No")
    musteri = st.text_input("Müşteri Adı")
    tonaj = st.text_input("Tonaj Bilgisi")
    teslim_tarihi = st.date_input("Teslim Tarihi", value=datetime(2026, 1, 1))
    
    st.divider()
    
    vinc = st.selectbox("Vinç Seçenek Türü", ["", "ÇİFT KİRİŞ VİNÇ", "MONORAY KİRİŞ VİNÇ", "PORTAL VİNÇ", "PERGEL VİNÇ", "KALDIRMA MAKİNESİ", "ÇELİK KONSTRÜKSİYON"])
    sistem = st.selectbox("Sistem Türü", ["NORMAL SİSTEM", "EX-PROOF SİSTEM"])
    
    baslik = st.selectbox("Üretim Başlığı", [""] + list(uretim_yapisi.keys()))
    
    surec_opsiyonlari = uretim_yapisi.get(baslik, [])
    surec = st.selectbox("Üretim Süreci", [""] + surec_opsiyonlari)
    
    # Personel Atama (Tüm personeller arasından seçim yapılabilsin istedin)
    personel_adlari = [p['ad'] for p in st.session_state.personel_listesi]
    secilen_personel = st.selectbox("Görevli Personel Atama", personel_adlari)
    
    baslangic = st.date_input("İş Başlangıç", value=datetime(2026, 5, 1))
    sure = st.number_input("Süre (Gün)", min_value=1, value=1)
    
    if st.button("İşi Takvime Ekle"):
        yeni_is = {
            "is_no": is_no, "musteri": musteri, "baslik": baslik, 
            "surec": surec, "personel": secilen_personel,
            "baslangic": baslangic, "bitis": baslangic + timedelta(days=sure-1),
            "renk": renkler.get(baslik, "#cccccc")
        }
        st.session_state.planlanan_isler.append(yeni_is)
        st.success("İş başarıyla eklendi!")

# --- ANA EKRAN: TAKVİM GÖRÜNÜMÜ ---
col1, col2 = st.columns([4, 1])

with col1:
    st.subheader("📅 2026 Üretim Çizelgesi")
    # Basit bir Gantt/Takvim Görünümü (Dataframe kullanarak)
    if st.session_state.planlanan_isler:
        df = pd.DataFrame(st.session_state.planlanan_isler)
        st.dataframe(df[["is_no", "musteri", "baslik", "surec", "personel", "baslangic", "bitis"]])
    else:
        st.info("Henüz eklenmiş bir iş emri yok.")

with col2:
    st.subheader("🖨️ İşlemler")
    if st.button("PDF Çıktısı Al"):
        st.write("PDF hazırlanıyor... (Bu aşamada tabloyu PDF olarak indirir)")
        # Gerçek uygulamada burada fpdf kütüphanesi çalışır.

# --- PERSONEL YÖNETİMİ ---
with st.expander("👤 Personel Ekle/Sil/Düzenle"):
    p_ad = st.text_input("Personel Adı Soyadı")
    p_alan = st.selectbox("Çalışma Alanı", ["TALAŞLI İMALAT", "KAYNAKLI İMALAT", "ELEKTRİKHANE", "BOYAHANE", "KESİM", "KALİTE"])
    if st.button("Personeli Kaydet"):
        st.session_state.personel_listesi.append({"ad": p_ad, "alan": p_alan, "gorev": ""})
        st.rerun()

    st.write("Mevcut Personel Listesi:")
    st.table(pd.DataFrame(st.session_state.personel_listesi))
