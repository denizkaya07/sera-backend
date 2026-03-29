"""
BKU Tarimorman Scraper
Tum bitkiler icin ruhsatli urunleri ceker ve JSON olarak kaydeder.

Kullanim:
    pip install requests beautifulsoup4
    python bku_scraper.py
"""

import requests
import json
import time
from bs4 import BeautifulSoup

BASE_URL = "https://bku.tarimorman.gov.tr"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9",
}

session = requests.Session()
session.headers.update(HEADERS)


def get_bitkiler():
    """Tum bitki listesini ceker."""
    print("Bitki listesi aliniyor...")
    r = session.get(f"{BASE_URL}/Kullanim/TavsiyeArama", timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")

    bitkiler = []
    select = soup.find("select", {"name": "BitId"}) or soup.find("select", {"id": "BitId"})
    if select:
        for opt in select.find_all("option"):
            val = opt.get("value", "").strip()
            text = opt.get_text(strip=True)
            if val and val != "0":
                bitkiler.append({"id": val, "ad": text})
        print(f"  {len(bitkiler)} bitki bulundu.")
    else:
        print("  Bitki select bulunamadi, alternatif yontem deneniyor...")
        # Alternatif: JSON endpoint
        r2 = session.get(f"{BASE_URL}/Kullanim/GetBitkiList", timeout=30)
        try:
            data = r2.json()
            for item in data:
                bitkiler.append({"id": str(item.get("Id", item.get("id", ""))), "ad": item.get("Ad", item.get("ad", ""))})
            print(f"  {len(bitkiler)} bitki bulundu (JSON).")
        except:
            print("  JSON de alinamadi.")

    return bitkiler


def get_urunler_for_bitki(bitki_id, bitki_ad):
    """Belirli bir bitki icin ruhsatli urunleri ceker."""
    urunler = []
    sayfa = 1

    while True:
        try:
            # POST ile arama
            data = {
                "BitId": bitki_id,
                "ZarId": "0",
                "AktId": "0",
                "Page": sayfa,
            }
            r = session.post(f"{BASE_URL}/Kullanim/TavsiyeArama", data=data, timeout=30)
            soup = BeautifulSoup(r.text, "html.parser")

            # Urun satirlarini bul
            rows = soup.select("table tbody tr") or soup.select(".table tbody tr")
            if not rows:
                # Alternatif: JSON endpoint
                r2 = session.get(
                    f"{BASE_URL}/Kullanim/GetUrunList",
                    params={"bitId": bitki_id, "page": sayfa},
                    timeout=30
                )
                try:
                    data2 = r2.json()
                    items = data2.get("data", data2) if isinstance(data2, dict) else data2
                    if not items:
                        break
                    for item in items:
                        urunler.append({
                            "bitki": bitki_ad,
                            "ruhsat_no": str(item.get("RuhsatNo", "")),
                            "urun_adi": item.get("UrunAdi", ""),
                            "firma": item.get("FirmaAdi", ""),
                            "etken_madde": item.get("EtkenMadde", ""),
                            "formulas": item.get("Formulas", ""),
                            "doz": item.get("Doz", ""),
                            "zarali": item.get("ZararliOrganizma", ""),
                            "son_ilac_hasat": item.get("SonIlacHasat", ""),
                        })
                    if len(items) < 20:
                        break
                    sayfa += 1
                    time.sleep(0.5)
                    continue
                except:
                    break

            if not rows:
                break

            for row in rows:
                cells = row.find_all("td")
                if len(cells) >= 4:
                    urunler.append({
                        "bitki": bitki_ad,
                        "ruhsat_no": cells[0].get_text(strip=True),
                        "urun_adi": cells[1].get_text(strip=True),
                        "firma": cells[2].get_text(strip=True) if len(cells) > 2 else "",
                        "etken_madde": cells[3].get_text(strip=True) if len(cells) > 3 else "",
                        "formulas": cells[4].get_text(strip=True) if len(cells) > 4 else "",
                        "doz": cells[5].get_text(strip=True) if len(cells) > 5 else "",
                        "zarali": cells[6].get_text(strip=True) if len(cells) > 6 else "",
                        "son_ilac_hasat": cells[7].get_text(strip=True) if len(cells) > 7 else "",
                    })

            # Sonraki sayfa var mi?
            next_btn = soup.find("a", string=lambda s: s and ("Sonraki" in s or ">" in s or "Next" in s))
            if not next_btn:
                break
            sayfa += 1
            time.sleep(0.5)

        except Exception as e:
            print(f"    HATA ({bitki_ad} sayfa {sayfa}): {e}")
            break

    return urunler


def main():
    print("BKU Scraper basliyor...")
    print("=" * 50)

    bitkiler = get_bitkiler()

    if not bitkiler:
        print("Bitki listesi alinamadi! Manuel test yapiliyor...")
        # Manuel test - domates
        bitkiler = [{"id": "1", "ad": "Domates"}]

    tum_urunler = []
    for i, bitki in enumerate(bitkiler):
        print(f"[{i+1}/{len(bitkiler)}] {bitki['ad']} isleniyor...")
        urunler = get_urunler_for_bitki(bitki["id"], bitki["ad"])
        tum_urunler.extend(urunler)
        print(f"  {len(urunler)} urun bulundu. Toplam: {len(tum_urunler)}")
        time.sleep(1)  # Sunucuya nazik ol

    # Kaydet
    with open("bku_urunler.json", "w", encoding="utf-8") as f:
        json.dump(tum_urunler, f, ensure_ascii=False, indent=2)

    print("=" * 50)
    print(f"Tamamlandi! {len(tum_urunler)} urun kaydedildi.")
    print("Dosya: bku_urunler.json")

    # Ozet
    bitkiler_ozet = {}
    for u in tum_urunler:
        b = u["bitki"]
        bitkiler_ozet[b] = bitkiler_ozet.get(b, 0) + 1
    print("\nBitkiye gore urun sayilari:")
    for b, c in sorted(bitkiler_ozet.items(), key=lambda x: -x[1])[:20]:
        print(f"  {b}: {c}")


if __name__ == "__main__":
    main()
