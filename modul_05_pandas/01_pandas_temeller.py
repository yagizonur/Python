"""
=================================================================================================================================
    MODUL 5 - BÖLÜM 1: Pandas Temelleri
    Konu: DataFrame oluşturma, temel işlemler, sütun seçme
=================================================================================================================================
"""

import pandas as pd # Veri analizi ve Excel benzeri tablolarla çalışmak için Pandas kütüphanesni çağırdık.

# ===============================================================================================================
# 1. DATAFRAME OLUŞTURMA
# ===============================================================================================================

print("--- 1. DataFrame Oluşturma ---")

# Yöntem 1: Dictionary'den(en yaygın)
veri: dict[str, list] = {
    "ad":["Salman","Ayda","Arda","Onur"],
    "yas":[24,19,26,17],
    "sehir":["Sivas","Balıkesir","Adıyaman","Sivas"],
    "maas":[45000,13000,67000,145000],
    "departman":["Yazilim","Pazarlama","Yazilim","Finans"]
}

df: pd.DataFrame = pd.DataFrame(veri) # Elimizdeki sözlük verisini(dictionary) Pandas'ın anlayacağı 'DataFrame' adında bir tabloya dönüştürürüz.
print(df)
print(f"\nSatır Sayısı:  {len(df)}") # Tablonun kaç tane satırdan oluştuğunu buluruz.
print(f"Sütun Sayısı: {len(df.columns)}")
print(f"Boyut(Satır, Sütun): {df.shape}")


# Yöntem 2: Liste of dict'lerden
print("\n--- Liste of Dict'lerden ---")
kayitlar: list[dict[str, str | int]] = [
    {"urun":"Laptop", "fiyat":35000, "stok":15},
    {"urun":"Klavye", "fiyat":1500, "stok":120},
    {"urun":"Mouse", "fiyat":850, "stok":75},
]

df_urun: pd.DataFrame = pd.DataFrame(kayitlar) # listeleri kullanarak da tablo(DataFrame) oluşturabiliriz.
print(df_urun)

# ===============================================================================================================
# 2. TEMEL BİLGİ METOTLARI
# ===============================================================================================================
print("\n--- 2. DataFrame Bilgileri ---")

# İlk/Son N Satır(Varsayılan 5)
print("İlk 3 satir:")
print(df.head(3)) # Büyük tablodan sadece en baştaki 3 satırını gösterir. (Önizleme yapmak için kullanılır)

print("\nSon 2 Satır:")
print(df.tail(2)) 

# Veri tipleri
print(f"\nVeri Tipleri:\n{df.dtypes}")

print("\nGenel Bilgi:")
print(df.info())

print("\nIstatistiksel Özet: ")
print(df.describe()) # Tablodaki SAYISAL sütunların(yas, maas vb) ortalamasını , en büyük/küçük değerini otomatik hesaplar.


# =============================================================================================================== 
# 3. SÜTUN SEÇME
# =============================================================================================================== 
print("\n --- 3. Sütun Seçme ---")

# Tek sütun(Series döner)
adlar: pd.Series =df["ad"] # Sadece "ad" isimli sütunu koparıp alır. Pandas'ta tek bir sütuna "Series" adı verilir.
print(f"Adlar:\n{adlar}\n")
print(f"Tip: {type(adlar)}") # pandas.Series

secim:pd.DataFrame = df[["ad","maas"]] # İki köşeli parantez kullanarak birden fazla sütunu alırız ve yeni bir tablo elde ederiz.
print(f"\nAd ve Maaş:\n{secim}")


# =============================================================================================================== 
# 4. SATIR SEÇME(loc ve iloc)
# =============================================================================================================== 
print("\n--- 4.Satır Seçme ---")

# iloc: Pozisyon bazlı
print(f"İlk satır (iloc[0]):\n{df.iloc[0]}\n") # iloc(index location): Matematikteki gibi sıra numarası ile o satırı getirir(0 = İlk satır)
print(f"3. satır, 'ad' sütunu: {df.iloc[2,0]}") # (Satır numarası, sütun numarası) şeklinde spesifik bir hücreyi bulur(Arda)

# loc: Etiket bazlı
print(f"\nİlk 3 satır, belirli sütunlar:")
print(df.loc[0:2, ["ad","sehir","maas"]]) # loc(location): Satır numarası ve SÜTUN İSMİ kullanılarak arama yapar.

# =============================================================================================================== 
# 5. YENİ SÜTUN EKLEME
# =============================================================================================================== 
print("\n --- 5. Yeni Sütun Ekleme ---")

df["yillik_maas"] = df["maas"] * 12 # 'yillik_maas' adında yeni bir sütun açar. Maas sütunundaki TÜM verileri aynı anda(dongusuz) 12 ile çarpar.
df["vergi"] = df["maas"] * 0.15 # Yüzde 15 vergiyi otomatik hesaplar.
df["net_maas"] = df["maas"] - df["vergi"]

print(df[["ad","maas","yillik_maas","vergi","net_maas"]])

# Koşullu Sütun 
df["maas_seviye"] = df["maas"].apply(#apply() fonksiyonu sütundaki tüm satırlara tek tek kural uygular(maaşı 60000'den büyüksek 'Yüksek' yaz vb.)
lambda m: "Yuksek" if m > 60000 else "Normal"
)

print(f"\n{df[["ad","maas","maas_seviye"]]}")

# =============================================================================================================== 
# 6. TEMEL İSTATİSTİKLER
# =============================================================================================================== 
print("\n--- 6. Temel İstatistikler ---")

print(f"Toplam Maaş: {df["maas"].sum():,.0f} TL")
print(f"Ortalama Maaş: {df["maas"].mean():,.0f} TL")
print(f"En Yüksek Maaş: {df["maas"].max():,.0f} TL")
print(f"En Düşük Maaş: {df["maas"].min():,.0f} TL")
print(f"Medyan Maaş: {df["maas"].median():,.0f} TL")
print(f"Standart Maaş: {df["maas"].std():,.0f} TL")

# Benzersiz Değerler
print(f"\nŞehirler: {df['sehir'].unique().tolist()}")
print(f"Benzersiz şehir sayısı: {df['sehir'].nunique()}")

# Değer Sayıları
print(f"\nŞehir Dağılımı:\n{df['sehir'].value_counts()}") # Hangi şehirden(değerden) kaç tane olduğunu sayar

# =============================================================================================================== 
# 7. SIRALAMA
# ===============================================================================================================
print("\n--- 7. Sıralama ---")

# Maaşa göre artan
print("Maaşa göre(artan):")
print(df[['ad',"maas"]].sort_values("maas"))

# Maaşa göre azalan
print("Maaşa göre(artan):")
print(df[['ad',"maas"]].sort_values("maas", ascending=False))

# Birden fazla sütuna göre
print("\nŞehir + Maas'a göre:")
print(df[["ad","sehir","maas"]].sort_values(["sehir","maas"], ascending=[True,False]))

# =============================================================================================================== 
# 8. GERÇEK DÜNYA VERİSİ OKUMA(CSV)
# ===============================================================================================================
print(f"\n--- 8. Gerçek Veri Seti Okuma(CSV) ---")

gercek_csv_yolu: str = "veri_setleri/satis_verileri.csv"

try:
    df_satislar: pd.DataFrame = pd.read_csv(gercek_csv_yolu) # Bilgisayardaki CSV dosyasını(Excel) okuyup devasa bir Pandas tablosuna dönüştürürüz.
    print(f"Büyük veri seti başarıyla okundu! Toplam {len(df_satislar)} satır, {len(df_satislar.columns)} sütun")

    print("\nİlk 5 Satış Kaydı Önizleme:")
    print(df_satislar.head()) # Tablonun ilk 5 satırını gösterir. 


    print("\nİstatistiksel Özet(Birim Fiyat, Adet, Toplam Tutar):")
    print(df_satislar.describe()) # Binlerce satırın ortalamasını saniyeler içinde hesaplar.

except FileNotFoundError:
    print(f"HATA: '{gercek_csv_yolu}' bulunamadı. Lütfen ana dizinde 'veri_setleri' klasörünün varlığından emin olun.")