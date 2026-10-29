#!/bin/bash
# HAYALET v1.0 — Bağımlılık Kontrol Scripti

echo "================================================"
echo " HAYALET v1.0 — Bağımlılık Kontrolü"
echo "================================================"
echo ""

EKSIK=0

echo "[1] Python paketleri:"
for mod in tkinter PIL requests socks stem; do
    if python3 -c "import $mod" 2>/dev/null; then
        echo "  ✓ $mod"
    else
        echo "  ✗ $mod EKSİK"
        EKSIK=$((EKSIK+1))
    fi
done

echo ""
echo "[2] Sistem komutları:"
for cmd in nmap nmcli iwgetid curl tor; do
    if which $cmd >/dev/null 2>&1; then
        echo "  ✓ $cmd"
    else
        echo "  ✗ $cmd EKSİK"
        EKSIK=$((EKSIK+1))
    fi
done

if which speedtest-cli >/dev/null 2>&1; then
    echo "  ✓ speedtest-cli"
else
    echo "  ⚠ speedtest-cli (opsiyonel, Speedtest için gerekli)"
fi

echo ""
echo "[3] Dosya ve dizinler:"
if [ -f /etc/tor/torrc ]; then echo "  ✓ /etc/tor/torrc"; else echo "  ✗ /etc/tor/torrc"; EKSIK=$((EKSIK+1)); fi
if [ -f ~/onionshare-env/bin/onionshare-cli ]; then echo "  ✓ onionshare-cli"; else echo "  ✗ onionshare-cli (OnionShare için)"; EKSIK=$((EKSIK+1)); fi
if [ -f ~/cyberdeck_icons/ghost.png ]; then echo "  ✓ ghost.png"; else echo "  ⚠ ghost.png (opsiyonel, logo için)"; fi

echo ""
echo "[4] Tor servisi:"
if systemctl is-active tor >/dev/null 2>&1; then
    echo "  ✓ Tor çalışıyor"
else
    echo "  ✗ Tor durmuş (sudo systemctl start tor)"
    EKSIK=$((EKSIK+1))
fi

echo ""
echo "================================================"
if [ $EKSIK -eq 0 ]; then
    echo " ✓ Tüm bağımlılıklar hazır! Program çalışabilir."
else
    echo " ✗ $EKSIK eksik var. Kurulum için README.md'ye bakın."
fi
echo "================================================"