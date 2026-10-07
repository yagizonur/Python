"""
===========================================================
MODUL 4 - BÖLÜM 1: Matplotlib Temelleri
Konu: Çizgi, Sütun ve Dağılım Grafikleri, Stil Özelleştirme
===========================================================
"""
import matplotlib
matplotlib.use("Agg") # GUI penceresi açmadan dosyaya kaydetmek için

import matplotlib.pyplot as plt # Çizim yapmak için kullanacağımız fırça ve kalemlerç Genelde "plt" diye kısaltılır.
import numpy as np # Sayılarla kolay çalışmak için NumPy(bir önceki modül)

print("-- 1. Basit Çizgi Grafiği --")
aylar: list[str] = ["Oca","Sub","Mar","Nis","May","Haz"]
satislar: list[int] = [120,150,180,130,200,160]

plt.figure(figsize=(8,5)) # Önce boş bir resim kağıdı(tuval) açıyoruz. Boyutu genişlik 8, yükseklik 5 olsun
plt.plot(aylar,satislar,marker="o",color="royalblue",linewidth = 2) # Çizgi grafiğini çizeriz. "marker=o" çizgilerin kırılma noktalarına yuvarlak(nokta) koyar
plt.title("2026 İlk Yarı Satış Grafiği") # Grafiğin en üstündeki ana başlığı belirler.
plt.xlabel("Aylar") # Alt taraftaki yatay(X) eksene isim verir.
plt.ylabel("Satış(Adet)") # Sol taraftaki dikey(Y) eksene isim verir.
plt.grid(True,linestyle="--",alpha=0.7) # Okumayı kolaylaştırması için arka plana çizgiler(ızgara/kareli defter) ekler.
plt.tight_layout() # Başlıkların ve sayıların dışarı taşmaması için grafiği düzgünce sığdırır.
plt.savefig("modul_04_matplotlib/grafikler/01_cizgi_grafik.png",dpi=150) # Oluşturduğumuz kağıdı bilgisayara resim(.png) olarak kaydederiz.
plt.close() # Kağıdı çöpe atıp(hafızadan silip) yeni çizimler için yeri temizleriz.

print(" 01_cizgi_grafik.png kaydedildi.")

# ===========================================================
# 2. SÜTUN GRAFİĞİ(Bar Chart)
# ===========================================================
print("-- 2. Sütun Grafiği ---")

dersler: list[str] = ["Matematik","Fizik","İngilizce","Psikoloji","Fransızca"]
ortalamar: list[int] = [78, 86, 72, 90, 65]
renkler: list[str] = ["#e74c3c","#3498db","#2ecc71","#9b59d6","#f39c12"]

plt.figure(figsize=(8,5))
plt.bar(dersler,ortalamar,color=renkler, edgecolor="black",linewidth=0.5)
plt.title("Ders Bazlı Sınıf Ortalamaları")
plt.xlabel("Dersler")
plt.ylabel("Ortalama Not")
plt.ylim(0,100)

for i, ort in enumerate(ortalamar):
    plt.text(i, ort + 2, str(ort), ha="center",fontweight="bold",fontstyle="italic") # text() metodu istediğimiz x,y koordinatına yazı yazmamızı sağlar.

plt.tight_layout()
plt.savefig("modul_04_matplotlib/grafikler/02_sutun_grafik.png",dpi=150)
plt.close()

print("02_sutun_grafik.png kaydedildi.")

# ===========================================================
# 3. DAĞILIM GRAFİĞİ(Scatte Plot)
# ===========================================================
print("\n -- 3. Dağılım Grafiği ---")
np.random.seed(42)
calisma_saati: np.ndarray = np.random.uniform(1,10,30) # 1 ile 10 saat arasında değişen, 30 adet rastgele çalışma saati üretir. Uniform(Düzgün) dağılım demektir. 
sinav_notu: np.ndarray = calisma_saati * 8 + np.random.normal(0,5,30) # Gerçekçilik / Gürültü ekleme. calisma_saati * 8: İşin temel kuralı
                                                                      # Her 1 saatlik çalışma, nota 8 puan ekler. +np.random.normal(0,5,30) Gerçek hayatta herkesin çalıştığı saatin tam
                                                                      # karşılığını alamaz. Kimi sınav günü stres yapar vs kiminin şansı yaver gider yüksek alır.
                                                                      # Burada ortalaması 0, Standart sapması 5 olan bir normal(çan) dağılımı ekledik.
                                                                      # Yani öğrencinin notlarına rastgele olarak +5, -3 , +1, -6 gibi küçük şans/şanssızlık ekledik.
sinav_notu = np.clip(sinav_notu, 0, 100) # 0 ile 100 arasına sınırla
plt.figure(figsize=(8,5))
plt.scatter(calisma_saati,sinav_notu,
c = sinav_notu, # Noktaların rengi(color)
cmap="RdYlGn", # Kırmızı-Sarı-Yeşil renk haritası
s =80, # Nokta boyutu
edgecolors="black",
linewidth=0.5,
alpha=0.8)#scatter komutu verileri birbirine bağlamadan serbest noktalar halinde püskürtür.

plt.colorbar(label="SInav Notu")
plt.title("Çalışma Saati vs Sınav Notu")
plt.xlabel("Günlük Çalışma Saati")
plt.ylabel("Sınav Notu")
plt.grid(True,alpha=0.8)
plt.tight_layout()
plt.savefig("modul_04_matplotlib/grafikler/03_dagilim_grafik.png",dpi=150)
plt.close()

print(f"03_dagilim_grafik.png kaydedildi.")

# ===========================================================
# 4. GRAFİK ÖZELLEŞTİRME
# ===========================================================
# Birden fazla veri serisini aynı grafikte gösterme, 
# açıklama kutusu(legend), çizgi stilleri vs

print("\n-- 4.Grafik Özelleştirme -- ")
x: np.ndarray = np.arange(1,13)
takim_a: np.ndarray = np.array([45,52,48,61,85,84,91,56,23,70,65,56])
takim_b: np.ndarray = np.array([30,22,48,50,60,78,67,81,36,27,82,64])

plt.figure(figsize=(10,5))

plt.plot(x,takim_a, marker="o", linestyle="-", color ="#e73c3c",linewidth=2,label="Takım A")
plt.plot(x,takim_b, marker="s", linestyle="--", color ="#3498db",linewidth=2,label="Takım B")
plt.title("Takım Performans Karşılaştırması(Aylık)")
plt.xlabel("Ay")
plt.ylabel("Puan")
plt.xticks(x,["Oca","Sub","Mar","Nis","May","Haz",
              "Tem","Agu","Eyl","Eki","Kas","Ara"]) # X eksenindeki numaralar(1,2,3) yerine ayların adları yazar
plt.legend(loc="upper left") # Hangi rengin hangi takıma ait olduğunu gösteren açıklama kutusunu(lejant) sol üst köşeye koyar
plt.grid(True,linestyle=":",alpha=0.5)
plt.tight_layout()
plt.savefig("modul_04_matplotlib/grafikler/04_ozellestirilmis_grafik.png",dpi=150)
plt.close()

print("04_ozellestirilmis_grafik.png kaydedildi.")


# ===============================================================
# 5.YATAY SÜTUN GRAFİĞİ(Horizantal Bar)
# ===============================================================

print("\n--- 5. Yatay Sütun Grafiği ---")

diller: list[str] = ["Python","JavaScript","Java","C#","C++","Go"]
populerlik: list[int] = [92,88,76,70,65,45]
plt.figure(figsize=(8,5))
plt.barh(diller,populerlik,color="steelblue",edgecolor="black",linewidth=0.5)
plt.title("Proglama Dilleri Popülerlik Endeksi")
plt.xlabel("Popülerlik Skoru")
plt.xlim(0,100)

for i, val in enumerate(populerlik):
    plt.text(val + 1, i, str(val), va="center",fontweight="bold")

plt.tight_layout()
plt.savefig("modul_04_matplotlib/grafikler/05_yatay_sutun_grafik.png",dpi=150)
plt.close()

print("05_yatay_sutun_grafik.png kaydedildi.")

# =====================================================
# 6. PRATIK ALISTIRMA
# =====================================================
"""
ALISTIRMA: Asagidaki veriyi kullanarak iki farkli grafik olusturun:

sehirler = ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya"]
nufus_milyon = [16.0, 5.7, 4.5, 3.2, 2.6]
buyume_orani = [1.2, 0.8, 1.0, 1.5, 2.1]  # Yuzdesel buyume

Gereksinimler:
  1. Nufus icin bir sutun grafigi olusturun (her sutun farkli renkte).
  2. Buyume orani icin bir cizgi grafigi olusturun (marker ile).
  3. Her iki grafigi de dosyaya kaydedin.
"""