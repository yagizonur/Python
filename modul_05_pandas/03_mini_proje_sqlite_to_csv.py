"""
=============================================================
  MODUL 4 - MINI PROJE: SQLite -> Pandas -> CSV Aktarimi
=============================================================
  Senaryo:
    1. Modul 3'teki API projesinin SQLite veritabanini oku
    2. Pandas ile isle, filtrele, ozetle
    3. CSV ve Excel formatinda disa aktar

  Eger Modul 3'un veritabani yoksa, ornek veri ile olusturur.
=============================================================
"""

import sqlite3  # Veritabani iletisimi kurmak icin
import pandas as pd  # Verileri tablo yapisinda islemek ve CSV'ye cevirmek icin
from pathlib import Path  # Dosyalarin boyutlarini olcmek vb. islemler icin


# =====================================================
# VERITABANI HAZIRLAMA
# =====================================================

DB_YOLU: str = "modul_05_pandas/satis_verileri.db"
CSV_CIKTI: str = "modul_05_pandas/satis_raporu.csv"
OZET_CIKTI: str = "modul_05_pandas/satis_ozeti.csv"


def veritabani_hazirla(db_yolu: str) -> None:
    """Ornek satis veritabanini olusturur (yoksa)."""
    with sqlite3.connect(db_yolu) as conn:
        cursor: sqlite3.Cursor = conn.cursor()

        # Urunler tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS urunler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT NOT NULL,
                kategori TEXT NOT NULL,
                birim_fiyat REAL NOT NULL
            )
        """)

        # Satislar tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS satislar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                urun_id INTEGER NOT NULL,
                tarih TEXT NOT NULL,
                adet INTEGER NOT NULL,
                musteri TEXT NOT NULL,
                sehir TEXT NOT NULL,
                FOREIGN KEY (urun_id) REFERENCES urunler(id)
            )
        """)

        # Veri varsa ekleme
        cursor.execute("SELECT COUNT(*) FROM urunler")
        if cursor.fetchone()[0] > 0:
            return

        # Ornek urunler
        urunler: list[tuple[str, str, float]] = [
            ("Laptop", "Elektronik", 35000.0),
            ("Mouse", "Aksesuar", 450.0),
            ("Klavye", "Aksesuar", 850.0),
            ("Monitor", "Elektronik", 12000.0),
            ("Kulaklik", "Aksesuar", 1200.0),
            ("SSD Disk", "Donanim", 2500.0),
            ("RAM 16GB", "Donanim", 3200.0),
            ("Webcam", "Aksesuar", 900.0),
        ]
        cursor.executemany(
            "INSERT INTO urunler (ad, kategori, birim_fiyat) VALUES (?, ?, ?)",
            urunler
        )

        # Ornek satislar
        satislar: list[tuple[int, str, int, str, str]] = [
            (1, "2025-01-10", 2, "Ahmet Yilmaz", "Istanbul"),
            (2, "2025-01-15", 10, "Fatma Kaya", "Ankara"),
            (1, "2025-02-03", 1, "Can Demir", "Izmir"),
            (3, "2025-02-18", 5, "Derya Celik", "Istanbul"),
            (4, "2025-03-01", 3, "Emre Sahin", "Ankara"),
            (2, "2025-03-12", 15, "Gul Arslan", "Istanbul"),
            (5, "2025-03-25", 8, "Hakan Oz", "Izmir"),
            (6, "2025-04-05", 12, "Ahmet Yilmaz", "Istanbul"),
            (7, "2025-04-15", 6, "Fatma Kaya", "Ankara"),
            (1, "2025-05-01", 1, "Murat Sen", "Bursa"),
            (3, "2025-05-20", 20, "Selin Kara", "Istanbul"),
            (4, "2025-06-02", 2, "Can Demir", "Izmir"),
            (8, "2025-06-15", 10, "Zeynep Ak", "Ankara"),
            (2, "2025-06-20", 30, "Ali Veli", "Istanbul"),
            (6, "2025-06-28", 5, "Derya Celik", "Istanbul"),
        ]
        cursor.executemany(
            "INSERT INTO satislar (urun_id, tarih, adet, musteri, sehir) VALUES (?, ?, ?, ?, ?)",
            satislar
        )

        conn.commit()
        print(f"Veritabani hazir: {len(urunler)} urun, {len(satislar)} satis")


# =====================================================
# ANA ISLEM: SQLITE -> PANDAS -> CSV
# =====================================================

def main() -> None:
    """SQLite'tan oku, Pandas ile isle, CSV'ye aktar."""

    print("=" * 60)
    print("  SQLite -> Pandas -> CSV Pipeline")
    print("=" * 60)

    # 1. Veritabanini hazirla
    veritabani_hazirla(DB_YOLU)

    # 2. SQLite'tan Pandas'a veri cek
    print("\n--- SQLite'tan Veri Okuma ---")

    conn: sqlite3.Connection = sqlite3.connect(DB_YOLU)  # Veritabanina baglaniriz

    # pd.read_sql() ile dogrudan SQL sorgusundan DataFrame olusturma
    # Tek satirda SQL kodunu calistirip sonucu Pandas tablosuna donusturur! (En sevilen ozelliklerden biri)
    df: pd.DataFrame = pd.read_sql("""  
        SELECT
            s.id as satis_id,
            u.ad as urun,
            u.kategori,
            u.birim_fiyat,
            s.tarih,
            s.adet,
            s.musteri,
            s.sehir,
            (s.adet * u.birim_fiyat) as toplam_tutar
        FROM satislar s
        INNER JOIN urunler u ON s.urun_id = u.id
        ORDER BY s.tarih
    """, conn)

    conn.close()

    # Tarih sutununu datetime'a cevir
    df["tarih"] = pd.to_datetime(df["tarih"])  # Metin (string) olan tarih yazisini gercek tarih/zaman yapisina cevirir.
    df["ay"] = df["tarih"].dt.strftime("%Y-%m")  # Sadece yil ve ay (2025-01) kismini koparip yeni sutun yapar.
    df["ay_adi"] = df["tarih"].dt.strftime("%B")  # Ayin ismini (Ocak, Subat) metin olarak verir.

    print(f"Toplam kayit: {len(df)}")
    print(f"Tarih araligi: {df['tarih'].min().date()} - {df['tarih'].max().date()}")
    print(f"\n{df.head()}")

    # 3. Veri Analizi
    print("\n" + "=" * 50)
    print("VERI ANALIZI")
    print("=" * 50)

    # Genel ozet
    print(f"\nToplam satis tutari: {df['toplam_tutar'].sum():>15,.0f} TL")
    print(f"Toplam satis adedi:  {df['adet'].sum():>15,}")
    print(f"Ortalama siparis:    {df['toplam_tutar'].mean():>15,.0f} TL")

    # Urune gore satis
    print("\n--- Urune Gore Satis ---")
    urun_ozet: pd.DataFrame = df.groupby("urun").agg(  # Ayni urunleri bir araya toplayip grup yapar.
        toplam_tutar=("toplam_tutar", "sum"),  # Grubun toplam tutarini hesapla
        toplam_adet=("adet", "sum"),           # Grubun toplam kac tane satildigini hesapla
        siparis_sayisi=("satis_id", "count"),  # Gruba kac siparis geldigini say
        ort_birim_fiyat=("birim_fiyat", "mean") # Ortalama fiyatini bul
    ).sort_values("toplam_tutar", ascending=False).reset_index()  # Ve bu tabloyu en cok para getirenden aza dogru sirala.

    print(urun_ozet.to_string(index=False))

    # Kategoriye gore
    print("\n--- Kategoriye Gore Satis ---")
    kategori_ozet: pd.DataFrame = df.groupby("kategori").agg(
        toplam_tutar=("toplam_tutar", "sum"),
        toplam_adet=("adet", "sum")
    ).sort_values("toplam_tutar", ascending=False).reset_index()

    # Yuzde hesapla
    genel_toplam: float = kategori_ozet["toplam_tutar"].sum()
    kategori_ozet["yuzde"] = (
        kategori_ozet["toplam_tutar"] / genel_toplam * 100
    ).round(1)

    print(kategori_ozet.to_string(index=False))

    # Sehir bazli
    print("\n--- Sehir Bazli Satis ---")
    sehir_ozet: pd.DataFrame = df.groupby("sehir").agg(
        toplam_tutar=("toplam_tutar", "sum"),
        siparis_sayisi=("satis_id", "count")
    ).sort_values("toplam_tutar", ascending=False).reset_index()
    print(sehir_ozet.to_string(index=False))

    # Aylik trend
    print("\n--- Aylik Satis Trendi ---")
    aylik: pd.DataFrame = df.groupby("ay").agg(
        toplam_tutar=("toplam_tutar", "sum"),
        siparis_sayisi=("satis_id", "count")
    ).reset_index()
    print(aylik.to_string(index=False))

    # En iyi musteriler
    print("\n--- En Iyi 5 Musteri ---")
    musteri_ozet: pd.DataFrame = df.groupby("musteri").agg(
        toplam_harcama=("toplam_tutar", "sum"),
        siparis_sayisi=("satis_id", "count")
    ).sort_values("toplam_harcama", ascending=False).head(5).reset_index()
    print(musteri_ozet.to_string(index=False))

    # 4. Filtreleme ornegi
    print("\n--- 10.000 TL Ustu Satislar ---")
    buyuk_satislar: pd.DataFrame = df[df["toplam_tutar"] > 10000]
    print(buyuk_satislar[["urun", "musteri", "sehir", "adet", "toplam_tutar"]].to_string(index=False))

    # 5. CSV'ye aktarma
    print("\n" + "=" * 50)
    print("CSV AKTARIMI")
    print("=" * 50)

    # Detayli rapor
    df.to_csv(CSV_CIKTI, index=False, encoding="utf-8-sig")  # Hazirladigimiz tabloyu bilgisayara Excel ile acilabilecek CSV dosyasi olarak kaydeder.
    print(f"Detayli rapor: {CSV_CIKTI}")

    # Ozet rapor
    urun_ozet.to_csv(OZET_CIKTI, index=False, encoding="utf-8-sig")
    print(f"Ozet rapor: {OZET_CIKTI}")

    # Dosya boyutlari
    for dosya in [CSV_CIKTI, OZET_CIKTI]:
        boyut: float = Path(dosya).stat().st_size / 1024
        print(f"  {dosya}: {boyut:.1f} KB")

    print("\nCSV dosyalarini Excel ile acabilirsiniz.")
    print("utf-8-sig encoding sayesinde Turkce karakterler dogru gorunecektir.")


if __name__ == "__main__":
    # Her calistirmada temiz basla
    import os
    if os.path.exists(DB_YOLU):
        os.remove(DB_YOLU)
    for f in [CSV_CIKTI, OZET_CIKTI]:
        if os.path.exists(f):
            os.remove(f)

    main()
