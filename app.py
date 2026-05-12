import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Üretim Planlama v2026", layout="wide")
st.title("🏗️ Üretim Planlama Sistemi")

# --- VERİ YAPILARI (Senin Belirlediğin Mantık) ---
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

renkler = {
    "KÖPRÜ": "#3498db", "BAŞLIK": "#e67e22", "KALDIRMA MAKİNASI": "#2ecc71", "ELEKTRİK": "#f1c40f", "FONKSİYON TESTİ": "#9b59b6"
}

# --- HAFIZA YÖNETİMİ ---
if 'personel_listesi' not in st.session_state:
    st.session_state.personel_listesi = []

if 'planlanan_isler' not in st.session_state:
    st.session_state.planlanan_isler = []

# --- SOL PANEL: GİRİŞ VE SEÇİMLER ---
with st.sidebar:
    st.header("📋 İş Emri Girişi")
    is_no = st.text_input("İş Emri No")
    musteri = st.text_input("Müşteri Adı")
    tonaj = st.text_input("Tonaj Bilgisi")
    teslim_tarihi = st.date_input("Teslim Tarihi", value=datetime(2026, 5, 12))
    miktar = st.text_input("Miktar")
    
    st.divider()
    
    vinc = st.selectbox("Vinç Seçenek Türü", ["", "ÇİFT KİRİŞ VİNÇ", "MONORAY KİRİŞ VİNÇ", "PORTAL VİNÇ", "PERGEL VİNÇ", "KALDIRMA MAKİNESİ", "ÇELİK KONSTRÜKSİYON SİSTEM"])
    sistem = st.selectbox("Sistem Türü", ["", "NORMAL SİSTEM", "EX-PROOF SİSTEM"])
    
    baslik = st.selectbox("Üretim Başlığı", [""] + list(uretim_yapisi.keys()))
    surec_opsiyonlari = uretim_yapisi.get(baslik, [])
    surec = st.selectbox("Üretim Süreci", [""] + surec_opsiyonlari)
    
    # Personel Atama (Eklenen personeller arasından)
    personel_adlari = [p['ad'] for p in st.session_state.personel_listesi]
    secilen_personel = st.selectbox("Görevli Personel", ["Seçiniz"] + personel_adlari)
    
    baslangic = st.date_input("İş Başlangıç Tarihi", value=datetime(2026, 5, 12))
    sure = st.number_input("Süre (Gün)", min_value=1, value=1)
    
    if st.button("İşi Takvime Kaydet"):
        if is_no and secilen_personel != "Seçiniz":
            yeni_is = {
                "id": len(st.session_state.planlanan_isler),
                "İş Emri": is_no, "Müşteri": musteri, "Başlık": baslik, 
                "Süreç": surec, "Personel": secilen_personel,
                "Başlangıç": baslangic, "Bitiş": baslangic + timedelta(days=sure-1),
                "Renk": renkler.get(baslik, "#cccccc")
            }
            st.session_state.planlanan_isler.append(yeni_is)
            st.success("İş kaydedildi!")
        else:
            st.error("Lütfen İş No ve Personel seçiniz!")

# --- ANA EKRAN ---
tab1, tab2 = st.tabs(["📅 Üretim Çizelgesi", "👤 Personel İşlemleri"])

with tab1:
    st.subheader("2026 Üretim Planı")
    if st.session_state.planlanan_isler:
        df_is = pd.DataFrame(st.session_state.planlanan_isler)
        # Tablo Görünümü
        for index, row in df_is.iterrows():
            col_is, col_sil = st.columns([10, 1])
            col_is.info(f"**{row['İş Emri']}** - {row['Müşteri']} | {row['Başlık']} > {row['Süreç']} | Personel: {row['Personel']} | Tarih: {row['Başlangıç']} / {row['Bitiş']}")
            if col_sil.button("Sil", key=f"is_sil_{index}"):
                st.session_state.planlanan_isler.pop(index)
                st.rerun()
    else:
        st.write("Henüz planlanmış bir iş yok.")

with tab2:
    st.subheader("Personel Yönetimi")
    p_col1, p_col2 = st.columns(2)
    
    with p_col1:
        p_ad = st.text_input("Personel Adı Soyadı")
        p_alan = st.selectbox("Çalışma Alanı", [""] + list(personel_alan_yapisi.keys()))
        
        # Otomatik Filtreleme: Alan seçince Görevler çıkar
        p_gorev_opsiyonlari = personel_alan_yapisi.get(p_alan, [])
        p_gorev = st.selectbox("Görevi", [""] + p_gorev_opsiyonlari)
        
        if st.button("Personel Ekle"):
            if p_ad and p_alan and p_gorev:
                st.session_state.personel_listesi.append({"ad": p_ad, "alan": p_alan, "gorev": p_gorev})
                st.success(f"{p_ad} eklendi.")
                st.rerun()
            else:
                st.warning("Lütfen tüm alanları doldurun.")

    with p_col2:
        st.write("Mevcut Personel Listesi")
        if st.session_state.personel_listesi:
            for idx, p in enumerate(st.session_state.personel_listesi):
                c1, c2 = st.columns([4, 1])
                c1.text(f"{p['ad']} - {p['alan']} ({p['gorev']})")
                if c2.button("Sil", key=f"per_sil_{idx}"):
                    st.session_state.personel_listesi.pop(idx)
                    st.rerun()
        else:
            st.write("Liste boş.")

# --- ÇIKTI ---
st.divider()
if st.button("PDF Çıktısı Al (Hazırla)"):
    st.write("PDF dosyası üretim verilerine göre oluşturuluyor...")
