"""
===================================================================
MODUL 4 - BOLUM 2: Matplotlib İleri Konular
Konu: Subplots, histogram, pasta grafiği, NumPy entegrasyonu

- fig(figure): Çizim yapacağımız boş A4 kağıdı
- ax(Axes): Kağıdın üzerine çizdiğimiz çerçeveler(grafik alanları)
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

# =========================================================
# 1. SUBPLOTS - ÇOKLU GRAFİK PANELİ
# =========================================================
# Matplotlib'de fig, axes = plt.subplots(satir,sütun) ile yapılır
print("---- 1. Subplots(Çoklu Grafik Paneli) ---- ")
fig,axes = plt.subplots(1,3,figsize=(15,5)) # Yan yana 3 tane grafik çizebilmek için boş bir kağıt(fig) ve üzerinde 3 tane çerçeve(axes) oluşturur
# axes artık 3 elemanlı bir dizi: axes[0] birinci çerçeve, axes[1] ikinci, axes[2] üçüncü

# Sol Grafik: Çizgi
x: np.ndarray = np.arange(1,8)
axes[0].plot(x,x ** 2, marker="o", color="#e74c3c",linewidth=2) # En soldaki çerçeveye(index 0) çizgi grafiği çizer
axes[0].set_title("Karesi (x²)")
axes[0].set_xlabel("x")
axes[0].set_xlabel("x²")
axes[0].grid(True,alpha=0.3)

# Orta Grafik: Sütun
kategoriler: list[str] = ["Elektronik","Aksesuar","Giyim","Parfüm"]
degerler: list[int] = [25,40,30,55]
axes[1].bar(kategoriler,degerler,color=["#3498db","#2ecc71","#9b59d6","#f39c12"])
axes[1].set_title("Kategori Bazlı Değerler")
axes[1].set_ylabel("Değer")

# Sağ grafik : Dağılım
np.random.seed(42)
axes[2].scatter(

    np.random.rand(30), np.random.rand(30), # Grafikteki noktaların X ve Y koordinatlarıdır. 0 ile 1 arasında rastgele 30 adet X değeri ve 30 adet Y değeri üretir. Toplamda 30 adet nokta çizilir.
    c=np.random.rand(30),cmap="viridis",s=100,alpha=0.7 # c=np.random.rand(30): Noktaların renklerini(color) belirler. Her bir nokta için 0 ile 1 arasında rastgele bir renk değeri atar.
) # cmap ="viridis": Kullanılacak renk plaretini seçer(viridis). mor mavi, yeşil e sarı tonlarını barındırır.

axes[2].set_title("Rastgele Dağılım")
fig.suptitle("Üç Farklı Grafik Türü",fontsize=14,fontweight="bold")
plt.tight_layout()
plt.savefig("modul_04_matplotlib/grafikler/07_subplots.png",dpi=150)
plt.close()

print("07_subplots.png kaydedildi.")

# =========================================================
# 2. HISTOGRAM(GERÇEK VERİ İLE)
# =========================================================
# Verilerin dağılımını görmek için kullanılır.
print("\n-- 2. Histogram(Gerçek Öğrenci Verisi) ---")

import csv

gercek_notlar_yolu: str = "veri_setleri/ogrenci_notlari.csv"
notlar_listesi: list[float] = []

try:
    with open(gercek_notlar_yolu,"r",encoding="utf-8") as dosya:
        okuyucu = csv.DictReader(dosya)
        for satir in okuyucu:
            notlar_listesi.append(float(satir["Gecme_Notu"]))
except FileNotFoundError:
    print(f"HATA: '{gercek_notlar_yolu}' bulunamadı! Örnek rastgele veri üretiliyor...")
    np.random.seed(42)
    notlar_listesi = np.clip(np.random.normal(loc=70,scale=12,size=300),0,100).tolist()

notlar: np.ndarray = np.array(notlar_listesi)
plt.figure(figsize=(8,5))
plt.hist(
notlar,
bins=15, #Tüm notları 15 farklı dilime(kutucuğa) böler.
color="steelblue",
edgecolor="black",
alpha=0.8
)

plt.axvline(notlar.mean(), color="red", linestyle="--",linewidth=2,
            label=f"Sınıf Ortalaması: {notlar.mean():.1f}") # grafik üzerine yukarıdan aşağıya dik(dikey) bir çizgi çizmek için kullanılır.
plt.title("Gerçek Öğrenci Not Dağılımı(Geçme Notu)")
plt.xlabel("Not (0-100)")
plt.ylabel("Öğrenci Sayısı")
plt.legend()
plt.tight_layout()
plt.savefig("modul_04_matplotlib/grafikler/08_histogram.png",dpi=150)
plt.show()
plt.close()

print("08_histogram.png kaydedildi.")