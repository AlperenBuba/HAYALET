# 👻 HAYALET v1.0

**Raspberry Pi Zero 2W için dokunmatik ekranlı, Tor destekli anonim OSINT cyberdeck.**

Küçük, taşınabilir, avuç içi büyüklüğünde bir siber keşif aracı. OnionShare, Nmap, 13 OSINT aracı, çift panelli dosya yöneticisi ve daha fazlası tek bir Tkinter arayüzünde.

[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-green.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-red.svg)](https://www.raspberrypi.com/)

---

## ✨ Özellikler

### 🔐 Anonimlik
- **Tor Entegrasyonu** — Otomatik `torrc` yapılandırması (ControlPort, TransPort, DNSPort)
- **IP Rotasyonu** — Her N istekte otomatik yeni devre (`NEWNYM`)
- **Tor'suz Mod** — Riskli ama hızlı, "Continue without Tor" seçeneği
- **SOCKS5 Proxy** — OSINT araçları `socks5h://127.0.0.1:9050` üzerinden çalışır

### 🌐 Ağ Araçları
- **Nmap Scanner** — 12 tarama modu (INTENSE, ALL PORTS, VULN, STEALTH, QUICK, OS+VER, PING, UDP, TRACEROUTE, DFLT SCRIPTS, ARP, EVASION)
- **Cihaz Keşfi** — Otomatik ağ taraması (hostname + IP çözümleme)
- **Dir Scanner** — Baseline detection ile false positive filtreleme, wordlist desteği, DIRECT/TOR seçeneği
- **Wi-Fi Yönetimi** — SSID tarama, bağlanma, şifre gösterimi

### 🔍 OSINT (13 Araç)

| Araç | Açıklama |
|---|---|
| WHOIS | Domain kayıt bilgileri (RDAP) |
| DNS Lookup | A, AAAA, MX, TXT, NS, CNAME |
| Sub Enum | crt.sh üzerinden subdomain keşfi |
| HTTP Headers | Sunucu header'ları |
| SSL Cert | Sertifika geçmişi |
| IP Info | Geo + ISP bilgisi (ip-api + ipwho.is) |
| Reverse IP | Aynı sunucudaki domain'ler |
| Tech Stack | Framework/CMS tespiti |
| Wayback | Arşiv snapshot'ları |
| Robots.txt | Gizli dizinler |
| Sitemap.xml | Site haritası |
| Sec Headers | 6 güvenlik header kontrolü |
| Port Check | Tek port testi (Tor üzerinden) |

### 🧅 OnionShare
- **Onion Chat** — Tor üzerinden anonim sohbet
- **File Receive** — Tor üzerinden dosya alma
- **File Send** — Tor üzerinden dosya paylaşımı
- PUBLIC/PRIVATE mod desteği
- `.onion` adresi otomatik dosyaya kaydedilir

### 🗂️ Dosya Yönetimi
- **Dual Pane File Manager** — Norton Commander tarzı çift panel
- **USB Otomatik Algılama** — `/media/*` ve `/mnt/*` mount noktaları
- **İşlemler:** Kopyala, Taşı, Yeniden Adlandır, Sil, Yeni Dizin
- **Renk Kodlu Aktif Panel** — Yeşil kenarlık hangi panelin aktif olduğunu gösterir

### 🛠️ Yardımcı Araçlar
- MAC Changer (rastgele MAC)
- Analog Clock
- Hesap Makinesi (Normal / Scientific / Programmer)
- Speedtest
- Snake (dokunmatik kontrollü)

### 🎨 Arayüz
- 480×320 dokunmatik ekran için optimize
- Sanal klavyeler (Wi-Fi, Nmap, File Manager, Search)
- **Quick Launcher** — SEARCH butonu ile 26 özellik aranabilir
- Log alanları salt-okunur (metin seçimi engellendi)
- 500 satır log limiti (RAM dostu)
- Tam ekran (kiosk) modu

---

## 🖥️ Donanım Gereksinimleri

| Bileşen | Minimum | Önerilen |
|---|---|---|
| **SBC** | Raspberry Pi Zero 2W | Raspberry Pi 4 (2GB+) |
| **RAM** | 512 MB (zram aktif) | 1 GB+ |
| **Depolama** | 8 GB (USB flash önerilen) | 16 GB+ |
| **Ekran** | 3.5" TFT (480×320) | 5" HDMI dokunmatik |
| **Ağ** | Dahili Wi-Fi | Harici Wi-Fi + monitor mode |
| **OS** | Raspberry Pi OS 64-bit Lite | Kali ARM / Debian |

**Not:** Zram aktifse 512 MB RAM yeterlidir. SD kart yerine USB flash önerilir (dayanıklılık + hız).

---

## 📦 Kurulum

### 1. İşletim Sistemi

**Raspberry Pi OS 64-bit Lite** (önerilen):

```bash
# Raspberry Pi Imager ile SD/USB'ye yaz
# İlk açılışta: sudo raspi-config → Expand Filesystem
```

**Ekran sürücüsü** (3.5" TFT için):

```bash
git clone https://github.com/goodtft/LCD-show.git
cd LCD-show
sudo ./LCD35-show
sudo reboot
```

### 2. Sistem Paketleri

```bash
sudo apt update
sudo apt install -y \
    python3 python3-pip python3-tk python3-venv \
    python3-pil python3-pil.imagetk \
    tor proxychains4 nmap network-manager wireless-tools \
    curl git
```

**Speedtest (opsiyonel):**

```bash
sudo apt install -y speedtest-cli
```

### 3. Python Bağımlılıkları

```bash
cd ~/hayalet
pip3 install -r requirements.txt
```

### 4. Tor Yapılandırması

**Otomatik:** İlk açılışta kod `torrc` dosyasını otomatik düzenler.

**Manuel kontrol:**

```bash
sudo nano /etc/tor/torrc
```

Şu satırların yorumlu olmadığından emin ol:

```
ControlPort 9051
CookieAuthentication 1
TransPort 9040
DNSPort 5353
VirtualAddrNetworkIPv4 10.192.0.0/10
AutomapHostsOnResolve 1
```

Sonra:

```bash
sudo systemctl enable tor
sudo systemctl restart tor
sudo systemctl status tor  # "active (running)" görmelisin
```

### 5. OnionShare

OnionShare izole bir venv'de kurulmalı:

```bash
python3 -m venv ~/onionshare-env
~/onionshare-env/bin/pip install --upgrade pip
~/onionshare-env/bin/pip install onionshare-cli
```

**Doğrulama:**

```bash
~/onionshare-env/bin/onionshare-cli --version
```

### 6. Klasör Yapısı

Uygulama aşağıdaki klasörleri otomatik oluşturur, ama önceden oluşturabilirsin:

```bash
mkdir -p ~/cyberdeck_icons
mkdir -p ~/wordlists
mkdir -p ~/nmap_scans
mkdir -p ~/dirscan_logs
mkdir -p ~/osint_logs
mkdir -p ~/received_files
mkdir -p ~/send_files
mkdir -p ~/downloads
```

**`cyberdeck_icons/`** içine `ghost.png` (veya `.jpg`) koymalısın — logo için.

**`~/wordlists/`** içine wordlist dosyaları (`.txt`, `.lst`) ekleyebilirsin. Ayrıca `/usr/share/wordlists/` (Kali/Debian) otomatik taranır.

### 7. OnionShare Yollarını Düzenle

`cyberdeck.py` dosyasında `/home/buba/` yollarını kendi kullanıcı adına göre düzenle:

```bash
sed -i "s|/home/buba/|$HOME/|g" cyberdeck.py
```

### 8. Çalıştırma

```bash
cd ~/hayalet
python3 cyberdeck.py
```

**Otomatik başlatma** (opsiyonel):

```bash
echo "python3 ~/hayalet/cyberdeck.py" >> ~/.xinitrc
```

---

## 🚀 Kullanım

### Başlangıç

1. **CONNECT TO TOR** — Tor başlat ve doğrula (önerilen)
2. **⚠ Continue without Tor** — Riskli, sadece test için

### Menü Navigasyonu

- **Sağ ok (›)** — Sonraki sayfa
- **Sol ok (‹)** — Önceki sayfa
- **SEARCH** — Hızlı arama (26 özellik aranabilir)

### Sayfalar

| Sayfa | İçerik |
|---|---|
| 1 | OnionShare Chat, File Receive, File Send, Nmap |
| 2 | SMS Bomber*, MAC Changer, Dir Scan, WHOIS |
| 3 | DNS, Sub Enum, HTTP Headers, SSL Cert |
| 4 | IP Info, Reverse IP, Tech Stack, Wayback |
| 5 | Robots.txt, Sitemap.xml, Sec Headers, Port Check |
| 6 | File Manager, Clock, Calculator, Speedtest, Snake |

*SMS Bomber varsayılan olarak **kapalıdır** (`ENABLE_SMS_BOMBER = False`).

### Hızlı İpuçları

- **Log'ları kaydır:** Log alanlarında yukarı/aşağı kaydırılabilir
- **Dosya kopyala:** File Manager'da TAB ile panel değiştir → COPY
- **USB'ye dön:** File Manager'da sarı path yazısına tıkla
- **OSINT'te IP değiştir:** NEW ID butonu

---

## 🐛 Sorun Giderme

| Sorun | Çözüm |
|---|---|
| `ImportError: No module named 'PIL'` | `pip3 install Pillow` |
| `Tor not running` | `sudo systemctl start tor` |
| `Permission denied: nmap` | Nmap sudo'suz çalışmaz, `sudo -v` ile yetki ver |
| OnionShare boş çıkıyor | `ls ~/onionshare-env/bin/onionshare-cli` ile varlığını kontrol et |
| Wi-Fi listesi boş | `nmcli device status` ile NetworkManager aktif mi? |
| Ekran donuyor | `free -h` ile RAM kontrol et, zram aç |
| `socks5h` bağlanamıyor | `curl --socks5-hostname 127.0.0.1:9050 ifconfig.me` ile test et |
| Log'lar kaybolmuyor | `~/osint_logs/`, `~/nmap_scans/` dolu olabilir, `rm -rf ~/osint_logs/*` |

### Zram Aktifleştirme (512 MB için)

```bash
sudo apt install -y zram-tools
sudo systemctl enable --now zramswap
```

---

## 📁 Proje Yapısı

```
hayalet/
├── cyberdeck.py          # Ana uygulama (~3300 satır)
├── requirements.txt      # Python bağımlılıkları
├── README.md             # Bu dosya
├── LICENSE               # GPL v2
├── .gitignore            # Git için
├── screenshots/          # Ekran görüntüleri
│   ├── boot.png
│   ├── menu.png
│   └── ...
└── docs/
    └── HARDWARE.md       # Donanım kurulum rehberi (opsiyonel)
```

Kullanıcı dizininde:

```
~/cyberdeck_icons/       # Ghost logosu ve ikonlar
~/wordlists/             # Dir Scan wordlist'leri
~/nmap_scans/            # Nmap çıktıları
~/dirscan_logs/          # Dir Scan çıktıları
~/osint_logs/            # OSINT çıktıları
~/received_files/        # OnionShare alınan dosyalar
~/send_files/            # OnionShare gönderilen dosyalar
~/onionshare-env/        # OnionShare venv
```

---

## 🤝 Katkıda Bulunma

1. Fork et
2. Feature branch oluştur (`git checkout -b feature/yeni-ozellik`)
3. Commit et (`git commit -m 'Yeni özellik: ...'`)
4. Push et (`git push origin feature/yeni-ozellik`)
5. Pull Request aç

**Kod stili:** PEP 8 uyumlu, yorumlar Türkçe, değişken isimleri anlamlı.

---

## 📄 Lisans

Bu proje **GNU General Public License v2.0** altında lisanslanmıştır.

[![GPLv2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html)

Detaylar için [LICENSE](LICENSE) dosyasına bakın.

**Özet:** Bu kodu kullanabilir, değiştirebilir ve dağıtabilirsiniz. Ancak türev çalışmalarınızı da **GPL v2** ile ve **açık kaynak** olarak paylaşmak zorundasınız. Kapalı kaynaklı ticari bir üründe kullanamazsınız.

---

## ⚠️ Yasal Uyarı

Bu proje **eğitim ve kişisel kullanım** için tasarlanmıştır. Yalnızca:

- **Kendi** sunucularınızda
- **Yasal izin aldığınız** hedeflerde
- **CTF yarışmalarında**
- **Bug bounty programlarında** (kapsamı okuyarak)

kullanın.

**İzinsiz tarama** Türkiye'de **TCK 243** (bilişim sistemine girme) ve **TCK 244** (bilişim sisteminin işleyişini engelleme/bozma) kapsamında suçtur.

**Tor kullanmak** yasal sorumluluğu ortadan kaldırmaz. Sadece teknik izini gizler, yasal sorumluluğu **gizlemez**.

Bu kodun kullanımından doğacak her türlü yasal sorumluluk **kullanıcıya aittir**.

---

## 🙏 Teşekkürler

- **Raspberry Pi Foundation** — Donanım
- **Tor Project** — Anonimlik altyapısı
- **OnionShare** — Güvenli dosya paylaşımı
- **Nmap** — Ağ tarama
- **crt.sh, rdap.org, ip-api.com, ipwho.is** — OSINT API'leri

---

**⭐ Projeyi beğendiyseniz yıldız verin!**