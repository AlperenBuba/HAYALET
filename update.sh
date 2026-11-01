#!/bin/bash
# ============================================================
# HAYALET — Otomatik Güncelleme Scripti
# Kullanım: bash update.sh [--restart] [--quiet]
# ============================================================

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

# --- 1) İnternet var mı? ---
if ! ping -c 1 -W 3 8.8.8.8 >/dev/null 2>&1; then
    log "⚠ İnternet yok, güncelleme atlandı."
    exit 0
fi

# --- 2) GitHub'a erişim var mı? ---
if ! curl -sf --max-time 10 https://github.com >/dev/null 2>&1; then
    log "⚠ GitHub'a erişilemiyor, güncelleme atlandı."
    exit 0
fi

cd "$PROJE_DIZINI"

# --- 3) Git repo mu? ---
if [ ! -d ".git" ]; then
    log "✗ Git repo değil, güncelleme yapılamaz."
    exit 1
fi

# --- 4) Uzak repoyu kontrol et ---
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

# --- 5) PAKET KONTROLÜ — HER ZAMAN ÇALIŞIR ---
log "→ Sistem paketleri kontrol ediliyor..."

INSTALLED_PKGS=$(dpkg-query -W -f='${Package}\n' 2>/dev/null)

pkg_installed() {
    grep -qx "$1" <<< "$INSTALLED_PKGS"
}

REQUIRED_PKGS=(
    python3 python3-pip python3-tk python3-venv
    python3-pil python3-pil.imagetk
    python3-socketio python3-websocket
    tor proxychains4 nmap network-manager wireless-tools
    curl git speedtest-cli zram-tools dsniff
    xserver-xorg xinit x11-xserver-utils unclutter
    build-essential libssl-dev libffi-dev python3-dev
    iptables thc-ipv6
)

MISSING=()
for pkg in "${REQUIRED_PKGS[@]}"; do
    pkg_installed "$pkg" || MISSING+=("$pkg")
done

if [ ${#MISSING[@]} -gt 0 ]; then
    log "⚠ Eksik sistem paketi: ${MISSING[*]}"
    if sudo -n true 2>/dev/null; then
        log "→ Kuruluyor..."
        if sudo apt install -y "${MISSING[@]}" >>"$LOG_FILE" 2>&1; then
            log "✓ Eksik paketler kuruldu"
        else
            log "✗ Paket kurulumu başarısız (update.log'a bakın)"
        fi
    else
        log "⚠ sudo NOPASSWD yok, otomatik kurulum atlandı"
        log "→ Elle kurun: sudo apt install -y ${MISSING[*]}"
    fi
else
    log "✓ Tüm sistem paketleri kurulu"
fi

PY_PKGS=(python3-requests python3-socks python3-stem python3-dotenv)
PY_MISSING=()
for pkg in "${PY_PKGS[@]}"; do
    pkg_installed "$pkg" || PY_MISSING+=("$pkg")
done
if [ ${#PY_MISSING[@]} -gt 0 ]; then
    log "⚠ Eksik Python paketi: ${PY_MISSING[*]}"
    if sudo -n true 2>/dev/null; then
        sudo apt install -y "${PY_MISSING[@]}" >>"$LOG_FILE" 2>&1 \
            && log "✓ Python paketleri kuruldu" \
            || log "✗ Python paket kurulumu başarısız"
    fi
fi

if [ ! -x "$HOME/onionshare-env/bin/onionshare-cli" ]; then
    log "⚠ OnionShare CLI yok, venv yeniden kurulacak..."
    python3 -m venv "$HOME/onionshare-env" 2>>"$LOG_FILE" || {
        log "✗ venv oluşturulamadı (python3-venv kurulu mu?)"
    }
    "$HOME/onionshare-env/bin/pip" install --upgrade pip >>"$LOG_FILE" 2>&1
    "$HOME/onionshare-env/bin/pip" install onionshare-cli >>"$LOG_FILE" 2>&1 \
        && log "✓ OnionShare CLI kuruldu" \
        || log "✗ OnionShare kurulumu başarısız"
else
    log "✓ OnionShare CLI mevcut"
fi

# --- 6) Güncel mi? (STASH'E DOKUNMADAN) ---
if [ "$LOCAL" = "$REMOTE" ]; then
    log "✓ Zaten güncel (${LOCAL:0:7})"
    [ $QUIET -eq 0 ] && echo "Güncel: $LOCAL"
    exit 0
fi

# --- 7) GÜNCELLEME VAR — şimdi yedekle ---
STASHED=0
if ! git diff-index --quiet HEAD -- 2>/dev/null || [ -n "$(git ls-files --others --exclude-standard)" ]; then
    log "⚠ Yerel/untracked değişiklik var, stash'leniyor..."
    if git stash push -u -m "auto-update-$(date +%s)" >>"$LOG_FILE" 2>&1; then
        STASHED=1
    fi
fi

# --- 8) Güncellemeyi uygula ---
log "→ Güncelleme: ${LOCAL:0:7} → ${REMOTE:0:7}"
if git pull --quiet origin "$(git rev-parse --abbrev-ref HEAD)" >>"$LOG_FILE" 2>&1; then
    NEW=$(git rev-parse HEAD)
    log "✓ Güncellendi: ${NEW:0:7}"

    if [ "$STASHED" -eq 1 ]; then
        if git stash pop >>"$LOG_FILE" 2>&1; then
            log "✓ Yerel değişiklikler geri yüklendi."
        else
            log "⚠ Stash çakıştı, manuel çözüm gerekli: git stash list"
        fi
    fi
else
    log "✗ git pull başarısız"
    if [ "$STASHED" -eq 1 ]; then
        git stash pop >>"$LOG_FILE" 2>&1 || true
        log "↩ Yerel değişiklikler geri yüklendi (pull başarısızdı)."
    fi
    exit 1
fi

# --- 9) install.sh değiştiyse uyar (paket kontrolü # 5'te yapıldı) ---
if git diff --name-only "$LOCAL" "$NEW" | grep -qE "^install\.sh$"; then
    log "ℹ install.sh değişmiş — elle çalıştırmanız önerilir:"
    log "   bash $PROJE_DIZINI/install.sh"
fi

# --- 10) İsteğe bağlı: yeniden başlat ---
if [ "$RESTART" -eq 1 ]; then
    log "→ Uygulama yeniden başlatılıyor..."
    if pgrep -f "cyberdeck.py" >/dev/null; then
        pkill -f "cyberdeck.py" || true
        sleep 3
        DISPLAY=:0 startx >/dev/null 2>&1 &
    fi
fi

log "✓ Güncelleme tamamlandı."
exit 0