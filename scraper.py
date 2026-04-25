import os
import json
import requests

API_URL = "https://cms.aksu.bel.tr/wp-json/wp/v2/duyurular?per_page=100"
BASE_URL = "https://www.aksu.bel.tr/duyurular"
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
    resp = requests.get(API_URL, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    announcements = []
    for item in data:
        post_id = item.get("id")
        title = item.get("title", {}).get("rendered", "").strip()
        slug = item.get("slug", "")
        date = item.get("date", "")

        if not post_id or not title or not slug:
            continue

        public_url = f"{BASE_URL}/{slug}"
        announcements.append({
            "id": post_id,
            "title": title,
            "url": public_url,
            "date": date,
        })

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


def send_telegram(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram kimlik bilgileri eksik, bildirim atlanıyor.")
        return False

    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "disable_web_page_preview": True,
    }
    try:
        resp = requests.post(api_url, json=payload, timeout=30)
        resp.raise_for_status()
        print("Telegram bildirimi gonderildi.")
        return True
    except Exception as e:
        print(f"Telegram gonderimi basarisiz: {e}")
        return False


def send_telegram_list(header, announcements):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram kimlik bilgileri eksik, bildirim atlanıyor.")
        return

    chunks = []
    current = header

    for ann in announcements:
        block = f"\n- {ann['title']}\n  {ann['url']}"
        if len(current) + len(block) > 4000:
            chunks.append(current)
            current = block
        else:
            current += block
    chunks.append(current)

    for text in chunks:
        send_telegram(text)


def main():
    print("Duyurular cekiliyor...")
    current = fetch_announcements()
    print(f"API'den {len(current)} duyuru alindi.")

    if not current:
        raise RuntimeError("API'den duyuru alinamadi, baglanti veya yapi degismis olabilir.")

    previous = load_previous()
    previous_ids = {ann["id"] for ann in previous}

    new_announcements = [ann for ann in current if ann["id"] not in previous_ids]

    try:
        if previous and new_announcements:
            print(f"{len(new_announcements)} yeni duyuru tespit edildi.")
            send_telegram_list(
                "🔔 Aksu Belediyesi'nde Yeni Duyurular:",
                new_announcements,
            )
        elif not previous:
            print("Ilk calistirma: mevcut duyurular Telegram'a gonderiliyor...")
            send_telegram_list(
                "🤖 Bot baslatildi. Takip edilen duyurular:",
                current,
            )
        else:
            print("Yeni duyuru yok.")
            send_telegram("📭 Aksu Belediyesi'nde yeni duyuru yok.")
    finally:
        save_current(current)
        print("Snapshot kaydedildi.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        error_text = f"⚠️ Bot Hatasi: {type(e).__name__}: {e}"
        print(error_text)
        send_telegram(error_text)
        raise SystemExit(1)
