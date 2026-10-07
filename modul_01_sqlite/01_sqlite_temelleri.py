"""
=====================================================================
BÖLÜM 1: SQLite Temelleri
Konu: Bağlantı, tablo oluşturma, INSERT, SELECT, UPDATE, DELETE

1. CREATE - Oluşturma
2. INSERT - Veri Ekleme
3. SELECT - Veri Okuma
4. UPDATE - Güncelleme
5. DELETE - Silme

with bloğunu odaya girerken ışığı açıp, çıkarken ışığı kapatmak gibi düşünebiliriz. Kaynakları otomatik kapatır.
"""
import sqlite3
from pathlib import Path

# ====================================================================
# 1. VERİTABANI BAĞLANTISI
# ====================================================================
# Ptyhon'da CREATE DATABASE komutuna gerek yoktur, dosya yoksa oluşturulur.

# Veritabanı dosyasının yolunu belirleyelim
DB_YOLU: str = "modul_01_sqlite/okul.db"

# Bağlantı oluşturma --dosya yoksa oluşturulur
conn:sqlite3.Connection = sqlite3.connect(DB_YOLU)
# print(f"Veritabanı bağlantısı kuruldu: {DB_YOLU}")
# print(f"Dosya mevcut mu: {Path(DB_YOLU).exists}")

cursor: sqlite3.Cursor = conn.cursor() # Cursor'u bir kalem ucu gibi düşünebilirsiniz, bizim yerimize yazıp silecek

# # ====================================================================
# # 2. TABLO OLUŞTURMA(CREATE TABLE)
# # ====================================================================

# cursor.execute("""
#     CREATE TABLE IF NOT EXISTS ogrenciler(
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     ad TEXT NOT NULL,
#     soyad TEXT NOT NULL,
#     yas INTEGER,
#     bolum TEXT DEFAULT 'Belirsiz',
#     ortalama REAL DEFAULT 0.0
#     )
# """)

# # SQL Server'daki IDENTITY = SQlite'taki AUTOINCREMENT
# # SQL Server'daki NVARCHAR = SQLite'taki TEXT
# # SQL Server'daki FLOAT = SQLite'taki REAL

# conn.commit() # DDL işlemlerinde commit
# print("'ogrenciler' tablosu oluşturuldu(veya zaten vardı)")

# # ====================================================================
# # 3. VERİ EKLEME(INSERT)
# # ====================================================================

# # Tek kayıt ekleme
# # cursor.execute(
# # "INSERT INTO ogrenciler(ad,soyad,yas,bolum,ortalama) VALUES(?,?,?,?,?)",
# # ('Salman','Ronaldo',24,'Makina','87.6')
# # )

# # Birden fazla kayıt ekleme(executemany)
# ogrenci_listesi: list[tuple[str, str, int, str, float]] = [
#     ('Salman','Messi',24,'Makina Mühendisliği',2.40),
#     ('Onur','Yağız',22,'Yazılım Mühendisliği',3.60),
#     ('Halil','İbrahim',26,'Gastronomi',1.80),
#     ('Arda','Yaman',19,'İnşaat Mühendisliği',2.80),
# ]

# cursor.executemany(
# "INSERT INTO ogrenciler(ad,soyad,yas,bolum,ortalama) VALUES(?,?,?,?,?)",
# ogrenci_listesi
# )

# conn.commit()
# print(f"{cursor.rowcount + 1} öğrenci eklendi.") #rowcount son işlemin etkilediği satır

# ====================================================================
# 4. VERİ OKUMA(SELECT)
# ====================================================================
# Tüm kayıtları getir
cursor.execute("SELECT * FROM ogrenciler")
tum_ogrenciler: list[tuple] = cursor.fetchall()

# print("\nTüm Öğrenciler: ")
# for ogr in tum_ogrenciler:
#     # ogr bir tuple: (id, ad, soyad, yas, bolum, ortalama)
#     print(f"Id:[{ogr[0]}]  Ad: {ogr[1]} - Soyad: {ogr[2]} - Yaş: {ogr[3]},"
#           f"Bölüm: {ogr[4]} - Ortalama: {ogr[5]}"
#           )

# Belirli sütunları seç
# cursor.execute("SELECT ad, soyad, ortalama FROM ogrenciler ORDER BY ortalama DESC")
# sonuclar: list[tuple] = cursor.fetchall()

# # print("\n---Ortalamaya Göre Sıralama(En Yüksek)---")
# # for ad, soyad, ort in sonuclar: # tuple unpacking
# #     print(f" {ad} {soyad}: {ort:.2f}")

# # Tek kayıt getir.
# cursor.execute("SELECT * FROM ogrenciler WHERE id = ?",(1,)) # (1, ) Parametre, yani ID'si 1 olanı getir.
# tek_ogr: tuple | None = cursor.fetchone()

# if tek_ogr:
#     print(f"\nID= 1: {tek_ogr[1]} {tek_ogr[2]}")
# else:
#     print("\nKayıt bulunamadı!")

# ====================================================================
# 5. SATIR FABRİKASI(Row Factory)
# ====================================================================
# Tuple yerine dictionary benzeri erişim için

# conn.row_factory = sqlite3.Row # Bu satırdan sonra Cursor'lar Row döndürür.
# cursor2: sqlite3.Cursor = conn.cursor()

# cursor2.execute("SELECT * FROM ogrenciler WHERE bolum = ?",("Makina Mühendisliği",))
# makina_muh: list[sqlite3.Row] = cursor2.fetchall()

# print(f"\nMakina Mühendisliği Öğrencileri(Row Factory)")
# for ogr in makina_muh:
#     # Artık sütun adlarıyla erişebiliyoruz.
#     print(f"  {ogr['ad']} {ogr['soyad']} - Ortalama: {ogr['ortalama']}")

# ====================================================================
# 6. VERİ GÜNCELLEME(UPDATE)
# ====================================================================
# cursor.execute(
# "UPDATE ogrenciler SET ortalama = ? WHERE ad = ? AND soyad = ?",
# (3.40,'Salman','Messi')
# )

# conn.commit()
# print(f"\n{cursor.rowcount} kayıt güncellendi")

# ====================================================================
# 7. VERİ SİLME(DELETE)
# ====================================================================
# cursor.execute("DELETE FROM ogrenciler WHERE ortalama < ?",(2.0,))
# conn.commit()
# print(f"{cursor.rowcount} kayıt silindi (ortalama < 2.0).")

# ====================================================================
# 8. CONTEXT MANAGER İLE KULLANIM(En İyi Pratik)
# ====================================================================
# Bu yöntem tercih edilmeli

# def ogrenci_sayisi_getir(db_yolu: str) -> int:
#     """Veritabanındaki toplam öğrenci sayısını döndürür."""
#     with sqlite3.connect(db_yolu) as baglanti:
#         imlec: sqlite3.Cursor = baglanti.cursor()
#         imlec.execute("SELECT COUNT(*) FROM ogrenciler")
#         sonuc: tuple = imlec.fetchone()
#         return sonuc[0]
#         # with bloğu bitince commit ve close otomatik kapanır


# sayi: int = ogrenci_sayisi_getir(DB_YOLU)
# print(f"\nToplam Öğrenci Sayısı: {sayi}")

# ====================================================================
# 9. TRANSACTİON ÖRNEĞİ
# ====================================================================
# def toplu_not_guncelleme(db_yolu: str, bolum: str, ek_puan: float) -> int:
#     """Belirli bir bölümdeki tüm öğrencilerin ortalamasına ek puan ekler
    
#     Args: 
#         db_yolu: Veritabanı dosya yolu
#         bolum: Bölüm Adı
#         ek_puan: Eklenecek puan
    
#     Returns:
#         Güncellenen kayıt listesi
#     """
#     with sqlite3.connect(db_yolu) as baglanti:
#         try:
#             imlec: sqlite3.Cursor = baglanti.cursor()
#             imlec.execute(
#                 "UPDATE ogrenciler SET ortalama = MIN(ortalama + ?, 4.0) WHERE bolum = ?",
#                 (ek_puan,bolum)
#             )
#             guncellenen: int = imlec.rowcount
#             baglanti.commit()
#             print(f"Transaction başarılı: {guncellenen} kayıt güncellendi.")
#             return guncellenen
#         except sqlite3.Error as hata:
#             baglanti.rollback()
#             print(f"Transaction geri alındı Hata: {hata}")
#             return 0

# toplu_not_guncelleme(DB_YOLU,'İnşaat Mühendisliği',0.10)

# ====================================================================
# 10. TEMİZLİK
# ====================================================================
# Bağlantı açıksa kapatıyoruz.
conn.close()
print(f"Bağlantı kapatıldı")

db_dosya: Path = Path(DB_YOLU)
if db_dosya.exists():
    boyut_kb: float = db_dosya.stat().st_size / 1024
    print(f"Veritabanı dosyası: {db_dosya.absolute()} ({boyut_kb:.1f}) KB")