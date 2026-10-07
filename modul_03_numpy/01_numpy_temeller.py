"""
=====================================================================
MODUL 3: NumPy Temeleri ve Diziler(Arrays)
Konu: np.ndrarray, dizi oluşturma, slicing ve boyut işlemleri

NumPy(Numerical Python), Python programlama dilinde büyük ve çok boyutlu diziler, 
matrisler ile yüksek performanslı matematiksel işlemler yapmayı sağlayan açık kaynaklı 
bir bilimsel hesaplama kütüphanesidir.

ndarray nesnesi: Standart Python listelerine göre daha az bellek harcayan ve aynı türden verileri saklayan
güçlü bir çok boyutlu dizi yapısı sunar. 

Kullanım Alanları:

Veri Bilimi: Verilerin temizlenmesi, dönüştürülmesi ve analiz edilmesi süreçlerinde temel oluşturur.

Yapay Zeka ve Makine Öğrenmesi(AI and Machine Learning): Model eğitiminde kullanılan girdilerin, ağırlıkların
ve matrislerin işlenmesinde aktif rol oynar.
========================================================================
"""

import numpy as np # NumPy kütüphanesini içeri alıyoruz. Uzun yazmamak için genelde "np" kısatlması kullanılır

print("--- 1. Basit Dizi Oluşturma ---")

# Standart Python listesini, matematikteki çok hızlı işlenen "vektör/dizi" formuna dönüştürür.
# Vektör: NumPy kütüphanesinde tek boyutlu 1D dizilerdir. Matematiksel ve fizik dünyasında hem büyüklüğü(şiddeti) hem de yönü olan
# çizgileri temsil eder. Programlamada yan yana dizilmiş bir sayı listesi olarak kabul edilirler.

liste: list[int] = [10,20,30,40,50]
dizi: np.ndarray = np.array(liste)

print(f"Liste: {liste} (Tip: {type(liste)})")
print(f"Dizi: {dizi} (Tip: {type(dizi)})")
print(f"Dizinin veri tipi(type): {dizi.dtype}")

matris_listesi: list[list[int]] = [[1,2,3],[4,5,6]] # İç içe listeler satırlar ve sütunlar demektir. 
matris: np.ndarray = np.array(matris_listesi) # Excel tablosuna benzeyen, satırı ve sütun olan 2 boyutlu bir yapı(matris) oluşturduk
print("\n2 Boyutlu Dizi(Matris):")
print(matris)


# =======================================================================
# 2. HAZIR METOTLAR İLE DİZİ OLUŞTURMA 
# =======================================================================

print("\n--- Hazır Metotlar ile Dizi Oluşturma ---")

# Sıfırlarla dolu dizi(Varsayılan tipi float'tır)
sifirlar: np.ndarray = np.zeros(5) # İçine peş peşe 5 adet 0 yazılmış bir dizi hazırlar(Sıfırdan başlamak istediğimizde)
print(f"np.zeros(5): \n{sifirlar}")


# Birler ve belirli tiplerle dizi
birler_2d: np.ndarray = np.ones((2,4), dtype=int) # İçerisinde sadece 1'lerin olduğu, 2 satır 4 sütunluk tablo oluşturur. dtype = int data tipi int olsun demekttir.
print(f"\nnp.ones((2,4), dtype=int):\n{birler_2d}")

ardisik:np.ndarray = np.arange(0,11,2) # 0'dan başla 10'a kadar 2'şer 2'şer
print(f"\nnp.arange(0,10,2):\n{ardisik}") 

esit_aralik: np.ndarray = np.linspace(0,1,5) # 0'dan 1'e kadar olan aralığı(0 ile 1 dahil) tam eşit 5 parçaya bölecek sayıları bulur
print(f"\nnp.linspace(0,1,5): {esit_aralik}")

# Rastgele sayılarlar dizi oluşturma(0-1 arasında) 
rastgele: np.ndarray = np.random.rand(2,3) # 2 satır ve 3 sütundan oluşan, içine rastgele ondalıklı sayıların yerleştirildiği tablo
print(f"\nnp.random(2,3): {rastgele}")

# =======================================================================
# 3. DİZİ ÖZELLİKLERİ VE BOYUT DEĞİŞİMİ(shape, reshape)
# =======================================================================
print("\n-- 3. Dizi Özellikleri ve ReShape ---")

dizi_3d: np.ndarray = np.array([
 [[1,2],[3,4]],
 [[5,6],[7,8]],
])

print(f"Boyut sayısı(ndim): {dizi_3d.ndim}")
print(f"Boyut şekli(shape): {dizi_3d.shape}")
print(f"Toplam eleman(size): {dizi_3d.size}")

# Reshape: Eleman sayısını değiştirmeden boyutları yeniden şekillendirme
# Örneğin elimizde 12 elemanlı 1D dizi olsun
dizi_1d: np.ndarray= np.arange(12)
print(f"\n1D Dizi(12 Eleman): \n{dizi_1d}")

# Bunu 3 satır ve 4 sütunlu 2D diziye çevirelim:
dizi_2d: np.ndarray = dizi_1d.reshape(3,4) # Yan yana duran 12 elemanı bozmadan 3 satırlık 4 sütunluk bir tablo haline getirir.
print(f"Reshape(3,4):\n{dizi_2d}")

# -1 parametresi: NumPy'ın diğer boyutu otomatik hesaplamasını sağlar.
otomatik_reshape: np.ndarray = dizi_1d.reshape(2,-1) # -1 yadığımız yere hangi sayının gelmesi gerektiğini Python kendisi hesaplar.
print(f"Reshape(2,-1):\n{otomatik_reshape}")

# =======================================================================
# 4. INDEKSLEME VE DİLİMLEME(slicing)
# =======================================================================
print("\n-- 4. Indeksleme ve Slicing ---")

sayilar: np.ndarray = np.array([10,20,30,40,50,60])

print(f"Son eleman: {sayilar[-1]}")
print(f"Sondan ikinci eleman: {sayilar[-2]}")

# Dilimleme(Slicing): [baslangic: bitis: adim]
print(f"Indeks 1'den 4'e kadar(4 dahil değil): {sayilar[1:4]}")
print(f"İlk 3 eleman: {sayilar[:3]}")
print(f"Indeks 2'den sonuna kadar: {sayilar[2:]}")
print(f"2'şer adımla git: {sayilar[::2]}")

matris_ornek: np.ndarray = np.array([
    [10,20,30],
    [40,50,60],
    [70,80,90],
])

print(f"Örnek matris:\n {matris_ornek}")
print(f"İlk satır: {matris_ornek[0,:]}")
print(f"İkinci sütun: {matris_ornek[:,1]}")

# Alt matris seç(sol üstteki 2x2'lik alan)
print(f"2x2 alt matris:\n{matris_ornek[0:2,0:2]}")


# =======================================================================
# 5. BELLEK YÖNETİMİ: COPY VS VIEW
# =======================================================================
# NumPy'da dilimleme yaptığınızda gerçek veri kopyalanmaz, bir View(görünüm) oluşturulur 
# orijinal verinin bozulmaması isteniyorsa .copy() kullanılmalıdır.

print("\n--5. Copy vs View Mantığı ---")
orijinal: np.ndarray = np.array([1,2,3,4,5])

dilim: np.ndarray = orijinal[0:3] # NumPy dizilerinde bu işlem hızlı olsun diye yeni kopya üretmez, aynı veriye "başka pencereden" bakar

dilim[0] = 99
print(f"Dilim güncellendikten sonra orijinal: {orijinal}")  # orijinal de [99  2  3  4  5] oldu!

# Güvenli Kopyalama
orijinal2: np.ndarray = np.array([1,2,3,4,5])
kopya: np.ndarray = orijinal2[0:3].copy() # Gerçekten bağımsız yeni bir hafıza alanı açıp verileri kopyalar(diğerini bozmaz)

kopya[0] = 99
print(f"Kopya güncellendikten sonra orijinal2: {orijinal2}")

# ===================================================
# 6. PRATIK ALIŞIRMA
# ===================================================
"""
ALISTIRMA: NumPy dizileri uzerinde asagidaki adimlari izleyin:

  1. 1 ile 16 (dahil) arasindaki tamsayilardan olusan 1D bir dizi olusturun.
  2. Bu diziyi 4 satir ve 4 sutunlu (4x4) bir matrise donusturun.
  3. Bu matrisin tam ortasindaki 2x2'lik alt matrisi secip ekrana yazdirin:
     [ [ 6,  7],
       [10, 11] ]
  4. Alt matrisi degistirdiginizde ana matrisin etkilenmemesi icin kopyalama yontemini kullanin.
"""
