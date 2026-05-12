import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta

# Sayfa Ayarları
st.set_page_config(page_title="Üretim Planlama v1.0", layout="wide")

# --- VERİ YAPILARI (Senin İstediğin Filtreler) ---
VINC_TIPLERI = ["ÇİFT KİRİŞ VİNÇ", "MONORAY KİRİŞ VİNÇ", "PORTAL VİNÇ", "PERGEL VİNÇ", "KALDIRMA MAKİNESİ", "ÇELİK KONSTRÜKSİYON SİSTEM"]
SISTEM_TIPLERI = ["NORMAL SİSTEM", "EX-PROOF SİSTEM"]

URETIM_BASLIKLARI = {
    "KÖPRÜ": ["KESİM", "KİRİŞ ÇATIM", "KAYNAK (TOZ&ALIN)", "KEP ÇATIM", "KAYNAK (DİĞER)", "YÜZEY"],
    "BAŞLIK": ["KESİM (TESTERE)", "KESİM (PLAZMA)", "İŞLEME", "KAYNAK", "MONTAJ", "YÜZEY"],
    "KALDIRMA MAKİNASI": ["KESİM (TESTERE)", "KESİM (PLAZMA)", "ÇATIM", "KAYNAK", "İŞLEME", "YÜK TESTİ", "YÜZEY", "MONTAJ"],
    "ELEKTRİK": ["HAZIRLIK", "İŞLEME"],
    "FONKSİYON TESTİ": ["HAZIRLIK VE FİNAL TEST"]
}

PERSONEL_ALANLARI = {
    "TALAŞLI İMALAT": ["FORMEN", "CNC TORNA OPERATÖRÜ", "DİK İŞLEM OPERATÖRÜ", "FREZE OPERATÖRÜ", "ÜNİVERSAL TORNA OPERATÖRÜ", "MAKİNE MONTAJ OPERATÖRÜ", "MAKİNE İMALAT OPERATÖRÜ", "YARDIMCI ELEMAN"],
    "KAYNAKLI İMALAT": ["FORMEN", "KAYNAKÇI", "TAŞLAMACI", "YARDIMCI ELEMAN"],
    "BOYAHANE": ["FORMEN", "BOYA OPERATÖRÜ", "YARDIMCI ELEMAN"],
    "ELEKTRİKHANE": ["FORMEN", "ELEKTRİK USTASI", "YARDIMCI ELEMAN"],
    "KESİM": ["FORMEN", "PLAZMA OPERATÖRÜ", "TESTERE OPERATÖRÜ", "YARDIMCI ELEMAN"],
    "KALİTE": ["KALİTE OPERATÖRÜ"]
}

# Örnek Personel Listesi (Düzenlenebilir)
if 'personeller' not in st.session_state:
    st.session_state.personeller = pd.DataFrame([
        {"İsim": "Emre Balcıoğlu", "Alan": "KAYNAKLI İMALAT", "Alt Başlık": "FORMEN"},
        {"İsim": "Ahmet Yılmaz", "Alan": "TALAŞLI İMALAT", "Alt Başlık": "CNC TORNA OPERATÖRÜ"},
        {"İsim": "Mehmet Demir", "Alan": "KESİM", "Alt Başlık": "PLAZMA OPERATÖRÜ"}
    ])

# --- BAĞLANTI ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0)
    
    st.title("🏭 Üretim Planlama ve İş Emri Yönetimi")

    tab1, tab2, tab3 = st.tabs(["📝 İş Emri Kaydı", "👥 Personel Yönetimi", "📅 Üretim Takvimi"])

    # --- TAB 1: İŞ EMRİ KAYDI ---
    with tab1:
        st.subheader("Üretim Bilgilerini Girin")
        with st.form("ana_form", clear_on_submit=True):
            c1, c2, c3, c4, c5 = st.columns(5)
            ie_no = c1.text_input("İş Emri No")
            musteri = c2.text_input("Müşteri Adı")
            tonaj = c3.text_input("Tonaj")
            teslim = c4.date_input("Teslim Tarihi")
            miktar = c5.number_input("Miktar", min_value=1)

            st.divider()
            
            # Seçim Sütunları
            col_vinc, col_sistem = st.columns(2)
            secilen_vinc = col_vinc.selectbox("Vinç Seçeneği", ["Seçiniz"] + VINC_TIPLERI)
            secilen_sistem = col_sistem.selectbox("Sistem Türü", ["Seçiniz"] + SISTEM_TIPLERI)

            st.divider()
            
            # Üretim ve Personel Atama (Filtreli)
            col_u1, col_u2, col_u3, col_u4 = st.columns(4)
            u_baslik = col_u1.selectbox("Üretim Başlığı", ["Seçiniz"] + list(URETIM_BASLIKLARI.keys()))
            
            u_surec = "Seçiniz"
            if u_baslik != "Seçiniz":
                u_surec = col_u2.selectbox("Üretim Süreci", URETIM_BASLIKLARI[u_baslik])
            
            p_alan = col_u3.selectbox("Personel Alanı", list(PERSONEL_ALANLARI.keys()))
            ilgili_personeller = st.session_state.personeller[st.session_state.personeller["Alan"] == p_alan]["İsim"].tolist()
            secilen_personel = col_u4.selectbox("Personel Atama", ilgili_personeller if ilgili_personeller else ["Kayıtlı Personel Yok"])

            # Takvim için Süre
            gun_sayisi = st.number_input("Bu İş Kaç Gün Sürecek?", min_value=1, value=1)
            baslangic_tarihi = st.date_input("İş Başlangıç Tarihi")

            submit = st.form_submit_button("Sisteme Kaydet ve Takvime İşle")

            if submit:
                yeni_is = pd.DataFrame([{
                    "İş Emri": ie_no, "Müşteri": musteri, "Tonaj": tonaj, "Teslim": teslim.strftime("%d/%m/%Y"),
                    "Vinç": secilen_vinc, "Sistem": secilen_sistem, "Üretim": u_baslik, "Süreç": u_surec,
                    "Personel": secilen_personel, "Başlangıç": baslangic_tarihi, 
                    "Bitiş": baslangic_tarihi + timedelta(days=gun_sayisi)
                }])
                guncel_df = pd.concat([df, yeni_is], ignore_index=True)
                conn.update(data=guncel_df)
                st.success("İş Emri Kaydedildi!")
                st.rerun()

    # --- TAB 2: PERSONEL YÖNETİMİ ---
    with tab2:
        st.subheader("Personel Ekle / Sil")
        p_c1, p_c2, p_c3 = st.columns(3)
        p_isim = p_c1.text_input("Personel İsim Soyisim")
        p_alan_yeni = p_c2.selectbox("Çalışma Alanı", list(PERSONEL_ALANLARI.keys()), key="p_alan_yeni")
        p_alt_yeni = p_c3.selectbox("Alt Başlık/Görev", PERSONEL_ALANLARI[p_alan_yeni])
        
        if st.button("Personeli Kaydet"):
            yeni_p = {"İsim": p_isim, "Alan": p_alan_yeni, "Alt Başlık": p_alt_yeni}
            st.session_state.personeller = pd.concat([st.session_state.personeller, pd.DataFrame([yeni_p])], ignore_index=True)
            st.success("Personel eklendi.")
            st.rerun()
        
        st.write("### Kayıtlı Personel Listesi")
        st.dataframe(st.session_state.personeller, use_container_width=True)

    # --- TAB 3: TAKVİM VE ÇIKTI ---
    with tab3:
        st.subheader("🗓️ Üretim Programı Takvimi")
        if not df.empty:
            # Basit bir takvim listelemesi (Gantt Chart mantığı)
            st.write("Hangi iş ne zaman başlıyor?")
            df['Başlangıç'] = pd.to_datetime(df['Başlangıç'])
            df['Bitiş'] = pd.to_datetime(df['Bitiş'])
            
            # Tabloyu çıktı alınabilir formatta göster
            st.table(df[["İş Emri", "Müşteri", "Üretim", "Süreç", "Personel", "Başlangıç", "Bitiş"]])
            
            # CSV Çıktısı Alma
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📊 Listeyi Excel/CSV Olarak İndir", csv, "uretim_programi.csv", "text/csv")
        else:
            st.info("Takvimde gösterilecek veri bulunamadı.")

except Exception as e:
    st.error(f"Bağlantı Hatası: {e}")
