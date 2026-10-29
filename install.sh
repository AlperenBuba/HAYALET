#!/bin/bash
# ============================================================
# HAYALET v1.0 — Tam Kurulum Scripti
# Kullanım: chmod +x install.sh && ./install.sh
# ============================================================

set -e

echo "================================================"
echo " HAYALET v1.0 — Tam Kurulum"
echo "================================================"
echo ""

# Root kontrolü
if [ "$EUID" -eq 0 ]; then
    echo "✗ Bu scripti root olarak çalıştırmayın!"
    echo "  Kullanım: ./install.sh"
    exit 1
fi

# ============================================================
# 1. Sistem Paketleri
# ============================================================
echo "[1/5] Sistem paketleri kuruluyor..."
sudo apt update
sudo apt install -y \
    python3 python3-pip python3-tk python3-venv \
    python3-pil python3-pil.imagetk \
    tor proxychains4 nmap network-manager wireless-tools \
    curl git \
    speedtest-cli \
    zram-tools

echo "✓ Sistem paketleri tamam"
echo ""

# ============================================================
# 2. Python Bağımlılıkları
# ============================================================
echo "[2/5] Python bağımlılıkları kuruluyor..."
pip3 install --upgrade pip
pip3 install Pillow requests PySocks stem
echo "✓ Python paketleri tamam"
echo ""

# ============================================================
# 3. OnionShare (izole venv)
# ============================================================
echo "[3/5] OnionShare kuruluyor..."
if [ -d ~/onionshare-env ]; then
    echo "  ⚠ ~/onionshare-env zaten var, atlanıyor"
else
    python3 -m venv ~/onionshare-env
    ~/onionshare-env/bin/pip install --upgrade pip
    ~/onionshare-env/bin/pip install onionshare-cli
    echo "✓ OnionShare venv hazır"
fi
echo ""

# ============================================================
# 4. Tor Yapılandırması
# ============================================================
echo "[4/5] Tor yapılandırılıyor..."
sudo systemctl enable tor
sudo systemctl start tor

# torrc otomatik kontrol (kod zaten yapıyor ama garanti olsun)
TORRC="/etc/tor/torrc"
if ! grep -q "^ControlPort 9051" "$TORRC"; then
    echo "  ControlPort 9051 ekleniyor..."
    sudo bash -c "echo 'ControlPort 9051' >> $TORRC"
fi
if ! grep -q "^CookieAuthentication 1" "$TORRC"; then
    echo "  CookieAuthentication 1 ekleniyor..."
    sudo bash -c "echo 'CookieAuthentication 1' >> $TORRC"
fi
if ! grep -q "^TransPort 9040" "$TORRC"; then
    sudo bash -c "echo 'TransPort 9040' >> $TORRC"
fi
if ! grep -q "^DNSPort 5353" "$TORRC"; then
    sudo bash -c "echo 'DNSPort 5353' >> $TORRC"
fi

sudo systemctl restart tor
echo "✓ Tor hazır"
echo ""

# ============================================================
# 5. Klasör Yapısı
# ============================================================
echo "[5/5] Klasörler oluşturuluyor..."
mkdir -p ~/cyberdeck_icons
mkdir -p ~/wordlists
mkdir -p ~/nmap_scans
mkdir -p ~/dirscan_logs
mkdir -p ~/osint_logs
mkdir -p ~/received_files
mkdir -p ~/send_files
mkdir -p ~/downloads
echo "✓ Klasörler hazır"
echo ""

# ============================================================
# Zram (opsiyonel, 512 MB RAM için önerilen)
# ============================================================
if command -v zramctl >/dev/null 2>&1; then
    echo "[Bonus] Zram aktifleştiriliyor..."
    sudo systemctl enable --now zramswap
    echo "✓ Zram aktif"
    echo ""
fi

# ============================================================
# Yol düzeltme (farklı kullanıcıysa)
# ============================================================
if [ -f cyberdeck.py ]; then
    if grep -q "/home/buba/" cyberdeck.py; then
        echo "[Bonus] /home/buba/ yolları düzeltiliyor..."
        sed -i "s|/home/buba/|$HOME/|g" cyberdeck.py
        echo "✓ Yollar düzeltildi: $HOME/"
        echo ""
    fi
fi

# ============================================================
# Özet
# ============================================================
echo "================================================"
echo " ✓ KURULUM TAMAMLANDI"
echo "================================================"
echo ""
echo "Şimdi çalıştırabilirsin:"
echo "  python3 cyberdeck.py"
echo ""
echo "İlk kez çalıştırmadan önce:"
echo "  1. ~/cyberdeck_icons/ghost.png ekle (logo)"
echo "  2. ~/wordlists/ klasörüne wordlist ekle (opsiyonel)"
echo ""
echo "Sorun olursa README.md → Sorun Giderme bölümüne bak."
echo "================================================"