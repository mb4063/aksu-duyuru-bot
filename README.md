# Aksu Belediyesi Duyuru Botu

GitHub Actions üzerinde günlük çalışan bir bot. [Aksu Belediyesi Duyurular](https://www.aksu.bel.tr/duyurular) sayfasını tarar, önceki günle karşılaştırır ve yeni duyuruları Telegram üzerinden gönderir.

## Özellikler

- Her gün otomatik çalışır (09:00, UTC+3)
- Manuel tetiklemeye de destekler (`workflow_dispatch`)
- Popup/duyuru penceresini filtreler
- İlk çalıştırmada snapshot oluşturur, bildirim göndermez
- Yeni duyuru bulunmazsa sessizce devam eder
- Snapshot'ı repo'ya geri kaydeder (geçmiş referansı)

## Kurulum

### 1. Repository'yi forklayın veya kopyalayın

Bu projeyi kendi GitHub hesabınıza alın.

### 2. Telegram Botu oluşturun

1. Telegram'da [@BotFather](https://t.me/BotFather) ile konuşun.
2. `/newbot` komutunu gönderin ve ad verin.
3. Size verilen **bot token**'ı kopyalayın (örn: `123456:ABC-DEF...`).

### 3. Chat ID öğrenin

Botunuza bir mesaj atın, ardından şu URL'yi tarayıcıda açın:

```
https://api.telegram.org/bot<TOKEN>/getUpdates
```

`chat` altındaki `id` değerini kopyalayın (örn: `123456789` veya `-1001234567890` grup için).

### 4. GitHub Secrets ayarlayın

Repo'nuzda **Settings → Secrets and variables → Actions → New repository secret** bölümünden şu iki secret'ı ekleyin:

| Secret Adı | Değer |
|-----------|-------|
| `TELEGRAM_BOT_TOKEN` | BotFather'dan aldığınız token |
| `TELEGRAM_CHAT_ID` | Öğrendiğiniz chat ID |

### 5. Workflow izinlerini kontrol edin

**Settings → Actions → General** sayfasında:

- **Workflow permissions** bölümünde `Read and write permissions` seçili olduğundan emin olun (snapshot dosyasını commit'leyebilmesi için).

### 6. İlk çalıştırma

Actions sekmesinden **Aksu Duyuru Scraper** workflow'unu seçip **Run workflow** ile manuel başlatın. İlk çalıştırma snapshot oluşturur, bildirim göndermez.

## Dosya Yapısı

```
.
├── .github/workflows/scraper.yml   # GitHub Actions tanımı
├── data/
│   └── duyurular.json              # Önceki duyuruların snapshot'ı
├── scraper.py                      # Ana Python scripti
├── requirements.txt                # Python bağımlılıkları
└── README.md                       # Bu dosya
```

## Cron Ayarını Değiştirme

`.github/workflows/scraper.yml` dosyasındaki `cron` satırını düzenleyin:

```yaml
  schedule:
    - cron: '0 9 * * *'   # Her gün 09:00
```

Cron formatı UTC'dir. Türkiye saati için şu an UTC+3 uygulanır. Örneğin 09:00 UTC = 12:00 TSİ.

## Sorun Giderme

- **Sayfada hiç duyuru bulunamadı hatası**: Aksu Belediyesi sitesinin HTML yapısı değişmiş olabilir. `scraper.py` içindeki seçicileri güncelleyin.
- **Telegram bildirimi gitmiyor**: `TELEGRAM_BOT_TOKEN` ve `TELEGRAM_CHAT_ID` secret'larını kontrol edin. Botun chat'e ekli olduğundan ve başlatıldığından emin olun.
- **Commit hatası**: Actions'ın yazma izni olduğundan emin olun (repo Settings > Actions > General).
