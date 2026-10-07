"""
================================================================================
MODUL 3 - MINI PROJE: API'den Veri Çek, SQLite'a Kaydet
================================================================================
"""
import sqlite3
import requests
from datetime import datetime

# ============================================
# VERİTABANI İŞLEMLERİ
# ============================================
class KullaniciDB:
    """Kullanıcı verilerini SQLite'ta yöneten sınıf"""

    def __init__(self,db_yolu: str) -> None:
        self._db_yolu: str = db_yolu # Veritabanı dosyasının yolunu class içinde saklar
        self._tablo_olustur() # Sınıf çağrılır çağrılmaz tabloyu hazırla

    def _baglanti_al(self) -> sqlite3.Connection:
        conn: sqlite3.Connection = sqlite3.connect(self._db_yolu) # Veritabanı dosyasına bağlanır(yoksa oluşturur)
        conn.row_factory = sqlite3.Row # Sonuçları sütun ismine göre(dictionary gibi) seçebilmemizi sağlar.
        return conn

    def _tablo_olustur(self) -> None:
        with self._baglanti_al() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS kullanicilar(
            id INTEGER PRIMARY KEY,
            ad TEXT NOT NULL,
            kullanici_adi TEXT NOT NULL,
            email TEXT NOT NULL,
            telefon TEXT,
            sehir TEXT,
            sirket TEXT,
            web_sitesi TEXT,
            guncelleme_tarihi TEXT NOT NULL
            )"""
            ) # execute: İçine yazdığımız SQL kodunu veritabanında çalıştırır.
            conn.commit() # commit(): Yapılan değişiklikleri veritabanında kalıcı olarak kaydeder.

    def kaydet(self, kullanici: dict[str, str | int]) -> None:
        """Tek bir kullanıcıyı veritabanına kaydeder(varsa günceller)"""
        with self._baglanti_al() as conn:
            conn.execute("""
            INSERT OR REPLACE INTO kullanicilar
            (id, ad, kullanici_adi, email, telefon, sehir, sirket,
            web_sitesi, guncelleme_tarihi)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,(
             kullanici["id"],
             kullanici["ad"],
             kullanici["kullanici_adi"],
             kullanici["email"],
             kullanici["telefon"],
             kullanici["sehir"],
             kullanici["sirket"],
             kullanici["web_sitesi"],
             datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            conn.commit()

    def toplu_kaydet(self, kullanicilar: list[dict[str, str | int]]) -> int:
        """Birden fazla kullanıcıyı kaydeder"""
        sayac: int = 0
        for kullanici in kullanicilar:
            self.kaydet(kullanici)
            sayac += 1
        return sayac

    def hepsini_getir(self) -> list[dict]:
        """Tüm kullanıcıları döndürür."""
        with self._baglanti_al() as conn:
            cursor: sqlite3.Cursor = conn.execute(
                "SELECT * FROM kullanicilar ORDER BY ad" # Tablodaki tüm verileri adlarına göre sıralayıp getir
            )
            return [dict(row) for row in cursor.fetchall()] # Tüm satırları al(fetchall) ve her birini sözlük yapısına çevirerek liste olarak ver

    def sehre_gore_getir(self, sehir: str) -> list[dict]:
        """Belirli şehirdeki kullanıcıları döndürür"""
        with self._baglanti_al() as conn:
            cursor: sqlite3.Cursor = conn.execute(
                "SELECT * FROM kullanicilar WHERE sehir = ?",(sehir,)
            )
            return [dict(row) for row in cursor.fetchall()]
        
    def ara(self, terim: str) -> list[dict]:
        """Ad veya email içinde arama yapar"""
        with self._baglanti_al() as conn:
            cursor: sqlite3.Cursor = conn.execute(
                """SELECT * FROM kullanicilar
                    WHERE ad LIKE ? OR email LIKE ?
                """,
                (f"%{terim}%",f"%{terim}%")
            )
            return [dict(row) for row in cursor.fetchall()]

    @property
    def kayit_sayisi(self) -> int:
        with self._baglanti_al() as conn:
            cursor: sqlite3.Cursor = conn.execute(
                "SELECT COUNT(*) FROM kullanicilar"
            )
            return cursor.fetchone()[0]

# ============================================
# API İŞLEMLERİ
# ============================================
class KullaniciAPI:
    """JSONPlaceHolder API'den kullanici verisi çeken sınıf"""

    BASE_URL: str = "https://jsonplaceholder.typicode.com"

    def kullanicilari_cek(self) -> list[dict[str, str | int]]:
        """
        API'den tüm kullanıcıları çeker ve sadelestirilmiş formata dönüştürür.

        Returns: 
            Sadeleştirilmiş kullanıcı listesi
        """
        print("API'den veri çekiliyor...")
        yanit: requests.Response = requests.get(
            f"{self.BASE_URL}/users",
            timeout=10
        )
        yanit.raise_for_status() 

        ham_veri: list[dict] = yanit.json() # Gelen text formatındaki JSON verisini Python listesine(sözlüklerden oluşan bir listeye) dönüştürür.
        print(f"  {len(ham_veri)} kullanıcı çekildi.")

        sadelestirilmis: list[dict[str, str | int]] = []
        for k in ham_veri:
            sadelestirilmis.append({
                "id": k["id"],
                "ad": k["name"],
                "kullanici_adi": k["username"],
                "email": k["email"],
                "telefon": k.get("phone",""),
                "sehir": k.get("address",{}).get("city","Bilinmiyor"),
                "sirket": k.get("company",{}).get("name","Bilinmiyor"),
                "web_sitesi": k.get("website",""),
                })
        return sadelestirilmis

    def tek_kullanici_cek(self, kullanici_id: int) -> dict[str, str | int] | None:
        """Tek bir kullanıcıyı ID ile çeker"""
        yanit: requests.Response = requests.get(
            f"{self.BASE_URL}/users/{kullanici_id}",
            timeout=10
        )

        if not yanit.ok:
            return None

        k: dict = yanit.json()
        return {
            "id": k["id"],
            "ad":k["name"],
            "kullanici_adi":k["username"],
            "email":k["email"],
            "telefon":k.get("phone",""),
            "sehir": k.get("address",{}).get("city","Bilinmiyor"),
            "sirket": k.get("company",{}).get("name","Bilinmiyor"),
            "web_sitesi": k.get("website",""),
        }

# ===================================
# ANA PROGRAM
# ===================================
def main() -> None:
    """API'den veri çek, SQLite'a kaydet, sorgula"""

    DB_YOLU: str = "modul_02_api_json/kullanicilar.db"

    print("=" * 60)
    print("  API -> JSON -> SQLite Pipelibne")
    print("=" * 60)

    # 1. API'den veri çek
    api: KullaniciAPI = KullaniciAPI()

    try:
        kullanicilar: list[dict[str, str | int]] = api.kullanicilari_cek()
    except requests.exceptions.RequestException as hata:
        print(f"API hatası: {hata}")
        print("İnternet bağlantınızı kontrol edin")
        return

    # SQLite'a kaydet
    print("\nVeritabanına kaydediliyor...")
    db: KullaniciDB = KullaniciDB(DB_YOLU)
    kaydedilen: int = db.toplu_kaydet(kullanicilar)
    print(f"   {kaydedilen} kullanıcı kaydedildi.")

    # Veritabanından oku ve göster
    print(f"\n---Veritabanındaki Kullanıcılar ({db.kayit_sayisi} kayıt)---\n")

    print(f"  {'ID':>3} {'Ad':<25} {'Email':<30} {'Sehir':<15} {'Sirket':<20}")
    print(" " + "-" * 95)

    for k in db.hepsini_getir():
        print(
            f"   {k['id']:>3} "
            f"{k['ad']:<25} "
            f"{k['email']:<30} "
            f"{k['sehir']:<15} "
            f"{k['sirket']:<20} "
        )

    # Arama testi
    print("\n---Arama: 'Clem'---")
    arama_sonuclari: list[dict] = db.ara('Clem')
    for k in arama_sonuclari:
        print(f"  {k['ad']} ({k['email']})")

    if not arama_sonuclari:
        print("Sonuç bulunamadı!")

    # Şehir filtresi
    print("\n---Şehir: 'Gwenborough'")
    sehir_sonuclari: list[dict] = db.sehre_gore_getir('Gwenborough')
    for k in sehir_sonuclari:
        print(f"  {k['ad']} - ({k['sirket']})")

    if not sehir_sonuclari:
        print("Sonuç bulunamadı!")

    print(f"\nVeritabanı dosyası: {DB_YOLU}")
    print("Bu dosya kapattıktan sonra bile verileri tutar(kalici)")

main()

# if __name__ == '__main__':
#     import os
#     db_dosya: str = "modul_02_api_json/kullanicilar.db"
#     if os.path.exists(db_dosya):
#         os.remove(db_dosya)

   

  
