"""
================================================================================
MODUL 2: BÖLÜM 2: JSON Parse ve İç İçe Veri Yapıları
Konu: json modulü, iç içe dict/list, veri dönüştürme
================================================================================
"""
import json # JSON verileri okumak ve yazmak için kullanılan kütüphane
import requests # İnternet üzerinden veri çekmek için kullanılan kütüphane

# ===============================================================================
# 1. JSON NEDİR? (Pyhton Perspektifi)
# ===============================================================================
# Python'da JSON -> dict veya list:
# veri = json.loads(json_string)

# Dönüşüm tablosu:
# JSON object    { }        -> Python dict
# JSON array     [ ]        -> Python list
# JSON string    "abc"      -> Python str
# JSON number    42         -> Python int
# JSON number    3.14       -> Python float
# JSON true/false           -> Python True/False
# JSON null                 -> Python None

print("---1. JSON <-> Python Dönüşümleri---")

# Python dict -> JSON string(serialize)
kullanici: dict[str,str | int | bool] = {
    "ad":"Ali",
    "yas":49,
    "aktif":True,
    "adres":None # JSON'Da null döner
}

json_string: str = json.dumps(kullanici, ensure_ascii=False,indent=2) # Python verisini JSON metnine dönüştürür. (ensure_ascii = False: Türkçe karakter bozulmasını engeller, indent = 2: güzel görünmesi için boşluk bırakır)
print(f"Python -> JSON:\n{json_string}")

# JSON string -> Python dict
geri_donusum: dict = json.loads(json_string) # JSON metnini alıp, Python'da kullanabileceğimiz sözlük(dictionary) yapısına geri döndürür.(loads = load string)
print(f"\nJSON -> Python: {geri_donusum}")
print(f"Tip: {type(geri_donusum)}") 

# ===============================================================================
# 2. İÇ İÇE JSON VERİSİNE ERİŞİM
# ===============================================================================
print("\n-- 2. İç İçe JSON Erişimi---")

# Örnek: Karmaşık JSON yapısı
karmasik_json: str = """
{
    "kullanici":{
        "id":1,
        "ad": "Ali Şelli",
        "iletisim":{
            "email": "ali@email.com",
            "telefon": {
                "ev": "0212-1234567",
                "cep":"0532-1234567"
            }
        },
        "hobiler":["futbol","kodlama","yuzme"],
        "adresler":[
            {"tur":"ev", "sehir":"İstanbul","ilce":"Kadıköy"},
            {"tur":"is", "sehir":"İstanbul","ilce":"Levent"}
        ]
    }
}

"""

veri: dict = json.loads(karmasik_json) # Metin halindeki JSON verisini Python'un anlayabileceği veri yapılarına çeviriyoruz.

# Düz erişim
kullanici_adi: str = veri["kullanici"]["ad"] # İç içe girerek değeri buluyoruz. Önce "kullanici" kutusuna, sonra onun içindeki "ad" kutusuna bakıyoruz.
print(f"Ad: {kullanici_adi}")

# İç içe dict erişimi
cep: str = veri["kullanici"]["iletisim"]["telefon"]["cep"]
print(f"Cep: {cep}")

# Liste erişimi
ilk_hobi: str = veri["kullanici"]["hobiler"][0]
print(f"İlk hobi: {ilk_hobi}")

# İç içe liste + dict
is_adresi_ilce: str = veri["kullanici"]["adresler"][1]["ilce"]
print(f"İş Adresi İlçe: {is_adresi_ilce}")

# Tüm hobiler
print(f"Hobiler: {', '.join(veri["kullanici"]["hobiler"])}")

# ===============================================================================
# 3. GÜVENLİ ERİŞİM(.get() metodu)
# ===============================================================================
# Python'da; deger = dict.get("key","varsayılan")

print("\n---3. Güvenli Erişim(get)---")

eksik_veri: dict = {"ad":"Ali", "yas":49}

# Tehlikeli: KeyError verebilir
# print(eksik_veri["email"])

# Güvenli: get() ile varsayılan değer
email: str = eksik_veri.get("email","belirtilmemis") # .get() metodu ile güvenli arama yapıyoruz. Eğer email anahtarı yoksa program hata vermesin diye varsayılan bir değer dönüyoruz.
print(f"Email: {email}")

# None kontrolü
telefon: str| None = eksik_veri.get("telefon")
print(f"Telefon: {telefon}")
if telefon is None:
    print(" Telefon bilgisi mevcut değil.")

# ===============================================================================
# 4. API'DEN GELEN JSON'I PARSE ETME
# ===============================================================================
print("\n---4. API'den JSON Parse---")

def kullanici_bilgisi_getir(kullanici_id: int) -> dict[str, str] | None:
    """
    JSON PlaceHolder API'den kullanıcı bilgisi getirir ve sadeleleştirilmiş bir dict oluşturur.

    Args: 
        kullanici_ad: Kullanıcı ID'si(1-10 arası)
    Returns:
    Sadeleştirilmiş kullanıcı bilgisi veya None
    """
    yanit: requests.Response = requests.get(
         f"https://jsonplaceholder.typicode.com/users/{kullanici_id}",
         timeout=10
)

    if not yanit.ok:
        return None

    ham_veri: dict = yanit.json()

    sadelestirilmis: dict[str, str] = {
        "ad": ham_veri["name"],
        "email": ham_veri["email"],
        "telefon": ham_veri["phone"],
        "sehir": ham_veri["address"]["city"],
        "sirket": ham_veri["company"]["name"],
        "web": ham_veri.get("website","yok"),
    }

    return sadelestirilmis

bilgi: dict[str, str] | None = kullanici_bilgisi_getir(10)
if bilgi:
    print("Kullanıcı Bilgisi: ")
    for anahtar,deger in bilgi.items():
        print(f"  {anahtar:<10}: {deger}")

# ===============================================================================
# 5. JSON LİSTESİ İŞLEME
# ===============================================================================
print("\n---5. JSON Listesi İşleme---")

def gonderileri_analiz_et() -> dict[str, int | float]:
    """
    Tüm gönderileri çeker ve basit istatitikler hesaplar.

    Returns: 
        İstatistik sözlüğü
    """
    yanit: requests.Response = requests.get(
        "https://jsonplaceholder.typicode.com/posts",
        timeout=10
    )

    yanit.raise_for_status()

    gonderiler: list[dict] = yanit.json()

    # İstatistik hesaplama
    toplam: int = len(gonderiler)
    baslik_uzunluklari: list[int] = [len(g['title']) for g in gonderiler]   
    icerik_uzunluklari: list[int] = [len(g['body']) for g in gonderiler]   

    # Kullanıcı başına gönderi sayısı
    kullanici_sayilari: dict[int, int] = {}
    for gonderi in gonderiler:
        uid: int = gonderi["userId"]
        kullanici_sayilari[uid] = kullanici_sayilari.get(uid,0) + 1

    return{

        "toplam_gonderi":toplam,
        "ort_baslik_uzunlugu":sum(baslik_uzunluklari) // toplam,
        "ort_icerik_uzunlugu":sum(icerik_uzunluklari) // toplam,
        "benzersiz_kullanici":len(kullanici_sayilari),
        "max_gonderi_bir_kullanici":max(kullanici_sayilari.values()),
    }

istatistikler: dict[str, int | float] = gonderileri_analiz_et()
print("Gönderi İstatistikleri")
for anahtar, deger in istatistikler.items():
    print(f" {anahtar}: {deger}")    

# ===============================================================================
# 6.  JSON DOSYAYA KAYDETME / OKUMA
# ===============================================================================

print("\n---6. JSON Dosya İşlemleri---")

# Dosyaya kaydetme
ornek_veri: list[dict[str, str | int]] = [
    {"ad":"Ali", "yas":25,"sehir":"İstanbul"},
    {"ad":"Ayse", "yas":22,"sehir":"Ankara"},
    {"ad":"Mehmet", "yas":21,"sehir":"İzmir"},
]

dosya_yolu: str = "modul_02_api_json/kullanicilar.json"

# Yazma
with open(dosya_yolu,"w",encoding="utf-8") as dosya:
    json.dump(ornek_veri,dosya,ensure_ascii=False,indent=2)
print(f"Veri dosyaya kaydedildi: {dosya_yolu}")

# Okuma
with open(dosya_yolu,"r",encoding="utf-8") as dosya:
    okunan: list[dict] = json.load(dosya)

print(f"Dosyadan okunan: {len(okunan)} kayıt")
for kayit in okunan:
    print(f"  {kayit['ad']} ({kayit['yas']}) - {kayit ['sehir']}")

# =====================================================
# 7. OZET TABLO
# =====================================================
"""
JSON ISLEMLERI OZET:

| Islem              | json modulu              | requests modulu     |
|--------------------|--------------------------|---------------------|
| String -> dict     | json.loads(metin)        | response.json()     |
| dict -> String     | json.dumps(veri)         | -                   |
| Dosyadan oku       | json.load(dosya)         | -                   |
| Dosyaya yaz        | json.dump(veri, dosya)   | -                   |
| Turkce karakter    | ensure_ascii=False       | -                   |
| Guzel format       | indent=2                 | -                   |
| Guvenli erisim     | veri.get("key", default) | -                   |
"""

# Temizlik
import os
if os.path.exists(dosya_yolu):
    os.remove(dosya_yolu)