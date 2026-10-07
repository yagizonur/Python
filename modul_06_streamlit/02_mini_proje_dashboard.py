"""
=============================================================
  MODUL 5 - MINI PROJE: Satis Dashboard
=============================================================
  API'den veri cekip, Pandas ile isleyip, Streamlit'te gosteren
  tam bir dashboard uygulamasi.

  Calistirmak icin:
    streamlit run 02_mini_proje_dashboard.py
=============================================================

    Bu dosya Modul 6'in FINAL PROJESIDIR.
    Modul (API), Modul (Pandas), Modul  (Matplotlib/Plotly) ve
    Modul (Streamlit) konularini tek bir "Gercek Dunya" uygulamasinda birlestirir.

      1. @st.cache_data dekoratorunu: "Veriyi her saniye API'den
         cekersek hem API cokebilir hem uygulama yavaslar. Cache ile veriyi
         bellekte tutuyoruz." 
      3. Matplotlib yerine Plotly (st.plotly_chart) kullandik cunku Plotly
         grafiklerin uzerine gelince (hover) degerleri gosterir.

  ONKOSUL: API'den veri cekme (requests), Pandas DataFrame, Streamlit temelleri.
  HEDEF:  Farklı modulleri birlestirerek interaktif ve filtreli
         bir is zekasi (BI) paneli geliştirebiliriz.

         Çalıştırmak için terminalde:  py -m streamlit run 02_mini_proje_dashboard.py
=============================================================
"""

import streamlit as st
import pandas as pd
import requests
import sqlite3
from datetime import datetime


# =====================================================
# SAYFA YAPILANDIRMASI
# =====================================================

st.set_page_config(
    page_title="Satis Dashboard",
    page_icon="",
    layout="wide"
)


# =====================================================
# VERI SERVISLERI
# =====================================================

@st.cache_data(ttl=3600)  # st.cache_data: Veriyi her tiklamada internetten tekrar indirmek yerine, hafizada (onbellek) saklar. Uygulamayi inanilmaz hizlandirir!
def api_den_veri_cek() -> list[dict]:
    """
    JSONPlaceholder API'den ornek veri ceker.
    @st.cache_data sayesinde ayni veri tekrar cekilmez
    """
    yanit: requests.Response = requests.get(  # Internet adresinden (API'den) verileri getirmesi icin istek atariz.
        "https://jsonplaceholder.typicode.com/users",
        timeout=10
    )
    if yanit.ok:
        return yanit.json()
    return []


def ornek_satis_verisi_olustur() -> pd.DataFrame:
    """Dashboard icin ornek satis verisi olusturur."""
    import random
    random.seed(42)

    urunler: list[str] = ["Laptop", "Mouse", "Klavye", "Monitor", "Kulaklik", "SSD Disk"]
    kategoriler: dict[str, str] = {
        "Laptop": "Elektronik", "Mouse": "Aksesuar", "Klavye": "Aksesuar",
        "Monitor": "Elektronik", "Kulaklik": "Aksesuar", "SSD Disk": "Donanim"
    }
    fiyatlar: dict[str, int] = {
        "Laptop": 35000, "Mouse": 450, "Klavye": 850,
        "Monitor": 12000, "Kulaklik": 1200, "SSD Disk": 2500
    }
    sehirler: list[str] = ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya"]
    temsilciler: list[str] = ["Salman", "Arda", "Ayda", "Onur"]

    kayitlar: list[dict] = []
    for ay in range(1, 7):
        for _ in range(random.randint(8, 15)):
            urun: str = random.choice(urunler)
            gun: int = random.randint(1, 28)
            kayitlar.append({
                "tarih": f"2025-{ay:02d}-{gun:02d}",
                "urun": urun,
                "kategori": kategoriler[urun],
                "birim_fiyat": fiyatlar[urun],
                "adet": random.randint(1, 20),
                "sehir": random.choice(sehirler),
                "temsilci": random.choice(temsilciler),
            })

    df: pd.DataFrame = pd.DataFrame(kayitlar)
    df["tarih"] = pd.to_datetime(df["tarih"])  # Tarihleri duz yazidan cikarip gercek tarih formatina donustururuz.
    df["toplam"] = df["adet"] * df["birim_fiyat"]
    df["ay"] = df["tarih"].dt.strftime("%Y-%m")  # Yil ve Ay kismini koparip aliriz.
    return df.sort_values("tarih").reset_index(drop=True)


# =====================================================
# VERIYI YUKLE
# =====================================================

df: pd.DataFrame = ornek_satis_verisi_olustur()


# =====================================================
# SIDEBAR -- FILTRELER
# =====================================================

with st.sidebar:
    st.header("Filtreler")

    # Tarih araligi
    min_tarih = df["tarih"].min().date()
    max_tarih = df["tarih"].max().date()
    tarih_araligi = st.date_input(  # Kullaniciya baslangic ve bitis tarihlerini secebilecegi bir takvim acar.
        "Tarih Araligi:",
        value=(min_tarih, max_tarih),
        min_value=min_tarih,
        max_value=max_tarih,
        key="tarih_filtre"
    )

    # Kategori filtresi
    kategoriler_secim: list[str] = st.multiselect(  # Kullanicinin BIRDAN FAZLA secenek isaretleyebilecegi acilir liste kutusu (dropdown).
        "Kategori:",
        options=df["kategori"].unique().tolist(),
        default=df["kategori"].unique().tolist(),
        key="kategori_filtre"
    )

    # Sehir filtresi
    sehirler_secim: list[str] = st.multiselect(
        "Sehir:",
        options=df["sehir"].unique().tolist(),
        default=df["sehir"].unique().tolist(),
        key="sehir_filtre"
    )

    # Temsilci filtresi
    temsilciler_secim: list[str] = st.multiselect(
        "Temsilci:",
        options=df["temsilci"].unique().tolist(),
        default=df["temsilci"].unique().tolist(),
        key="temsilci_filtre"
    )

    st.divider()  # Ekrana boydan boya yatay bir cizgi (ayrac) ceker.
    st.caption("Streamlit Mini Proje -- Modul 5")  # Kucuk ve gri renkli bir alt yazi yazar.

# =====================================================
# FILTRELEMEYI UYGULA
# =====================================================

filtrelenmis: pd.DataFrame = df.copy()

# Tarih filtresi
if len(tarih_araligi) == 2:  # Kullanici takvimden hem baslangic hem bitis tarihi secmis mi diye bakar.
    baslangic, bitis = tarih_araligi
    filtrelenmis = filtrelenmis[
        (filtrelenmis["tarih"].dt.date >= baslangic) &
        (filtrelenmis["tarih"].dt.date <= bitis)
    ]

# Kategori filtresi
if kategoriler_secim:  # Eger kullanici bir seyler secmisse (liste bos degilse)
    filtrelenmis = filtrelenmis[filtrelenmis["kategori"].isin(kategoriler_secim)]  # Tablodaki kategoriler, kullanicinin sectikleri listesinde VARSA goster (isin).

# Sehir filtresi
if sehirler_secim:
    filtrelenmis = filtrelenmis[filtrelenmis["sehir"].isin(sehirler_secim)]

# Temsilci filtresi
if temsilciler_secim:
    filtrelenmis = filtrelenmis[filtrelenmis["temsilci"].isin(temsilciler_secim)]


# =====================================================
# ANA ICERIK
# =====================================================

st.title("Satis Dashboard")
st.caption(f"Gosterilen: {len(filtrelenmis)} / {len(df)} kayit")

# --- Metrikler ---
met1, met2, met3, met4 = st.columns(4)

toplam_satis: float = filtrelenmis["toplam"].sum()
toplam_adet: int = int(filtrelenmis["adet"].sum())
benzersiz_musteri: int = filtrelenmis["sehir"].nunique()
ort_siparis: float = filtrelenmis["toplam"].mean() if len(filtrelenmis) > 0 else 0

met1.metric("Toplam Satis", f"{toplam_satis:,.0f} TL")  # Hesaplanan toplami kocaman bir sayi olarak ekranda gosterir.
met2.metric("Toplam Adet", f"{toplam_adet:,}")
met3.metric("Siparis Sayisi", len(filtrelenmis))
met4.metric("Ort. Siparis", f"{ort_siparis:,.0f} TL")

st.divider()

# --- Grafikler ---
grafik1, grafik2 = st.columns(2)

with grafik1:
    st.subheader("Aylik Satis Trendi")
    aylik: pd.DataFrame = filtrelenmis.groupby("ay")["toplam"].sum().reset_index()
    aylik.columns = ["Ay", "Toplam Satis"]
    st.line_chart(aylik.set_index("Ay"))

with grafik2:
    st.subheader("Kategoriye Gore Satis")
    kat_ozet: pd.DataFrame = filtrelenmis.groupby("kategori")["toplam"].sum()
    st.bar_chart(kat_ozet)

# --- Alt Grafikler ---
alt1, alt2 = st.columns(2)

with alt1:
    st.subheader("Sehir Bazli Satis")
    sehir_ozet: pd.DataFrame = filtrelenmis.groupby("sehir")["toplam"].sum()
    st.bar_chart(sehir_ozet)

with alt2:
    st.subheader("Temsilci Performansi")
    temsilci_ozet: pd.DataFrame = filtrelenmis.groupby("temsilci")["toplam"].sum()
    st.bar_chart(temsilci_ozet)

st.divider()

# --- Tablolar ---
tab1, tab2, tab3 = st.tabs(["Detay Tablosu", "Urun Ozeti", "En Iyi Satislar"])

with tab1:
    st.dataframe(
        filtrelenmis[["tarih", "urun", "kategori", "adet", "birim_fiyat", "toplam", "sehir", "temsilci"]],
        width="stretch",
        hide_index=True
    )

with tab2:
    urun_ozet: pd.DataFrame = filtrelenmis.groupby("urun").agg(
        Toplam_Tutar=("toplam", "sum"),
        Toplam_Adet=("adet", "sum"),
        Siparis_Sayisi=("toplam", "count"),
        Ort_Fiyat=("birim_fiyat", "mean")
    ).sort_values("Toplam_Tutar", ascending=False).reset_index()
    st.dataframe(urun_ozet, width="stretch", hide_index=True)

with tab3:
    en_iyiler: pd.DataFrame = filtrelenmis.nlargest(10, "toplam")[
        ["tarih", "urun", "adet", "birim_fiyat", "toplam", "sehir"]
    ]
    st.dataframe(en_iyiler, width="stretch", hide_index=True)

# --- CSV Indirme ---
st.divider()
csv_veri: bytes = filtrelenmis.to_csv(index=False).encode("utf-8-sig")  # utf-8-sig: Excel'de Turkce karakterler bozulmaz
st.download_button(  # Kullanicinin ekrandaki sonuclari bilgisayarina indirebilmesi icin bir "Indir" butonu koyar.
    label="CSV Olarak Indir",
    data=csv_veri,
    file_name=f"satis_raporu_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv"
)
