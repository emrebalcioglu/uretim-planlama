import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import io

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Üretim Planlama Pro v2026", layout="wide")
st.title("🏗️ Üretim Planlama ve Akıllı Hafıza Sistemi")

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
            if not (yeni_is['Bitiş'] < eski_is['Başlangıç'] or yeni_is['Başlangıç'] > eski_is['Bitiş']):
                return eski_is
    return None

# --- VERİ YÜKLEME / KAYDETME FONKSİYONLARI ---
def veriyi_excele_donustur():
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        if st.session_state.planlanan_isler:
            pd.DataFrame(st.session_state.planlanan_isler).to_sheet(writer, sheet_name='Isler', index=False)
        if st.session_state.personel_listesi:
            pd.DataFrame(st.session_state.personel_listesi).to_sheet(writer, sheet_name='Personeller', index=False)
    return output.getvalue()

# --- SOL PANEL: GİRİŞ ---
with st.sidebar:
    st.header("💾 Veri Yönetimi (Hafıza)")
    
    # Dışa Aktar
    if st.session_state.planlanan_isler or st.session_state.personel_listesi:
        # Excel dosyasını basitçe oluşturma (Daha güvenli yöntem)
        df_isler = pd.DataFrame(st.session_state.planlanan_isler)
        df_personel = pd.DataFrame(st.session_state.personel_listesi)
        
        towrite = io.BytesIO()
        with pd.ExcelWriter(towrite, engine='xlsxwriter') as writer:
            df_isler.to_excel(writer, sheet_name='Isler', index=False)
            df_personel.to_excel(writer, sheet_name='Personeller', index=False)
        
        st.download_button(label="📥 Tüm Verileri Excel'e Yedekle", 
                          data=towrite.getvalue(),
                          file_name=f"uretim_plan_yedek_{datetime.now().strftime('%d_%m_%Y')}.xlsx",
                          mime="application/vnd.ms-excel")
    
    # İçe Aktar
    yuklenen_dosya = st.file_uploader("📂 Yedek Dosyayı Yükle", type=["xlsx"])
    if yuklenen_dosya:
        if st.button("✅ Verileri Geri Yükle"):
            try:
                st.session_state.planlanan_isler = pd.read_excel(yuklenen_dosya, sheet_name='Isler').to_dict('records')
                st.session_state.personel_listesi = pd.read_excel(yuklenen_dosya, sheet_name='Personeller').to_dict('records')
                # Tarih sütunlarını tekrar datetime nesnesine çevir
                for is_emri in st.session_state.planlanan_isler:
                    is_emri['Başlangıç'] = pd.to_datetime(is_emri['Başlangıç'])
                    is_emri['Bitiş'] = pd.to_datetime(is_emri['Bitiş'])
                st.success("Veriler başarıyla yüklendi!")
                st.rerun()
            except Exception as e:
                st.error("Dosya okunurken hata oluştu. Lütfen doğru yedeği seçin.")

    st.divider()
    st.header("📋 Yeni İş Girişi")
    with st.expander("İş ve Üretim Detayları", expanded=True):
        is_no = st.text_input("İş Emri No")
        musteri = st.text_input("Müşteri Adı")
        baslik = st.selectbox("Üretim Başlığı", [""] + list(uretim_yapisi.keys()))
        surec = st.selectbox("Üretim Süreci", [""] + uretim_yapisi.get(baslik, []))
        
        personel_adlari = [p['ad'] for p in st.session_state.personel_listesi]
        secilen_personel = st.selectbox("Görevli Personel", ["Seçiniz"] + personel_adlari)
        baslangic = st.date_input("Başlangıç", value=datetime(2026, 5, 12))
        sure = st.number_input("Süre (Gün)", min_value=1, value=1)

    if st.button("🚀 Çizelgeye Ekle"):
        if is_no and secilen_personel != "Seçiniz":
            bitis = baslangic + timedelta(days=sure-1)
            yeni_is = {
                "İş No": is_no, "Müşteri": musteri, "Başlık": baslik, 
                "Süreç": surec, "Personel": secilen_personel,
                "Başlangıç": pd.to_datetime(baslangic), "Bitiş": pd.to_datetime(bitis),
                "Renk": renkler.get(baslik, "#cccccc")
            }
            cakisma = cakisma_var_mi(yeni_is)
            if cakisma:
                st.error(f"⚠️ {secilen_personel} zaten dolu!")
            else:
                st.session_state.planlanan_isler.append(yeni_is)
                st.success("Eklendi!")
                st.rerun()

# --- ANA EKRAN ---
tab1, tab2, tab3 = st.tabs(["📊 Görsel Çizelge", "📑 İş Detayları", "👤 Personel"])

with tab1:
    if st.session_state.planlanan_isler:
        df_gantt = pd.DataFrame(st.session_state.planlanan_isler)
        fig = px.timeline(df_gantt, x_start="Başlangıç", x_end="Bitiş", y="Personel", 
                          color="Başlık", color_discrete_map=renkler,
                          title="2026 Üretim Takvimi")
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Hafızadan veri yükleyin veya yeni iş ekleyin.")

with tab2:
    if st.session_state.planlanan_isler:
        for idx, row in enumerate(st.session_state.planlanan_isler):
            c1, c2 = st.columns([9, 1])
            c1.write(f"**{row['İş No']}** - {row['Müşteri']} ({row['Süreç']})")
            if c2.button("Sil", key=f"del_{idx}"):
                st.session_state.planlanan_isler.pop(idx)
                st.rerun()

with tab3:
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        p_ad = st.text_input("Ad Soyad")
        p_alan = st.selectbox("Alan", list(personel_alan_yapisi.keys()))
        p_gorev = st.selectbox("Görev", personel_alan_yapisi[p_alan])
        if st.button("Personel Ekle"):
            st.session_state.personel_listesi.append({"ad": p_ad, "alan": p_alan, "gorev": p_gorev})
            st.rerun()
    with p_col2:
        for i, p in enumerate(st.session_state.personel_listesi):
            c1, c2 = st.columns([4,1])
            c1.text(f"{p['ad']} ({p['gorev']})")
            if c2.button("❌", key=f"pdel_{i}"):
                st.session_state.personel_listesi.pop(i)
                st.rerun()
