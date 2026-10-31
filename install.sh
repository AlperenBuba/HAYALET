#!/bin/bash
# ============================================================
# HAYALET v1.0 — Nihai Kurulum (Headless / Kiosk + Auto-Update)
# Kullanım: bash install.sh
# ============================================================

set -e

echo "================================================"
echo " HAYALET v1.0 — Tam Kurulum"
echo "================================================"

if [ "$EUID" -eq 0 ]; then
    echo "✗ Bu scripti root olarak çalıştırmayın!"
    exit 1
fi

PROJE_DIZINI=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
export PROJE_DIZINI
echo "Proje dizini: $PROJE_DIZINI"
echo "OnionShare venv: $HOME/onionshare-env"
echo ""

# ============================================================
# 1. Sistem Paketleri
# ============================================================
echo "[1/8] Sistem paketleri kuruluyor..."
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
echo "[2/8] Python bağımlılıkları kuruluyor..."
sudo apt install -y \
    python3-pil \
    python3-requests \
    python3-socks \
    python3-stem \
    python3-dotenv
echo "✓ Python paketleri tamam"

# ============================================================
# 3. OnionShare (EV DİZİNİNDE)
# ============================================================
echo "[3/8] OnionShare kuruluyor..."

if [ -d "$PROJE_DIZINI/onionshare-env" ]; then
    echo "  ↳ Eski $PROJE_DIZINI/onionshare-env siliniyor..."
    rm -rf "$PROJE_DIZINI/onionshare-env"
fi

NEED_VENV=0
if [ ! -d "$HOME/onionshare-env" ]; then
    NEED_VENV=1
elif [ ! -x "$HOME/onionshare-env/bin/onionshare-cli" ]; then
    echo "  ↳ ~/onionshare-env bozuk, yeniden oluşturulacak..."
    rm -rf "$HOME/onionshare-env"
    NEED_VENV=1
fi

if [ "$NEED_VENV" -eq 1 ]; then
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
echo "[4/8] Tor yapılandırılıyor..."
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
# 5. Klasörler + .env
# ============================================================
echo "[5/8] Klasörler ve .env oluşturuluyor..."
mkdir -p ~/cyberdeck_icons ~/wordlists ~/nmap_scans \
         ~/dirscan_logs ~/osint_logs ~/received_files \
         ~/send_files ~/downloads

cat <<EOF > "$PROJE_DIZINI/.env"
ONIONSHARE_CLI=$HOME/onionshare-env/bin/onionshare-cli
RECEIVE_DIR=$HOME/received_files
SEND_DIR=$HOME/send_files
ICON_DIR=$HOME/cyberdeck_icons
EOF
echo "✓ .env yeniden yazıldı: $PROJE_DIZINI/.env"

# ============================================================
# 6. Zram + cyberdeck.py onarım
# ============================================================
echo "[6/8] Zram ve cyberdeck.py otomatik onarım..."

if command -v zramctl >/dev/null 2>&1; then
    if [ -f /etc/default/zramswap ]; then
        sudo sed -i 's/^ALGO=lz4/ALGO=lzo/' /etc/default/zramswap || true
    fi
    sudo systemctl enable --now zramswap || true
    echo "✓ Zram aktif"
fi

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

    # /home/buba/ -> ev dizini
    content = content.replace('/home/buba/', os.path.expanduser('~') + '/')

    # load_dotenv çağrısı yoksa ekle
    if 'from dotenv import load_dotenv' in content and 'load_dotenv(' not in content:
        content = content.replace(
            'from dotenv import load_dotenv',
            'from dotenv import load_dotenv\n'
            'load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))'
        )

    # fallback: abspath -> expanduser
    content = content.replace(
        'os.path.abspath("onionshare-env/bin/onionshare-cli")',
        'os.path.expanduser("~/onionshare-env/bin/onionshare-cli")'
    )

    # ICON_DIR .env'den okunsun
    content = content.replace(
        'ICON_DIR = os.path.expanduser("~/cyberdeck_icons")',
        'ICON_DIR = os.path.expanduser(os.getenv("ICON_DIR", "~/cyberdeck_icons"))'
    )

    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print('✓ cyberdeck.py otomatik onarıldı.')
    else:
        print('✓ cyberdeck.py zaten güncel.')
PYEOF

# ============================================================
# 7. Kiosk Modu (.xinitrc + .bash_profile)
# ============================================================
echo "[7/8] Kiosk modu ayarlanıyor..."

cat <<EOF > ~/.xinitrc
#!/bin/sh
xset s off
xset -dpms
xset s noblank
unclutter -idle 0.1 -root &
cd $PROJE_DIZINI

# Açılışta sessiz güncelleme kontrolü (internet yoksa 3s içinde atlar)
timeout 15 bash $PROJE_DIZINI/update.sh --quiet || true

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
# 8. OTOMATİK GÜNCELLEME SİSTEMİ
# ============================================================
echo "[8/8] Otomatik güncelleme sistemi kuruluyor..."

# 8a) update.sh oluştur (tek tırnaklı heredoc → değişkenler genişlemesin)
cat <<'UPDATEEOF' > "$PROJE_DIZINI/update.sh"
#!/bin/bash
# ============================================================
# HAYALET — Otomatik Güncelleme Scripti
# Kullanım: bash update.sh [--restart] [--quiet]
# ============================================================

set -e

PROJE_DIZINI=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
LOG_FILE="$PROJE_DIZINI/update.log"
RESTART=0
QUIET=0

for arg in "$@"; do
    case $arg in
        --restart) RESTART=1 ;;
        --quiet)   QUIET=1 ;;
    esac
done

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 1) İnternet var mı?
if ! ping -c 1 -W 3 8.8.8.8 >/dev/null 2>&1; then
    log "⚠ İnternet yok, güncelleme atlandı."
    exit 0
fi

# 2) GitHub erişilebilir mi?
if ! curl -sf --max-time 10 https://github.com >/dev/null 2>&1; then
    log "⚠ GitHub'a erişilemiyor, güncelleme atlandı."
    exit 0
fi

cd "$PROJE_DIZINI"

# 3) Git repo mu?
if [ ! -d ".git" ]; then
    log "✗ Git repo değil, güncelleme yapılamaz."
    exit 1
fi

# 4) Yerel değişiklik varsa yedekle
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    log "⚠ Yerel değişiklik var, stash'leniyor..."
    git stash push -m "auto-update-$(date +%s)" >>"$LOG_FILE" 2>&1 || true
fi

# 5) Uzak repoyu kontrol et
log "→ GitHub kontrol ediliyor..."
git fetch --quiet origin 2>>"$LOG_FILE" || {
    log "✗ git fetch başarısız"
    exit 1
}

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main 2>/dev/null || git rev-parse origin/master 2>/dev/null || echo "")

if [ -z "$REMOTE" ]; then
    log "✗ origin/main veya origin/master bulunamadı"
    exit 1
fi

if [ "$LOCAL" = "$REMOTE" ]; then
    log "✓ Zaten güncel (${LOCAL:0:7})"
    [ $QUIET -eq 0 ] && echo "Güncel: $LOCAL"
    exit 0
fi

# 6) Güncellemeyi uygula
log "→ Güncelleme: ${LOCAL:0:7} → ${REMOTE:0:7}"
git pull --quiet origin $(git rev-parse --abbrev-ref HEAD) >>"$LOG_FILE" 2>&1 || {
    log "✗ git pull başarısız"
    exit 1
}
NEW=$(git rev-parse HEAD)
log "✓ Güncellendi: ${NEW:0:7}"

# 7) Bağımlılıklar değiştiyse install.sh çalıştır
if git diff --name-only "$LOCAL" "$NEW" | grep -qE "^(install\.sh|requirements\.txt)$"; then
    log "→ Bağımlılıklar değişmiş, install.sh çalıştırılıyor..."
    bash install.sh >>"$LOG_FILE" 2>&1 || log "⚠ install.sh uyarı verdi"
fi

# 8) İsteğe bağlı: yeniden başlat
if [ $RESTART -eq 1 ]; then
    log "→ Uygulama yeniden başlatılıyor..."
    if pgrep -f "cyberdeck.py" >/dev/null; then
        pkill -f "cyberdeck.py" || true
        sleep 3
        DISPLAY=:0 startx >/dev/null 2>&1 &
    fi
fi

log "✓ Güncelleme tamamlandı."
exit 0
UPDATEEOF

chmod +x "$PROJE_DIZINI/update.sh"
echo "✓ update.sh oluşturuldu ($PROJE_DIZINI/update.sh)"

# 8b) systemd service (değişkenler genişlesin → çift tırnak heredoc)
sudo tee /etc/systemd/system/hayalet-update.service > /dev/null <<SERVICEEOF
[Unit]
Description=HAYALET Auto Update
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=$USER
WorkingDirectory=$PROJE_DIZINI
ExecStart=$PROJE_DIZINI/update.sh --restart --quiet
StandardOutput=append:$PROJE_DIZINI/update.log
StandardError=append:$PROJE_DIZINI/update.log
SERVICEEOF
echo "✓ /etc/systemd/system/hayalet-update.service oluşturuldu"

# 8c) systemd timer
sudo tee /etc/systemd/system/hayalet-update.timer > /dev/null <<TIMEREOF
[Unit]
Description=HAYALET Update Check (every 6h)

[Timer]
OnBootSec=5min
OnUnitActiveSec=6h
Persistent=true

[Install]
WantedBy=timers.target
TIMEREOF
echo "✓ /etc/systemd/system/hayalet-update.timer oluşturuldu"

# 8d) Aktifleştir
sudo systemctl daemon-reload
sudo systemctl enable --now hayalet-update.timer
echo "✓ Otomatik güncelleme aktif (her 6 saatte bir)"

# ============================================================
# Özet
# ============================================================
echo ""
echo "================================================"
echo " ✓ KURULUM TAMAMLANDI"
echo "================================================"
echo ""
echo "  Proje dizini    : $PROJE_DIZINI"
echo "  OnionShare CLI  : $HOME/onionshare-env/bin/onionshare-cli"
echo "  Konfigürasyon   : $PROJE_DIZINI/.env"
echo "  Güncelleme logu : $PROJE_DIZINI/update.log"
echo ""
echo "Sistemi yeniden başlatın:"
echo "  sudo reboot"
echo ""
echo "Güncelleme sistemi:"
echo "  • Otomatik: her 6 saatte bir (systemd timer)"
echo "  • Manuel  : bash $PROJE_DIZINI/update.sh"
echo "  • Log     : tail -f $PROJE_DIZINI/update.log"
echo "  • Timer   : systemctl list-timers | grep hayalet"
echo ""
echo "⚠️  Otomatik açılmazsa:"
echo "  sudo raspi-config → System Options → Boot / Auto Login → Console Autologin"
echo ""
echo "⚠️  TFT ekran bozuksa:"
echo "  sudo nano /boot/firmware/config.txt → dtoverlay=... ekle"
echo "================================================"