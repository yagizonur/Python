"""
=====================================================
MODUL 5 - BÖLÜM 2: Filtreleme, Gruplama, Birleştirme 
Konu: Sorgulama, GroupBy, Merge
=====================================================
"""

import pandas as pd

# =================================================================
# VERİ SETİNİ YÜKLEME
# =================================================================

print("--Satış Verilerini Yükleme ---")
csv_yolu: str = "veri_setleri/satis_verileri.csv"

try:
    satislar: pd.DataFrame = pd.read_csv(csv_yolu)

    # Sütun isimlerini koddaki eski isimlendirmeye uydurmak için değiştiriyoruz.
    satislar = satislar.rename(columns={
        "Tarih":"tarih",
        "Kategori":"kategori",
        "Urun":"urun",
        "Birim_Fiyat":"birim_fiyat",
        "Adet":"adet",
        "Toplam_Tutar":"toplam",
        "Sehir":"sehir",
        "Satis_Temsilcisi": "satis_temsilcisi"
    })
    satislar["tarih"] = pd.to_datetime(satislar["tarih"]) # Tarihi metinden gerçek tarihe çevirir.

    print(f"Veri başarıyla yüklendi! Satır sayısı: {len(satislar)}")
    print(satislar.head())

except FileNotFoundError:
    print(f"HATA: {csv_yolu} bulunamadı!")
    exit()

print(f"\nToplam satış tutarı: {satislar['toplam'].sum():,.0f} TL")

# =================================================================
# 1. FİLTRELEME
# =================================================================
print("\n" + "=" * 50)
print("1. FİLTRELEME")
print("=" * 50)

print("\n --- Birim fiyatı 10.000'den büyük ---")
pahali: pd.DataFrame = satislar[satislar["birim_fiyat"] > 10000] # Tabloda sadece fiyatı 10000'den büyük olan satışları süzer/filtreler
print(pahali[["urun","birim_fiyat","toplam"]])

# Birden fazla koşul(VE)
print("\n--- Elektronik VE 1'den fazla adet ---")
filtre_ve: pd.DataFrame = satislar[
    (satislar["kategori"] == "Elektronik") & (satislar["adet"] > 1)
]

print(filtre_ve[["urun", "adet", "toplam"]])


# Birden fazla koşul(VEYA)
print("\n--- Mouse VEYA Klavye ---")
filtre_veya: pd.DataFrame = satislar[
    (satislar["urun"] == "Krem") | (satislar["urun"] == "Sandalye")
]

print(filtre_veya[["urun", "adet", "birim_fiyat"]])

# --- isin() ile çoklu değer kontrolü
print("\n-- isin() ile çoklu filtre --")
aranan_urunler: list[str] = ["Krem","Sandalye","Masa"]
filtre_isin: pd.DataFrame = satislar[satislar["urun"].isin(aranan_urunler)] # VEYA yazmaktan kurtarır. Bir değerin listede olup olmadığına bakar.
print(filtre_isin[["urun","adet","toplam"]])

# String içinde arama
print("\n --- String arama(str.contains) ---")
filtre_str: pd.DataFrame = satislar[
    satislar["urun"].str.contains("op",case=False) # İçerisinde 'op' harfleri geçenleri bulur.
]
print(filtre_str[["urun","toplam"]])

# =================================================================
# 2. GRUPLAMA
# =================================================================

print("\n" + "=" * 50)
print("2. GRUPLAMA")
print("=" * 50)

# Basit Gruplama 
print(f"\n-- Ürüne Göre Gruplama --")
urun_grup: pd.DataFrame = satislar.groupby("urun").agg(#groupby() aynı olan satislari bir araya toplar(örn: tüm Laptopları birleştirir.) agg() ise onları nasıl toplayacağını söyler
toplam_satis = ("toplam","sum"),
toplam_adet=("adet","sum"),
satis_sayisi=("toplam","count"),
ortalama_fiyat=("birim_fiyat","mean")
).reset_index()

# Toplam satışa göre azalan sıralama
urun_grup = urun_grup.sort_values("toplam_satis",ascending=False)
print(urun_grup)

# Kategoriye Göre 
print("\n-- Kategoriye Göre Özet ---")
kategori_ozet: pd.DataFrame = satislar.groupby("kategori").agg(
    toplam_satis = ("toplam","sum"),
    toplam_adet=("adet","sum"),
    ortalama_tutar=("toplam","mean")
).reset_index()
print(kategori_ozet)


print("\n-- Temsilci Performansı---")
temsilci: pd.DataFrame = satislar.groupby("satis_temsilcisi").agg(
    toplam_satis = ("toplam","sum"),
    satis_adedi=("toplam","count")
).reset_index().sort_values("toplam_satis",ascending=False)
print(temsilci)

# Çoklu gruplama
print("\n-- Kategori + Temsilci---")
coklu: pd.DataFrame = satislar.groupby(
    ["kategori","satis_temsilcisi"]
)["toplam"].sum().reset_index()
print(coklu)

# Aylık özet
print("\n--- Aylık Satış Özeti ---")
satislar["ay"] = satislar["tarih"].dt.strftime("%Y-%m")
aylik: pd.DataFrame = satislar.groupby("ay").agg(
    toplam=("toplam","sum"),
    adet=("adet","sum")
).reset_index() # DataFrame'in mevcut satır indekslerini sıfırlayarak 0,1,2.. şeklinde ardışık tam sayılardan oluşan varsayılan indeks düzeni sağlar.
print(aylik)

# =================================================================
# 3. BİRLEŞTİRME
# =================================================================
print("\n" + "=" * 50)
print("3. Birleştirme(Merge")
print("=" * 50)

urunler_df: pd.DataFrame = pd.DataFrame({
    "urun_kodu":["LP01","MS01","KL01","MN01"],
    "urun_adi":["Laptop","Mouse","Klavye","Monitor"],
    "marka":["Lenovo","Logitech","Corsair","Samsung"]
})

siparisler_df: pd.DataFrame = pd.DataFrame({
    "siparis_id":[1,2,3,4,5],
    "urun_kodu":["LP01","MS01","LP01","KL01","MN01"],
    "miktar":[1,5,2,3,1],
    "musteri":["Ayda","Arda","Salman","Can","Onur"]
})

# INNER JOIN
print("\n -- Inner Join --")
birlesik: pd.DataFrame = pd.merge(# pd.merge() iki farklı tabloyu aynı Excel'de VLOOKUP gibi birlestirir.
    siparisler_df,urunler_df,
    on="urun_kodu", #İki tablodaki ortak sütunun ismini söylüyoruz.
    how="inner" # Sadece ikisinde de eşleşen kayıtları(inner) eşleştirir.
)
print(birlesik)

# =================================================================
# 4. PIVOT TABLE
# =================================================================
print("\n" + "=" * 50)
print("3. Birleştirme(Merge")
print("=" * 50)

pivot:pd.DataFrame = satislar.pivot_table(
    values="toplam",
    index="urun",
    columns="satis_temsilcisi",
    aggfunc="sum",
    fill_value=0
)
print(pivot)

# =====================================================
# 5. PRATIK ALISTIRMA
# =====================================================
"""
ALISTIRMA: Asagidaki veri setinde su sorulari cevaplayin:

1. En cok satis yapan temsilci kim? (toplam tutara gore)
2. Hangi urun en cok adet satilmis?
3. Mart ayinda yapilan satislarin toplam tutari nedir?
4. Her kategorinin ortalama birim fiyati nedir?
5. Birim fiyati 1000 TL'den yuksek urunlerin listesi (tekrarsiz)

Her soru icin Pandas koduyla cevap verin.
"""
