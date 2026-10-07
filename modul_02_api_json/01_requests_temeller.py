"""
===================================================================
MODUL 2: BÖLÜM 1: request Modülü ile HTTP İstekleri
Konu: GET İsteği, durum kodları, headers, timeout
===================================================================
"""
import requests # İnternetten(başka sunuculardan) veri çekmemizi sağlayan kütüphane
import json # Gelen JSON(paket) formatındaki veriyi okumak için

# ======================================================================
# 1. BASİT GET İSTEĞİ
# ======================================================================
print("--- 1.BASİT GET İSTEĞİ ---")

url: str = "https://jsonplaceholder.typicode.com/posts/1" # İstek atacağımız adres(URL)
response: requests.Response = requests.get(url, timeout= 10) # Adrese git, veriyi al ve 'response'(yanıt) değişkenine koy. Eğer cevap 10 saniye içinde gelmezse iptal et(timeout)

print(f"URL: {url}")
print(f"Durum Kodu: {response.status_code}") # 200 = Başarılı
print(f"Başarılı Mı: {response.ok}")
print(f"Content-Type: {response.headers.get('Content-Type')}")
print(f"Yanıt Süresi: {response.elapsed.total_seconds():.3f} saniye")

# ======================================================================
# 2. YANIT İÇERİĞİNİ OKUMA
# ======================================================================
print("\n--- 2. Yanıt İçeriği ---")

# Ham metin olarak 
ham_metin: str = response.text # Gelen veriyi olduğu gibi düz yazı(string) olarak alır
print(f"Ham metin(İlk 100 karakter): {ham_metin[:100]}...")

# JSON olarak parse
# En çok kullanacağınız yöntem
veri: dict = response.json() # Gelen JSON formatındaki veriyi anında Python sözlüğüne(Dictionary) dönüştürür. Artık verilere erişmek çok daha kolay
print(f"\nJSON olarak: ")
print(f" ID: {veri['id']}")
print(f" Başlık: {veri['title']}")
print(f" Kullanıcı Id: {veri['userId']}")
print(f" İçerik: {veri['body'][:50]}...")

# ======================================================================
# 3. HTTP DURUM KODLARI KONTROLÜ
# ======================================================================
print("\n-- 3.Durum Kodu Kontrolü --")

def guvenli_istek(url: str) -> dict | None:
    """
    URL'e GET isteği atar, durum kodunu kontrol eder.
    
    Args:
        url: İstek atılacak URL 
    Returns:
        Başarılı ise JSON verisi(dict), değilse None
    """

    try:
        yanit: requests.Response = requests.get(url,timeout=10)

        if yanit.status_code == 200:
            print(f" [200 OK] {url}")
            return yanit.json()
        elif yanit.status_code == 404:
            print(f" [404 NOT FOUND] {url}")
        elif yanit.status_code == 500:
            print(f" [500 SERVER ERROR] {url}")
            return None
        else:
            print(f" [{yanit.status_code}] {url}")
            return None
    except requests.exceptions.Timeout: # Eğer sunucu 10 saniye içinde yanıt vermezse burası çalışır
        print(f" [TIMEOUT] istek zaman aşımına uğradı: {url}")
    except requests.exceptions.ConnectionError: # İnternet bağlantısı yoksa veya sunucu çökmüşse burası çalışır
        print(f" [CONNECTION ERROR] bağlantı kurulamadı: {yanit}")
        return None
    except requests.exceptions.RequestException as hata:
        print(f" [HATA] {hata}")
        return None

# Başarılı istek
veri1: dict | None = guvenli_istek(
    "https://jsonplaceholder.typicode.com/posts/1"
)

# 404 hatası(var olmayan kaynak)
veri2: dict | None = guvenli_istek(
     "https://jsonplaceholder.typicode.com/posts/99999"
) 

# ======================================================================
# 4. QUERY PARAMETRELERİ
# ======================================================================
# Yöntem 1: URL içine gömme(okunması zor)
url = "https://jsonplaceholder.typicode.com/posts?userId=1&_limit=3"

# Yöntem 2: params dict'i(tercih edilen)
parametreler: dict[str, str | int] = {
    "userId":1,
    "_limit":3
}

yanit: requests.Response = requests.get(
    "https://jsonplaceholder.typicode.com/posts",
    params= parametreler, 
    timeout=10
)

print(f"Gerçek URL: {yanit.url}") # Parametreler otomatik eklenir.
print(f"Sonuç sayısı: {len(yanit.json())}")

gonderiler: list[dict] = yanit.json()
for gonderi in gonderiler:
    print(f" [{gonderi['id']}] {gonderi['title'][:50]}...")


# ======================================================================
# 5. HEADERS 
# ======================================================================
print("\n-- 5. Request Headers --")
# Bazı API'ler özel header ister(API KEY, Accept, User-Agent vs)

ozel_basliklar: dict[str, str] = {
    "Accept": "application/json",
    "User-Agent": "PythonEgitim/1.0"
}

yanit_h = requests.Response = requests.get(
    "https://jsonplaceholder.typicode.com/users/1",
    headers=ozel_basliklar,
    timeout=10
)

if yanit_h.ok:
    kullanici: dict = yanit_h.json()
    print(f"Kullanıcı: {kullanici['name']}")
    print(f"Email: {kullanici['email']}")
    print(f"Şehir: {kullanici['address']['city']}")

# ======================================================================
# 6. LİSTE VERİSİ ÇEKME
# ======================================================================
print(f"\n--- 6. Liste Verisi ---")

yanit_liste = requests.Response = requests.get(
    "https://jsonplaceholder.typicode.com/users",
    timeout=10
)

if yanit_liste.ok:
    kullanicilar: list[dict] = yanit_liste.json()
    print(f"Toplam Kullanıcı: {len(kullanicilar)}")

    print(f"     {'ID':>3} {'Ad':<25} {'Sehir':<20} {'Şirket':<25}")
    print(" " + "-" * 75)

    for k in kullanicilar:
        print(
            f"   {k['id']:>3} "
            f"{k['name']:<25} "
            f"{k['address']['city']:<20} "
            f"{k['company']['name']:<25} "
        )
# ======================================================================
# 7. raise_for_status() KULLANIMI
# ======================================================================
print("\n --7. raise_for_status() --")

try:
    yanit_hata: requests.Response = requests.get(
        "https://jsonplaceholder.typicode.com/posts/9999",
        timeout=10
    )
    yanit_hata.raise_for_status() # Gelenm yanıtın kodu hatalıysa(404 gibi), otomatik olarak hata fırlatır ve programın akışını 'except' bloğuna atar
    print("Başarılı")
except requests.exceptions.HTTPError as hata:
    print(f"HTTP Hatası: {hata}")

"""
ALISTIRMA: Asagidaki API'den veri cekin ve ekrana yazin.

API: https://jsonplaceholder.typicode.com/todos
(Yapilacaklar listesi)

Gereksinimler:
  1. GET istegi atin
  2. Durum kodunu kontrol edin
  3. Sadece "completed": true olanlari filtreleyin
  4. Ilk 5 tanesini ekrana yazin: ID, baslik, tamamlandi mi
  5. Type Hints kullanin

Ipucu: todo["completed"] bir bool degeridir.
"""
