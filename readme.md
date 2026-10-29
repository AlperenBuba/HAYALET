# 👻 HAYALET v1.0

**Raspberry Pi Zero 2W için dokunmatik ekranlı, Tor destekli anonim OSINT cyberdeck.**

Küçük, taşınabilir, avuç içi büyüklüğünde bir siber keşif aracı. OnionShare, Nmap, 13 OSINT aracı, çift panelli dosya yöneticisi ve daha fazlası tek bir Tkinter arayüzünde.

[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-green.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-red.svg)](https://www.raspberrypi.com/)

---

## 📸 Galeri

<table>
  <tr>
    <td align="center"><b>Boot Screen</b><br><img src="screenshots/boot.jpeg" width="380"></td>
    <td align="center"><b>Ana Menü</b><br><img src="screenshots/menu.jpeg" width="380"></td>
  </tr>
  <tr>
    <td align="center"><b>Nmap Scanner</b><br><img src="screenshots/nmap.jpeg" width="380"></td>
    <td align="center"><b>Dir Scanner</b><br><img src="screenshots/dirscan.jpeg" width="380"></td>
  </tr>
  <tr>
    <td align="center"><b>WHOIS (OSINT)</b><br><img src="screenshots/whois.jpeg" width="380"></td>
    <td align="center"><b>File Manager</b><br><img src="screenshots/filemanager.jpeg" width="380"></td>
  </tr>
  <tr>
    <td align="center"><b>OnionShare Chat</b><br><img src="screenshots/onionchat.jpeg" width="380"></td>
    <td align="center"><b>Quick Launcher</b><br><img src="screenshots/search.jpeg" width="380"></td>
  </tr>
</table>

> **Not:** Tüm Ekran görüntüleri `screenshots/` klasöründedir. Diğer ekran görüntüleri için `screenshots/` klasörünü kontrol edin.

---

## ✨ Özellikler

### 🔐 Anonimlik
- **Tor Entegrasyonu** — Otomatik `torrc` yapılandırması (ControlPort, TransPort, DNSPort)
- **IP Rotasyonu** — Her N istekte otomatik yeni devre (`NEWNYM`)
- **Tor'suz Mod** — Riskli ama hızlı, "Continue without Tor" seçeneği
- **SOCKS5 Proxy** — OSINT araçları `socks5h://127.0.0.1:9050` üzerinden çalışır

### 🌐 Ağ Araçları
- **Nmap Scanner** — 12 tarama modu
- **Cihaz Keşfi** — Otomatik ağ taraması (hostname + IP çözümleme)
- **Dir Scanner** — Baseline detection ile false positive filtreleme
- **Wi-Fi Yönetimi** — SSID tarama, bağlanma, şifre gösterimi

### 🔍 OSINT (13 Araç)
| Araç | Açıklama |
|---|---|
| WHOIS | Domain kayıt bilgileri (RDAP) |
| DNS Lookup | A, AAAA, MX, TXT, NS, CNAME |
| Sub Enum | crt.sh üzerinden subdomain keşfi |
| HTTP Headers | Sunucu header'ları |
| SSL Cert | Sertifika geçmişi |
| IP Info | Geo + ISP bilgisi |
| Reverse IP | Aynı sunucudaki domain'ler |
| Tech Stack | Framework/CMS tespiti |
| Wayback | Arşiv snapshot'ları |
| Robots.txt | Gizli dizinler |
| Sitemap.xml | Site haritası |
| Sec Headers | 6 güvenlik header kontrolü |
| Port Check | Tek port testi (Tor üzerinden) |

### 🧅 OnionShare
- Onion Chat, File Receive, File Send
- PUBLIC/PRIVATE mod desteği
- `.onion` adresi otomatik dosyaya kaydedilir

### 🗂️ Dosya Yönetimi
- **Dual Pane File Manager** — Norton Commander tarzı
- **USB Otomatik Algılama**
- Kopyala, Taşı, Yeniden Adlandır, Sil, Yeni Dizin

### 🛠️ Yardımcı Araçlar
- MAC Changer, Analog Clock, Calculator, Speedtest, Snake

### 🎨 Arayüz
- 480×320 dokunmatik ekran için optimize
- Sanal klavyeler (Wi-Fi, Nmap, File Manager, Search)
- **Quick Launcher** — SEARCH butonu ile 26 özellik aranabilir
- 500 satır log limiti (RAM dostu)
- Tam ekran (kiosk) modu

---

## 🖥️ Donanım Gereksinimleri

| Bileşen | Minimum | Önerilen |
|---|---|---|
| **SBC** | Raspberry Pi Zero 2W | Raspberry Pi 4 (2GB+) |
| **RAM** | 512 MB (zram aktif) | 1 GB+ |
| **Depolama** | 8 GB USB flash | 16 GB+ USB flash |
| **Ekran** | 3.5" TFT (480×320) | 5" HDMI dokunmatik |
| **OS** | Raspberry Pi OS 64-bit Lite | Kali ARM / Debian |

**Platform Notu:** Bu proje Linux (Raspberry Pi OS / Debian) için tasarlanmıştır. macOS veya Windows'ta çalıştırırsanız sadece OSINT araçları, Clock, Calculator ve Snake çalışır. Wi-Fi yönetimi, MAC Changer ve Nmap gibi Linux komutlarına bağımlı özellikler çalışmayacaktır.

---

## 🚀 Hızlı Kurulum (Önerilen)

Tüm bağımlılıkları otomatik kuran script:

```bash
git clone https://github.com/KULLANICI_ADIN/hayalet.git
cd hayalet
chmod +x install.sh
./install.sh
python3 cyberdeck.py
```

`install.sh` şunları yapar:
- Sistem paketlerini kurar (`tor`, `nmap`, `python3-tk`, vs.)
- Python bağımlılıklarını kurar
- OnionShare venv oluşturur
- Tor'u yapılandırır
- Gerekli klasörleri oluşturur
- Zram'ı aktifleştirir

**Sorun çıkarsa:** `./check_deps.sh` ile hangi bağımlılığın eksik olduğunu gör.

---

## 📦 Manuel Kurulum

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
    curl git speedtest-cli zram-tools
```

### 3. Python Bağımlılıkları

```bash
pip3 install -r requirements.txt
```

### 4. OnionShare

```bash
python3 -m venv ~/onionshare-env
~/onionshare-env/bin/pip install --upgrade pip
~/onionshare-env/bin/pip install onionshare-cli
```

### 5. Tor Yapılandırması

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
sudo systemctl status tor
```

### 6. Klasör Yapısı

```bash
mkdir -p ~/cyberdeck_icons ~/wordlists ~/nmap_scans
mkdir -p ~/dirscan_logs ~/osint_logs
mkdir -p ~/received_files ~/send_files ~/downloads
```

**`~/cyberdeck_icons/`** içine `ghost.png` ekle (logo için).

**`~/wordlists/`** içine wordlist dosyaları ekleyebilirsin.

### 7. Yol Düzeltme

`cyberdeck.py` dosyasında `/home/buba/` yolları varsa kendi kullanıcı adına göre düzelt:

```bash
sed -i "s|/home/buba/|$HOME/|g" cyberdeck.py
```

### 8. Çalıştırma

```bash
python3 cyberdeck.py
```

---

## 📖 Kullanım Rehberi

### 🎬 Başlangıç Ekranı

![Boot](screenshots/boot.jpeg)

Program açıldığında **Boot Screen** karşılar:

- **👻 Ghost logosu** — Ortada dönen animasyon
- **WI-FI** — Sağ üstte, bağlı ağın SSID'sini gösterir
- **CONNECT TO TOR** — Tor'u başlatır ve doğrular (önerilen)
- **⚠ Continue without Tor** — Tor olmadan devam (riskli)
- **SYSTEM** — Altta kırmızı buton, kapatma menüsü

**Öneri:** Normal kullanımda **CONNECT TO TOR** ile başla. Tor bağlanana kadar 30-60 saniye bekler, ardından ana menüye geçer.

---

### 🏠 Ana Menü

![Menu](screenshots/menu.jpeg)

Ana menüde **6 sayfa** arasında gezinirsin:

- **Sağ ok (›)** — Sonraki sayfa
- **Sol ok (‹)** — Önceki sayfa
- **SEARCH** — Hızlı arama (26 özellik aranabilir)
- **WI-FI** — Wi-Fi yönetimi
- **HAYALET v1.0** — Sol üstte sürüm bilgisi
- **SYSTEM** — Altta kırmızı buton, kapatma

#### Sayfa Düzeni

| Sayfa | Butonlar |
|---|---|
| **1** | OnionShare Chat, File Receive, File Send, Nmap |
| **2** | SMS Bomber*, MAC Changer, Dir Scan, WHOIS |
| **3** | DNS, Sub Enum, HTTP Headers, SSL Cert |
| **4** | IP Info, Reverse IP, Tech Stack, Wayback |
| **5** | Robots.txt, Sitemap.xml, Sec Headers, Port Check |
| **6** | File Manager, Clock, Calculator, Speedtest, Snake |

*SMS Bomber varsayılan olarak **kapalıdır** (`ENABLE_SMS_BOMBER = False`).

---

### 🔍 Quick Launcher (SEARCH)

![Search](screenshots/search.jpeg)

**SEARCH** butonuna bas → tam ekran arama menüsü açılır:

1. **Üst:** Arama kutusu (yazdığın metin)
2. **Orta:** Filtrelenmiş uygulama ızgarası
3. **Alt:** Sanal klavye (qwerty)

**Kullanım:**
- Klavyeden `who` yaz → sadece **WHOIS** kalır
- Butona tıkla → direkt o sayfaya gider
- **X** butonu → aramayı kapat
- **SPACE / DEL** → boşluk ve silme

26 özellik arasında tek tuşla arama yapabilirsin.

---

### 🌐 Nmap Scanner

![Nmap](screenshots/nmap.jpeg)

**Adım 1: Hedef Seç**
- **AUTO SCAN** — Otomatik olarak tüm ağı tarar (`192.168.1.0/24`)
- **CUSTOM TARGET** — Manuel IP gir veya cihaz seç
- **CLEAR SAVED SCANS** — Eski taramaları sil

**Adım 2: Tarama Modu Seç** (12 mod)

| Mod | Komut | Kullanım |
|---|---|---|
| **INTENSE** | `-A -T4` | Detaylı tarama |
| **ALL PORTS** | `-p- -T4` | Tüm portlar (yavaş) |
| **VULN** | `--script vuln` | Zafiyet taraması |
| **STEALTH** | `-sS -T2 -f` | Gizli tarama |
| **QUICK** | `-F -T4` | Hızlı (top 100) |
| **OS+VER** | `-sV -O` | OS + servis tespiti |
| **PING** | `-sn` | Sadece ping |
| **UDP** | `-sU --top 50` | UDP portları |
| **TRACEROUTE** | `--traceroute` | Rota takibi |
| **DFLT SCRIPTS** | `-sC` | Varsayılan scriptler |
| **ARP SCAN** | `-sn -PR` | ARP taraması |
| **EVASION** | `-f -T2` | IDS atlatma |

**Çıktı:** `~/nmap_scans/nmap_YYYYMMDD_HHMMSS_mod.txt` — her tarama ayrı dosya.

**Renk Anlamları:**
- 🟢 **Yeşil** — Yoğun tarama (yavaş ama detaylı)
- 🟡 **Turuncu** — Zafiyet taraması
- ⚪ **Gri** — Hızlı/hafif tarama

---

### 🔎 Dir Scanner

![Dir Scan](screenshots/dirscan.jpeg)

**4 Aşamalı Wizard:**

1. **URL Gir** — `http://example.com` (veya sadece `example.com`)
2. **Mod Seç** — QUICK (150 kelime) veya WORDLIST (dosya seç)
3. **Bağlantı Seç** — DIRECT (hızlı) veya VIA TOR (anonim)
4. **Sonuçları İzle**

**Wordlist Kaynakları:**
- `~/wordlists/`
- `/usr/share/wordlists/` (Kali)
- `./wordlists/` (proje dizini)

**Baseline Detection:** Sunucu tüm yollara `200` dönerse, boyut filtresi ile false positive elenir.

**Loglar:** `~/dirscan_logs/YYYYMMDD_HHMMSS_domain.txt`

**BACK Tuşu:**
- Tarama sırasında basarsan → durdurur, URL ekranına döner
- Tarama bittikten sonra → bir üst menüye döner

---

### 🔍 OSINT Araçları (13 Adet)

Tüm OSINT araçları aynı şablonu kullanır:

![WHOIS](screenshots/whois.jpegf)

**Her Araçta:**
- **Hedef girişi** — Domain, IP veya URL
- **RUN** — Sorguyu başlat
- **CLEAR** — Girişi temizle
- **NEW ID** — Tor devresini yenile (IP değiştir)
- **Sanal klavye** — 4 satır (sayı + harf + özel karakter)

**Çıktı:** `~/osint_logs/{TOOL}_{tarih}_{hedef}.txt`

**Araçların Kullanımı:**

#### WHOIS
```
Hedef: example.com
Çıktı: Domain sahibi, kayıt/bitiş tarihi, nameserver'lar
```

#### DNS Lookup
```
Hedef: example.com
Çıktı: A, AAAA, MX, TXT, NS, CNAME kayıtları
```

#### Sub Enum
```
Hedef: example.com
Çıktı: crt.sh üzerinden tüm subdomain'ler
Örnek: admin.example.com, dev.example.com, ...
```

#### HTTP Headers
```
Hedef: https://example.com
Çıktı: Server, X-Powered-By, Set-Cookie, vs.
```

#### SSL Cert
```
Hedef: example.com
Çıktı: Sertifika geçmişi, issuer, subject
```

#### IP Info
```
Hedef: 8.8.8.8
Çıktı: Ülke, şehir, ISP, ASN, koordinatlar
```

#### Reverse IP
```
Hedef: 8.8.8.8
Çıktı: Aynı IP'deki domain'ler
```

#### Tech Stack
```
Hedef: https://example.com
Çıktı: WordPress, Nginx, PHP 7.4, jQuery, ...
```

#### Wayback
```
Hedef: example.com
Çıktı: En son arşiv tarihi + URL
```

#### Robots.txt
```
Hedef: example.com
Çıktı: Disallow kuralları (gizli dizinler)
```

#### Sitemap.xml
```
Hedef: example.com
Çıktı: Tüm URL'ler (SEO haritası)
```

#### Sec Headers
```
Hedef: https://example.com
Çıktı: 6 güvenlik header kontrolü (HSTS, CSP, X-Frame, ...)
```

#### Port Check
```
Hedef: 8.8.8.8:53
Çıktı: Port OPEN / CLOSED (Tor üzerinden)
```

---

### 🧅 OnionShare

![OnionChat](screenshots/onionchat.jpeg)

3 mod:

**1. Onion Chat**
- Tıkla → PUBLIC/PRIVATE seç
- **START** → Tor üzerinden chat odası kurulur
- `.onion` adresi `~/onionshare_chat.txt`'ye kaydedilir

**2. File Receive**
- Tor üzerinden dosya al
- Dosyalar `~/received_files/`'a indirilir

**3. File Send**
- `~/send_files/` klasöründekileri paylaş
- Boşsa: "Empty dir!" uyarısı

**PUBLIC vs PRIVATE:**
- **PUBLIC** — Herkes `.onion` adresiyle bağlanabilir
- **PRIVATE** — Sadece davet edilenler (private key gerekir)

---

### 🗂️ File Manager

![File Manager](screenshots/filemanager.jpeg)

**Dual-Pane** (Norton Commander tarzı):

- **Sol Panel** — USB bellek (otomatik)
- **Sağ Panel** — Ev dizini (`~`)
- **Aktif Panel** — Yeşil kenarlık

**Kontroller:**
- **TAB** — Paneller arası geçiş
- **OPEN** — Seçili dosya/dizini aç
- **UP** — Üst dizine çık
- **REFRESH** — Yenile
- **COPY** — Karşı panele kopyala
- **MOVE** — Karşı panele taşı
- **RENAME** — Yeniden adlandır
- **DELETE** — Sil (onaylı)
- **NEW DIR** — Yeni klasör

**USB'ye Dön:** Üstteki sarı path yazısına tıkla.

**Klavye:** Yeni dosya/klasör oluştururken açılır (sayı + harf + özel karakter).

---

### 📶 Wi-Fi Yönetimi

**Boot ekranı** veya **ana menü** üstündeki **WI-FI** butonuna tıkla:

- **Ağ Listesi** — SSID + sinyal % + güvenlik
- **Ağa Tıkla** — Şifre gir (sanal klavye)
- **CONNECT** — Bağlan
- **DISCONNECT** — Bağlantıyı kes
- **SCAN NETWORKS** — Yeniden tara

**Bağlı Ağ Bilgisi:** SSID + şifre ekranda gösterilir.

---

### 🎮 Yardımcı Araçlar

**MAC Changer:**
- Rastgele MAC üretir
- `wlan0`'a uygular
- Wi-Fi 3-5 saniye kopabilir

**Clock:**
- Analog saat + dijital zaman
- Saniye çizgisi sürekli döner

**Calculator:**
- 3 mod: Normal, Scientific, Programmer
- Programmer modda HEX/DEC/OCT/BIN dönüşümü

**Speedtest:**
- `speedtest-cli` ile hız ölçümü
- Ping, Download, Upload

**Snake:**
- Dokunmatik kontrollü klasik yılan oyunu
- D-Pad + swipe ile yönlendirme

---

## 🐛 Sorun Giderme

### Hızlı Kontrol

```bash
./check_deps.sh
```

Eksik bağımlılıkları gösterir.

### Yaygın Sorunlar

| Sorun | Çözüm |
|---|---|
| `ModuleNotFoundError: No module named 'PIL'` | `pip3 install Pillow` |
| `Tor not running` | `sudo systemctl start tor` |
| `Permission denied: nmap` | `sudo -v` (bir kez şifre gir) |
| OnionShare boş çıkıyor | `ls ~/onionshare-env/bin/onionshare-cli` |
| Wi-Fi listesi boş | `nmcli device status` |
| Ekran donuyor | `free -h` → zram kontrol |
| `socks5h` bağlanamıyor | `curl --socks5-hostname 127.0.0.1:9050 ifconfig.me` |
| `ghost.png` görünmüyor | `~/cyberdeck_icons/ghost.png` var mı? |
| Program açılmıyor | `python3 cyberdeck.py` çıktısını kontrol et |

### Zram Aktifleştirme

```bash
sudo apt install -y zram-tools
sudo systemctl enable --now zramswap
```

### Log Temizleme

```bash
rm -rf ~/osint_logs/* ~/nmap_scans/* ~/dirscan_logs/*
```

---

## 📁 Proje Yapısı

```
hayalet/
├── cyberdeck.py          # Ana uygulama (~2900 satır)
├── requirements.txt      # Python bağımlılıkları
├── install.sh            # Otomatik kurulum
├── check_deps.sh         # Bağımlılık kontrolü
├── README.md             # Bu dosya
├── LICENSE               # GPL v2
├── .gitignore            # Git için
└── screenshots/          # Ekran görüntüleri
    ├── boot.png
    ├── menu.png
    ├── nmap.png
    ├── dirscan.png
    ├── whois.png
    ├── filemanager.png
    ├── onionchat.png
    └── search.png
```

Kullanıcı dizininde:

```
~/cyberdeck_icons/       # Ghost logosu
~/wordlists/             # Wordlist'ler
~/nmap_scans/            # Nmap çıktıları
~/dirscan_logs/          # Dir Scan çıktıları
~/osint_logs/            # OSINT çıktıları
~/received_files/        # OnionShare alınan dosyalar
~/send_files/            # OnionShare gönderilen dosyalar
~/onionshare-env/        # OnionShare venv
```

---

## 🔧 Ekran Görüntüsü Alma

Pi'de ekran görüntüsü almak için:

```bash
sudo apt install -y scrot
mkdir -p ~/hayalet/screenshots

# Al
scrot -o ~/hayalet/screenshots/boot.png
scrot -o ~/hayalet/screenshots/menu.png
scrot -o ~/hayalet/screenshots/nmap.png
scrot -o ~/hayalet/screenshots/dirscan.png
scrot -o ~/hayalet/screenshots/whois.png
scrot -o ~/hayalet/screenshots/filemanager.png
scrot -o ~/hayalet/screenshots/onionchat.png
scrot -o ~/hayalet/screenshots/search.png
```

Ya da `import` (ImageMagick) ile:

```bash
import -window root ~/hayalet/screenshots/boot.png
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
- **Tüm açık kaynak topluluğu**

---

**⭐ Projeyi beğendiyseniz yıldız verin!**