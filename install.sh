#!/bin/bash
# ============================================================
# HAYALET v1.0 — Nihai Kurulum (Her Şeyi Otomatik Halleder)
# Kullanım: bash install.sh
# ============================================================

set -e

echo "================================================"
echo " HAYALET v1.0 — Tam Kurulum ve Kiosk Ayarları"
echo "================================================"

if [ "$EUID" -eq 0 ]; then
    echo "✗ Bu scripti root olarak çalıştırmayın!"
    exit 1
fi

PROJE_DIZINI=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
export PROJE_DIZINI
echo "Proje dizini: $PROJE_DIZINI"
echo "OnionShare venv hedefi: $HOME/onionshare-env"
echo ""

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
# 3. OnionShare — Ev dizininde ($HOME/onionshare-env)
#    Eski proje-dizini venv'i otomatik silinir
# ============================================================
echo "[3/7] OnionShare kuruluyor..."

# 3a) Eski/yanlış konumdaki venv'i temizle
if [ -d "$PROJE_DIZINI/onionshare-env" ]; then
    echo "  ↳ Eski $PROJE_DIZINI/onionshare-env siliniyor..."
    rm -rf "$PROJE_DIZINI/onionshare-env"
fi

# 3b) Ev dizinindeki venv sağlam mı?
NEED_VENV=0
if [ ! -d "$HOME/onionshare-env" ]; then
    NEED_VENV=1
elif [ ! -x "$HOME/onionshare-env/bin/onionshare-cli" ]; then
    echo "  ↳ ~/onionshare-env bozuk, yeniden oluşturulacak..."
    rm -rf "$HOME/onionshare-env"
    NEED_VENV=1
fi

# 3c) Gerekiyorsa sıfırdan kur
if [ "$NEED_VENV" -eq 1 ]; then
    echo "  ↳ python3 -m venv $HOME/onionshare-env"
    python3 -m venv "$HOME/onionshare-env"
    "$HOME/onionshare-env/bin/pip" install --upgrade pip
    "$HOME/onionshare-env/bin/pip" install onionshare-cli
    echo "✓ OnionShare venv hazır: $HOME/onionshare-env"
else
    echo "  ⚠ ~/onionshare-env sağlam, atlanıyor"
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
# 5. Klasörler + .env (Her zaman doğru yol ile)
# ============================================================
echo "[5/7] Klasörler ve .env oluşturuluyor..."
mkdir -p ~/cyberdeck_icons ~/wordlists ~/nmap_scans \
         ~/dirscan_logs ~/osint_logs ~/received_files \
         ~/send_files ~/downloads

# .env her zaman yeniden yaz (yol değişmiş olabilir)
cat <<EOF > "$PROJE_DIZINI/.env"
ONIONSHARE_CLI=$HOME/onionshare-env/bin/onionshare-cli
RECEIVE_DIR=$HOME/received_files
SEND_DIR=$HOME/send_files
ICON_DIR=$HOME/cyberdeck_icons
EOF
echo "✓ .env yeniden yazıldı: $PROJE_DIZINI/.env"

# ============================================================
# 6. Zram + cyberdeck.py otomatik onarım
# ============================================================
echo "[6/7] Zram ve cyberdeck.py otomatik onarım..."

# Zram (lz4 -> lzo fix, hata olsa bile devam)
if command -v zramctl >/dev/null 2>&1; then
    if [ -f /etc/default/zramswap ]; then
        sudo sed -i 's/^ALGO=lz4/ALGO=lzo/' /etc/default/zramswap || true
    fi
    sudo systemctl enable --now zramswap || true
    echo "✓ Zram aktif (veya uyarı verdi, sorun değil)"
fi

# cyberdeck.py içindeki eski yolları ve fallback'i otomatik düzelt
python3 << 'PYEOF'
import os
proje = os.environ.get('PROJE_DIZINI', os.getcwd())
path = os.path.join(proje, 'cyberdeck.py')
if not os.path.exists(path):
    print('  ⚠ cyberdeck.py bulunamadı, atlanıyor.')
else:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    original = content

    # 1) /home/buba/ -> ev dizini
    content = content.replace('/home/buba/', os.path.expanduser('~') + '/')

    # 2) load_dotenv çağrısı yoksa ekle
    if 'from dotenv import load_dotenv' in content and 'load_dotenv(' not in content:
        content = content.replace(
            'from dotenv import load_dotenv',
            'from dotenv import load_dotenv\n'
            'load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))'
        )

    # 3) fallback: abspath -> expanduser
    content = content.replace(
        'os.path.abspath("onionshare-env/bin/onionshare-cli")',
        'os.path.expanduser("~/onionshare-env/bin/onionshare-cli")'
    )

    # 4) ICON_DIR .env'den okunsun
    content = content.replace(
        'ICON_DIR = os.path.expanduser("~/cyberdeck_icons")',
        'ICON_DIR = os.path.expanduser(os.getenv("ICON_DIR", "~/cyberdeck_icons"))'
    )

    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print('✓ cyberdeck.py otomatik onarıldı (yollar + load_dotenv + fallback).')
    else:
        print('✓ cyberdeck.py zaten güncel.')
PYEOF

# ============================================================
# 7. Kiosk Modu (.xinitrc + .bash_profile)
# ============================================================
echo "[7/7] Kiosk modu ayarlanıyor..."

cat <<EOF > ~/.xinitrc
#!/bin/sh
xset s off
xset -dpms
xset s noblank
unclutter -idle 0.1 -root &
cd $PROJE_DIZINI
exec python3 $PROJE_DIZINI/cyberdeck.py
EOF
chmod +x ~/.xinitrc

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
echo "OnionShare CLI : $HOME/onionshare-env/bin/onionshare-cli"
echo "Proje dizini   : $PROJE_DIZINI"
echo ".env           : $PROJE_DIZINI/.env"
echo ""
echo "Sistemi yeniden başlatın:"
echo "  sudo reboot"
echo ""
echo "⚠️  Otomatik açılmazsa:"
echo "  sudo raspi-config → System Options → Boot / Auto Login → Console Autologin"
echo "================================================"