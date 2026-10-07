"""
=================================================
MODUL 1 - BÖLÜM 2: Parametrik Sorgular ve SQL Injection Önleme
Konu: Güvenli sorgu yazımı, SQL Injection tehlikesi, en iyi pratikler
=================================================
Bu ders SQL Injection'ın ne olduğunu, neden tehlikeli olduğunu ve Python'da nasıl önleneceğini gösterir.

ÖNEMLİ: f-string veya string birleştirme ile SQL sorgusu yazmak TEHLİKELİDİR!
"""
import sqlite3

# ===================================================================
# 1. SQL INJECTION NEDİR? 
# ===================================================================
# Aşağıdaki fonksiyon YANLIŞ ve TEHLİKELİ bir örnektir.
# def tehlikeli_giris(db_yolu: str, kullanici_adi: str, sifre: str) -> bool:
#     """
#     YANLIŞ ÖRNEK -- SQL INJECTION'a açık kod
#     Bu fonksiyonu ASLA production'da kullanmayın!
#     """
#     with sqlite3.connect(db_yolu) as conn:
#         cursor: sqlite3.Cursor = conn.cursor()

#         # TEHLİKELİ
#         sorgu: str = (
#             f"SELECT * FROM kullanicilar "
#             f"WHERE ad = '{kullanici_adi}' AND sifre = '{sifre}'"
#         )

#         print(f" Oluşturulan SQL: {sorgu}")

#         cursor.execute(sorgu)
#         sonuc: tuple | None = cursor.fetchone()
#         return sonuc is not None

# # Örnek veritabanı oluşturalım 
DB_YOLU: str = "modul_01_sqlite/guvenlik.demo.db"

# with sqlite3.connect(DB_YOLU) as conn:
#     cursor: sqlite3.Cursor = conn.cursor()
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS kullanicilar(
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             ad TEXT NOT NULL,
#             sifre TEXT NOT NULL,
#             rol TEXT DEFAULT 'kullanici'
#         )
# """)

#     # Örnek kullanıcı ekliyoruz(tablo boşsa)
#     cursor.execute("SELECT COUNT(*) FROM kullanicilar")
#     if cursor.fetchone()[0] == 0:
#         cursor.execute(
#             "INSERT INTO kullanicilar (ad, sifre, rol) VALUES(?,?,?)",
#             ("admin", "gizli123","yonetici")
#         )
#         conn.commit()

# # Normal giriş 
# print(f"-- Normal Giriş Denemesi --")
# sonuc: bool = tehlikeli_giris(DB_YOLU, "admin", "gizli123")
# print(f"Giriş Başarılı: {sonuc}\n")

# # SQL Injection Saldırısı
# print("---SQL Injection Saldırısı---")
# # Saldırgan şifre yerine: OR '1'='1
# # Oluşturulan SQL 
# # SELECT * FROM kullanicilar WHERE ad = 'admin' AND sifre = '' OR '1' = '1'
# # '1'='1' her zaman True olduğu için TÜM kayıtları döner.
# sonuc_hack: bool = tehlikeli_giris(DB_YOLU, "admin", "' OR '1' = '1")
# print(f"Giriş Başarılı(HACK!): {sonuc_hack}")
# print(f"Saldırgan şifre bilmeden giriş yaptı!\n")


# =====================================================================
# 2. GÜVENLİ YOL: PARAMETRİK SORGULAR
# =====================================================================
# Python'da ? placeholder kullanılır
# SQLite parametreleri otomatik olarak escape eder
# def guvenli_giris(db_yolu: str, kullanici_adi: str, sifre: str) -> bool:
#     """
#     DOĞRU ÖRNEK: Parametrik sorgu ile SQL Injection önleme
#     """ 

#     with sqlite3.connect(db_yolu) as conn:
#         cursor: sqlite3.Cursor = conn.cursor()

#         # ? placeholder --değer ayrı parametre olarak verilir. 
#         # SQlite bu değerleri otomatik escape eder
#         cursor.execute(
#             "SELECT * FROM kullanicilar WHERE ad = ? AND sifre = ?",
#             (kullanici_adi, sifre)
#         )
#         sonuc: tuple | None = cursor.fetchone()
#         return sonuc is not None

# print(f"Güvenli Giriş(Normal)")
# sonuc_normal: bool = guvenli_giris(DB_YOLU, "admin","gizli123")
# print(f" Giriş Başarılı: {sonuc_normal}\n")

# print("Güvenli Giriş(Saldırı Denemesi)")
# sonuc_guvenli: bool = guvenli_giris(DB_YOLU, "admin", "' OR '1' = '1")
# print(f" Saldırı Başarısız - Parametrik Sorgu Korudu: {sonuc_guvenli}")

# =====================================================================
# 3. PARAMETRİK SORGU ÇEŞİTLERİ
# =====================================================================
# def parametrik_sorgu_ornekleri(db_yolu: str) -> None:
#     """Farklı parametrik sorgu yöntemlerini gösterir"""

#     with sqlite3.connect(db_yolu) as conn:
#         conn.row_factory = sqlite3.Row
#         cursor: sqlite3.Cursor = conn.cursor()

#         # Örnek tablo ve veriler 
#         cursor.execute("""
#         CREATE TABLE IF NOT EXISTS urunler(
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             ad TEXT NOT NULL,
#             kategori TEXT,
#             fiyat REAL,
#             stok INTEGER DEFAULT 0
#         )
# """)

# # Tablo boşsa veri ekle
#     # cursor.execute("SELECT COUNT(*) FROM urunler")
#     # if cursor.fetchone()[0] == 0:
#     #     urunler: list[tuple[str, str, float, int]] = [
#     #         ("Laptop","Elektronik",35000.0, 15),
#     #         ("Mouse","Elektronik",750.0, 100),
#     #         ("Klavye","Elektronik",3245.0, 20),
#     #         ("Monitor","Elektronik",18495.0, 67),
#     #         ("Çanta","Aksesuar",1000.0, 500),
#     #         ("Pantolon","Giyim",2000.0, 68),
#     #     ]
#     #     cursor.executemany(
#     #         "INSERT INTO urunler(ad, kategori, fiyat, stok) VALUES (?,?,?,?)",
#     #         urunler
#     #     )

#         # conn.commit()

#         # Yöntem 1: ? placeholder(tuple ile)
#         print("Yöntem 1: ? placeholder")
#         cursor.execute(
#             "SELECT * FROM urunler WHERE fiyat > ? AND kategori = ?",
#             (3000,"Elektronik")
#         )

#         for urun in cursor.fetchall():
#             print(f"  {urun["ad"]}: {urun["fiyat"]:.2f} TL")

#         # LIKE ile arama
#         print(f"\n---LIKE ile arama---")
#         arama_terimi: str = "Mo"
#         cursor.execute(
#             "SELECT * FROM urunler WHERE ad LIKE ?",
#             (f"%{arama_terimi}%",)
#         )

#         for urun in cursor.fetchall():
#             print(f"Bulunan: {urun["ad"]}")

#         print("\n-- IN ile Çoklu Değer --")
#         aranan_kategoriler: list[str] = ["Elektronik","Aksesuar"]
#         placeholder: str = ",".join("?" * len(aranan_kategoriler))
#         cursor.execute(
#             f"SELECT kategori, COUNT(*) as adet, AVG(fiyat) as ort_fiyat "
#             f"FROM urunler WHERE kategori IN({placeholder}) GROUP BY kategori",
#             aranan_kategoriler
#         )        

#         for row in cursor.fetchall():
#             print(f" {row["kategori"]}: {row['adet']} urun, "
#                   f"Ortalama Fiyat: {row['ort_fiyat']:.2f} TL"
#                   )
# parametrik_sorgu_ornekleri(DB_YOLU)


# =====================================================================
# 4. TOPLU İŞLEMLER(Bacth Operations)
# =====================================================================
def toplu_urun_ekle(db_yolu: str, urunler: list[dict[str, str | float | int]]) -> int:
    """
    Birden fazla ürünü tek seferde ekler.

    Args: 
        db_yolu: Veritabanı dosya yolu
        urunler: Eklenecek ürünlerin listesi
    Returns:
        Eklenen kayıt listesi
    """
    with sqlite3.connect(db_yolu) as conn:
        cursor: sqlite3.Cursor = conn.cursor()

        # Dict listesinden tuple listesine dönüştürme
        veri: list[tuple[str, str, float, int]] = [
            (str(u["ad"]), str(u["kategori"]), float(u["fiyat"]), int(u["stok"]))
            for u in urunler
        ]

        cursor.executemany(
            "INSERT INTO urunler(ad, kategori, fiyat, stok) VALUES(?,?,?,?)",
            veri
        )

        conn.commit()
        return len(veri)

yeni_urunler: list[dict[str, str | float | int]] = [
    {"ad": "Kulaklık", "kategori": "Elektronik", "fiyat":860.0, "stok":100},
    {"ad": "Gaming Mouse", "kategori": "Elektronik", "fiyat":1850.0, "stok":20},
]

eklenen: int = toplu_urun_ekle(DB_YOLU, yeni_urunler)
print(f"\n{eklenen} yeni ürün eklendi.")

# =====================================================
# 5. OGRENCIYE OZET TABLO
# =====================================================
"""
PARAMETRIK SORGU KURALLARI:

| Kural | Ornek |
|-------|-------|
| Degerlerde ? kullan          | WHERE ad = ?                    |
| Tuple olarak parametre ver   | cursor.execute(sql, (deger,))   |
| Tek deger icin bile tuple    | (deger,) -- virgulu unutma!     |
| String birlestirme YAPMA    | f"...{deger}..." -- TEHLIKELI   |
| executemany toplu islem icin | cursor.executemany(sql, liste)  |
| :isim ile dict kullanilabilir| WHERE ad = :ad, {"ad": "Ali"}   |
"""