import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Üretim Planlama Pro v2026", layout="wide")
st.title("🏗️ Üretim Planlama ve Görsel Çizelgeleme")

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

renkler = {
    "KÖPRÜ": "#3498db", "BAŞLIK": "#e67e22", "KALDIRMA MAKİNASI": "#2ecc71", "ELEKTRİK": "#f1c40f", "FONKSİYON TESTİ": "#9b59b6"
}

# --- HAFIZA YÖNETİMİ ---
if 'personel_listesi' not in st.session_state:
    st.session_state.personel_listesi = []
if 'planlanan_isler' not in st.session_state:
    st.session_state.planlanan_isler = []

# --- YARDIMCI FONKSİYONLAR ---
def cakisma_var_mi(yeni_is):
    for eski_is in st.session_state.planlanan_isler:
        if yeni_is['Personel'] == eski_is['Personel']:
            # Tarih aralığı kontrolü
            if not (yeni_is['Bitiş'] < eski_is['Başlangıç'] or yeni_is['Başlangıç'] > eski_is['Bitiş']):
                return eski_is
    return None

# --- SOL PANEL: GİRİŞ ---
with st.sidebar:
    st.header("📋 İş ve Üretim Detayları")
    with st.expander("1. İş Emri Bilgileri", expanded=True):
        is_no = st.text_input("İş Emri No")
        musteri = st.text_input("Müşteri Adı")
        tonaj = st.text_input("Tonaj (Ton)")
        teslim_tarihi = st.date_input("Teslim Tarihi", value=datetime(2026, 12, 31))
        miktar = st.text_input("Miktar (Adet)")

    with st.expander("2. Üretim ve Personel", expanded=True):
        vinc = st.selectbox("Vinç Türü", ["", "ÇİFT KİRİŞ VİNÇ", "MONORAY KİRİŞ VİNÇ", "PORTAL VİNÇ", "PERGEL VİNÇ", "KALDIRMA MAKİNESİ", "ÇELİK KONSTRÜKSİYON SİSTEM"])
        sistem = st.selectbox("Sistem Türü", ["", "NORMAL SİSTEM", "EX-PROOF SİSTEM"])
        baslik = st.selectbox("Üretim Başlığı", [""] + list(uretim_yapisi.keys()))
        surec = st.selectbox("Üretim Süreci", [""] + uretim_yapisi.get(baslik, []))
        
        personel_adlari = [p['ad'] for p in st.session_state.personel_listesi]
        secilen_personel = st.selectbox("Görevli Personel", ["Seçiniz"] + personel_adlari)
        baslangic = st.date_input("Başlangıç Tarihi", value=datetime(2026, 5, 12))
        sure = st.number_input("Süre (Gün)", min_value=1, value=1)

    if st.button("🚀 Çizelgeye Ekle"):
        if is_no and secilen_personel != "Seçiniz" and baslik:
            bitis = baslangic + timedelta(days=sure-1)
            yeni_is = {
                "İş No": is_no, "Müşteri": musteri, "Tonaj": tonaj, "Miktar": miktar,
                "Başlık": baslik, "Süreç": surec, "Personel": secilen_personel,
                "Başlangıç": pd.to_datetime(baslangic), "Bitiş": pd.to_datetime(bitis),
                "Renk": renkler.get(baslik, "#cccccc"), "Vinç": vinc, "Sistem": sistem
            }
            
            # Çakışma kontrolü
            cakisma = cakisma_var_mi(yeni_is)
            if cakisma:
                st.error(f"⚠️ ÇAKIŞMA: {secilen_personel} zaten '{cakisma['İş No']}' işinde bu tarihlerde görevli!")
            else:
                st.session_state.planlanan_isler.append(yeni_is)
                st.success("İş başarıyla eklendi!")
        else:
            st.warning("Lütfen zorunlu alanları (İş No, Başlık, Personel) doldurun.")

# --- ANA EKRAN ---
tab1, tab2, tab3 = st.tabs(["📊 Görsel Çizelge (Gantt)", "📑 İş Listesi", "👤 Personel Yönetimi"])

with tab1:
    st.subheader("📅 2026 Üretim Akış Şeması")
    if st.session_state.planlanan_isler:
        df_gantt = pd.DataFrame(st.session_state.planlanan_isler)
        fig = px.timeline(df_gantt, x_start="Başlangıç", x_end="Bitiş", y="Personel", 
                          color="Başlık", hover_data=["İş No", "Müşteri", "Süreç"],
                          color_discrete_map=renkler,
                          title="Personel Bazlı İş Dağılımı")
        fig.update_yaxes(autorange="reversed") 
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Çizelgeyi görmek için sol panelden iş ekleyin.")

with tab2:
    st.subheader("📋 Kayıtlı İşlerin Detaylı Listesi")
    if st.session_state.planlanan_isler:
        for idx, row in enumerate(st.session_state.planlanan_isler):
            with st.expander(f"İş No: {row['İş No']} - {row['Müşteri']} ({row['Süreç']})"):
                c1, c2, c3 = st.columns(3)
                c1.write(f"**Tonaj:** {row['Tonaj']} | **Miktar:** {row['Miktar']}")
                c2.write(f"**Vinç:** {row['Vinç']} | **Sistem:** {row['Sistem']}")
                c3.write(f"**Tarih:** {row['Başlangıç'].date()} / {row['Bitiş'].date()}")
                if st.button("Bu İşi Sil", key=f"del_is_{idx}"):
                    st.session_state.planlanan_isler.pop(idx)
                    st.rerun()
    else:
        st.write("Kayıtlı iş bulunmuyor.")

with tab3:
    # Personel ekleme/silme bölümü (Aynı mantık, geliştirilmiş görsel)
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        st.write("### Yeni Personel")
        p_ad = st.text_input("Ad Soyad")
        p_alan = st.selectbox("Alan", [""] + list(personel_alan_yapisi.keys()))
        p_gorev = st.selectbox("Görev", [""] + personel_alan_yapisi.get(p_alan, []))
        if st.button("Personeli Sisteme Ekle"):
            if p_ad and p_gorev:
                st.session_state.personel_listesi.append({"ad": p_ad, "alan": p_alan, "gorev": p_gorev})
                st.rerun()
    with p_col2:
        st.write("### Mevcut Personel")
        for i, p in enumerate(st.session_state.personel_listesi):
            st.text(f"👤 {p['ad']} - {p['gorev']}")
            if st.button("Sil", key=f"del_per_{i}"):
                st.session_state.personel_listesi.pop(i)
                st.rerun()

# --- PDF HAZIRLIK ---
st.divider()
st.button("📄 Tüm Çizelgeyi PDF Raporu Yap")
