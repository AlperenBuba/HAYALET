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
        --quiet) QUIET=1 ;;
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

# --- 5) Güncel mi? (STASH'E DOKUNMADAN) ---
if [ "$LOCAL" = "$REMOTE" ]; then
    log "✓ Zaten güncel (${LOCAL:0:7})"
    [ $QUIET -eq 0 ] && echo "Güncel: $LOCAL"
    exit 0
fi

# --- 6) GÜNCELLEME VAR — şimdi yedekle ---
STASHED=0
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    log "⚠ Yerel değişiklik var, stash'leniyor..."
    if git stash push -m "auto-update-$(date +%s)" >>"$LOG_FILE" 2>&1; then
        STASHED=1
    fi
fi

# --- 7) Güncellemeyi uygula ---
log "→ Güncelleme: ${LOCAL:0:7} → ${REMOTE:0:7}"
if git pull --quiet origin "$(git rev-parse --abbrev-ref HEAD)" >>"$LOG_FILE" 2>&1; then
    NEW=$(git rev-parse HEAD)
    log "✓ Güncellendi: ${NEW:0:7}"

    # 7b) Stash'i geri yükle
    if [ "$STASHED" -eq 1 ]; then
        if git stash pop >>"$LOG_FILE" 2>&1; then
            log "✓ Yerel değişiklikler geri yüklendi."
        else
            log "⚠ Stash çakıştı, manuel çözüm gerekli: git stash list"
        fi
    fi
else
    log "✗ git pull başarısız"
    # Pull başarısız olsa bile stash'i geri yükle (veri kaybı olmasın)
    if [ "$STASHED" -eq 1 ]; then
        git stash pop >>"$LOG_FILE" 2>&1 || true
        log "↩ Yerel değişiklikler geri yüklendi (pull başarısızdı)."
    fi
    exit 1
fi

# --- 8) Bağımlılıklar değiştiyse yeniden kur ---
if git diff --name-only "$LOCAL" "$NEW" | grep -qE "^(install\.sh|requirements\.txt)$"; then
    log "→ Bağımlılıklar değişmiş, install.sh çalıştırılıyor..."
    bash install.sh >>"$LOG_FILE" 2>&1 || log "⚠ install.sh uyarı verdi"
fi

# --- 9) İsteğe bağlı: yeniden başlat ---
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