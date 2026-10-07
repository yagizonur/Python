"""
=====================================================================
MODUL 3 - BÖLÜM 2: NumPy matematiksel ve istatistiksel işlemler
Konu: Vektörel İşlemler, broadcasting, istatistikler ve filtreleme 
========================================================================
"""

import numpy as np

print("--- 1. Vektörel İşlemler ---")
a: np.ndarray = np.array([1,2,3,4])
b: np.ndarray = np.array([10,20,30,40])

print(f"a: {a}")
print(f"b: {b}")

# Matematiksel operatorler eleman bazı(element-wise) çalışır
print(f"a + b: {a + b}") # Döngü kurmadan a ve b dizilerindeki aynı sıradaki elemanları tek seferde karşılıklı toplar.
print(f"a * b: {a * b}")
print(f"b / a: {b / a}")
print(f"a ** 2(Karesi): {a ** 2}")

# =============================================================================
# HAZIR MATEMATİKSEL FONKSİYONLAR(Universal Functions - ufuncts)
# =============================================================================

print(f"--- 2. Matematiksel Fonksiyonlar ---")
sayilar: np.ndarray = np.array([1,4,9,16])
print(f"Sayılar: {sayilar}")

print(f"Karekökler: {np.sqrt(sayilar)}") 

# Eksponansiyonel (e ^ x) ve Logaritma(ln) 
print(f"e^x değerleri: {np.exp(np.array([1,2]))}")
print(f"Logaritma (Taban e): {np.log(np.array([2.718,10]))}")

# =============================================================================
# 3. BROADCASTING(YAYMA)
# =============================================================================
# Farklı boyutlardaki dizilerin matematiksel işlemlere sokulabilmesidir. 
# En basit örnek: Bir diziyle bir sabiti(skaler) toplamak/çıkarmak

print(f"\n ---3. Broadcasting(Yayma) ---")
dizi: np.ndarray = np.array([1,2,3])
print("Dizi: ",dizi)

# Sabitle çarpma(Her eleman 10 ile çarpılır)
print(f"Dizi * 10: {dizi * 10}") # Dizi içindeli elemanların TAMAMINI 10 ile çarpara(Buna broadcasting/yayma denir)

# Martis ve Dizisi İşlemi 
# 3 x 3 bir matrise 1 x 3'lük bir satırı ekleyelim. Satır her satıra tek tek uygulanır
matris: np.ndarray = np.array([
    [10,20,30],
    [40,50,60],
    [70,80,90],
])

satir: np.ndarray = np.array([1,2,3])

print(f"Matris:\n {matris}")
print(f"Satır(Eklenecek): {satir}")
print(f"Sonuç(Matris + Satır):\n{matris + satir}") # Satır dizisini, matrisin içindeki HER BİR SATIRLA ayrı ayrı toplar.


# =============================================================================
# 4. TEMEL İSTATİSTİKSEL FONKSİYONLAR VE AXIS MANTIĞI
# =============================================================================
print("\n-- 4. İstatistiksel Fonksiyonlar ve Axis ---")
puanlar: np.ndarray = np.array([
    [80,90,85], # 1. Öğrenci(Mat, Fiz, Kim)
    [40,70,25], # 2.Öğrenci
    [100,58,65], # 3.Öğrenci
])

print(f"Puanlar:\n {puanlar}")

# Genel İstatistikler
print(f"Genel Toplam: {puanlar.sum()}") 
print(f"Genel Ortalama: {puanlar.mean():.2f}")
print(f"En Yüksek Not: {puanlar.max()}")

# Axis Mantığı:
# axis = 0: Sütun bazlı işlem yapar(Dikey yukarı-aşağı) -> Çok değerli
# axis = 1: Satır bazlı işlem yapar(Yatay soldan - sağa) -> Çok değerli

# Derslerin ortalamaları(Sütunlar Matematik, Fizik, Kimya)
ders_ortalamalari = puanlar.mean(axis=0) # axis = 0: Sütunlara(yukarıdan aşağıya doğru) göre ortalama hesaplar.
print(f"\nDers Ortalamaları(Mat, Fiz, Kim): {ders_ortalamalari.round(2)}")

ogrenci_ortalamalari = puanlar.mean(axis=1) # axis = 1: Satırlara(soldan sağa doğru) göre ortalama hesaplar.
for i, ort in enumerate(ogrenci_ortalamalari,1):
    print(f" {i}. öğrencinin ortalaması: {ort:.2f}")

# =============================================================================
# 5. BOOLEAN INDEXING(MANTIKSAL FİLTRELEME)
# =============================================================================
print("\n-- 5. Mantıksal Filtreleme ---")
notlar: np.ndarray = np.array([45,30,54,66,67,89])
print(f"Notlar: {notlar}")

maske: np.ndarray = notlar >= 50 # Dizideki her notu tek tek kontrol eder. Eğer 50 veya daha büyükse True değilse False yazar ve yeni bir liste oluşturur
print(f"Maske(>= 50): {maske}")


# Bu maskeyi diziye indeks olarak vererek sadece True olanları çeker.
gecen_notlar: np.ndarray = notlar[maske] 

# Kısa yazım: gecen_notlar = notlar[notlar >= 50]
print(f"Geçen notlar: {gecen_notlar}")

# Birden fazla koşul 
# Ve(&) veya(|) operatorleri kullanılabilir. Her koşul parantez içinde yazılmalıdır
orta_notlar: np.ndarray = notlar[(notlar >= 50) & (notlar <= 80)]
print(f"50 ile 80 arasındaki notlar: {orta_notlar}")

"""
ALISTIRMA: Bir sirketin 5 calisaninin son 3 aydaki satis miktarlari matris olarak verilmistir.
Satirlar calisanlari, sutunlar ise aylari temsil etmektedir.

satislar = np.array([
    [12000, 15000, 14000],
    [9000,  11000, 10500],
    [18000, 20000, 22000],
    [15000, 13000, 16000],
    [8000,  8500,  9000]
])

Gereksinimler:
  1. Her calisanin 3 aylik toplam satis tutarini bulun.
  2. Sirketin 3 aylik genel satis ortalamasini hesaplayin.
  3. Aylik satis ortalamasindan yuksek satis yapan calisanlarin (toplam satisi baz alarak) 
     toplam satislarini filtreleyin.
"""
print("\n--- Alistirma Cozumu ---")

satislar = np.array([
    [12000, 15000, 14000],
    [9000,  11000, 10500],
    [18000, 20000, 22000],
    [15000, 13000, 16000],
    [8000,  8500,  9000]
])

# 1. Her calisanin 3 aylik toplam satisi (Satir bazli: axis=1)
calisan_toplamlari: np.ndarray = satislar.sum(axis=1)
print(f"Calisanlarin Toplam Satislari: {calisan_toplamlari}")

# 2. Genel satis ortalamasi (Her ay icin sirket ortalamasini bulup toplam satislarin ortalamasina bakmak)
# Calisan basina ortalama satis toplamini bulalim:
sirket_toplam_ortalamasi = calisan_toplamlari.mean()
print(f"Calisan Basina Dusecek Ortalama Toplam Satis: {sirket_toplam_ortalamasi:,.2f} TL")

# 3. Ortalamanin uzerinde satis yapanlari filtreleme
basarili_calisanlar: np.ndarray = calisan_toplamlari[calisan_toplamlari > sirket_toplam_ortalamasi]
print(f"Basarili Calisanlarin Toplam Satislari: {basarili_calisanlar}")
