"""
================================================================================
    MODÜL 6 - BÖLÜM 1: Streamlit ile Profesyonel Tek Sayfa Uygulama
    Konu: requests ile canlı API verisi + Matplotlib grafikleri
================================================================================
Çalıştırmak için (bu klasörde):  streamlit run 01_streamlit_temeller.py veya py -m streamlit run .\01_streamlit_temeller.py
Kurulum: pip install streamlit pandas requests matplotlib

Kullanılan ücretsiz servisler (API anahtarı gerekmez):
  - Open-Meteo Geocoding : şehir adı -> enlem / boylam
  - Open-Meteo Forecast  : anlık, saatlik ve günlük hava tahmini
  - Frankfurter (ECB)    : Avrupa Merkez Bankası günlük döviz kurları

Sayfa akışı:
  1. Yan menüden ayarlar okunur (şehir, gün sayısı, dövizler, dönem)
  2. requests ile API'lerden veri çekilir (st.cache_data ile önbelleklenir)
  3. Veriler pandas DataFrame'e çevrilir
  4. Özet metrikler, Matplotlib grafikleri ve tablolar sekmelerde gösterilir
"""

from datetime import date, timedelta

import matplotlib.dates as mdates
import pandas as pd
import requests
import streamlit as st
from matplotlib.axes import Axes
from matplotlib.figure import Figure

# ========================================================
# 1. SAYFA YAPILANDIRMASI
# ========================================================
# Bu satırdan önce başka streamlit komutu olmamalı
st.set_page_config(
    page_title="Şehir & Piyasa Paneli",
    page_icon=":material/monitoring:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ========================================================
# 2. SABİTLER
# ========================================================
GEO_URL: str = "https://geocoding-api.open-meteo.com/v1/search"
HAVA_URL: str = "https://api.open-meteo.com/v1/forecast"
KUR_URL: str = "https://api.frankfurter.dev/v1"
ZAMAN_ASIMI: int = 10  # saniye; API cevap vermezse sayfa sonsuza kadar beklemesin

SEHIRLER: list[str] = ["İstanbul", "Ankara", "İzmir", "Bursa", "Balıkesir", "Antalya", "Trabzon", "Diyarbakır"]
DIGER: str = "Başka bir şehir…"

PARA_BIRIMLERI: dict[str, str] = {
    "USD": "ABD Doları",
    "EUR": "Euro",
    "GBP": "İngiliz Sterlini",
    "CHF": "İsviçre Frangı",
    "JPY": "Japon Yeni",
}
DONEMLER: dict[str, int] = {"1 Ay": 30, "3 Ay": 90, "6 Ay": 182, "1 Yıl": 365}

# WMO hava durumu kodları -> Türkçe açıklama
HAVA_KODLARI: dict[int, str] = {
    0: "Açık", 1: "Çoğunlukla açık", 2: "Parçalı bulutlu", 3: "Kapalı",
    45: "Sisli", 48: "Kırağılı sis",
    51: "Hafif çisenti", 53: "Çisenti", 55: "Yoğun çisenti",
    56: "Dondurucu çisenti", 57: "Yoğun dondurucu çisenti",
    61: "Hafif yağmur", 63: "Yağmurlu", 65: "Şiddetli yağmur",
    66: "Dondurucu yağmur", 67: "Şiddetli dondurucu yağmur",
    71: "Hafif kar", 73: "Karlı", 75: "Yoğun kar", 77: "Kar taneleri",
    80: "Hafif sağanak", 81: "Sağanak", 82: "Şiddetli sağanak",
    85: "Kar sağanağı", 86: "Yoğun kar sağanağı",
    95: "Gök gürültülü fırtına", 96: "Dolulu fırtına", 99: "Şiddetli dolulu fırtına",
}

# Grafik renkleri: şeffaf zemin + gri yazı, hem açık hem koyu temada okunur
METIN_RENGI: str = "#8a8f98"
SICAK_RENGI: str = "#f97316"
SOGUK_RENGI: str = "#3b82f6"
YAGIS_RENGI: str = "#06b6d4"
ARTIS_RENGI: str = "#ef4444"
AZALIS_RENGI: str = "#10b981"
SERI_RENKLERI: list[str] = ["#2563eb", "#f97316", "#10b981", "#8b5cf6", "#e11d48", "#ca8a04", "#0891b2", "#65a30d"]
KART_SAYISI: int = 5  # bir satırda en fazla kaç kur kartı gösterilsin


def tr_sayi(deger: float, basamak: int = 2) -> str:
    """1234.5 -> '1.234,50' (Türkçe sayı biçimi)."""
    return f"{deger:,.{basamak}f}".replace(",", "_").replace(".", ",").replace("_", ".")


# ========================================================
# 3. VERİ KATMANI (requests + st.cache_data)
# ========================================================
# st.cache_data: Aynı parametrelerle tekrar çağrılınca API'ye gitmez,
# sonucu hafızadan döndürür. ttl = kaç saniye geçerli kalacağı.

@st.cache_data(ttl=24 * 3600, show_spinner=False)
def sehir_bul(ad: str) -> dict | None:
    """Şehir adını enlem/boylam bilgisine çevirir. Bulamazsa None döner."""
    yanit = requests.get(
        GEO_URL,
        params={"name": ad, "count": 1, "language": "tr", "format": "json"},
        timeout=ZAMAN_ASIMI,
    )
    yanit.raise_for_status()  # 4xx / 5xx durumunda hata fırlatır
    sonuclar = yanit.json().get("results")
    return sonuclar[0] if sonuclar else None


@st.cache_data(ttl=600, show_spinner=False)
def hava_getir(enlem: float, boylam: float, gun: int) -> dict:
    """Anlık, saatlik ve günlük hava tahminini getirir (10 dk önbellek)."""
    yanit = requests.get(
        HAVA_URL,
        params={
            "latitude": enlem,
            "longitude": boylam,
            "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code",
            "hourly": "temperature_2m,precipitation_probability",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "auto",
            "forecast_days": gun,
        },
        timeout=ZAMAN_ASIMI,
    )
    yanit.raise_for_status()
    return yanit.json()


@st.cache_data(ttl=3600, show_spinner=False)
def kurlari_getir(semboller: tuple[str, ...], baslangic: date) -> pd.DataFrame:
    """Seçilen dövizlerin TL karşılığını (1 birim = X TL) tarih sırasıyla döndürür."""
    yanit = requests.get(
        f"{KUR_URL}/{baslangic.isoformat()}..",
        params={"base": "TRY", "symbols": ",".join(semboller)},
        timeout=ZAMAN_ASIMI,
    )
    yanit.raise_for_status()
    df = pd.DataFrame.from_dict(yanit.json()["rates"], orient="index")
    df.index = pd.to_datetime(df.index)
    # API "1 TL = 0,0207 USD" verir; tersini alarak "1 USD = 48,3 TL" elde ederiz
    return (1 / df).sort_index()[list(semboller)]


def saatlik_tablo(hava: dict) -> pd.DataFrame:
    df = pd.DataFrame(hava["hourly"])
    df["time"] = pd.to_datetime(df["time"])
    return df.set_index("time")


def gunluk_tablo(hava: dict) -> pd.DataFrame:
    df = pd.DataFrame(hava["daily"])
    df["time"] = pd.to_datetime(df["time"])
    return df.set_index("time")


# ========================================================
# 4. GRAFİKLER (Matplotlib)
# ========================================================
# matplotlib.pyplot yerine doğrudan Figure kullanıyoruz: Streamlit aynı anda
# birden çok kullanıcıya hizmet verdiğinde pyplot'un global durumu karışabilir.

def _eksen_stili(ax: Axes) -> None:
    ax.set_facecolor("none")
    for kenar in ("top", "right"):
        ax.spines[kenar].set_visible(False)
    for kenar in ("left", "bottom"):
        ax.spines[kenar].set_color(METIN_RENGI)
    ax.tick_params(colors=METIN_RENGI, labelsize=9)
    ax.xaxis.label.set_color(METIN_RENGI)
    ax.yaxis.label.set_color(METIN_RENGI)
    ax.grid(axis="y", color=METIN_RENGI, alpha=0.2, linewidth=0.8)
    ax.set_axisbelow(True)


def _yeni_figur(genislik: float = 10, yukseklik: float = 3.6) -> tuple[Figure, Axes]:
    fig = Figure(figsize=(genislik, yukseklik), dpi=110)
    fig.patch.set_alpha(0)  # şeffaf zemin
    ax = fig.subplots()
    _eksen_stili(ax)
    return fig, ax


def _lejant(ax: Axes, *ekstra: Axes, **kwargs) -> None:
    tutamaclar, etiketler = ax.get_legend_handles_labels()
    for diger in ekstra:
        t, e = diger.get_legend_handles_labels()
        tutamaclar += t
        etiketler += e
    ax.legend(tutamaclar, etiketler, frameon=False, labelcolor=METIN_RENGI, fontsize=9, **kwargs)


def grafik_saatlik(df: pd.DataFrame, simdi: pd.Timestamp) -> Figure:
    """Saatlik sıcaklık (çizgi) + yağış olasılığı (çubuk, ikinci eksen)."""
    fig, ax = _yeni_figur()
    ax2 = ax.twinx()  # aynı x eksenini paylaşan ikinci y ekseni

    ax2.bar(df.index, df["precipitation_probability"], width=1 / 24,
            color=YAGIS_RENGI, alpha=0.3, label="Yağış olasılığı (%)")
    ax2.set_ylim(0, 100)
    ax2.set_ylabel("Yağış olasılığı (%)")
    ax2.set_facecolor("none")
    ax2.tick_params(colors=METIN_RENGI, labelsize=9)
    ax2.yaxis.label.set_color(METIN_RENGI)
    for kenar in ("top", "left", "bottom"):
        ax2.spines[kenar].set_visible(False)
    ax2.spines["right"].set_color(METIN_RENGI)

    sicaklik = df["temperature_2m"]
    ax.plot(df.index, sicaklik, color=SICAK_RENGI, linewidth=2, label="Sıcaklık (°C)")
    ax.fill_between(df.index, sicaklik, sicaklik.min() - 1, color=SICAK_RENGI, alpha=0.08)
    ax.axvline(simdi, color=METIN_RENGI, linestyle="--", linewidth=1)
    ax.annotate("şimdi", xy=(simdi, 1), xycoords=("data", "axes fraction"),
                xytext=(4, -12), textcoords="offset points", color=METIN_RENGI, fontsize=8)
    ax.set_ylabel("°C")
    ax.set_xlim(df.index.min(), df.index.max())
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m"))

    # Çizgi, çubukların önünde dursun
    ax.set_zorder(ax2.get_zorder() + 1)
    ax.patch.set_visible(False)
    _lejant(ax, ax2, loc="lower left", bbox_to_anchor=(0, 1.0), ncols=2)
    fig.tight_layout()
    return fig


def grafik_gunluk_sicaklik(df: pd.DataFrame) -> Figure:
    """Günlük en düşük / en yüksek sıcaklık bandı."""
    fig, ax = _yeni_figur(genislik=6, yukseklik=3.4)
    en_yuksek = df["temperature_2m_max"]
    en_dusuk = df["temperature_2m_min"]

    ax.fill_between(df.index, en_dusuk, en_yuksek, color=SICAK_RENGI, alpha=0.12)
    ax.plot(df.index, en_yuksek, marker="o", color=SICAK_RENGI, linewidth=2, label="En yüksek")
    ax.plot(df.index, en_dusuk, marker="o", color=SOGUK_RENGI, linewidth=2, label="En düşük")
    for x, ust, alt in zip(df.index, en_yuksek, en_dusuk):
        ax.annotate(f"{ust:.0f}°", (x, ust), xytext=(0, 6), textcoords="offset points",
                    ha="center", fontsize=8, color=SICAK_RENGI)
        ax.annotate(f"{alt:.0f}°", (x, alt), xytext=(0, -13), textcoords="offset points",
                    ha="center", fontsize=8, color=SOGUK_RENGI)

    ax.set_ylim(en_dusuk.min() - 4, en_yuksek.max() + 4)
    ax.set_ylabel("°C")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m"))
    _lejant(ax, loc="lower right", bbox_to_anchor=(1, 1.0), ncols=2)
    fig.tight_layout()
    return fig


def grafik_gunluk_yagis(df: pd.DataFrame) -> Figure:
    """Günlük toplam yağış miktarı (mm)."""
    fig, ax = _yeni_figur(genislik=6, yukseklik=3.4)
    yagis = df["precipitation_sum"].fillna(0)
    cubuklar = ax.bar(df.index, yagis, width=0.6, color=YAGIS_RENGI)
    ax.bar_label(cubuklar, labels=[f"{v:.1f}" if v > 0 else "" for v in yagis],
                 padding=2, fontsize=8, color=METIN_RENGI)
    ax.set_ylim(0, max(yagis.max() * 1.25, 1))
    ax.set_ylabel("mm")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m"))
    fig.tight_layout()
    return fig


def grafik_kur_seyri(df: pd.DataFrame, endeks: bool, hareketli_ortalama: bool) -> Figure:
    """Kurların zaman içindeki seyri. Endeks modunda tüm seriler 100'den başlar."""
    fig, ax = _yeni_figur(yukseklik=3.8)
    veri = df / df.iloc[0] * 100 if endeks else df

    for sira, sembol in enumerate(veri.columns):
        renk = SERI_RENKLERI[sira % len(SERI_RENKLERI)]  # renkler biterse baştan döner
        ax.plot(veri.index, veri[sembol], color=renk, linewidth=2, label=sembol)
        if hareketli_ortalama:
            ax.plot(veri.index, veri[sembol].rolling(7).mean(), color=renk,
                    linewidth=1, linestyle="--", alpha=0.7)

    if endeks:
        ax.axhline(100, color=METIN_RENGI, linewidth=1, linestyle=":")
        ax.set_ylabel("Endeks (başlangıç = 100)")
    else:
        ax.set_ylabel("TL")
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=8))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m.%y"))
    _lejant(ax, loc="lower left", bbox_to_anchor=(0, 1.0), ncols=len(veri.columns))
    fig.tight_layout()
    return fig


def grafik_degisim(degisim: pd.Series) -> Figure:
    """Dönem başından bugüne yüzde değişim (yatay çubuk)."""
    fig, ax = _yeni_figur(genislik=6, yukseklik=0.6 + 0.55 * len(degisim))
    degisim = degisim.sort_values()
    renkler = [ARTIS_RENGI if v >= 0 else AZALIS_RENGI for v in degisim]
    cubuklar = ax.barh(degisim.index, degisim.values, color=renkler, height=0.6)
    ax.bar_label(cubuklar, labels=[f"%{tr_sayi(v, 1)}" for v in degisim],
                 padding=4, fontsize=9, color=METIN_RENGI)
    ax.axvline(0, color=METIN_RENGI, linewidth=1)
    sinir = max(abs(degisim).max() * 1.35, 1)
    ax.set_xlim(-sinir if degisim.min() < 0 else 0, sinir)
    ax.grid(axis="x", color=METIN_RENGI, alpha=0.2, linewidth=0.8)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("TL karşısında değişim (%)")
    fig.tight_layout()
    return fig


# ========================================================
# 5. YAN MENÜ (AYARLAR)
# ========================================================
with st.sidebar:
    st.header("Ayarlar")

    st.subheader("Hava durumu", divider="gray")
    secim: str = st.selectbox("Şehir", options=SEHIRLER + [DIGER])
    sehir_adi: str = st.text_input("Şehir adı", value="Eskişehir") if secim == DIGER else secim
    gun_sayisi: int = st.slider("Tahmin süresi (gün)", min_value=3, max_value=14, value=7)

    st.subheader("Döviz kurları", divider="gray")
    semboller: list[str] = st.multiselect(
        "Para birimleri",
        options=list(PARA_BIRIMLERI),
        default=["USD", "EUR", "GBP"],
        format_func=lambda kod: f"{kod} · {PARA_BIRIMLERI[kod]}",
    )
    donem: str = st.select_slider("Dönem", options=list(DONEMLER), value="3 Ay")

    st.divider()
    if st.button("Verileri yenile", icon=":material/refresh:", width="stretch"):
        st.cache_data.clear()  # önbelleği boşalt -> bir sonraki çağrıda API'ye yeniden gidilir

    st.caption(
        "Veri kaynakları: [Open-Meteo](https://open-meteo.com) · "
        "[Frankfurter / ECB](https://frankfurter.dev)"
    )


# ========================================================
# 6. VERİLERİ ÇEK
# ========================================================
# Ağ hataları (internet yok, servis kapalı, zaman aşımı) requests.RequestException
# olarak gelir. Yakalayıp kullanıcıya düzgün bir mesaj gösteriyoruz; sayfa çökmez.

konum: dict | None = None
hava: dict | None = None
hava_hatasi: str | None = None
kurlar: pd.DataFrame | None = None
kur_hatasi: str | None = None

with st.spinner("Veriler yükleniyor…"):
    try:
        konum = sehir_bul(sehir_adi.strip()) if sehir_adi.strip() else None
        if konum is None:
            hava_hatasi = f"“{sehir_adi}” adında bir şehir bulunamadı."
        else:
            hava = hava_getir(konum["latitude"], konum["longitude"], gun_sayisi)
    except requests.RequestException as hata:
        hava_hatasi = f"Hava durumu servisine ulaşılamadı: {hata}"

    if semboller:
        try:
            baslangic = date.today() - timedelta(days=DONEMLER[donem])
            kurlar = kurlari_getir(tuple(semboller), baslangic)
        except requests.RequestException as hata:
            kur_hatasi = f"Döviz kuru servisine ulaşılamadı: {hata}"
    else:
        kur_hatasi = "Kurları görmek için yan menüden en az bir para birimi seçin."


# ========================================================
# 7. BAŞLIK VE ÖZET METRİKLER
# ========================================================
st.title("Şehir & Piyasa Paneli")
if konum:
    bolge = ", ".join(p for p in (konum.get("admin1"), konum.get("country")) if p)
    st.caption(f"{konum['name']} · {bolge} · Canlı hava tahmini ve güncel döviz kurları")
else:
    st.caption("Canlı hava tahmini ve güncel döviz kurları")

if hava:
    anlik = hava["current"]
    birim = hava["current_units"]
    with st.container(border=True):
        st.markdown(
            f"**Şu an:** {HAVA_KODLARI.get(anlik['weather_code'], 'Bilinmiyor')}"
            f" · <span style='color:{METIN_RENGI}'>ölçüm {anlik['time'].replace('T', ' ')}</span>",
            unsafe_allow_html=True,
        )
        h1, h2, h3, h4 = st.columns(4)
        h1.metric("Sıcaklık", f"{tr_sayi(anlik['temperature_2m'], 1)} {birim['temperature_2m']}")
        h2.metric(
            "Hissedilen",
            f"{tr_sayi(anlik['apparent_temperature'], 1)} {birim['apparent_temperature']}",
            delta=f"{anlik['apparent_temperature'] - anlik['temperature_2m']:+.1f}°".replace(".", ","),
            delta_color="off",
        )
        h3.metric("Nem", f"%{anlik['relative_humidity_2m']}")
        h4.metric("Rüzgar", f"{anlik['wind_speed_10m']:.0f} {birim['wind_speed_10m']}")

if kurlar is not None and len(kurlar) >= 2:
    with st.container(border=True):
        st.markdown(
            f"**Kurlar:** 1 birim = ? TL · "
            f"<span style='color:{METIN_RENGI}'>ECB, {kurlar.index[-1]:%d.%m.%Y}</span>",
            unsafe_allow_html=True,
        )
        # Çok para birimi seçilirse kartlar KART_SAYISI'lık satırlara bölünür
        for bas in range(0, len(semboller), KART_SAYISI):
            satir = semboller[bas:bas + KART_SAYISI]
            for kolon, sembol in zip(st.columns(min(len(semboller), KART_SAYISI)), satir):
                son, onceki = kurlar[sembol].iloc[-1], kurlar[sembol].iloc[-2]
                gunluk_degisim = (son / onceki - 1) * 100
                kolon.metric(
                    f"{sembol}/TRY",
                    tr_sayi(son, 4),
                    # Streamlit ok yönünü metnin ilk karakterinden anlar: "-%0,82" aşağı, "+%0,82" yukarı
                    delta=f"{'-' if gunluk_degisim < 0 else '+'}%{tr_sayi(abs(gunluk_degisim), 2)}",
                    delta_color="inverse",  # döviz yükselişi TL açısından kırmızı
                )


# ========================================================
# 8. SEKMELER: HAVA, DÖVİZ, VERİ
# ========================================================
sekme_hava, sekme_kur, sekme_veri = st.tabs(
    [":material/partly_cloudy_day: Hava Durumu", ":material/currency_exchange: Döviz Kurları", ":material/table: Veri Tabloları"]
)

with sekme_hava:
    if hava_hatasi:
        st.warning(hava_hatasi)
    else:
        saatlik = saatlik_tablo(hava)
        gunluk = gunluk_tablo(hava)

        st.subheader("Saatlik tahmin")
        st.pyplot(grafik_saatlik(saatlik, pd.Timestamp(hava["current"]["time"])))

        sol, sag = st.columns(2)
        with sol:
            st.subheader("Günlük sıcaklık aralığı")
            st.pyplot(grafik_gunluk_sicaklik(gunluk))
        with sag:
            st.subheader("Günlük toplam yağış")
            st.pyplot(grafik_gunluk_yagis(gunluk))

        en_sicak = gunluk["temperature_2m_max"].idxmax()
        en_yagisli = gunluk["precipitation_sum"].idxmax()
        st.info(
            f"Önümüzdeki {gun_sayisi} günün en sıcak günü **{en_sicak:%d.%m}** "
            f"({gunluk.loc[en_sicak, 'temperature_2m_max']:.0f}°C). "
            + (
                f"En yağışlı gün **{en_yagisli:%d.%m}** "
                f"({tr_sayi(gunluk.loc[en_yagisli, 'precipitation_sum'], 1)} mm)."
                if gunluk["precipitation_sum"].max() > 0
                else "Yağış beklenmiyor."
            ),
            icon=":material/insights:",
        )

with sekme_kur:
    if kur_hatasi:
        st.warning(kur_hatasi)
    elif kurlar is not None:
        ayar1, ayar2 = st.columns([2, 1])
        gorunum: str = ayar1.segmented_control(
            "Görünüm", options=["Endeks", "TL değeri"], default="Endeks"
        ) or "Endeks"
        hareketli: bool = ayar2.toggle("7 günlük hareketli ortalama")

        st.subheader(f"Kur seyri · son {donem.lower()}")
        st.pyplot(grafik_kur_seyri(kurlar, endeks=gorunum == "Endeks", hareketli_ortalama=hareketli))
        if gorunum == "Endeks":
            st.caption("Endeks görünümü, farklı büyüklükteki kurları aynı ölçekte karşılaştırır: "
                       "dönem başı = 100, 110 = %10 artış.")

        sol, sag = st.columns(2)
        with sol:
            st.subheader("Dönemsel değişim")
            degisim = (kurlar.iloc[-1] / kurlar.iloc[0] - 1) * 100
            st.pyplot(grafik_degisim(degisim))
        with sag:
            st.subheader("Dönem özeti")
            ozet = pd.DataFrame({
                "Başlangıç": kurlar.iloc[0],
                "Son": kurlar.iloc[-1],
                "En düşük": kurlar.min(),
                "En yüksek": kurlar.max(),
                "Değişim %": degisim,
            })
            st.dataframe(ozet.style.format(precision=4).format({"Değişim %": "{:+.2f}"}), width="stretch")

with sekme_veri:
    sol, sag = st.columns(2)
    with sol:
        st.subheader("Günlük hava tahmini")
        if hava:
            gunluk_tr = gunluk_tablo(hava).rename(columns={
                "temperature_2m_max": "En yüksek (°C)",
                "temperature_2m_min": "En düşük (°C)",
                "precipitation_sum": "Yağış (mm)",
            })
            gunluk_tr.index = gunluk_tr.index.strftime("%d.%m.%Y")
            gunluk_tr.index.name = "Tarih"
            st.dataframe(gunluk_tr, width="stretch")
            st.download_button(
                "CSV indir",
                data=gunluk_tr.to_csv().encode("utf-8-sig"),  # utf-8-sig: Excel'de Türkçe karakterler bozulmaz
                file_name=f"hava_{konum['name']}.csv",
                mime="text/csv",
                icon=":material/download:",
            )
        else:
            st.caption("Hava verisi yok.")
    with sag:
        st.subheader("Günlük döviz kurları (TL)")
        if kurlar is not None:
            kurlar_tr = kurlar.sort_index(ascending=False).round(4)
            kurlar_tr.index = kurlar_tr.index.strftime("%d.%m.%Y")
            kurlar_tr.index.name = "Tarih"
            st.dataframe(kurlar_tr, width="stretch", height=320)
            st.download_button(
                "CSV indir",
                data=kurlar_tr.to_csv().encode("utf-8-sig"),
                file_name="doviz_kurlari.csv",
                mime="text/csv",
                icon=":material/download:",
            )
        else:
            st.caption("Kur verisi yok.")

with st.expander("Bu sayfa nasıl çalışıyor?"):
    st.markdown(
        """
- **requests** ile üç farklı REST API'ye `GET` isteği atılır, cevap `.json()` ile sözlüğe çevrilir.
- `@st.cache_data(ttl=...)` aynı istek tekrarlandığında API'ye gitmeden sonucu hafızadan verir.
- Veriler **pandas** DataFrame'e dönüştürülür, grafikler **Matplotlib** `Figure` ile çizilip `st.pyplot` ile gösterilir.
- Ağ hataları `requests.RequestException` ile yakalanır; servis kapalı olsa bile sayfa çökmez.
"""
    )
    st.code(
        'yanit = requests.get(url, params={"name": "Ankara"}, timeout=10)\n'
        "yanit.raise_for_status()\n"
        "veri = yanit.json()",
        language="python",
    )
