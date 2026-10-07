"""
=========================================================================
MODUL 1 - MINI PROJE: Çalışan Yönetim Sistemi(OOP - Sqlite)
=========================================================================
"""
import sqlite3
from datetime import datetime

# ==============================================================
# MODEL SINIFI
# ==============================================================
class Calisan:
    """
    Çalışan bilgilerini tutan sınıf
    """

    def __init__(
        self,
        ad: str,
        soyad: str,
        departman: str,
        maas: float,
        baslama_tarihi: str | None = None,
        calisan_id: int | None = None    
    ) -> None: 
        self.id: int | None = calisan_id
        self.ad: str = ad
        self.soyad: str = soyad
        self.departman: str = departman
        self.maas: float = maas
        self.baslama_tarihi: str = baslama_tarihi or datetime.now().strftime("%Y-%m-%d")

    @property
    def tam_ad(self) -> str:
        return f"{self.ad} {self.soyad}"

    @property
    def yillik_maas(self) -> float:
        return self.maas * 12

    def __str__(self) -> str:
        id_str: str = str(self.id) if self.id else "?"
        return(
            f"[{id_str}] {self.tam_ad} | "
            f"[{self.departman}]| "
            f"[{self.maas:,.2f}] TL | "
            f"Başlangıç: {self.baslama_tarihi} "
        )

    def __repr__(self) -> str:
        return(
            f"Çalışan(ad='{self.ad}', soyad = '{self.soyad}'," 
            f"departman='{self.departman}', maaş='{self.maas}')"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Calisan):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

# ==============================================================
# REPOSITORY SINIFI
# ==============================================================
class CalisanRepository:
    """
    SQLite ile çalışan CRUD(Create, Read, Update, Delete) işlemlerini yöneten sınıf
    """

    def __init__(self, db_yolu: str) -> None:
        self._db_yolu: str = db_yolu
        self._tablo_olustur()

    def _baglanti_al(self) -> sqlite3.Connection:
        """Yeni bir veritabanı bağlantısı oluşturur"""
        conn: sqlite3.Connection = sqlite3.connect(self._db_yolu)
        conn.row_factory = sqlite3.Row
        return conn

    def _tablo_olustur(self) -> None:
        """Çalışanlar tablosunu oluşturur(yoksa)"""
        with self._baglanti_al() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS calisanlar(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT NOT NULL,
                soyad TEXT NOT NULL,
                departman TEXT NOT NULL,
                maas REAL NOT NULL,
                baslama_tarihi TEXT NOT NULL
                )
""")
        conn.commit()

    # CREATE
    def ekle(self, calisan: Calisan) -> int:
        """Yeni bir çalışan ekler ve oluşan ID'yi döndürür"""

        with self._baglanti_al() as conn:
            cursor: sqlite3.Cursor = conn.execute(
                """INSERT INTO calisanlar (ad, soyad, departman, maas, baslama_tarihi)
                VALUES(?,?,?,?,?)""",
                (calisan.ad, calisan.soyad, calisan.departman, calisan.maas, calisan.baslama_tarihi)
            )
            conn.commit()
            calisan.id = cursor.lastrowid
            return cursor.lastrowid or 0

    # CREATE MANY
    def toplu_ekle(self, calisanlar: list[Calisan]) -> int:
        """Birden fazla çalışanı tek seferde ekler"""
        with self._baglanti_al() as conn:
            veri: list[tuple[str, str, str, float, str]] = [
                (c.ad, c.soyad, c.departman, c.maas, c.baslama_tarihi)
                for c in calisanlar
            ]
            conn.executemany(
                """INSERT INTO calisanlar(ad, soyad, departman, maas, baslama_tarihi)
                VALUES(?,?,?,?,?)
                """,
                veri
            )
            conn.commit()
            return len(veri)

    # READ 
    def _row_to_calisan(self, row: sqlite3.Row) -> Calisan:
        """Sqlite Row nesnesini Calisan nesnesine dönüştürür."""
        return Calisan(
            ad = row["ad"],
            soyad = row["soyad"],
            departman = row["departman"],
            maas = row["maas"],
            baslama_tarihi = row["baslama_tarihi"],
            calisan_id = row["id"],
        )

    def getir_by_id(self, calisan_id: int) -> Calisan | None:
        """ID ile çalışan getirir."""
        with self._baglanti_al() as conn:
            cursor: sqlite3.Cursor = conn.execute(
                "SELECT * FROM calisanlar WHERE id = ?",(calisan_id,)
            )
            row: sqlite3.Row | None = cursor.fetchone()
            return self._row_to_calisan(row) if row else None

    def getir_hepsi(self) -> list[Calisan]:
        """Tüm çalışanları getirir."""
        with self._baglanti_al() as conn:
            cursor: sqlite3.Cursor = conn.execute(
                "SELECT * FROM calisanlar ORDER BY ad, soyad"
            )
            return [self._row_to_calisan(row) for row in cursor.fetchall()]

    def getir_by_departman(self, departman: str) -> list[Calisan]:
        """Belirli departmandaki çalışanları getirir."""
        with self._baglanti_al() as conn:
            cursor: sqlite3.Cursor = conn.execute(
                "SELECT * FROM calisanlar WHERE departman = ? ORDER BY maas DESC",
                (departman,)
            )
            return [self._row_to_calisan(row) for row in cursor.fetchall()]

    def ara(self, arama: str) -> list[Calisan]:
        """Ad ve soyad içinde arama yapar"""
        with self._baglanti_al() as conn:
            cursor: sqlite3.Cursor = conn.execute(
                """
                SELECT * FROM calisanlar
                WHERE ad LIKE ? OR soyad LIKE ? 
                ORDER BY ad
                """,
                (f"%{arama}%", f"%{arama}%")
            )

            return [self._row_to_calisan(row) for row in cursor.fetchall()]

    def guncelle(self, calisan: Calisan) -> bool:
        """Çalışan bilgilerini günceller"""
        if calisan.id is None:
            return False
        with self._baglanti_al() as conn:
            cursor: sqlite3.Cursor = conn.execute(
                """
                UPDATE calisanlar 
                SET ad = ?, soyad = ?, departman = ? , maas = ? , baslama_tarihi = ? 
                WHERE id = ? 
                """,
                (calisan.ad, calisan.soyad, calisan.departman, calisan.maas, calisan.baslama_tarihi, calisan.id)
            )
            conn.commit()
            return cursor.rowcount > 0

    def zam_yap(self, calisan_id: int, oran: float) -> float | None:
        """Belirli çalışana yüzdelik zam yapar, yeni maaşı döndürür"""
        calisan: Calisan | None = self.getir_by_id(calisan_id)
        if calisan is None:
            return None
        calisan.maas *= (1 + oran)
        self.guncelle(calisan)
        return calisan.maas

    def sil(self, calisan_id: int) -> bool:
        """Çalışan Id ile siler"""
        with self._baglanti_al() as conn:
            cursor: sqlite3.Cursor = conn.execute(
                "DELETE FROM calisanlar WHERE id = ?", (calisan_id,)
            )

            conn.commit()
            return cursor.rowcount > 0

    def departman_istatistikleri(self) -> list[dict[str, str | int | float]]: 
        """Her departmanın çalışan sayısı ve ortalama maaşını döndürür."""
        with self._baglanti_al() as conn:
            cursor: sqlite3.Cursor = conn.execute("""
            SELECT 
                departman,
                COUNT(*) as calisan_sayisi,
                AVG(maas) as ortalama_maas,
                MIN(maas) as min_maas,
                MAX(maas) as max_maas,
                SUM(maas) as toplam_maas
            FROM calisanlar
            GROUP BY departman 
            ORDER BY calisan_sayisi DESC
""")
        return [dict(row) for row in cursor.fetchall()]    

    @property
    def toplam_calisan(self) -> int:
        """Toplam çalışan sayısı"""
        with self._baglanti_al() as conn:
            cursor: sqlite3.Cursor = conn.execute(
                "SELECT COUNT(*) FROM calisanlar"
            )

            return cursor.fetchone()[0]


# ==========================================================
# ANA PROGRAM
# ==========================================================
def main() -> None:
    """Çalışan Yönetim sistemi ---OOP + SQLite demo"""

    DB_YOLU: str = "modul_01_sqlite/calisan_yonetim.db"

    print("=" * 60)
    print(" ÇALIŞAN YÖNETİM SİSTEMİ(OOP + SQLite)")
    print("=" * 60)

    # Repository oluştur(tablo otomatik oluşur)
    repo: CalisanRepository = CalisanRepository(DB_YOLU)

    # 1. Çalışan Ekleme
    print("\n---Çalışan Ekleme---")

    ahmet: Calisan = Calisan("Ahmet","Yesevi","Pazarlama",120000.0,"2026-08-06")
    ahmet_id: int = repo.ekle(ahmet)
    print(f"Eklendi: {ahmet} (ID: {ahmet_id})")

    #Toplu Ekleme
    yeni_calisanlar: list[Calisan] = [
        Calisan("Salman","Ronaldo","Yazılım",140000.0,"2024-01-10"),
        Calisan("Ayda","Sayar","Pazarlama",87000.0,"2023-06-12"),
        Calisan("Onur","Yağız","İnsan Kaynakları",170000.0,"2021-06-19"),
        Calisan("Rumeysa","Yok","İnsan Kaynakları",49000.0,"2019-09-25"),
        Calisan("Arda","Güler","Yazılım",120000.0,"2024-05-15"),
        Calisan("Ebrar","Arslan","Finans",115000.0,"2022-02-28"),
    ]
    eklenen: int = repo.toplu_ekle(yeni_calisanlar)
    print(f"{eklenen} çalışan toplu olarak eklendi")


# Listeleme
    print(f"\n---Tüm Çalışanlar ({repo.toplam_calisan} kişi)---")
    for calisan in repo.getir_hepsi():
        print(f" {calisan}")


# Departmana Göre Filtreleme
    print("\n---Yazılım Departmanı---")
    yazilimcilar: list[Calisan] = repo.getir_by_departman("Yazılım")
    for c in  yazilimcilar:
        print(f"  {c}")

# Arama
    print("\n---'Salman' Araması---")     
    sonuclar: list[Calisan] = repo.ara("Salman")
    for c in sonuclar:
        print(f" {c}")

   # Güncelleme
    print("\n---Zam İşlemi---")
    yeni_maas: float | None = repo.zam_yap(ahmet_id,0.15)
    if yeni_maas:
        print(f" Ahmet'nin yeni maaşı: {yeni_maas:,.2f} TL (%15 zam)")

    # İstatistikler
    print("\n---Departman İstatistikleri---")
    print(f"   {'Departman':<20} {'Kisi':>5} {'Ort. Maas':>12}"
          f"{'Min':>10} {'Max':>10}")
    print(" " + "-" * 62)

    istatistikler: list[dict[str, str | int | float]] = repo.departman_istatistikleri()
    for ist in istatistikler:
        print(
        f" {str(ist['departman']):<20} "
        f" {ist['calisan_sayisi']:>5} "
        f" {float(str(ist['ortalama_maas'])):>12,.2f} "
        f" {float(str(ist['min_maas'])):>10,.2f} "
        f" {float(str(ist['max_maas'])):>10,.2f} "
        )        

    # Silme 
    print("\n---Çalışan Silme---")
    silindi: bool= repo.sil(7)
    #print(f" ID={ali_id} silindi: {silindi}")
    print(f" Kalan çalışan sayısı: {repo.toplam_calisan}")

    # Kalıcılık Testi
    print("\n---Kalıcılık Testi---")
    print(f" Veritabanı Dosyası: {DB_YOLU}")
    print("  Bu programı tekrar çalıştırdığımızda veriler hala orada olacak ")
    print(" (Çünkü bellekte değil, .db dosyasında saklanıyor)")

if __name__ == "__main__":
    # Her çalıştırmada temiz başlayalım(demo için)
    import os
    db: str = "modul_01_sqlite/calisan_yonetimi.db"
    if os.path.exists(db):
        os.remove()

    main()

            
        
        
        