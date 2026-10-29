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

PROJE_DIZINI=$(pwd)

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
    xserver-xorg xinit x11-xserver-utils unclutter

echo "✓ Sistem paketleri tamam"

# ============================================================
# 2. Python Bağımlılıkları
# ============================================================
echo "[2/7] Python bağımlılıkları kuruluyor..."
pip3 install --upgrade pip
pip3 install Pillow requests PySocks stem python-dotenv
echo "✓ Python paketleri tamam"

# ============================================================
# 3. OnionShare (izole venv - Proje dizininde)
# ============================================================
echo "[3/7] OnionShare kuruluyor..."
if [ ! -d "$PROJE_DIZINI/onionshare-env" ]; then
    python3 -m venv "$PROJE_DIZINI/onionshare-env"
    "$PROJE_DIZINI/onionshare-env/bin/pip" install --upgrade pip
    "$PROJE_DIZINI/onionshare-env/bin/pip" install onionshare-cli
    echo "✓ OnionShare venv hazır (./onionshare-env)"
else
    echo "  ⚠ ./onionshare-env zaten var, atlanıyor"
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
ONIONSHARE_CLI=$PROJE_DIZINI/onionshare-env/bin/onionshare-cli
RECEIVE_DIR=$HOME/received_files
SEND_DIR=$HOME/send_files
ICON_DIR=$HOME/cyberdeck_icons
EOF
    echo "✓ .env dosyası oluşturuldu."
else
    echo "  ⚠ .env dosyası zaten var, atlanıyor."
fi

# ============================================================
# 6. Zram ve Yol Düzeltmesi (Güvenlik Önlemi)
# ============================================================
echo "[6/7] Zram aktifleştiriliyor ve eski yollar kontrol ediliyor..."
if command -v zramctl >/dev/null 2>&1; then
    sudo systemctl enable --now zramswap
    echo "✓ Zram aktif"
fi

# Eğer kodda hala "/home/buba/" gibi eski sabit yollar kaldıysa düzelt
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

# .xinitrc dosyası oluştur (X11 başladığında uygulamayı başlatır)
cat <<EOF > ~/.xinitrc
#!/bin/sh
# Ekranın kararmasını ve uyku moduna girmesini engelle
xset s off
xset -dpms
xset s noblank

# Fare imlecini ekrandan gizle (dokunmatik/TFT ekranlar için)
unclutter -idle 0.1 -root &

# Python uygulamasını tam ekran başlat
exec python3 $PROJE_DIZINI/cyberdeck.py
EOF
chmod +x ~/.xinitrc

# Sistem açıldığında (tty1 konsolunda) otomatik olarak 'startx' çalıştır
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
echo "⚠️ ÖNEMLİ EKRAN NOTU:"
echo "Eğer TFT ekranın görüntüsü ters, çözünürlüğü yanlış veya"
echo "ekranın yarısı siyahsa, ekran sürücünün (overlay) ayarlanması gerekir."
echo "Bunun için 'sudo nano /boot/firmware/config.txt' dosyasını açıp"
echo "ekran modeline uygun 'dtoverlay=...' satırlarını eklemelisin."
echo "Örneğin: dtoverlay=tft35a:rotate=90"
echo ""
echo "Sorun olursa README.md → Sorun Giderme bölümüne bak."
echo "================================================"