import os
import json
import requests
from bs4 import BeautifulSoup

URL = "https://www.aksu.bel.tr/duyurular"
DATA_FILE = "data/duyurular.json"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def fetch_announcements():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        )
    }
    resp = requests.get(URL, headers=headers, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    popup = soup.find("div", attrs={"role": "dialog", "aria-label": "Popup"})

    announcements = []
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if not href.startswith("/duyurular/"):
            continue

        # popup filtresi
        if popup and a.find_parent("div", attrs={"role": "dialog", "aria-label": "Popup"}):
            continue

        h3 = a.find("h3")
        if not h3:
            continue

        title = h3.get_text(strip=True)
        full_url = f"https://www.aksu.bel.tr{href}"

        announcements.append({"url": full_url, "title": title})

    return announcements


def load_previous():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_current(announcements):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(announcements, f, ensure_ascii=False, indent=2)


def send_telegram(new_announcements):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram kimlik bilgileri eksik, bildirim atlanıyor.")
        return

    chunks = []
    current = "🔔 *Aksu Belediyesi'nde Yeni Duyurular:*\n"

    for ann in new_announcements:
        block = f"\n• {ann['title']}\n🔗 {ann['url']}"
        if len(current) + len(block) > 4000:
            chunks.append(current)
            current = block
        else:
            current += block
    chunks.append(current)

    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    for text in chunks:
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        }
        resp = requests.post(api_url, json=payload, timeout=30)
        resp.raise_for_status()

    print("Telegram bildirimi başarıyla gönderildi.")


def main():
    print("Duyurular çekiliyor...")
    current = fetch_announcements()
    print(f"Sayfada {len(current)} duyuru bulundu.")

    if not current:
        raise RuntimeError("Sayfada hiç duyuru bulunamadı, site yapısı değişmiş olabilir.")

    previous = load_previous()
    previous_urls = {ann["url"] for ann in previous}

    new_announcements = [ann for ann in current if ann["url"] not in previous_urls]

    if previous and new_announcements:
        print(f"{len(new_announcements)} yeni duyuru tespit edildi.")
        send_telegram(new_announcements)
    elif not previous:
        print("İlk çalıştırma: snapshot oluşturuluyor, bildirim gönderilmiyor.")
    else:
        print("Yeni duyuru yok.")

    save_current(current)
    print("Snapshot kaydedildi.")


if __name__ == "__main__":
    main()
