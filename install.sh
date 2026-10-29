#!/bin/bash
# ============================================================
# HAYALET v1.0 — Nihai Kurulum Scripti (Headless / Kiosk)
# Kullanım: bash install.sh
# ============================================================

set -e

echo "================================================"
echo " HAYALET v1.0 — Tam Kurulum ve Kiosk Ayarları"
echo "================================================"

if [ "$EUID" -eq 0 ]; then
    echo "✗ Bu scripti root olarak çalıştırmayın!"
    echo "  Kullanım: bash install.sh"
    exit 1
fi

# Scriptin bulunduğu dizini kesin olarak tespit et
PROJE_DIZINI=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo "Proje dizini: $PROJE_DIZINI"

# ============================================================
# 1. Sistem Paketleri
# ============================================================
echo "[1/7] Sistem paketleri kuruluyor..."
sudo apt update
sudo apt install -y \
    python3 python3-pip python3-tk python3-venv \
    python3-pil python3-pil.imagetk \
    tor proxychains4 nmap network-manager wireless-tools \
    curl git speedtest-cli zram-tools \
    xserver-xorg xinit x11-xserver-utils unclutter \
    build-essential libssl-dev libffi-dev python3-dev

echo "✓ Sistem paketleri tamam"

# ============================================================
# 2. Python Bağımlılıkları (PEP 668 uyumlu)
# ============================================================
echo "[2/7] Python bağımlılıkları kuruluyor..."
sudo apt install -y \
    python3-pil \
    python3-requests \
    python3-socks \
    python3-stem \
    python3-dotenv
echo "✓ Python paketleri tamam"

# ============================================================
# 3. OnionShare (izole venv - EV DİZİNİNDE)
# ============================================================
echo "[3/7] OnionShare kuruluyor..."
if [ ! -d "$HOME/onionshare-env" ]; then
    python3 -m venv "$HOME/onionshare-env"
    "$HOME/onionshare-env/bin/pip" install --upgrade pip
    "$HOME/onionshare-env/bin/pip" install onionshare-cli
    echo "✓ OnionShare venv hazır ($HOME/onionshare-env)"
else
    echo "  ⚠ ~/onionshare-env zaten var, atlanıyor"
fi

# ============================================================
# 4. Tor Yapılandırması
# ============================================================
echo "[4/7] Tor yapılandırılıyor..."
sudo systemctl enable tor
sudo systemctl start tor

TORRC="/etc/tor/torrc"
for line in "ControlPort 9051" "CookieAuthentication 1" "TransPort 9040" "DNSPort 5353"; do
    if ! grep -q "^$line" "$TORRC"; then
        sudo bash -c "echo '$line' >> $TORRC"
    fi
done
sudo systemctl restart tor
echo "✓ Tor hazır"

# ============================================================
# 5. Klasör Yapısı ve .env Dosyası
# ============================================================
echo "[5/7] Klasörler ve .env oluşturuluyor..."
mkdir -p ~/cyberdeck_icons
mkdir -p ~/wordlists
mkdir -p ~/nmap_scans
mkdir -p ~/dirscan_logs
mkdir -p ~/osint_logs
mkdir -p ~/received_files
mkdir -p ~/send_files
mkdir -p ~/downloads

if [ ! -f "$PROJE_DIZINI/.env" ]; then
    cat <<EOF > "$PROJE_DIZINI/.env"
ONIONSHARE_CLI=$HOME/onionshare-env/bin/onionshare-cli
RECEIVE_DIR=$HOME/received_files
SEND_DIR=$HOME/send_files
ICON_DIR=$HOME/cyberdeck_icons
EOF
    echo "✓ .env dosyası oluşturuldu."
else
    echo "  ⚠ .env dosyası zaten var, atlanıyor."
fi

# ============================================================
# 6. Zram ve Yol Düzeltmesi
# ============================================================
echo "[6/7] Zram aktifleştiriliyor ve eski yollar kontrol ediliyor..."
if command -v zramctl >/dev/null 2>&1; then
    if [ -f /etc/default/zramswap ]; then
        sudo sed -i 's/^ALGO=lz4/ALGO=lzo/' /etc/default/zramswap
    fi
    sudo systemctl enable --now zramswap || true
    echo "✓ Zram aktif (veya uyarı verdi, sorun değil)"
fi

if [ -f "$PROJE_DIZINI/cyberdeck.py" ]; then
    if grep -q "/home/buba/" "$PROJE_DIZINI/cyberdeck.py"; then
        sed -i "s|/home/buba/|$HOME/|g" "$PROJE_DIZINI/cyberdeck.py"
        echo "✓ Eski /home/buba/ yolları $HOME/ olarak düzeltildi."
    fi
fi

# ============================================================
# 7. Ekran Kalibrasyonu ve Kiosk Modu (480x320 Özel)
# ============================================================
echo "[7/7] Kiosk modu ve ekran ayarları yapılandırılıyor..."

# .xinitrc dosyası oluştur
cat <<EOF > ~/.xinitrc
#!/bin/sh
# Ekranın kararmasını ve uyku moduna girmesini engelle
xset s off
xset -dpms
xset s noblank

# Fare imlecini ekrandan gizle
unclutter -idle 0.1 -root &

# Proje dizinine gir (CWD kritik - .env ve fallback yolları için)
cd $PROJE_DIZINI

# Python uygulamasını tam ekran başlat
exec python3 $PROJE_DIZINI/cyberdeck.py
EOF
chmod +x ~/.xinitrc

# Sistem açıldığında otomatik startx
if ! grep -q "startx" ~/.bash_profile 2>/dev/null; then
    echo "" >> ~/.bash_profile
    echo "# HAYALET Kiosk Modu Başlatıcı" >> ~/.bash_profile
    echo "if [ -z \"\$DISPLAY\" ] && [ \"\$(tty)\" = \"/dev/tty1\" ]; then" >> ~/.bash_profile
    echo "    startx" >> ~/.bash_profile
    echo "fi" >> ~/.bash_profile
    echo "✓ .bash_profile güncellendi."
fi

# ============================================================
# Özet
# ============================================================
echo "================================================"
echo " ✓ KURULUM TAMAMLANDI"
echo "================================================"
echo ""
echo "Sistemi yeniden başlattığınızda uygulama otomatik açılacaktır:"
echo "  sudo reboot"
echo ""
echo "⚠️ EĞER OTOMATİK AÇILMAZSA:"
echo "sudo raspi-config → System Options → Boot / Auto Login → Console Autologin"
echo ""
echo "⚠️ TFT EKRAN:"
echo "sudo nano /boot/firmware/config.txt → dtoverlay=tft35a:rotate=90"
echo "================================================"