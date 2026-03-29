"""
BKU Scraper v2 - Bitki bazlı ruhsat grubu POST scraper
Kullanim:
    pip install requests beautifulsoup4
    python bku_scraper_v2.py
"""

import requests
import json
import time
from bs4 import BeautifulSoup

BASE_URL = "https://bku.tarimorman.gov.tr"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "tr-TR,tr;q=0.9",
    "Referer": "https://bku.tarimorman.gov.tr/",
}

RUHSAT_GRUPLARI = [
    "Akarisit", "Bitki Aktivatörü", "Bitki Gelişim Düzenleyicisi (BGD)",
    "Biyolojik Fungisit", "Biyolojik İnsektisit", "Biyolojik Mücadele Etmeni",
    "Fungisit", "Fungisit + Akarisit", "Herbisit", "İnsektisit",
    "İnsektisit+Akarisit", "Nematisit", "Nematisit+Fungisit",
]

session = requests.Session()
session.headers.update(HEADERS)


def get_bitki_ids():
    """Tum bitki ID'lerini cek."""
    print("Bitki listesi aliniyor...")
    r = session.get(f"{BASE_URL}/Kullanim/TavsiyeArama", timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")

    # Bitki linklerini ara
    bitkiler = []
    links = soup.find_all("a", href=True)
    for link in links:
        href = link.get("href", "")
        if "/Bitki/Details/" in href:
            bid = href.split("/Bitki/Details/")[-1].strip()
            if bid.isdigit():
                bitkiler.append({"id": bid, "ad": link.get_text(strip=True)})

    if not bitkiler:
        # Alternatif: select kutusu
        select = soup.find("select", {"id": "BitId"}) or soup.find("select", {"name": "BitId"})
        if select:
            for opt in select.find_all("option"):
                val = opt.get("value", "").strip()
                text = opt.get_text(strip=True)
                if val and val not in ("0", ""):
                    bitkiler.append({"id": val, "ad": text})

    print(f"  {len(bitkiler)} bitki bulundu.")
    return bitkiler


def scrape_bitki_detay(bitki_id, bitki_ad):
    """Bir bitki icin tum ruhsat gruplarindaki urunleri cek."""
    url = f"{BASE_URL}/Bitki/Details/{bitki_id}"
    urunler = []

    # Once sayfayi cek, form bilgilerini al
    r = session.get(url, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")

    # Form action bul
    form = soup.find("form")
    form_action = url
    if form:
        action = form.get("action", "")
        if action:
            form_action = BASE_URL + action if action.startswith("/") else action

    # Ruhsat grubu select'ten secenekleri al
    ruhsat_select = soup.find("select", {"name": lambda x: x and "ruhsat" in x.lower()})
    if not ruhsat_select:
        ruhsat_select = soup.find("select")

    ruhsat_gruplari = RUHSAT_GRUPLARI
    if ruhsat_select:
        ruhsat_gruplari = []
        for opt in ruhsat_select.find_all("option"):
            val = opt.get("value", "").strip()
            if val and val not in ("0", ""):
                ruhsat_gruplari.append(val)
        if not ruhsat_gruplari:
            ruhsat_gruplari = RUHSAT_GRUPLARI

    # Hidden inputlari topla
    hidden_inputs = {}
    if form:
        for inp in form.find_all("input", {"type": "hidden"}):
            name = inp.get("name")
            val = inp.get("value", "")
            if name:
                hidden_inputs[name] = val

    print(f"  {len(ruhsat_gruplari)} ruhsat grubu bulundu.")

    for grup in ruhsat_gruplari:
        try:
            post_data = dict(hidden_inputs)
            post_data.update({
                "BitId": bitki_id,
                "RuhsatGrubu": grup,
            })

            # Select name bul
            if ruhsat_select:
                select_name = ruhsat_select.get("name", "RuhsatGrubu")
                post_data[select_name] = grup

            r2 = session.post(form_action, data=post_data, timeout=30)
            soup2 = BeautifulSoup(r2.text, "html.parser")

            # Tablo satirlarini bul
            tablo = soup2.find("table")
            if not tablo:
                continue

            rows = tablo.find_all("tr")[1:]  # Header'i atla
            for row in rows:
                cells = row.find_all("td")
                if len(cells) >= 3:
                    urun = {
                        "bitki": bitki_ad,
                        "ruhsat_grubu": grup,
                        "ruhsat_no": cells[0].get_text(strip=True) if len(cells) > 0 else "",
                        "urun_adi": cells[1].get_text(strip=True) if len(cells) > 1 else "",
                        "etken_madde": cells[2].get_text(strip=True) if len(cells) > 2 else "",
                        "firma": cells[3].get_text(strip=True) if len(cells) > 3 else "",
                        "doz": cells[4].get_text(strip=True) if len(cells) > 4 else "",
                        "zarali": cells[5].get_text(strip=True) if len(cells) > 5 else "",
                        "son_ilac_hasat": cells[6].get_text(strip=True) if len(cells) > 6 else "",
                    }
                    urunler.append(urun)

            if rows:
                print(f"    {grup}: {len(rows)} urun")
            time.sleep(0.3)

        except Exception as e:
            print(f"    HATA ({grup}): {e}")
            continue

    return urunler


def scrape_aktif_madde_gruplari(bitki_id, bitki_ad):
    """Aktif madde grup linklerinden urunleri cek."""
    url = f"{BASE_URL}/Bitki/Details/{bitki_id}"
    r = session.get(url, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")

    # AktifMaddeGrup linklerini bul
    am_links = []
    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        if "/AktifMaddeGrup/Details/" in href:
            amid = href.split("/AktifMaddeGrup/Details/")[-1].strip()
            if amid.isdigit():
                am_links.append({"id": amid, "ad": link.get_text(strip=True).replace("#", "").strip()})

    print(f"  {len(am_links)} aktif madde grubu bulundu.")

    urunler = []
    for am in am_links:
        try:
            r2 = session.get(f"{BASE_URL}/AktifMaddeGrup/Details/{am['id']}", timeout=30)
            soup2 = BeautifulSoup(r2.text, "html.parser")

            tablo = soup2.find("table")
            if not tablo:
                continue

            rows = tablo.find_all("tr")[1:]
            for row in rows:
                cells = row.find_all("td")
                if len(cells) >= 2:
                    urun = {
                        "bitki": bitki_ad,
                        "aktif_madde": am["ad"],
                        "ruhsat_no": cells[0].get_text(strip=True) if len(cells) > 0 else "",
                        "urun_adi": cells[1].get_text(strip=True) if len(cells) > 1 else "",
                        "etken_madde": am["ad"],
                        "firma": cells[2].get_text(strip=True) if len(cells) > 2 else "",
                        "doz": cells[3].get_text(strip=True) if len(cells) > 3 else "",
                        "zarali": cells[4].get_text(strip=True) if len(cells) > 4 else "",
                        "son_ilac_hasat": cells[5].get_text(strip=True) if len(cells) > 5 else "",
                    }
                    urunler.append(urun)

            if rows:
                print(f"    {am['ad']}: {len(rows)} urun")
            time.sleep(0.2)

        except Exception as e:
            print(f"    HATA ({am['ad']}): {e}")
            continue

    return urunler


def main():
    print("BKU Scraper v2 basliyor...")
    print("=" * 60)

    # Once domates sera test et (ID=68)
    print("\n[TEST] Domates Sera (ID=68) aktif madde gruplari...")
    urunler = scrape_aktif_madde_gruplari("68", "Domates (Sera)")

    if urunler:
        print(f"\nDomates Sera icin {len(urunler)} urun bulundu!")
        # Kaydet
        with open("bku_domates_sera.json", "w", encoding="utf-8") as f:
            json.dump(urunler, f, ensure_ascii=False, indent=2)
        print("Kaydedildi: bku_domates_sera.json")
        print("\nOrnek urunler:")
        for u in urunler[:5]:
            print(f"  - {u['urun_adi']} ({u['aktif_madde']}) | Doz: {u['doz']}")
        return

    print("\nAktif madde yontemi basarisiz, form POST deneniyor...")
    urunler = scrape_bitki_detay("68", "Domates (Sera)")

    if urunler:
        print(f"\n{len(urunler)} urun bulundu!")
        with open("bku_domates_sera.json", "w", encoding="utf-8") as f:
            json.dump(urunler, f, ensure_ascii=False, indent=2)
        print("Kaydedildi: bku_domates_sera.json")
    else:
        print("\nHicbir urun bulunamadi.")
        print("Site yapisi degismis olabilir.")
        print("HTML kaydediliyor: bku_debug.html")
        r = session.get(f"{BASE_URL}/Bitki/Details/68", timeout=30)
        with open("bku_debug.html", "w", encoding="utf-8") as f:
            f.write(r.text)


if __name__ == "__main__":
    main()
