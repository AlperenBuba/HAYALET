# 👻 HAYALET v1.0

**Raspberry Pi Zero 2W için dokunmatik ekranlı, Tor destekli anonim OSINT cyberdeck.**

Küçük, taşınabilir, avuç içi büyüklüğünde bir siber keşif aracı. 
OnionShare, Nmap, 13 OSINT aracı, çift panelli dosya yöneticisi ve daha fazlası 
tek bir Tkinter arayüzünde.

[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-green.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-red.svg)](https://www.raspberrypi.com/)

---

## 📸 Ekran Görüntüleri

| Boot | Ana Menü |
|---|---|
| ![boot](screenshots/boot.png) | ![menu](screenshots/menu.png) |

| Nmap | WHOIS | File Manager |
|---|---|---|
| ![nmap](screenshots/nmap.png) | ![whois](screenshots/whois.png) | ![fm](screenshots/filemanager.png) |

*(Ekran görüntüleri `screenshots/` klasörüne eklenmelidir)*

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