import tkinter as tk
from PIL import Image, ImageTk
import subprocess, sys, os, threading, signal, time, math, pty, re, shlex
import datetime, random, tempfile, requests
from random import choice, randint
from string import ascii_lowercase
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/HAYALET/.env"))

try:
    from stem import Signal
    from stem.control import Controller
    TOR_AVAILABLE = True
except ImportError:
    TOR_AVAILABLE = False

subprocess.Popen("xset s off -dpms", shell=True)
ICON_DIR = os.path.expanduser(os.getenv("ICON_DIR", "~/cyberdeck_icons"))

def bagimlilik_kontrol():
    eksik = []
    try: import tkinter
    except ImportError: eksik.append("tkinter — sudo apt install python3-tk")
    try: from PIL import Image
    except ImportError: eksik.append("Pillow — pip3 install Pillow")
    try: import requests
    except ImportError: eksik.append("requests — pip3 install requests")
    try: import socks
    except ImportError: eksik.append("PySocks — pip3 install PySocks")
    try: import stem
    except ImportError: eksik.append("stem — pip3 install stem")
    try: import dotenv  # YENİ EKLENDİ
    except ImportError: eksik.append("python-dotenv — pip3 install python-dotenv")

    if eksik:
        print("\n" + "="*60)
        print(" HAYALET v1.0 — EKSİK BAĞIMLILIKLAR")
        print("="*60)
        for e in eksik: print(f"  ✗ {e}")
        print("\nKurulum: README.md → Kurulum bölümü")
        print("="*60 + "\n")
        sys.exit(1)

def log_sinirla(text_widget, max_satir=500):
    """500 satırı geçince ilk 50 satırı siler. Disk kaydı etkilenmez."""
    try:
        satir = int(text_widget.index('end-1c').split('.')[0])
        if satir > max_satir:
            text_widget.delete('1.0', f'{satir - max_satir + 50}.0')
    except: pass

def make_readonly_text(text_widget):
    """Text widget'ı seçilemez yapar (kaydırma ve okuma hala çalışır)."""
    for evt in ["<Button-1>", "<B1-Motion>", "<Double-Button-1>", "<Triple-Button-1>"]:
        text_widget.bind(evt, lambda e: "break")

def torrc_kontrol_et():
    if not TOR_AVAILABLE: return
    p = "/etc/tor/torrc"; d = False
    gerekli = ["ControlPort 9051", "CookieAuthentication 1", "TransPort 9040",
               "DNSPort 5353", "VirtualAddrNetworkIPv4 10.192.0.0/10", "AutomapHostsOnResolve 1"]
    try:
        with open(p, "r") as f: lines = f.readlines()
        a = [l.strip() for l in lines if l.strip() and not l.strip().startswith("#")]
        for g in gerekli:
            if g not in a: lines.append(f"\n{g}\n"); d = True
        if d:
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as t:
                t.writelines(lines); tp = t.name
            subprocess.run(["sudo", "cp", tp, p], check=True); os.remove(tp)
            subprocess.run(["sudo", "systemctl", "restart", "tor"], check=True)
    except: pass


def ansi_temizle(m):
    return re.compile(r'\x1b\[[0-9;]*[a-zA-Z]|\x1b\][0-9];.*?\x07|\r').sub('', m)

def ikon_yukle(name, w=32, h=32):
    if not name.lower().endswith(('.png','.jpg','.jpeg')):
        for e in [".png",".jpg",".jpeg"]:
            p = os.path.join(ICON_DIR, name+e)
            if os.path.exists(p): yol = p; break
        else: return None
    else: yol = os.path.join(ICON_DIR, name)
    try:
        i = Image.open(yol); i.thumbnail((w,h), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(i)
    except: return None

class GhostDeckApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.attributes('-fullscreen', True); self.configure(bg='black')
        self.container = tk.Frame(self, bg='black', width=480, height=320)
        self.container.pack(fill="both", expand=True); self.container.pack_propagate(False)
        self.frames = {}; self.history = []; self.current_page_name = None
        for F in (BootPage, MainMenu, OnionPage, ReceivePage, SendPage, WifiPage, NmapPage,
                DirScanPage, WHOISPage, DNSPage, SubEnumPage, HTTPHeadersPage,
                SSLCertPage, IPInfoPage, ReverseIPPage, TechStackPage, WaybackPage,
                RobotsPage, SitemapPage, SecHeadersPage, PortCheckPage,
                ClockPage, CalculatorPage, FileManagerPage, SpeedtestPage, SnakePage):
            fr = F(parent=self.container, controller=self); self.frames[F.__name__] = fr
            fr.place(x=0, y=0, width=480, height=320)
        self.show_frame("BootPage", add_to_history=False)
    def show_frame(self, pn, add_to_history=True):
        if add_to_history and self.current_page_name and self.current_page_name != pn: self.history.append(self.current_page_name)
        self.current_page_name = pn
        fr = self.frames[pn]; fr.tkraise()
        if hasattr(fr, 'on_show'): fr.on_show()
    def go_back(self):
        self.show_frame(self.history.pop() if self.history else "MainMenu", add_to_history=False)
    def show_wifi(self, fp):
        self.frames["WifiPage"].previous_page = fp; self.show_frame("WifiPage")
    def show_chat_dialog(self):
        if hasattr(self, 'overlay_bg'): return
        self._create_mode_dialog("SELECT CHAT TYPE", "OnionPage", self.close_chat_dialog)
    def close_chat_dialog(self):
        if hasattr(self, 'overlay_bg'): self.overlay_bg.destroy(); del self.overlay_bg
    def show_receive_dialog(self):
        if hasattr(self, 'receive_overlay_bg'): return
        self._create_mode_dialog("SELECT RECEIVE TYPE", "ReceivePage", self.close_receive_dialog, is_receive=True)
    def close_receive_dialog(self):
        if hasattr(self, 'receive_overlay_bg'): self.receive_overlay_bg.destroy(); del self.receive_overlay_bg
    def show_send_dialog(self):
        if hasattr(self, 'send_overlay_bg'): return
        self._create_mode_dialog("SELECT SEND TYPE", "SendPage", self.close_send_dialog, is_send=True)
    def close_send_dialog(self):
        if hasattr(self, 'send_overlay_bg'): self.send_overlay_bg.destroy(); del self.send_overlay_bg
    def _create_mode_dialog(self, title, tp, cf, is_receive=False, is_send=False):
        attr = 'overlay_bg'
        if is_receive: attr = 'receive_overlay_bg'
        if is_send: attr = 'send_overlay_bg'
        setattr(self, attr, tk.Frame(self, bg="#050505"))
        bg = getattr(self, attr); bg.place(x=0, y=0, width=480, height=320)
        bg.bind("<Button-1>", lambda e: cf())
        ov = tk.Frame(bg, bg="#111111", bd=2, relief="solid", highlightbackground="#39ff14", highlightthickness=2)
        ov.place(relx=0.5, rely=0.5, anchor="center", width=320, height=150)
        tk.Label(ov, text=title, bg="#111111", fg="#39ff14", font=("Helvetica",14,"bold")).pack(pady=(15,10))
        bf = tk.Frame(ov, bg="#111111"); bf.pack(pady=10)
        def pub(): cf(); self.frames[tp].set_mod("PUBLIC"); self.show_frame(tp)
        def priv(): cf(); self.frames[tp].set_mod("PRIVATE"); self.show_frame(tp)
        tk.Button(bf, text="PUBLIC", font=("Helvetica",12,"bold"), bg="#005500", fg="white", command=pub, width=10).pack(side="left", padx=10)
        tk.Button(bf, text="PRIVATE", font=("Helvetica",12,"bold"), bg="#aa0000", fg="white", command=priv, width=10).pack(side="right", padx=10)
    def show_shutdown_dialog(self):
        if hasattr(self, 'shutdown_overlay_bg'): return
        self.shutdown_overlay_bg = tk.Frame(self, bg="#050505")
        self.shutdown_overlay_bg.place(x=0, y=0, width=480, height=320)
        self.shutdown_overlay_bg.bind("<Button-1>", lambda e: self.close_shutdown_dialog())
        so = tk.Frame(self.shutdown_overlay_bg, bg="#111111", bd=2, relief="solid", highlightbackground="#aa0000", highlightthickness=2)
        so.place(relx=0.5, rely=0.5, anchor="center", width=360, height=150)
        tk.Label(so, text="SYSTEM ACTION", bg="#111111", fg="#aa0000", font=("Helvetica",14,"bold")).pack(pady=(15,10))
        bf = tk.Frame(so, bg="#111111"); bf.pack(pady=10)
        tk.Button(bf, text="TO TTY", font=("Helvetica",11,"bold"), bg="#1a1a1a", fg="#39ff14", command=lambda: (self.close_shutdown_dialog(), sys.exit(0)), width=8).pack(side="left", padx=5)
        tk.Button(bf, text="RESTART", font=("Helvetica",11,"bold"), bg="#cc8800", fg="white", command=lambda: (self.close_shutdown_dialog(), subprocess.run("sudo reboot", shell=True)), width=8).pack(side="left", padx=5)
        tk.Button(bf, text="POWER OFF", font=("Helvetica",11,"bold"), bg="#aa0000", fg="white", command=lambda: (self.close_shutdown_dialog(), subprocess.run("sudo poweroff", shell=True)), width=8).pack(side="right", padx=5)
    def close_shutdown_dialog(self):
        if hasattr(self, 'shutdown_overlay_bg'): self.shutdown_overlay_bg.destroy(); del self.shutdown_overlay_bg

def ekle_cikis_butonu(p, c):
    tk.Button(p, text="SYSTEM", font=("Helvetica",11,"bold"), bg="#aa0000", fg="white", bd=0, command=c.show_shutdown_dialog).place(x=0, y=290, width=480, height=30)

class BootPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="black", width=480, height=320)
        self.controller = controller
        img = ikon_yukle("ghost", 300, 65)
        self.cx, self.cy, self.r, self.angle = 240, 60, 5, 0
        if img:
            self.lbl_logo = tk.Label(self, image=img, bg="black"); self.lbl_logo.image = img
            self.lbl_logo.place(x=self.cx, y=self.cy, anchor="center"); self.animasyon()
        self.btn_wifi = tk.Button(self, text="WI-FI", font=("Helvetica",10,"bold"), bg="#1a1a1a", fg="#39ff14", command=lambda: controller.show_wifi("BootPage"))
        self.btn_wifi.place(x=363, y=8, width=115, height=40)
        self.durum_lbl = tk.Label(self, text="System Ready. Connect to Tor.", bg="black", fg="#39ff14", font=("Helvetica",10))
        self.durum_lbl.place(relx=0.5, y=110, anchor="n")
        self.btn_tor = tk.Button(self, text="CONNECT TO TOR", font=("Helvetica",16,"bold"), bg="#1a1a1a", fg="#39ff14", bd=1, relief="solid", highlightbackground="#39ff14", highlightthickness=1, command=self.tor_baglan)
        self.btn_tor.place(relx=0.5, y=150, anchor="n", width=250, height=60)
        tk.Button(self, text="⚠ Continue without Tor (RISKY)", font=("Helvetica",9),
                  bg="black", fg="#cc8800", bd=1, relief="solid",
                  highlightbackground="#cc8800", highlightthickness=1,
                  command=lambda: controller.show_frame("MainMenu")).place(relx=0.5, y=218, anchor="n", width=240, height=24)
        ekle_cikis_butonu(self, controller)
    def on_show(self):
        r = subprocess.run("iwgetid -r", shell=True, stdout=subprocess.PIPE, text=True)
        s = r.stdout.strip(); self.btn_wifi.config(text=f"WI-FI:\n{s[:8]}" if s else "WI-FI", fg="#39ff14")
    def animasyon(self):
        x = self.cx + self.r * math.cos(math.radians(self.angle))
        y = self.cy + self.r * math.sin(math.radians(self.angle))
        self.lbl_logo.place(x=x, y=y, anchor="center"); self.angle = (self.angle+4)%360; self.after(50, self.animasyon)
    def tor_baglan(self):
        self.btn_tor.config(state=tk.DISABLED, text="CONNECTING...")
        self.durum_lbl.config(text="Starting Tor...", fg="yellow")
        def run():
            subprocess.run("sudo systemctl start tor", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            t = None
            for i in range(30):
                self.after(0, lambda idx=i: self.durum_lbl.config(text=f"Checking Tor... ({idx+1}/30)"))
                t = subprocess.run("curl -s --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip | grep -o '\"IsTor\":true'", shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
                if t.stdout.strip()=='"IsTor":true': break
                time.sleep(2)
            if t and t.stdout.strip()=='"IsTor":true':
                self.after(0, lambda: self.durum_lbl.config(text="Tor OK! Redirecting...", fg="#39ff14"))
                self.after(1500, lambda: self.master.master.show_frame("MainMenu"))
            else:
                self.after(0, lambda: self.durum_lbl.config(text="Tor Failed!", fg="red"))
                self.after(0, lambda: self.btn_tor.config(state=tk.NORMAL, text="RETRY"))
        threading.Thread(target=run, daemon=True).start()

class WifiPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="black", width=480, height=320)
        self.controller = controller; self.selected_ssid = None
        self.previous_page = "BootPage"; self.current_connected_ssid = None
        self.is_upper = False; self.letter_buttons = []
        tb = tk.Frame(self, bg="#111111"); tb.place(x=0, y=0, width=480, height=30)
        tk.Button(tb, text="< BACK", bg="#111111", fg="#39ff14", font=("Helvetica",11,"bold"), bd=0, command=controller.go_back).pack(side="left", fill="y")
        tk.Label(tb, text="WI-FI NETWORKS", bg="#111111", fg="#39ff14", font=("Helvetica",11,"bold")).pack(side="left", expand=True)
        self.connected_frame = tk.Frame(self, bg="black", width=480, height=260)
        tk.Label(self.connected_frame, text="CONNECTED TO:", bg="black", fg="#39ff14", font=("Helvetica",14,"bold")).pack(pady=(20,5))
        self.lbl_conn_ssid = tk.Label(self.connected_frame, text="", bg="black", fg="#39ff14", font=("Helvetica",18,"bold")); self.lbl_conn_ssid.pack(pady=5)
        self.lbl_conn_pass = tk.Label(self.connected_frame, text="", bg="black", fg="yellow", font=("Helvetica",12)); self.lbl_conn_pass.pack(pady=5)
        self.btn_disconnect = tk.Button(self.connected_frame, text="DISCONNECT", font=("Helvetica",14,"bold"), bg="#aa0000", fg="white", command=self.disconnect_wifi)
        self.btn_disconnect.pack(pady=30, ipadx=20, ipady=10)
        self.list_frame = tk.Frame(self, bg="black")
        sb = tk.Scrollbar(self.list_frame); sb.pack(side="right", fill="y")
        self.wifi_list = tk.Listbox(self.list_frame, bg="black", fg="#39ff14", font=("Helvetica",12), bd=0, yscrollcommand=sb.set)
        self.wifi_list.pack(side="left", fill="both", expand=True); sb.config(command=self.wifi_list.yview)
        self.wifi_list.bind('<<ListboxSelect>>', self.on_select)
        self.pass_frame = tk.Frame(self, bg="black")
        self.pass_entry = tk.Entry(self.pass_frame, show="*", font=("Helvetica",14), bg="#222", fg="white", bd=2, relief="solid")
        self.pass_entry.place(x=10, y=5, width=460, height=30)
        self.keyboard_frame = tk.Frame(self.pass_frame, bg="black"); self.keyboard_frame.place(x=0, y=40, width=480, height=210)
        self.create_keyboard()
        self.btn_connect = tk.Button(self.pass_frame, text="CONNECT", font=("Helvetica",12,"bold"), bg="#005500", fg="white", command=self.connect_wifi)
        self.btn_connect.place(x=0, y=260, width=240, height=30)
        tk.Button(self.pass_frame, text="CANCEL", font=("Helvetica",12,"bold"), bg="#aa0000", fg="white", command=self.show_list).place(x=240, y=260, width=240, height=30)
        self.scan_btn = tk.Button(self, text="SCAN NETWORKS", font=("Helvetica",12,"bold"), bg="#1a1a1a", fg="#39ff14", command=self.scan_wifi)
        self.status_lbl = tk.Label(self, text="", bg="black", fg="yellow", font=("Helvetica",10))
    def on_show(self): self.check_connection_status()
    def check_connection_status(self):
        r = subprocess.run("nmcli -t -f NAME,DEVICE connection show --active", shell=True, stdout=subprocess.PIPE, text=True)
        c = None
        for line in r.stdout.strip().split('\n'):
            p = line.split(':')
            if len(p)>=2 and p[1]=='wlan0': c = p[0]; break
        if c: self.current_connected_ssid = c; self.show_connected_screen(c)
        else: self.current_connected_ssid = None; self.show_list(); self.scan_wifi()
    def show_connected_screen(self, ssid):
        self.list_frame.place_forget(); self.pass_frame.place_forget(); self.scan_btn.place_forget(); self.status_lbl.place_forget()
        psk = subprocess.run(f"sudo nmcli -s -g 802-11-wireless-security.psk connection show '{ssid}'", shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True).stdout.strip()
        self.lbl_conn_ssid.config(text=ssid)
        self.lbl_conn_pass.config(text=f"PASSWORD: {psk}" if psk else "PASSWORD: (Open)")
        self.connected_frame.place(x=0, y=30, width=480, height=260)
    def create_keyboard(self):
        for row in ["1234567890","qwertyuiop","asdfghjkl","zxcvbnm",["SHIFT","SPACE","DEL"]]:
            f = tk.Frame(self.keyboard_frame, bg="black"); f.pack(side="top", fill="x", expand=True)
            if isinstance(row, list):
                for ch in row:
                    if ch=="SHIFT": b = tk.Button(f, text="SHIFT", command=self.toggle_shift, bg="#444", fg="yellow", font=("Helvetica",11,"bold"))
                    elif ch=="SPACE": b = tk.Button(f, text="SPACE", command=lambda: self.add_char(" "), bg="#333", fg="white", font=("Helvetica",11,"bold"))
                    else: b = tk.Button(f, text="DEL", command=self.del_char, bg="#aa0000", fg="white", font=("Helvetica",11,"bold"))
                    b.pack(side="left", fill="both", expand=True, padx=1, pady=1)
            else:
                for ch in row:
                    b = tk.Button(f, text=ch, command=lambda c=ch: self.add_char(c), bg="#222", fg="#39ff14", font=("Helvetica",14,"bold"))
                    b.pack(side="left", fill="both", expand=True, padx=1, pady=1)
                    if ch.isalpha(): self.letter_buttons.append(b)
    def toggle_shift(self):
        self.is_upper = not self.is_upper
        for b in self.letter_buttons:
            t = b.cget("text"); b.config(text=t.upper() if self.is_upper else t.lower())
    def add_char(self, ch):
        if self.is_upper and ch.isalpha(): ch = ch.upper()
        self.pass_entry.insert(tk.END, ch)
    def del_char(self):
        c = self.pass_entry.get()
        if c: self.pass_entry.delete(len(c)-1, tk.END)
    def scan_wifi(self):
        self.scan_btn.config(state=tk.DISABLED, text="SCANNING...")
        self.status_lbl.config(text="Scanning..."); self.status_lbl.place(relx=0.5, y=270, anchor="s")
        self.wifi_list.delete(0, tk.END)
        def run():
            try:
                subprocess.run("sudo nmcli device wifi rescan", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
                time.sleep(2)
                r = subprocess.run("nmcli -t -f SSID,SIGNAL,SECURITY device wifi list", shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, timeout=5)
                self.after(0, self.update_list, r.stdout)
            except:
                self.after(0, lambda: self.status_lbl.config(text="Scan failed.", fg="red"))
                self.after(0, lambda: self.scan_btn.config(state=tk.NORMAL, text="SCAN NETWORKS"))
        threading.Thread(target=run, daemon=True).start()
    def update_list(self, o):
        self.status_lbl.config(text=""); self.scan_btn.config(state=tk.NORMAL, text="SCAN NETWORKS")
        seen = set()
        for line in o.splitlines():
            p = line.split(":")
            if len(p)>=3:
                s, si, se = p[0], p[1], p[2]
                if s and s not in seen: seen.add(s); self.wifi_list.insert(tk.END, f"{s} [{si}%] {se}")
    def on_select(self, e):
        sel = self.wifi_list.curselection()
        if sel:
            ssid = self.wifi_list.get(sel[0]).split(" [")[0]; self.selected_ssid = ssid
            self.list_frame.place_forget(); self.scan_btn.place_forget(); self.status_lbl.place_forget()
            self.pass_frame.place(x=0, y=30, width=480, height=290)
            self.pass_entry.delete(0, tk.END); self.pass_entry.focus_set()
            self.is_upper = False
            for b in self.letter_buttons: b.config(text=b.cget("text").lower())
            self.status_lbl.config(text=f"Enter password for {ssid}"); self.status_lbl.place(relx=0.5, y=270, anchor="s")
    def show_list(self):
        self.connected_frame.place_forget(); self.pass_frame.place_forget()
        self.list_frame.place(x=0, y=30, width=480, height=260)
        self.scan_btn.place(x=0, y=290, width=480, height=30); self.status_lbl.place_forget()
    def connect_wifi(self):
        pw = self.pass_entry.get(); ssid = self.selected_ssid
        if not ssid: return
        self.btn_connect.config(state=tk.DISABLED, text="CONNECTING...")
        self.status_lbl.config(text="Connecting...", fg="yellow"); self.status_lbl.place(relx=0.5, y=270, anchor="s")
        def run():
            try:
                subprocess.run(f'sudo nmcli connection delete {shlex.quote(ssid)}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.run("sudo iw dev wlan0 set power_save off", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                cmd = f'sudo nmcli device wifi connect {shlex.quote(ssid)}'
                if pw: cmd += f' password {shlex.quote(pw)}'
                r = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=20)
                low = r.stdout.lower()
                if "successfully" in low or "activated" in low or r.returncode==0:
                    self.after(0, lambda: self.status_lbl.config(text="Connected!", fg="#39ff14"))
                    time.sleep(1); self.after(0, self.on_show)
                else:
                    e = r.stdout.strip().split('\n')[-1]
                    self.after(0, lambda: self.status_lbl.config(text=f"Failed: {e[:25]}", fg="red"))
            except subprocess.TimeoutExpired:
                self.after(0, lambda: self.status_lbl.config(text="Timed out.", fg="red"))
            finally:
                self.after(0, lambda: self.btn_connect.config(state=tk.NORMAL, text="CONNECT"))
        threading.Thread(target=run, daemon=True).start()
    def disconnect_wifi(self):
        if not self.current_connected_ssid: return
        self.btn_disconnect.config(state=tk.DISABLED, text="DISCONNECTING...")
        def run():
            subprocess.run(f'sudo nmcli connection down {shlex.quote(self.current_connected_ssid)}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.after(0, lambda: self.btn_disconnect.config(state=tk.NORMAL, text="DISCONNECT"))
            self.after(0, self.on_show)
        threading.Thread(target=run, daemon=True).start()

class NmapPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="black", width=480, height=320)
        self.controller = controller; self.process = None
        self.target_ip = None; self.discover_hosts = {}; self.cat_page = 0
        tb = tk.Frame(self, bg="#111111"); tb.place(x=0, y=0, width=480, height=30)
        tk.Button(tb, text="< BACK", bg="#111111", fg="#39ff14", font=("Helvetica",11,"bold"), bd=0, command=self.smart_back).pack(side="left", fill="y")
        tk.Label(tb, text="NMAP SCANNER", bg="#111111", fg="#39ff14", font=("Helvetica",11,"bold")).pack(side="left", expand=True)
        self.log_frame = tk.Frame(self, bg="black")
        sb = tk.Scrollbar(self.log_frame); sb.pack(side="right", fill="y")
        self.log_area = tk.Text(self.log_frame, bg="black", fg="#39ff14", font=("Helvetica",11), bd=0, padx=5, pady=5, yscrollcommand=sb.set)
        self.log_area.pack(side="left", fill="both", expand=True); sb.config(command=self.log_area.yview)
        make_readonly_text(self.log_area)
        self.btn_stop = tk.Button(self, text="STOP SCAN", font=("Helvetica",11,"bold"), bg="#aa0000", fg="white", command=self.stop_scan)
        self.target_frame = tk.Frame(self, bg="black")
        tk.Button(self.target_frame, text="AUTO SCAN", font=("Helvetica",12,"bold"), bg="#005500", fg="white", command=self.start_modem_scan).place(x=20, y=40, width=200, height=100)
        tk.Button(self.target_frame, text="CUSTOM TARGET", font=("Helvetica",12,"bold"), bg="#1a1a1a", fg="#39ff14", command=self.show_custom_options).place(x=260, y=40, width=200, height=100)
        tk.Button(self.target_frame, text="CLEAR SAVED SCANS", font=("Helvetica",11,"bold"), bg="#aa0000", fg="white", command=self.show_confirm_delete).place(x=100, y=160, width=280, height=45)
        self.custom_frame = tk.Frame(self, bg="black")
        tk.Button(self.custom_frame, text="MANUAL IP", font=("Helvetica",12,"bold"), bg="#1a1a1a", fg="#39ff14", command=self.show_ip_input).place(x=20, y=80, width=200, height=100)
        tk.Button(self.custom_frame, text="DISCOVER DEVICES", font=("Helvetica",12,"bold"), bg="#333", fg="#39ff14", command=self.show_discover_screen).place(x=260, y=80, width=200, height=100)
        self.input_frame = tk.Frame(self, bg="black")
        self.ip_entry = tk.Entry(self.input_frame, font=("Helvetica",14), bg="#222", fg="white", bd=2, relief="solid")
        self.ip_entry.place(x=10, y=5, width=460, height=30)
        self.keyboard_frame = tk.Frame(self.input_frame, bg="black"); self.keyboard_frame.place(x=0, y=40, width=480, height=210)
        self.create_keyboard()
        tk.Button(self.input_frame, text="CONFIRM", font=("Helvetica",11,"bold"), bg="#005500", fg="white", command=self.confirm_ip).place(x=0, y=260, width=240, height=30)
        tk.Button(self.input_frame, text="CANCEL", font=("Helvetica",11,"bold"), bg="#aa0000", fg="white", command=self.show_custom_options).place(x=240, y=260, width=240, height=30)
        self.discover_frame = tk.Frame(self, bg="black")
        self.discover_list = tk.Listbox(self.discover_frame, bg="black", fg="#39ff14", font=("Helvetica",12), bd=0)
        self.discover_list.pack(fill="both", expand=True, padx=10, pady=5)
        self.discover_list.bind("<<ListboxSelect>>", self.on_discover_select)
        self.btn_discover_scan = tk.Button(self.discover_frame, text="SCAN NETWORK", font=("Helvetica",11,"bold"), bg="#005500", fg="white", command=self.start_discover_scan)
        self.btn_discover_scan.pack(side="bottom", fill="x", padx=10, pady=5)
        self.category_frame = tk.Frame(self, bg="black")
        self.lbl_target = tk.Label(self.category_frame, text="", bg="black", fg="yellow", font=("Helvetica",12,"bold")); self.lbl_target.pack(pady=2)
        cc = tk.Frame(self.category_frame, bg="black"); cc.pack(fill="both", expand=True, padx=5, pady=2)
        tk.Button(cc, text="<", font=("Helvetica",14,"bold"), bg="#1a1a1a", fg="#39ff14", bd=1, relief="solid", highlightbackground="#39ff14", command=self.prev_cat_page).pack(side="left", fill="y", padx=2)
        self.cat_grid = tk.Frame(cc, bg="black"); self.cat_grid.pack(side="left", fill="both", expand=True)
        tk.Button(cc, text=">", font=("Helvetica",14,"bold"), bg="#1a1a1a", fg="#39ff14", bd=1, relief="solid", highlightbackground="#39ff14", command=self.next_cat_page).pack(side="right", fill="y", padx=2)
        self.confirm_bg = tk.Frame(self, bg="#050505")
        self.confirm_bg.bind("<Button-1>", lambda e: self.hide_confirm_delete())
        cb = tk.Frame(self.confirm_bg, bg="#111111", bd=2, relief="solid", highlightbackground="#aa0000", highlightthickness=2)
        cb.place(relx=0.5, rely=0.5, anchor="center", width=360, height=160)
        tk.Label(cb, text="CLEAR SCAN LOGS", bg="#111111", fg="#aa0000", font=("Helvetica",14,"bold")).pack(pady=(15,5))
        tk.Label(cb, text="Delete all saved nmap scans?", bg="#111111", fg="white", font=("Helvetica",11)).pack(pady=5)
        bf = tk.Frame(cb, bg="#111111"); bf.pack(pady=10)
        tk.Button(bf, text="YES, DELETE", font=("Helvetica",11,"bold"), bg="#aa0000", fg="white", command=self.do_clear_scans, width=12).pack(side="left", padx=10)
        tk.Button(bf, text="CANCEL", font=("Helvetica",11,"bold"), bg="#333", fg="white", command=self.hide_confirm_delete, width=12).pack(side="right", padx=10)
    def show_confirm_delete(self): self.confirm_bg.place(x=0, y=0, width=480, height=320)
    def hide_confirm_delete(self): self.confirm_bg.place_forget()
    def do_clear_scans(self):
        d = os.path.expanduser("~/nmap_scans")
        if os.path.exists(d):
            for f in os.listdir(d):
                tool_prefix = re.sub(r'[^a-zA-Z0-9]', '_', self.TOOL_NAME) + "_"
                if f.endswith(".txt") and f.startswith(tool_prefix):
                    try: os.remove(os.path.join(d, f))
                    except: pass
        self.hide_confirm_delete()
    def smart_back(self):
        if self.confirm_bg.place_info(): self.hide_confirm_delete()
        elif self.log_frame.place_info():
            if self.process: self.stop_scan()
            self.show_categories()
        elif self.input_frame.place_info(): self.show_custom_options()
        elif self.discover_frame.place_info(): self.show_custom_options()
        elif self.category_frame.place_info(): self.show_initial()
        elif self.custom_frame.place_info(): self.show_initial()
        else: self.controller.go_back()
    def on_show(self): self.show_initial()
    def show_initial(self):
        for f in (self.log_frame, self.custom_frame, self.input_frame, self.discover_frame, self.category_frame, self.confirm_bg): f.place_forget()
        self.btn_stop.place_forget(); self.target_frame.place(x=0, y=30, width=480, height=260)
    def show_custom_options(self):
        self.target_frame.place_forget(); self.input_frame.place_forget(); self.discover_frame.place_forget()
        self.custom_frame.place(x=0, y=30, width=480, height=260)
    def show_discover_screen(self):
        self.custom_frame.place_forget(); self.discover_frame.place(x=0, y=30, width=480, height=260)
        self.discover_list.delete(0, tk.END); self.start_discover_scan()
    def start_discover_scan(self):
        self.discover_list.delete(0, tk.END); self.discover_list.insert(tk.END, "Scanning...")
        self.btn_discover_scan.config(state=tk.DISABLED, text="SCANNING...")
        def run():
            subprocess.run("sudo iw dev wlan0 set power_save off", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            s = subprocess.run("ip -o -f inet addr show wlan0 | awk '{print $4}'", shell=True, stdout=subprocess.PIPE, text=True).stdout.strip()
            if s:
                r = subprocess.run(f"sudo nmap -sn -PR -PE -PS22,80,443 {s}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
                hosts = {}
                for line in r.stdout.splitlines():
                    if "Nmap scan report for" in line:
                        m = re.search(r'Nmap scan report for (.+?)(?:\s+\(([\d.]+)\))?\s*$', line)
                        if m:
                            n = m.group(1).strip(); ip = m.group(2) if m.group(2) else n
                            d = ip if re.match(r'^\d{1,3}(\.\d{1,3}){3}$', n) else f"{n} ({ip})"
                            hosts[d] = ip
                self.after(0, self.update_discover_list, hosts)
            else: self.after(0, self.update_discover_list, {})
        threading.Thread(target=run, daemon=True).start()
    def update_discover_list(self, hosts):
        self.discover_list.delete(0, tk.END); self.btn_discover_scan.config(state=tk.NORMAL, text="RESCAN")
        if not hosts: self.discover_list.insert(tk.END, "No devices."); return
        self.discover_hosts = hosts
        for d in hosts: self.discover_list.insert(tk.END, d)
    def on_discover_select(self, e):
        sel = self.discover_list.curselection()
        if sel:
            ip = self.discover_hosts.get(self.discover_list.get(sel[0]))
            if ip and re.match(r'^\d{1,3}(\.\d{1,3}){3}$', ip): self.target_ip = ip; self.cat_page = 0; self.show_categories()
    def create_keyboard(self):
        for row in ["1234567890","qwertyuiop","asdfghjkl","zxcvbnm",[".","-","DEL","CANCEL"]]:
            f = tk.Frame(self.keyboard_frame, bg="black"); f.pack(side="top", fill="x", expand=True)
            if isinstance(row, list):
                for ch in row:
                    if ch=="DEL": b = tk.Button(f, text="DEL", command=self.del_char, bg="#aa0000", fg="white", font=("Helvetica",11,"bold"))
                    elif ch=="CANCEL": b = tk.Button(f, text="CANCEL", command=self.show_custom_options, bg="#333", fg="white", font=("Helvetica",11,"bold"))
                    else: b = tk.Button(f, text=ch, command=lambda c=ch: self.add_char(c), bg="#222", fg="#39ff14", font=("Helvetica",14,"bold"))
                    b.pack(side="left", fill="both", expand=True, padx=1, pady=1)
            else:
                for ch in row:
                    b = tk.Button(f, text=ch, command=lambda c=ch: self.add_char(c), bg="#222", fg="#39ff14", font=("Helvetica",14,"bold"))
                    b.pack(side="left", fill="both", expand=True, padx=1, pady=1)
    def add_char(self, ch): self.ip_entry.insert(tk.END, ch)
    def del_char(self):
        c = self.ip_entry.get()
        if c: self.ip_entry.delete(len(c)-1, tk.END)
    def show_ip_input(self):
        self.custom_frame.place_forget(); self.input_frame.place(x=0, y=30, width=480, height=290); self.ip_entry.delete(0, tk.END)
    def confirm_ip(self):
        ip = self.ip_entry.get().strip()
        if len(ip) > 3: self.target_ip = ip; self.cat_page = 0; self.show_categories()
        else:
            self.ip_entry.config(bg="#500000"); self.after(500, lambda: self.ip_entry.config(bg="#222"))
    def start_modem_scan(self):
        s = subprocess.run("ip -o -f inet addr show wlan0 | awk '{print $4}'", shell=True, stdout=subprocess.PIPE, text=True).stdout.strip()
        if s: self.target_ip = s; self.cat_page = 0; self.show_categories()
        else: self.show_initial()
    def show_categories(self):
        for f in (self.input_frame, self.discover_frame, self.custom_frame, self.target_frame, self.log_frame): f.place_forget()
        self.btn_stop.place_forget(); self.lbl_target.config(text=f"TARGET: {self.target_ip}")
        self.render_categories(); self.category_frame.place(x=0, y=30, width=480, height=260)
    def prev_cat_page(self):
        if self.cat_page > 0: self.cat_page -= 1; self.render_categories()
    def next_cat_page(self):
        if self.cat_page < 1: self.cat_page += 1; self.render_categories()
    def render_categories(self):
        for w in self.cat_grid.winfo_children(): w.destroy()
        if self.cat_page == 0:
            cats = [("INTENSE\n-A -T4","#005500","intense"),("ALL PORTS\n-p- -T4","#005500","allports"),("VULN\n--script vuln","#cc8800","vuln"),
                    ("STEALTH\n-sS -T2","#1a1a1a","stealth"),("QUICK\n-F -T4","#1a1a1a","quick"),("OS+VER\n-sV -O","#1a1a1a","osver")]
        else:
            cats = [("PING\n-sn","#1a1a1a","ping"),("UDP\n-sU top 50","#1a1a1a","udp"),("TRACEROUTE","#1a1a1a","traceroute"),
                    ("DFLT SCRIPTS\n-sC","#1a1a1a","default"),("ARP SCAN\n-sn -PR","#1a1a1a","arp"),("EVASION\n-f -T2","#1a1a1a","evasion")]
        for i, (t, c, m) in enumerate(cats):
            tk.Button(self.cat_grid, text=t, font=("Helvetica",10,"bold"), bg=c, fg="white", bd=1, relief="solid", highlightbackground="#39ff14", highlightthickness=1, command=lambda mm=m: self.run_scan(mm)).grid(row=i//3, column=i%3, padx=2, pady=2, sticky="nsew")
        for i in range(2): self.cat_grid.grid_rowconfigure(i, weight=1)
        for i in range(3): self.cat_grid.grid_columnconfigure(i, weight=1)
    def run_scan(self, mode):
        self.category_frame.place_forget(); self.log_frame.place(x=0, y=30, width=480, height=260)
        self.btn_stop.place(x=240, y=290, width=240, height=30)
        self.log_area.config(state=tk.NORMAL); self.log_area.delete(1.0, tk.END)
        self.log_area.insert(tk.END, f"Starting {mode.upper()} on {self.target_ip}...\n\n"); self.log_area.config(state=tk.DISABLED)
        os.makedirs(os.path.expanduser("~/nmap_scans"), exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S"); fn = os.path.expanduser(f"~/nmap_scans/nmap_{ts}_{mode}.txt")
        cmds = {"intense":f"sudo nmap -A -T4 {self.target_ip}","allports":f"sudo nmap -p- -T4 {self.target_ip}",
                "vuln":f"sudo nmap --script vuln {self.target_ip}","stealth":f"sudo nmap -sS -T2 -f {self.target_ip}",
                "quick":f"sudo nmap -F -T4 {self.target_ip}","osver":f"sudo nmap -sV -O {self.target_ip}",
                "ping":f"nmap -sn {self.target_ip}","udp":f"sudo nmap -sU --top-ports 50 {self.target_ip}",
                "traceroute":f"sudo nmap --traceroute {self.target_ip}","default":f"sudo nmap -sC {self.target_ip}",
                "arp":f"sudo nmap -sn -PR {self.target_ip}","evasion":f"sudo nmap -f -T2 {self.target_ip}"}
        self._sureci(f"{cmds.get(mode, f'nmap {self.target_ip}')} | tee {fn}")
    def _sureci(self, cmd):
        m, s = pty.openpty()
        env = os.environ.copy(); env.update({"PYTHONUNBUFFERED":"1","TERM":"dumb","LANG":"C.UTF-8","LC_ALL":"C.UTF-8"})
        self.process = subprocess.Popen(cmd, shell=True, stdin=s, stdout=s, stderr=s, env=env, text=True, bufsize=1, start_new_session=True)
        os.close(s)
        def r():
            try:
                while True:
                    try:
                        d = os.read(m, 4096)
                        if not d: break
                        for line in d.decode('utf-8', errors='replace').splitlines():
                            if line.strip(): self.log(line.strip())
                    except OSError: break
            finally:
                try: os.close(m)
                except: pass
                self.after(0, lambda: self.btn_stop.place_forget()); self.after(0, lambda: self.log("\n[-] Done."))
        threading.Thread(target=r, daemon=True).start()
    def stop_scan(self):
        if self.process:
            self.log("\n[!] Stopping...")
            try: os.killpg(os.getpgid(self.process.pid), signal.SIGINT)
            except: pass
            self.process = None
    def log(self, m):
        t = ansi_temizle(m)
        if not t.strip(): return
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, t+"\n")
        log_sinirla(self.log_area)
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)


class DirScanPage(tk.Frame):
    QUICK_WORDS = [
        "admin","administrator","login","logout","dashboard","api","test","dev","staging","backup","backups",
        "config","configs","setup","install","upload","uploads","images","img","css","js","static","assets",
        "media","files","download","downloads","robots.txt","sitemap.xml","index.php","index.html","index.htm",
        ".git",".env",".htaccess",".htpasswd",".gitignore",".svn","wp-admin","wp-login.php","wp-content",
        "wp-includes","wp-config.php","xmlrpc.php","readme","readme.html","readme.txt","license","license.txt",
        "changelog","changelog.txt","phpmyadmin","mysql","myadmin","pma","adminer","adminer.php","cpanel",
        "webmail","mail","mailer","email","cgi-bin","server-status","server-info","status","info","phpinfo.php",
        "php_info.php","test.php","info.php","db","database","sql","backup.sql","dump.sql","api/v1","api/v2",
        "api/v3","rest","graphql","user","users","account","accounts","profile","profiles","settings",
        "preferences","options","register","signup","signin","auth","oauth","sso","search","query","find",
        "results","contact","about","help","faq","support","docs","portal","panel","console","manage",
        "management","control","cms","wordpress","joomla","drupal","magento","app","apps","application",
        "applications","log","logs","error","errors","debug","trace","web","www","public","private","internal",
        "old","new","temp","tmp","cache","shell","cmd","exec","run","system","config.php","config.json",
        "config.xml","config.ini","settings.php","settings.json","app.php","app.json","main.php","main.html",
        "home","home.html","page","pages","post","posts","article","articles","forum","blog","news","wiki",
        "vendor","node_modules","bower_components","composer.json","package.json","package-lock.json",
        "yarn.lock","Dockerfile","docker-compose.yml",".dockerignore","makefile","Makefile","build","dist",
        "uploads/2024","uploads/2023","uploads/files","uploads/images","cgi","cgi-bin/test.cgi",
        "cgi-bin/printenv","web.config","crossdomain.xml","clientaccesspolicy.xml","trace.axd","elmah.axd",
        "Global.asax","web.config.bak",
    ]
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="black", width=480, height=320)
        self.controller = controller; self.scanning = False
        self.target_url = None; self.scan_mode = None; self.selected_wordlist = None
        self.use_tor = False; self._wl_data = []; self.current_log_file = None; self.found_count = 0
        tb = tk.Frame(self, bg="#111111"); tb.place(x=0, y=0, width=480, height=30)
        tk.Button(tb, text="< BACK", bg="#111111", fg="#39ff14", font=("Helvetica",11,"bold"), bd=0, command=self.smart_back).pack(side="left", fill="y")
        tk.Label(tb, text="DIR SCANNER", bg="#111111", fg="#39ff14", font=("Helvetica",11,"bold")).pack(side="left", expand=True)
        tk.Button(tb, text="CLR LOGS", bg="#111111", fg="#aa0000", font=("Helvetica",9,"bold"), bd=0, command=self.show_clear_dialog).pack(side="right", fill="y", padx=(0,6))
        self.input_frame = tk.Frame(self, bg="black")
        self.url_entry = tk.Entry(self.input_frame, font=("Helvetica",14), bg="#222", fg="white", bd=2, relief="solid")
        self.url_entry.place(x=10, y=5, width=460, height=30)
        tk.Label(self.input_frame, text="Enter URL (http:// optional)", bg="black", fg="yellow", font=("Helvetica",9)).place(x=10, y=38)
        self.keyboard_frame = tk.Frame(self.input_frame, bg="black"); self.keyboard_frame.place(x=0, y=60, width=480, height=190)
        self.create_keyboard()
        tk.Button(self.input_frame, text="CONTINUE", font=("Helvetica",11,"bold"), bg="#005500", fg="white", command=self.go_to_mode_select).place(x=0, y=260, width=240, height=30)
        tk.Button(self.input_frame, text="CANCEL", font=("Helvetica",11,"bold"), bg="#aa0000", fg="white", command=controller.go_back).place(x=240, y=260, width=240, height=30)
        self.mode_frame = tk.Frame(self, bg="black")
        tk.Label(self.mode_frame, text="SCAN MODE", bg="black", fg="#39ff14", font=("Helvetica",14,"bold")).pack(pady=(15,5))
        self.mode_target_lbl = tk.Label(self.mode_frame, text="", bg="black", fg="yellow", font=("Helvetica",10), wraplength=440); self.mode_target_lbl.pack(pady=(0,10))
        tk.Button(self.mode_frame, text="QUICK SCAN\n(~150 words)", font=("Helvetica",12,"bold"), bg="#005500", fg="white", command=self.choose_short_mode, height=3).pack(pady=5, padx=20, fill="x")
        tk.Button(self.mode_frame, text="WORDLIST\n(Choose a file)", font=("Helvetica",12,"bold"), bg="#333", fg="#39ff14", command=self.choose_wordlist_mode, height=3).pack(pady=5, padx=20, fill="x")
        self.wordlist_frame = tk.Frame(self, bg="black")
        tk.Label(self.wordlist_frame, text="SELECT WORDLIST", bg="black", fg="#39ff14", font=("Helvetica",12,"bold")).pack(pady=(8,5))
        wl = tk.Frame(self.wordlist_frame, bg="black"); wl.pack(fill="both", expand=True, padx=10, pady=(0,8))
        sb = tk.Scrollbar(wl); sb.pack(side="right", fill="y")
        self.wl_listbox = tk.Listbox(wl, bg="black", fg="#39ff14", font=("Helvetica",10), bd=0, yscrollcommand=sb.set)
        self.wl_listbox.pack(side="left", fill="both", expand=True); sb.config(command=self.wl_listbox.yview)
        self.wl_listbox.bind('<<ListboxSelect>>', self.on_wordlist_select)
        self.tor_frame = tk.Frame(self, bg="black")
        tk.Label(self.tor_frame, text="CONNECTION MODE", bg="black", fg="#39ff14", font=("Helvetica",14,"bold")).pack(pady=(20,5))
        tk.Label(self.tor_frame, text="How should requests be sent?", bg="black", fg="white", font=("Helvetica",10)).pack(pady=5)
        tk.Button(self.tor_frame, text="DIRECT", font=("Helvetica",12,"bold"), bg="#005500", fg="white", command=lambda: self.start_scan(False), width=15, height=2).pack(pady=8)
        tk.Button(self.tor_frame, text="VIA TOR", font=("Helvetica",12,"bold"), bg="#330000", fg="#aa0000", command=lambda: self.start_scan(True), width=15, height=2).pack(pady=8)
        self.log_frame = tk.Frame(self, bg="black")
        lsb = tk.Scrollbar(self.log_frame); lsb.pack(side="right", fill="y")
        self.log_area = tk.Text(self.log_frame, bg="black", fg="#39ff14", font=("Helvetica",10), bd=0, padx=5, pady=5, yscrollcommand=lsb.set)
        self.log_area.pack(side="left", fill="both", expand=True); lsb.config(command=self.log_area.yview)
        make_readonly_text(self.log_area)
        self.btn_stop = tk.Button(self, text="STOP SCAN", font=("Helvetica",11,"bold"), bg="#aa0000", fg="white", command=self.stop_scan)
    def show_clear_dialog(self):
        if hasattr(self, 'clear_bg'): return
        d = os.path.expanduser("~/dirscan_logs")
        count = 0; total = 0
        if os.path.exists(d):
            for f in os.listdir(d):
                if f.endswith(".txt"):
                    try:
                        count += 1
                        total += os.path.getsize(os.path.join(d, f))
                    except: pass
        if count == 0:
            self.log("[*] No logs to clear."); return
        size_str = (f"{total/1024:.1f}KB" if total < 1024*1024 else f"{total/(1024*1024):.1f}MB")
        self.clear_bg = tk.Frame(self, bg="#050505")
        self.clear_bg.place(x=0, y=0, width=480, height=320)
        self.clear_bg.bind("<Button-1>", lambda e: self.hide_clear_dialog())
        ov = tk.Frame(self.clear_bg, bg="#111111", bd=2, relief="solid", highlightbackground="#aa0000", highlightthickness=2)
        ov.place(relx=0.5, rely=0.5, anchor="center", width=360, height=170)
        tk.Label(ov, text="CLEAR LOGS", bg="#111111", fg="#aa0000", font=("Helvetica",14,"bold")).pack(pady=(15,5))
        tk.Label(ov, text=f"Delete {count} dirscan log(s)\n({size_str})?", bg="#111111", fg="white", font=("Helvetica",11), justify="center").pack(pady=5)
        bf = tk.Frame(ov, bg="#111111"); bf.pack(pady=10)
        tk.Button(bf, text="YES, DELETE", font=("Helvetica",11,"bold"), bg="#aa0000", fg="white", command=self._do_clear_logs, width=12).pack(side="left", padx=10)
        tk.Button(bf, text="CANCEL", font=("Helvetica",11,"bold"), bg="#333", fg="white", command=self.hide_clear_dialog, width=12).pack(side="right", padx=10)

    def hide_clear_dialog(self):
        if hasattr(self, 'clear_bg'):
            self.clear_bg.destroy(); del self.clear_bg

    def _do_clear_logs(self):
        d = os.path.expanduser("~/dirscan_logs")
        count = 0
        if os.path.exists(d):
            for f in os.listdir(d):
                if f.endswith(".txt"):
                    try: os.remove(os.path.join(d, f)); count += 1
                    except: pass
        self.hide_clear_dialog()
        self.log(f"[*] Cleared {count} log file(s).")
    def on_show(self): self.show_input(); self.url_entry.delete(0, tk.END)
    def show_input(self):
        for f in (self.mode_frame, self.wordlist_frame, self.tor_frame, self.log_frame): f.place_forget()
        self.btn_stop.place_forget(); self.input_frame.place(x=0, y=30, width=480, height=290)
    def go_to_mode_select(self):
        u = self.url_entry.get().strip()
        if not u: return
        if not u.startswith("http://") and not u.startswith("https://"): u = "http://" + u
        if u.endswith("/"): u = u[:-1]
        self.target_url = u; self.mode_target_lbl.config(text=f"Target: {u}")
        self.input_frame.place_forget(); self.mode_frame.place(x=0, y=30, width=480, height=260)
    def choose_short_mode(self):
        self.scan_mode = "short"; self.mode_frame.place_forget(); self.tor_frame.place(x=0, y=30, width=480, height=260)
    def choose_wordlist_mode(self):
        self.scan_mode = "wordlist"; self.mode_frame.place_forget(); self.show_wordlist_select()
    def show_wordlist_select(self):
        self.wl_listbox.delete(0, tk.END); self._wl_data = []
        bases = [os.path.expanduser("~/wordlists"), "/usr/share/wordlists", os.path.join(os.getcwd(), "wordlists")]
        found = []
        for base in bases:
            if os.path.isdir(base):
                for root, dirs, files in os.walk(base):
                    if root[len(base):].count(os.sep) > 2: dirs[:] = []; continue
                    for f in files:
                        if f.lower().endswith(('.txt','.lst','.wordlist')):
                            p = os.path.join(root, f)
                            try: sz = os.path.getsize(p)
                            except: sz = 0
                            found.append((p, f, sz))
        if not found:
            self.wl_listbox.insert(tk.END, "No wordlists found.")
            self.wl_listbox.insert(tk.END, "Add .txt files to ~/wordlists/")
        else:
            for p, n, s in found:
                ss = f"{s/(1024*1024):.1f}MB" if s>=1024*1024 else f"{s/1024:.0f}KB" if s>=1024 else f"{s}B"
                self.wl_listbox.insert(tk.END, f"{n} ({ss})"); self._wl_data.append(p)
        self.wordlist_frame.place(x=0, y=30, width=480, height=260)
    def on_wordlist_select(self, e):
        sel = self.wl_listbox.curselection()
        if not sel: return
        i = sel[0]
        if i >= len(self._wl_data): return
        self.selected_wordlist = self._wl_data[i]
        self.wordlist_frame.place_forget(); self.tor_frame.place(x=0, y=30, width=480, height=260)
    def start_scan(self, use_tor):
        self.use_tor = use_tor; self.tor_frame.place_forget()
        self.log_frame.place(x=0, y=30, width=480, height=260); self.btn_stop.place(x=240, y=290, width=240, height=30)
        self.log_area.config(state=tk.NORMAL); self.log_area.delete(1.0, tk.END); self.log_area.config(state=tk.DISABLED)
        self.log(f"Target: {self.target_url}"); self.log(f"Mode: {self.scan_mode.upper()}")
        self.log(f"Connection: {'TOR' if use_tor else 'DIRECT'}")
        if self.scan_mode == "wordlist": self.log(f"Wordlist: {os.path.basename(self.selected_wordlist)}")
        self.log(""); self.scanning = True; self.found_count = 0
        threading.Thread(target=self._run_scan, daemon=True).start()
    def _run_scan(self):
        if self.scan_mode == "short": words = self.QUICK_WORDS.copy()
        else:
            try:
                with open(self.selected_wordlist, "r", errors="ignore") as f:
                    words = [l.strip() for l in f if l.strip() and not l.startswith("#")]
            except Exception as e:
                self.log(f"Error: {e}"); self._finish(); return
        words = list(dict.fromkeys(words))
        proxies = {"http":"socks5h://127.0.0.1:9050","https":"socks5h://127.0.0.1:9050"} if self.use_tor else None
        timeout = 8 if self.use_tor else 4
        import urllib3; urllib3.disable_warnings()
        self.log("[*] Detecting wildcard...")
        bs = None; bl = None; bb = None
        try:
            rp = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=24))
            r = requests.get(f"{self.target_url}/{rp}", timeout=timeout, allow_redirects=False, verify=False, headers={"User-Agent":"Mozilla/5.0"}, proxies=proxies)
            bs = r.status_code; bl = len(r.content); bb = r.content[:1000]
            self.log(f"[*] Baseline: {bs} ({bl}b)")
            if bs == 200: self.log("[!] Server returns 200 for all paths, filtering")
        except Exception as e:
            self.log(f"[*] Baseline failed: {str(e)[:40]}")
        os.makedirs(os.path.expanduser("~/dirscan_logs"), exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        cn = re.sub(r'[^a-zA-Z0-9]', '_', self.target_url.replace("http://","").replace("https://",""))[:30]
        lf = os.path.expanduser(f"~/dirscan_logs/{ts}_{cn}.txt"); self.current_log_file = lf
        try:
            with open(lf, "w") as f:
                f.write(f"# DIR SCAN\nTarget: {self.target_url}\nMode: {self.scan_mode}\n")
                f.write(f"Connection: {'TOR' if self.use_tor else 'DIRECT'}\nDate: {datetime.datetime.now()}\nBaseline: {bs} ({bl}b)\n\n")
        except: pass
        def save(l):
            try:
                with open(lf, "a") as f: f.write(l+"\n")
            except: pass
        self.log(f"Total words: {len(words)}")
        threads = 10 if self.use_tor else 30
        self.log(f"Threads: {threads}\n")
        from concurrent.futures import ThreadPoolExecutor, as_completed
        def check(w):
            if not self.scanning: return None
            u = f"{self.target_url}/{w}"
            try:
                r = requests.get(u, timeout=timeout, allow_redirects=False, verify=False, headers={"User-Agent":"Mozilla/5.0"}, proxies=proxies)
                c = r.status_code; s = len(r.content); b = r.content[:1000]
                if c >= 400 and c not in (401, 403): return None
                if bs == 200 and bl is not None:
                    if bb and b == bb: return None
                    if abs(s - bl) <= max(10, int(bl*0.02)): return None
                extra = ""
                if c in (301, 302):
                    loc = r.headers.get("Location", "")[:60]
                    if loc: extra = f"-> {loc}"
                return (u, c, s, extra)
            except: pass
            return None
        try:
            with ThreadPoolExecutor(max_workers=threads) as ex:
                futs = {ex.submit(check, w): w for w in words}
                for fut in as_completed(futs):
                    if not self.scanning: break
                    try:
                        res = fut.result()
                        if res:
                            u, c, s, e = res
                            line = f"[{c}] {u} ({s}b) {e}".strip()
                            self.log(line); save(line); self.found_count += 1
                    except: pass
        except Exception as e: self.log(f"Error: {e}")
        self.log(f"\n[+] Found: {self.found_count}")
        self.log(f"[-] Complete.")
        self.log(f"[*] Saved: ~/dirscan_logs/{os.path.basename(lf)}")
        self._finish()
    def _finish(self):
        self.scanning = False; self.after(0, lambda: self.btn_stop.place_forget())
    def stop_scan(self):
        self.scanning = False; self.log("\n[!] Stopping..."); self.btn_stop.place_forget()
    def smart_back(self):
        if hasattr(self, 'clear_bg'):
            self.hide_clear_dialog(); return
        if self.log_frame.place_info():
            if self.scanning: self.stop_scan()
            self.show_input()
        elif self.tor_frame.place_info():
            self.tor_frame.place_forget()
            if self.scan_mode == "wordlist": self.show_wordlist_select()
            else: self.mode_frame.place(x=0, y=30, width=480, height=260)
        elif self.wordlist_frame.place_info():
            self.wordlist_frame.place_forget()
            self.mode_frame.place(x=0, y=30, width=480, height=260)
        elif self.mode_frame.place_info(): self.show_input()
        else: self.controller.go_back()
    def create_keyboard(self):
        for row in ["1234567890","qwertyuiop","asdfghjkl","zxcvbnm",["/",".",":","-","DEL","CANCEL"]]:
            f = tk.Frame(self.keyboard_frame, bg="black"); f.pack(side="top", fill="x", expand=True)
            for ch in row:
                if ch=="DEL": b = tk.Button(f, text="DEL", command=self.del_char, bg="#aa0000", fg="white", font=("Helvetica",11,"bold"))
                elif ch=="CANCEL": b = tk.Button(f, text="CANCEL", command=self.controller.go_back, bg="#333", fg="white", font=("Helvetica",11,"bold"))
                else: b = tk.Button(f, text=ch, command=lambda c=ch: self.add_char(c), bg="#222", fg="#39ff14", font=("Helvetica",14,"bold"))
                b.pack(side="left", fill="both", expand=True, padx=1, pady=1)
    def add_char(self, ch): self.url_entry.insert(tk.END, ch)
    def del_char(self):
        c = self.url_entry.get()
        if c: self.url_entry.delete(len(c)-1, tk.END)
    def log(self, m):
        def _l():
            self.log_area.config(state=tk.NORMAL)
            self.log_area.insert(tk.END, m+"\n")
            log_sinirla(self.log_area)
            self.log_area.see(tk.END)
            self.log_area.config(state=tk.DISABLED)
        self.after(0, _l)

class FileManagerPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="black", width=480, height=320)
        self.controller = controller
        self.active_pane = "left"
        usb = self._find_usb()
        self.left_dir = usb
        self.right_dir = os.path.expanduser("~")
        self.msg_bg = None

        tb = tk.Frame(self, bg="#111111"); tb.place(x=0, y=0, width=480, height=30)
        tk.Button(tb, text="< BACK", bg="#111111", fg="#39ff14", font=("Helvetica",11,"bold"), bd=0, command=controller.go_back).pack(side="left", fill="y")
        tk.Label(tb, text="FILE MANAGER", bg="#111111", fg="#39ff14", font=("Helvetica",11,"bold")).pack(side="left", expand=True)

        self.left_frame = tk.Frame(self, bg="black", highlightbackground="#39ff14", highlightthickness=2)
        self.left_frame.place(x=1, y=31, width=238, height=214)
        self.left_path_lbl = tk.Label(self.left_frame, text="", bg="#111111", fg="yellow", font=("Helvetica",8,"bold"), anchor="w", cursor="hand2")
        self.left_path_lbl.pack(fill="x")
        self.left_path_lbl.bind("<Button-1>", lambda e: self._goto_usb("left"))
        left_inner = tk.Frame(self.left_frame, bg="black"); left_inner.pack(fill="both", expand=True)
        lsb_left = tk.Scrollbar(left_inner); lsb_left.pack(side="right", fill="y")
        self.left_list = tk.Listbox(left_inner, bg="black", fg="#39ff14", font=("Helvetica",10), bd=0, yscrollcommand=lsb_left.set, selectbackground="#005500", activestyle="none", exportselection=False)
        self.left_list.pack(side="left", fill="both", expand=True)
        lsb_left.config(command=self.left_list.yview)
        self.left_list.bind("<<ListboxSelect>>", lambda e: self.on_select("left"))

        self.right_frame = tk.Frame(self, bg="black", highlightbackground="#333333", highlightthickness=2)
        self.right_frame.place(x=241, y=31, width=238, height=214)
        self.right_path_lbl = tk.Label(self.right_frame, text="", bg="#111111", fg="yellow", font=("Helvetica",8,"bold"), anchor="w", cursor="hand2")
        self.right_path_lbl.pack(fill="x")
        self.right_path_lbl.bind("<Button-1>", lambda e: self._goto_usb("right"))
        right_inner = tk.Frame(self.right_frame, bg="black"); right_inner.pack(fill="both", expand=True)
        lsb_right = tk.Scrollbar(right_inner); lsb_right.pack(side="right", fill="y")
        self.right_list = tk.Listbox(right_inner, bg="black", fg="#39ff14", font=("Helvetica",10), bd=0, yscrollcommand=lsb_right.set, selectbackground="#005500", activestyle="none", exportselection=False)
        self.right_list.pack(side="left", fill="both", expand=True)
        lsb_right.config(command=self.right_list.yview)
        self.right_list.bind("<<ListboxSelect>>", lambda e: self.on_select("right"))

        bs = {"bg":"#1a1a1a","fg":"#39ff14","font":("Helvetica",9,"bold"),"bd":1,"relief":"solid","highlightbackground":"#39ff14"}
        tk.Button(self, text="TAB", command=self.switch_pane, **bs).place(x=0, y=246, width=118, height=21)
        tk.Button(self, text="OPEN", command=self.open_selected, **bs).place(x=120, y=246, width=118, height=21)
        tk.Button(self, text="UP", command=self.go_up, **bs).place(x=240, y=246, width=118, height=21)
        tk.Button(self, text="REFRESH", command=self.refresh_panes, **bs).place(x=360, y=246, width=120, height=21)
        tk.Button(self, text="COPY", command=self.copy_to_other, **bs).place(x=0, y=268, width=94, height=21)
        tk.Button(self, text="MOVE", command=self.move_to_other, **bs).place(x=96, y=268, width=94, height=21)
        tk.Button(self, text="RENAME", command=self.show_rename_dialog, **bs).place(x=192, y=268, width=94, height=21)
        tk.Button(self, text="DELETE", command=self.show_delete_dialog, bg="#330000", fg="#aa0000", font=("Helvetica",9,"bold"), bd=1, relief="solid", highlightbackground="#aa0000").place(x=288, y=268, width=94, height=21)
        tk.Button(self, text="NEW DIR", command=self.create_dir, **bs).place(x=384, y=268, width=96, height=21)

        ekle_cikis_butonu(self, controller)
        self.refresh_panes()

    def _find_usb(self):
        candidates = []
        if os.path.isdir("/media"):
            try:
                for user in os.listdir("/media"):
                    upath = os.path.join("/media", user)
                    if os.path.isdir(upath):
                        for label in os.listdir(upath):
                            lpath = os.path.join(upath, label)
                            if os.path.isdir(lpath) and os.path.ismount(lpath):
                                candidates.append(lpath)
            except: pass
        if os.path.isdir("/mnt"):
            try:
                for entry in os.listdir("/mnt"):
                    p = os.path.join("/mnt", entry)
                    if os.path.isdir(p) and os.path.ismount(p):
                        candidates.append(p)
            except: pass
        return candidates[0] if candidates else os.path.expanduser("~")

    def _goto_usb(self, pane):
        usb = self._find_usb()
        if pane == "left": self.left_dir = usb
        else: self.right_dir = usb
        self.refresh_panes()

    def on_show(self): self.refresh_panes()

    def _get_active(self):
        return (self.left_list, self.left_dir) if self.active_pane == "left" else (self.right_list, self.right_dir)

    def _short_path(self, p):
        home = os.path.expanduser("~")
        if p == home: return "~"
        if p.startswith(home + "/"): p = "~" + p[len(home):]
        return "..." + p[-31:] if len(p) > 34 else p

    def _list_items(self, path):
        try: entries = os.listdir(path)
        except: return [("..", True)]
        dirs, files = [], []
        for n in entries:
            try:
                (dirs if os.path.isdir(os.path.join(path, n)) else files).append(n)
            except: pass
        dirs.sort(key=str.lower); files.sort(key=str.lower)
        return [("..", True)] + [(d, True) for d in dirs] + [(f, False) for f in files]

    def _update_listbox(self, lb, items, keep=None):
        lb.delete(0, tk.END)
        for name, is_dir in items:
            if name == "..": lb.insert(tk.END, "..")
            elif is_dir: lb.insert(tk.END, f"[{name}]")
            else: lb.insert(tk.END, name)
        if keep is not None and 0 <= keep < lb.size(): lb.selection_set(keep)

    def refresh_panes(self):
        ls = self.left_list.curselection(); rs = self.right_list.curselection()
        self._update_listbox(self.left_list, self._list_items(self.left_dir), ls[0] if ls else None)
        self._update_listbox(self.right_list, self._list_items(self.right_dir), rs[0] if rs else None)
        self.left_path_lbl.config(text=self._short_path(self.left_dir))
        self.right_path_lbl.config(text=self._short_path(self.right_dir))
        self.update_pane_colors()

    def update_pane_colors(self):
        if self.active_pane == "left":
            self.left_frame.config(highlightbackground="#39ff14"); self.right_frame.config(highlightbackground="#333333")
        else:
            self.left_frame.config(highlightbackground="#333333"); self.right_frame.config(highlightbackground="#39ff14")

    def on_select(self, pane):
        self.active_pane = pane; self.update_pane_colors()

    def switch_pane(self):
        self.active_pane = "right" if self.active_pane == "left" else "left"; self.update_pane_colors()

    def go_up(self):
        if self.active_pane == "left":
            p = os.path.dirname(self.left_dir)
            if p and p != self.left_dir: self.left_dir = p
        else:
            p = os.path.dirname(self.right_dir)
            if p and p != self.right_dir: self.right_dir = p
        self.refresh_panes()

    def open_selected(self):
        lst, cur = self._get_active()
        sel = lst.curselection()
        if not sel: return
        name = lst.get(sel[0])
        if name == "..": self.go_up(); return
        is_dir = name.startswith("[") and name.endswith("]")
        clean = name[1:-1] if is_dir else name
        full = os.path.join(cur, clean)
        if is_dir:
            new_dir = os.path.abspath(full)
            if self.active_pane == "left": self.left_dir = new_dir
            else: self.right_dir = new_dir
            self.refresh_panes()
        else:
            try:
                st = os.stat(full); size = st.st_size
                sz = f"{size}B" if size < 1024 else f"{size/1024:.1f}KB" if size < 1024*1024 else f"{size/(1024*1024):.1f}MB"
                mt = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")
                self.show_msg(f"{clean}\n\nSize: {sz}\nModified: {mt}")
            except Exception as e: self.show_msg(f"Error: {e}")

    def copy_to_other(self):
        if self.active_pane == "left": src, dst, lst = self.left_dir, self.right_dir, self.left_list
        else: src, dst, lst = self.right_dir, self.left_dir, self.right_list
        sel = lst.curselection()
        if not sel: return
        name = lst.get(sel[0])
        if name == "..": return
        if name.startswith("[") and name.endswith("]"): self.show_msg("Directory copy not supported"); return
        s, d = os.path.join(src, name), os.path.join(dst, name)
        if os.path.exists(d): self.show_msg(f"Already exists:\n{name}"); return
        try:
            import shutil; shutil.copy2(s, d); self.refresh_panes()
        except Exception as e: self.show_msg(f"Error: {str(e)[:50]}")

    def move_to_other(self):
        if self.active_pane == "left": src, dst, lst = self.left_dir, self.right_dir, self.left_list
        else: src, dst, lst = self.right_dir, self.left_dir, self.right_list
        sel = lst.curselection()
        if not sel: return
        name = lst.get(sel[0])
        if name == "..": return
        if name.startswith("[") and name.endswith("]"): self.show_msg("Directory move not supported"); return
        s, d = os.path.join(src, name), os.path.join(dst, name)
        if os.path.exists(d): self.show_msg(f"Already exists:\n{name}"); return
        try:
            import shutil; shutil.move(s, d); self.refresh_panes()
        except Exception as e: self.show_msg(f"Error: {str(e)[:50]}")

    def show_delete_dialog(self):
        if self.msg_bg: return
        lst, cur = self._get_active()
        sel = lst.curselection()
        if not sel: return
        name = lst.get(sel[0])
        if name == "..": return
        is_dir = name.startswith("[") and name.endswith("]")
        clean = name[1:-1] if is_dir else name
        full = os.path.join(cur, clean)
        self.msg_bg = tk.Frame(self, bg="#050505"); self.msg_bg.place(x=0, y=0, width=480, height=320)
        self.msg_bg.bind("<Button-1>", lambda e: self.close_msg())
        ov = tk.Frame(self.msg_bg, bg="#111111", bd=2, relief="solid", highlightbackground="#aa0000", highlightthickness=2)
        ov.place(relx=0.5, rely=0.5, anchor="center", width=400, height=170)
        ov.bind("<Button-1>", lambda e: "break")
        tk.Label(ov, text="DELETE?", bg="#111111", fg="#aa0000", font=("Helvetica",14,"bold")).pack(pady=(15,5))
        tk.Label(ov, text=f"{clean}\n({'DIR' if is_dir else 'FILE'})", bg="#111111", fg="white", font=("Helvetica",11,"bold"), wraplength=360).pack(pady=5)
        bf = tk.Frame(ov, bg="#111111"); bf.pack(pady=10)
        tk.Button(bf, text="YES", font=("Helvetica",11,"bold"), bg="#aa0000", fg="white", command=lambda: self._do_delete(full, is_dir), width=10).pack(side="left", padx=10)
        tk.Button(bf, text="NO", font=("Helvetica",11,"bold"), bg="#333", fg="white", command=self.close_msg, width=10).pack(side="right", padx=10)

    def _do_delete(self, path, is_dir):
        self.close_msg()
        try:
            import shutil
            shutil.rmtree(path) if is_dir else os.remove(path)
            self.refresh_panes()
        except Exception as e: self.show_msg(f"Error: {str(e)[:50]}")

    def show_rename_dialog(self):
        if self.msg_bg: return
        lst, cur = self._get_active()
        sel = lst.curselection()
        if not sel: return
        name = lst.get(sel[0])
        if name == "..": return
        is_dir = name.startswith("[") and name.endswith("]")
        clean = name[1:-1] if is_dir else name
        full = os.path.join(cur, clean)
        self.msg_bg = tk.Frame(self, bg="#050505"); self.msg_bg.place(x=0, y=0, width=480, height=320)
        ov = tk.Frame(self.msg_bg, bg="#111111", bd=2, relief="solid", highlightbackground="#39ff14", highlightthickness=2)
        ov.place(relx=0.5, rely=0.5, anchor="center", width=440, height=290)
        ov.bind("<Button-1>", lambda e: "break")
        tk.Label(ov, text="RENAME", bg="#111111", fg="#39ff14", font=("Helvetica",12,"bold")).pack(pady=(8,3))
        name_entry = tk.Entry(ov, font=("Helvetica",12), bg="#222", fg="white", bd=1, relief="solid")
        name_entry.pack(fill="x", padx=10, pady=5)
        name_entry.insert(0, clean); name_entry.icursor(len(clean)); name_entry.focus_set()
        kb = tk.Frame(ov, bg="#111111"); kb.pack(fill="both", expand=True, padx=5, pady=3)
        for row in ["1234567890","qwertyuiop","asdfghjkl","zxcvbnm"]:
            f = tk.Frame(kb, bg="#111111"); f.pack(fill="x", expand=True)
            for ch in row:
                tk.Button(f, text=ch, command=lambda c=ch: name_entry.insert(tk.END, c), bg="#222", fg="#39ff14", font=("Helvetica",9,"bold"), bd=1, relief="solid", highlightbackground="#39ff14").pack(side="left", fill="both", expand=True, padx=1, pady=1)
        f = tk.Frame(kb, bg="#111111"); f.pack(fill="x", expand=True)
        for ch in [".", "-", "_"]:
            tk.Button(f, text=ch, command=lambda c=ch: name_entry.insert(tk.END, c), bg="#222", fg="#39ff14", font=("Helvetica",9,"bold"), bd=1, relief="solid").pack(side="left", fill="both", expand=True, padx=1, pady=1)
        tk.Button(f, text="DEL", command=lambda e=name_entry: e.delete(len(e.get())-1, tk.END) if e.get() else None, bg="#aa0000", fg="white", font=("Helvetica",9,"bold"), bd=1, relief="solid").pack(side="left", fill="both", expand=True, padx=1, pady=1)
        bf = tk.Frame(ov, bg="#111111"); bf.pack(fill="x", padx=10, pady=(3,8))
        tk.Button(bf, text="RENAME", font=("Helvetica",10,"bold"), bg="#005500", fg="white", command=lambda: self._do_rename(full, name_entry.get()), width=10).pack(side="left", padx=5)
        tk.Button(bf, text="CANCEL", font=("Helvetica",10,"bold"), bg="#aa0000", fg="white", command=self.close_msg, width=10).pack(side="right", padx=5)

    def _do_rename(self, old_path, new_name):
        new_name = new_name.strip(); self.close_msg()
        if not new_name: return
        parent = os.path.dirname(old_path)
        new_path = os.path.join(parent, new_name)
        if old_path == new_path: return
        if os.path.exists(new_path): self.show_msg(f"Already exists:\n{new_name}"); return
        try:
            os.rename(old_path, new_path); self.refresh_panes()
        except Exception as e: self.show_msg(f"Error: {str(e)[:50]}")

    def create_dir(self):
        if self.msg_bg: return
        self.msg_bg = tk.Frame(self, bg="#050505"); self.msg_bg.place(x=0, y=0, width=480, height=320)
        ov = tk.Frame(self.msg_bg, bg="#111111", bd=2, relief="solid", highlightbackground="#39ff14", highlightthickness=2)
        ov.place(relx=0.5, rely=0.5, anchor="center", width=440, height=290)
        ov.bind("<Button-1>", lambda e: "break")
        tk.Label(ov, text="NEW DIRECTORY", bg="#111111", fg="#39ff14", font=("Helvetica",12,"bold")).pack(pady=(8,3))
        name_entry = tk.Entry(ov, font=("Helvetica",12), bg="#222", fg="white", bd=1, relief="solid")
        name_entry.pack(fill="x", padx=10, pady=5); name_entry.focus_set()
        kb = tk.Frame(ov, bg="#111111"); kb.pack(fill="both", expand=True, padx=5, pady=3)
        for row in ["1234567890","qwertyuiop","asdfghjkl","zxcvbnm"]:
            f = tk.Frame(kb, bg="#111111"); f.pack(fill="x", expand=True)
            for ch in row:
                tk.Button(f, text=ch, command=lambda c=ch: name_entry.insert(tk.END, c), bg="#222", fg="#39ff14", font=("Helvetica",9,"bold"), bd=1, relief="solid", highlightbackground="#39ff14").pack(side="left", fill="both", expand=True, padx=1, pady=1)
        f = tk.Frame(kb, bg="#111111"); f.pack(fill="x", expand=True)
        for ch in [".", "-", "_"]:
            tk.Button(f, text=ch, command=lambda c=ch: name_entry.insert(tk.END, c), bg="#222", fg="#39ff14", font=("Helvetica",9,"bold"), bd=1, relief="solid").pack(side="left", fill="both", expand=True, padx=1, pady=1)
        tk.Button(f, text="DEL", command=lambda e=name_entry: e.delete(len(e.get())-1, tk.END) if e.get() else None, bg="#aa0000", fg="white", font=("Helvetica",9,"bold"), bd=1, relief="solid").pack(side="left", fill="both", expand=True, padx=1, pady=1)
        bf = tk.Frame(ov, bg="#111111"); bf.pack(fill="x", padx=10, pady=(3,8))
        tk.Button(bf, text="CREATE", font=("Helvetica",10,"bold"), bg="#005500", fg="white", command=lambda: self._do_create(name_entry.get()), width=10).pack(side="left", padx=5)
        tk.Button(bf, text="CANCEL", font=("Helvetica",10,"bold"), bg="#aa0000", fg="white", command=self.close_msg, width=10).pack(side="right", padx=5)

    def _do_create(self, name):
        name = name.strip(); self.close_msg()
        if not name: return
        cur = self.left_dir if self.active_pane == "left" else self.right_dir
        full = os.path.join(cur, name)
        if os.path.exists(full): self.show_msg(f"Already exists:\n{name}"); return
        try:
            os.mkdir(full); self.refresh_panes()
        except Exception as e: self.show_msg(f"Error: {str(e)[:50]}")

    def show_msg(self, text):
        if self.msg_bg: self.close_msg()
        self.msg_bg = tk.Frame(self, bg="#050505"); self.msg_bg.place(x=0, y=0, width=480, height=320)
        self.msg_bg.bind("<Button-1>", lambda e: self.close_msg())
        ov = tk.Frame(self.msg_bg, bg="#111111", bd=2, relief="solid", highlightbackground="#39ff14", highlightthickness=2)
        ov.place(relx=0.5, rely=0.5, anchor="center", width=320, height=140)
        ov.bind("<Button-1>", lambda e: "break")
        tk.Label(ov, text=text, bg="#111111", fg="white", font=("Helvetica",10), wraplength=290).pack(pady=(20,10))
        tk.Button(ov, text="OK", font=("Helvetica",11,"bold"), bg="#005500", fg="white", command=self.close_msg, width=10).pack(pady=(5,15))

    def close_msg(self):
        if self.msg_bg: self.msg_bg.destroy(); self.msg_bg = None

class BaseOSINTPage(tk.Frame):
    TOOL_NAME = "OSINT"
    PLACEHOLDER = "example.com"
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="black", width=480, height=320)
        self.controller = controller
        self.running = False
        self.target_val = ""
        self.output_buffer = []
        self.log_file_path = None
        tb = tk.Frame(self, bg="#111111"); tb.place(x=0, y=0, width=480, height=30)
        tk.Button(tb, text="< BACK", bg="#111111", fg="#39ff14", font=("Helvetica",11,"bold"), bd=0, command=self.smart_back).pack(side="left", fill="y")
        tk.Label(tb, text=self.TOOL_NAME, bg="#111111", fg="#aa0000", font=("Helvetica",11,"bold")).pack(side="left", expand=True)
        tk.Button(tb, text="CLR LOGS", bg="#111111", fg="#aa0000", font=("Helvetica",9,"bold"), bd=0, command=self.show_clear_dialog).pack(side="right", fill="y", padx=(0,6))
        self.input_frame = tk.Frame(self, bg="black")
        self.target_entry = tk.Entry(self.input_frame, font=("Helvetica",14), bg="#222", fg="white", bd=2, relief="solid")
        self.target_entry.place(x=10, y=5, width=460, height=30)
        tk.Label(self.input_frame, text=f"Target ({self.PLACEHOLDER})", bg="black", fg="yellow", font=("Helvetica",9)).place(x=10, y=38)
        self.keyboard_frame = tk.Frame(self.input_frame, bg="black"); self.keyboard_frame.place(x=0, y=60, width=480, height=190)
        self.create_keyboard()
        tk.Button(self.input_frame, text="RUN", font=("Helvetica",11,"bold"), bg="#005500", fg="white", command=self._start).place(x=0, y=260, width=160, height=30)
        tk.Button(self.input_frame, text="CLEAR", font=("Helvetica",11,"bold"), bg="#333", fg="white", command=lambda: self.target_entry.delete(0, tk.END)).place(x=160, y=260, width=160, height=30)
        tk.Button(self.input_frame, text="NEW ID", font=("Helvetica",11,"bold"), bg="#330000", fg="#aa0000", command=self._rotate).place(x=320, y=260, width=160, height=30)
        self.log_frame = tk.Frame(self, bg="black")
        sb = tk.Scrollbar(self.log_frame); sb.pack(side="right", fill="y")
        self.log_area = tk.Text(self.log_frame, bg="black", fg="#39ff14", font=("Helvetica",10), bd=0, padx=5, pady=5, yscrollcommand=sb.set, wrap="word", state=tk.DISABLED)
        self.log_area.pack(side="left", fill="both", expand=True); sb.config(command=self.log_area.yview)
        make_readonly_text(self.log_area)
    def show_clear_dialog(self):
        if hasattr(self, 'clear_bg'): return
        d = os.path.expanduser("~/osint_logs")
        count = 0; total = 0
        if os.path.exists(d):
            for f in os.listdir(d):
                if f.endswith(".txt"):
                    try:
                        count += 1
                        total += os.path.getsize(os.path.join(d, f))
                    except: pass
        if count == 0:
            self.log("[*] No logs to clear."); return
        size_str = (f"{total/1024:.1f}KB" if total < 1024*1024 else f"{total/(1024*1024):.1f}MB")
        self.clear_bg = tk.Frame(self, bg="#050505")
        self.clear_bg.place(x=0, y=0, width=480, height=320)
        self.clear_bg.bind("<Button-1>", lambda e: self.hide_clear_dialog())
        ov = tk.Frame(self.clear_bg, bg="#111111", bd=2, relief="solid", highlightbackground="#aa0000", highlightthickness=2)
        ov.place(relx=0.5, rely=0.5, anchor="center", width=360, height=170)
        tk.Label(ov, text="CLEAR LOGS", bg="#111111", fg="#aa0000", font=("Helvetica",14,"bold")).pack(pady=(15,5))
        tk.Label(ov, text=f"Delete {count} {self.TOOL_NAME} log(s)\n({size_str})?", bg="#111111", fg="white", font=("Helvetica",11), justify="center").pack(pady=5)
        bf = tk.Frame(ov, bg="#111111"); bf.pack(pady=10)
        tk.Button(bf, text="YES, DELETE", font=("Helvetica",11,"bold"), bg="#aa0000", fg="white", command=self._do_clear_logs, width=12).pack(side="left", padx=10)
        tk.Button(bf, text="CANCEL", font=("Helvetica",11,"bold"), bg="#333", fg="white", command=self.hide_clear_dialog, width=12).pack(side="right", padx=10)

    def hide_clear_dialog(self):
        if hasattr(self, 'clear_bg'):
            self.clear_bg.destroy(); del self.clear_bg

    def _do_clear_logs(self):
        d = os.path.expanduser("~/osint_logs")
        count = 0
        if os.path.exists(d):
            for f in os.listdir(d):
                if f.endswith(".txt"):
                    try: os.remove(os.path.join(d, f)); count += 1
                    except: pass
        self.hide_clear_dialog()
        self.log(f"[*] Cleared {count} log file(s).")
    def on_show(self):
        self.show_input(); self.target_entry.delete(0, tk.END)
    def show_input(self):
        self.log_frame.place_forget()
        self.input_frame.place(x=0, y=30, width=480, height=290)
    def smart_back(self):
        if hasattr(self, 'clear_bg'):
            self.hide_clear_dialog(); return
        if self.log_frame.place_info(): self.show_input()
        else: self.controller.go_back()
    def create_keyboard(self):
        for row in ["1234567890","qwertyuiop","asdfghjkl","zxcvbnm",[".", "-", "/", ":", "DEL", "CLR"]]:
            f = tk.Frame(self.keyboard_frame, bg="black"); f.pack(side="top", fill="x", expand=True)
            for ch in row:
                if ch=="DEL": b = tk.Button(f, text="DEL", command=self.del_char, bg="#aa0000", fg="white", font=("Helvetica",11,"bold"))
                elif ch=="CLR": b = tk.Button(f, text="CLR", command=lambda: self.target_entry.delete(0, tk.END), bg="#333", fg="white", font=("Helvetica",11,"bold"))
                else: b = tk.Button(f, text=ch, command=lambda c=ch: self.add_char(c), bg="#222", fg="#39ff14", font=("Helvetica",14,"bold"))
                b.pack(side="left", fill="both", expand=True, padx=1, pady=1)
    def add_char(self, ch): self.target_entry.insert(tk.END, ch)
    def del_char(self):
        c = self.target_entry.get()
        if c: self.target_entry.delete(len(c)-1, tk.END)
    def _get(self, url, **kw):
        try:
            import socket as sock
            s = sock.socket(); s.settimeout(1); s.connect(("127.0.0.1", 9050)); s.close()
        except: raise Exception("Tor not running (start Tor first)")
        kw.setdefault("timeout", 30); kw.setdefault("verify", False)
        kw.setdefault("headers", {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        return requests.get(url, proxies={"http":"socks5h://127.0.0.1:9050","https":"socks5h://127.0.0.1:9050"}, **kw)
    def _get_json(self, url, **kw):
        r = self._get(url, **kw)
        if r.status_code != 200:
            raise Exception(f"HTTP {r.status_code}: {r.text[:150]}")
        ctype = r.headers.get("Content-Type", "").lower()
        if "json" not in ctype and not r.text.strip().startswith(("{", "[")):
            raise Exception(f"Non-JSON ({ctype}): {r.text[:150]}")
        try: return r.json()
        except ValueError as e:
            raise Exception(f"JSON parse failed: {e} | Body: {r.text[:200]}")
    def _rotate(self):
        if TOR_AVAILABLE:
            def run():
                try:
                    with Controller.from_port(port=9051) as c:
                        c.authenticate(); c.signal(Signal.NEWNYM); time.sleep(1.5)
                except: pass
            threading.Thread(target=run, daemon=True).start()
    def _start(self):
        t = self.target_entry.get().strip()
        if not t: return
        self.running = True
        self.target_val = t
        self.output_buffer = []
        os.makedirs(os.path.expanduser("~/osint_logs"), exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_target = re.sub(r'[^a-zA-Z0-9._-]', '_', t)[:40]
        tool_safe = re.sub(r'[^a-zA-Z0-9]', '_', self.TOOL_NAME)
        self.log_file_path = os.path.expanduser(f"~/osint_logs/{tool_safe}_{ts}_{safe_target}.txt")
        header = (f"# {self.TOOL_NAME}\n# Target: {t}\n# Date: {datetime.datetime.now()}\n"
                  f"# Tor: {'active' if TOR_AVAILABLE else 'not installed'}\n\n")
        self.output_buffer.append(header)
        self.input_frame.place_forget()
        self.log_frame.place(x=0, y=30, width=480, height=260)
        self.log_area.config(state=tk.NORMAL); self.log_area.delete(1.0, tk.END); self.log_area.config(state=tk.DISABLED)
        self.log(f"[{self.TOOL_NAME}] {t}")
        def worker():
            if TOR_AVAILABLE:
                try:
                    with Controller.from_port(port=9051) as c:
                        c.authenticate(); c.signal(Signal.NEWNYM); time.sleep(1.5)
                except: pass
            try:
                result = self.run_tool(t)
                self.log(str(result)[:4000] if result else "No result.")
            except Exception as e:
                self.log(f"[!] {e}")
            finally:
                self.running = False
                self._save_output()
                self.log(f"\n[*] Saved: {self.log_file_path}")
        threading.Thread(target=worker, daemon=True).start()
    def _save_output(self):
        if not self.log_file_path: return
        try:
            with open(self.log_file_path, "w", encoding="utf-8") as f:
                f.write("".join(self.output_buffer))
        except Exception as e:
            print(f"[OSINT] Save error: {e}")
    def run_tool(self, target): raise NotImplementedError
    def log(self, m):
        self.output_buffer.append(m + "\n")
        def _l():
            self.log_area.config(state=tk.NORMAL)
            self.log_area.insert(tk.END, m+"\n")
            log_sinirla(self.log_area)
            self.log_area.see(tk.END)
            self.log_area.config(state=tk.DISABLED)
        self.after(0, _l)

class WHOISPage(BaseOSINTPage):
    TOOL_NAME = "WHOIS"
    def run_tool(self, d):
        data = self._get_json(f"https://rdap.org/domain/{d}")
        lines = [f"Domain: {data.get('ldhName', d)}"]
        for ev in data.get("events", []): lines.append(f"  {ev.get('eventAction','')}: {ev.get('eventDate','')}")
        for ns in data.get("nameservers", []): lines.append(f"  NS: {ns.get('ldhName','')}")
        return "\n".join(lines) if len(lines) > 1 else "No data"

class DNSPage(BaseOSINTPage):
    TOOL_NAME = "DNS LOOKUP"
    def run_tool(self, d):
        lines = []
        for t in ["A","AAAA","MX","TXT","NS","CNAME"]:
            try:
                data = self._get_json(f"https://dns.google/resolve?name={d}&type={t}")
                for a in data.get("Answer", []): lines.append(f"{t:5} {a.get('data')}")
            except Exception as e:
                lines.append(f"{t:5} [error: {str(e)[:40]}]")
        return "\n".join(lines) if lines else "No DNS records"

class SubEnumPage(BaseOSINTPage):
    TOOL_NAME = "SUB ENUM"
    def run_tool(self, d):
        data = self._get_json(f"https://crt.sh/?q=%25.{d}&output=json", timeout=50)
        subs = set()
        for e in data:
            for n in e.get("name_value", "").split("\n"):
                n = n.strip().lower()
                if n.endswith(f".{d}") or n == d: subs.add(n)
        res = sorted(subs)
        return f"Found {len(res)} subdomains:\n" + "\n".join(res[:200])

class HTTPHeadersPage(BaseOSINTPage):
    TOOL_NAME = "HTTP HEADERS"
    def run_tool(self, u):
        if not u.startswith("http"): u = "http://" + u
        r = self._get(u, allow_redirects=False)
        return f"Status: {r.status_code}\n\n" + "\n".join(f"{k}: {v}" for k,v in r.headers.items())

class SSLCertPage(BaseOSINTPage):
    TOOL_NAME = "SSL CERT"
    def run_tool(self, d):
        data = self._get_json(f"https://crt.sh/?q={d}&output=json", timeout=50)
        seen = set(); lines = []
        for c in data[:20]:
            n = c.get("name_value", "")
            if n in seen: continue
            seen.add(n)
            lines.append(f"Issuer: {c.get('issuer_name','')[:80]}")
            lines.append(f"  Subject: {n}")
        return "\n".join(lines[:40]) if lines else "No cert data"

class IPInfoPage(BaseOSINTPage):
    TOOL_NAME = "IP INFO"
    PLACEHOLDER = "8.8.8.8"
    def run_tool(self, ip):
        err1 = err2 = ""
        try:
            data = self._get_json(f"http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,zip,lat,lon,timezone,isp,org,as,query")
            if data.get("status") == "success":
                lines = []
                for k in ["query","country","regionName","city","zip","timezone","lat","lon","isp","org","as"]:
                    if k in data and data[k]: lines.append(f"{k:12}: {data[k]}")
                return "\n".join(lines)
            elif data.get("status") == "fail":
                raise Exception(f"ip-api: {data.get('message','unknown')}")
        except Exception as e: err1 = str(e)
        try:
            data = self._get_json(f"https://ipwho.is/{ip}")
            if data.get("success"):
                lines = []
                for k in ["ip","type","country","region","city","postal","timezone"]:
                    if k in data and data[k]:
                        v = data[k]
                        if isinstance(v, dict): v = v.get("id") or v.get("name") or str(v)
                        lines.append(f"{k:12}: {v}")
                if "connection" in data:
                    conn = data["connection"]
                    for k in ["isp","org","asn","domain"]:
                        if k in conn: lines.append(f"{k:12}: {conn[k]}")
                return "\n".join(lines)
            else: raise Exception(f"ipwho: {data.get('message','unknown')}")
        except Exception as e: err2 = str(e)
        return f"All APIs failed:\n\n1. ip-api.com:\n   {err1}\n\n2. ipwho.is:\n   {err2}\n\nTip: Try NEW ID to rotate Tor exit node."

class ReverseIPPage(BaseOSINTPage):
    TOOL_NAME = "REVERSE IP"
    PLACEHOLDER = "8.8.8.8"
    def run_tool(self, ip):
        r = self._get(f"https://api.hackertarget.com/reverseiplookup/?q={ip}")
        return r.text[:3000]

class TechStackPage(BaseOSINTPage):
    TOOL_NAME = "TECH STACK"
    def run_tool(self, u):
        if not u.startswith("http"): u = "http://" + u
        r = self._get(u)
        h = r.text.lower(); hd = str(r.headers).lower()
        pats = {"WordPress":["wp-content","wp-includes"],"Drupal":["drupal"],"Joomla":["joomla"],
                "React":["react","_react"],"Vue":["vue.js","__vue__"],"Angular":["ng-version","angular"],
                "Bootstrap":["bootstrap"],"jQuery":["jquery"],"Nginx":["nginx"],"Apache":["apache"],
                "Cloudflare":["cloudflare"],"PHP":["php"],"ASP.NET":["asp.net"],"Shopify":["shopify"],
                "Magento":["magento"],"Next.js":["_next/","__next"],"Tailwind":["tailwind"]}
        found = [n for n, sigs in pats.items() if any(s in h or s in hd for s in sigs)]
        return "Detected: " + ", ".join(found) if found else "No tech detected"

class WaybackPage(BaseOSINTPage):
    TOOL_NAME = "WAYBACK"
    def run_tool(self, u):
        if not u.startswith("http"): u = "http://" + u
        data = self._get_json(f"https://archive.org/wayback/available?url={u}")
        s = data.get("archived_snapshots", {}).get("closest", {})
        return f"Archived: {s.get('timestamp')}\nURL: {s.get('url')}" if s else "No archive"

class RobotsPage(BaseOSINTPage):
    TOOL_NAME = "ROBOTS.TXT"
    def run_tool(self, u):
        if not u.startswith("http"): u = "http://" + u
        if u.endswith("/"): u = u[:-1]
        r = self._get(f"{u}/robots.txt")
        return r.text[:3000] if r.status_code == 200 else f"HTTP {r.status_code}"

class SitemapPage(BaseOSINTPage):
    TOOL_NAME = "SITEMAP.XML"
    def run_tool(self, u):
        if not u.startswith("http"): u = "http://" + u
        if u.endswith("/"): u = u[:-1]
        r = self._get(f"{u}/sitemap.xml")
        return r.text[:3000] if r.status_code == 200 else f"HTTP {r.status_code}"

class SecHeadersPage(BaseOSINTPage):
    TOOL_NAME = "SEC HEADERS"
    def run_tool(self, u):
        if not u.startswith("http"): u = "http://" + u
        r = self._get(u, allow_redirects=True)
        checks = ["Strict-Transport-Security","Content-Security-Policy","X-Frame-Options",
                  "X-Content-Type-Options","Referrer-Policy","Permissions-Policy"]
        lines = [f"Status: {r.status_code}", ""]
        for h in checks: lines.append(f"{'[+]' if h in r.headers else '[-]'} {h}")
        return "\n".join(lines)

class PortCheckPage(BaseOSINTPage):
    TOOL_NAME = "PORT CHECK"
    PLACEHOLDER = "8.8.8.8:53"
    def run_tool(self, t):
        if ":" not in t: return "Format: IP:PORT"
        host, port = t.rsplit(":", 1)
        try: port = int(port)
        except: return "Invalid port"
        try:
            import socks
            s = socks.socksocket(); s.set_proxy(socks.SOCKS5, "127.0.0.1", 9050)
            s.settimeout(20); s.connect((host, port)); s.close()
            return f"Port {port} on {host}: OPEN (via Tor)"
        except ImportError: return "PySocks missing: pip install PySocks"
        except Exception as e: return f"Port {port}: CLOSED ({str(e)[:50]})"

class ClockPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="black", width=480, height=320)
        tb = tk.Frame(self, bg="#111111"); tb.place(x=0, y=0, width=480, height=30)
        tk.Button(tb, text="< BACK", bg="#111111", fg="#39ff14", font=("Helvetica",11,"bold"), bd=0, command=controller.go_back).pack(side="left", fill="y")
        tk.Label(tb, text="ANALOG CLOCK", bg="#111111", fg="#39ff14", font=("Helvetica",11,"bold")).pack(side="left", expand=True)
        self.canvas = tk.Canvas(self, width=480, height=260, bg="black", highlightthickness=0); self.canvas.place(x=0, y=30)
        self.draw(); self.update()
    def draw(self):
        cx, cy, r = 240, 120, 95
        self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline="#39ff14", width=3)
        for i in range(60):
            a = math.radians(i*6-90); ir = r-15 if i%5==0 else r-8; w = 3 if i%5==0 else 1
            self.canvas.create_line(cx+ir*math.cos(a), cy+ir*math.sin(a), cx+r*math.cos(a), cy+r*math.sin(a), fill="#39ff14", width=w)
    def update(self):
        self.canvas.delete("hands"); self.canvas.delete("digital")
        n = datetime.datetime.now(); h, m, s = n.hour%12, n.minute, n.second; cx, cy = 240, 120
        ah = math.radians((h*30)+(m*0.5)-90); self.canvas.create_line(cx, cy, cx+50*math.cos(ah), cy+50*math.sin(ah), fill="#39ff14", width=6, tags="hands", capstyle=tk.ROUND)
        am = math.radians((m*6)+(s*0.1)-90); self.canvas.create_line(cx, cy, cx+75*math.cos(am), cy+75*math.sin(am), fill="#39ff14", width=4, tags="hands", capstyle=tk.ROUND)
        a_s = math.radians(s*6-90); self.canvas.create_line(cx, cy, cx+85*math.cos(a_s), cy+85*math.sin(a_s), fill="#aa0000", width=2, tags="hands", capstyle=tk.ROUND)
        self.canvas.create_oval(cx-4, cy-4, cx+4, cy+4, fill="white", tags="hands")
        self.canvas.create_text(cx, 245, text=n.strftime("%H:%M:%S"), font=("Helvetica",16,"bold"), fill="#39ff14", tags="digital")
        self.after(1000, self.update)

class CalculatorPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="black", width=480, height=320)
        tb = tk.Frame(self, bg="#111111"); tb.place(x=0, y=0, width=480, height=30)
        tk.Button(tb, text="< BACK", bg="#111111", fg="#39ff14", font=("Helvetica",11,"bold"), bd=0, command=controller.go_back).pack(side="left", fill="y")
        tk.Label(tb, text="CALCULATOR", bg="#111111", fg="#39ff14", font=("Helvetica",11,"bold")).pack(side="left", expand=True)
        mb = tk.Frame(self, bg="#222"); mb.place(x=0, y=30, width=480, height=25)
        self.btn_mod_norm = tk.Button(mb, text="NORMAL", font=("Helvetica",9,"bold"), bg="#005500", fg="white", bd=0, command=lambda: self.set_mode("normal")); self.btn_mod_norm.pack(side="left", fill="both", expand=True, padx=1)
        self.btn_mod_sci = tk.Button(mb, text="SCIENTIFIC", font=("Helvetica",9,"bold"), bg="#333", fg="#39ff14", bd=0, command=lambda: self.set_mode("scientific")); self.btn_mod_sci.pack(side="left", fill="both", expand=True, padx=1)
        self.btn_mod_prog = tk.Button(mb, text="PROGRAMMER", font=("Helvetica",9,"bold"), bg="#333", fg="#39ff14", bd=0, command=lambda: self.set_mode("programmer")); self.btn_mod_prog.pack(side="left", fill="both", expand=True, padx=1)
        df = tk.Frame(self, bg="#111111", bd=2, relief="sunken"); df.place(x=10, y=60, width=460, height=45)
        self.expression = ""; self.input_var = tk.StringVar()
        tk.Entry(df, textvariable=self.input_var, font=("Helvetica",20,"bold"), bg="#111111", fg="#39ff14", bd=0, justify="right", state="readonly").pack(fill="both", expand=True, padx=5, pady=5)
        self.btn_frame = tk.Frame(self, bg="black"); self.btn_frame.place(x=10, y=110, width=460, height=200)
        self.current_mode = "normal"; self.calc_base = 10; self.buttons = []; self.render()
    def set_mode(self, mode):
        self.current_mode = mode; self.expression = ""; self.input_var.set("")
        for b, m in [(self.btn_mod_norm,"normal"),(self.btn_mod_sci,"scientific"),(self.btn_mod_prog,"programmer")]:
            b.config(bg="#005500" if mode==m else "#333", fg="white" if mode==m else "#39ff14")
        if mode == "programmer": self.calc_base = 10
        self.render()
    def render(self):
        for b in self.buttons: b.destroy()
        self.buttons.clear()
        for i in range(8): self.btn_frame.grid_rowconfigure(i, weight=0); self.btn_frame.grid_columnconfigure(i, weight=0)
        def add(t, r, c, color="#222", fg="#39ff14", fs=11):
            b = tk.Button(self.btn_frame, text=t, font=("Helvetica",fs,"bold"), bg=color, fg=fg, bd=1, relief="solid", highlightbackground="#39ff14", highlightthickness=1, command=lambda tt=t: self.click(tt))
            b.grid(row=r, column=c, padx=1, pady=1, sticky="nsew"); self.buttons.append(b)
        if self.current_mode == "normal":
            for i in range(4): self.btn_frame.grid_columnconfigure(i, weight=1)
            for i in range(5): self.btn_frame.grid_rowconfigure(i, weight=1)
            add('AC',0,0,'#aa0000','white'); add('(',0,1); add(')',0,2); add('/',0,3,'#333')
            add('7',1,0); add('8',1,1); add('9',1,2); add('*',1,3,'#333')
            add('4',2,0); add('5',2,1); add('6',2,2); add('-',2,3,'#333')
            add('1',3,0); add('2',3,1); add('3',3,2); add('+',3,3,'#333')
            add('0',4,0); add('.',4,1); add('DEL',4,2,'#aa0000','white'); add('=',4,3,'#005500','white')
        elif self.current_mode == "scientific":
            for i in range(5): self.btn_frame.grid_columnconfigure(i, weight=1)
            for i in range(6): self.btn_frame.grid_rowconfigure(i, weight=1)
            add('sin',0,0,'#333'); add('cos',0,1,'#333'); add('tan',0,2,'#333'); add('π',0,3,'#333'); add('e',0,4,'#333')
            add('√',1,0,'#333'); add('^',1,1,'#333'); add('(',1,2); add(')',1,3); add('/',1,4,'#333')
            add('7',2,0); add('8',2,1); add('9',2,2); add('*',2,3,'#333'); add('AC',2,4,'#aa0000','white')
            add('4',3,0); add('5',3,1); add('6',3,2); add('-',3,3,'#333'); add('DEL',3,4,'#aa0000','white')
            add('1',4,0); add('2',4,1); add('3',4,2); add('+',4,3,'#333'); add('log',4,4,'#333')
            add('0',5,0); add('.',5,1); add('=',5,2,'#005500','white'); add('ln',5,3,'#333'); add('exp',5,4,'#333')
        elif self.current_mode == "programmer":
            for i in range(4): self.btn_frame.grid_columnconfigure(i, weight=1)
            for i in range(8): self.btn_frame.grid_rowconfigure(i, weight=1)
            add('HEX',0,0,'#444' if self.calc_base!=16 else '#005500','white' if self.calc_base==16 else '#39ff14',10)
            add('DEC',0,1,'#444' if self.calc_base!=10 else '#005500','white' if self.calc_base==10 else '#39ff14',10)
            add('OCT',0,2,'#444' if self.calc_base!=8 else '#005500','white' if self.calc_base==8 else '#39ff14',10)
            add('BIN',0,3,'#444' if self.calc_base!=2 else '#005500','white' if self.calc_base==2 else '#39ff14',10)
            hc = '#333' if self.calc_base==16 else '#111'; hf = '#39ff14' if self.calc_base==16 else '#555'
            add('A',1,0,hc,hf,10); add('B',1,1,hc,hf,10); add('AND',1,2,'#333',fs=9); add('OR',1,3,'#333',fs=9)
            add('C',2,0,hc,hf,10); add('D',2,1,hc,hf,10); add('XOR',2,2,'#333',fs=9); add('NOT',2,3,'#333',fs=9)
            add('E',3,0,hc,hf,10); add('F',3,1,hc,hf,10); add('<<',3,2,'#333',fs=9); add('>>',3,3,'#333',fs=9)
            add('7',4,0,fs=10); add('8',4,1,fs=10); add('9',4,2,fs=10); add('/',4,3,'#333',fs=10)
            add('4',5,0,fs=10); add('5',5,1,fs=10); add('6',5,2,fs=10); add('*',5,3,'#333',fs=10)
            add('1',6,0,fs=10); add('2',6,1,fs=10); add('3',6,2,fs=10); add('-',6,3,'#333',fs=10)
            add('0',7,0,fs=10); add('AC',7,1,'#aa0000','white',fs=10); add('DEL',7,2,'#aa0000','white',fs=10); add('=',7,3,'#005500','white',fs=10)
    def eval_expr(self):
        e = self.expression
        if not e.strip(): return 0
        if self.current_mode == "scientific":
            e = e.replace("π","math.pi").replace("e","math.e").replace("^","**").replace("√(","math.sqrt(")
            def sin(x): return math.sin(math.radians(x))
            def cos(x): return math.cos(math.radians(x))
            def tan(x): return math.tan(math.radians(x))
            return eval(e, {"__builtins__":None}, {"math":math,"sin":sin,"cos":cos,"tan":tan,"log":math.log10,"ln":math.log,"exp":math.exp})
        elif self.current_mode == "programmer":
            if self.calc_base == 16: e = re.sub(r'\b([0-9A-F]+)\b', r'0x\1', e)
            elif self.calc_base == 8: e = re.sub(r'\b([0-7]+)\b', r'0o\1', e)
            elif self.calc_base == 2: e = re.sub(r'\b([01]+)\b', r'0b\1', e)
            return eval(e)
        return eval(e)
    def click(self, ch):
        if ch == 'AC': self.expression = ""
        elif ch == 'DEL': self.expression = self.expression[:-1]
        elif ch in ['HEX','DEC','OCT','BIN']:
            self.calc_base = 16 if ch=='HEX' else 10 if ch=='DEC' else 8 if ch=='OCT' else 2; self.render()
        elif ch == '=':
            try:
                r = self.eval_expr()
                if self.current_mode == "programmer":
                    i = int(r)
                    if self.calc_base==16: self.expression = hex(i)[2:].upper()
                    elif self.calc_base==8: self.expression = oct(i)[2:]
                    elif self.calc_base==2: self.expression = bin(i)[2:]
                    else: self.expression = str(i)
                else:
                    if isinstance(r, float) and r.is_integer(): r = int(r)
                    self.expression = str(r)
            except ZeroDivisionError: self.expression = "Div0"
            except: self.expression = "Error"
        else:
            if self.current_mode == "programmer":
                ok = (self.calc_base==16 and ch in '0123456789ABCDEF') or (self.calc_base==10 and ch in '0123456789') or (self.calc_base==8 and ch in '01234567') or (self.calc_base==2 and ch in '01') or ch in ['AND','OR','XOR','NOT','<<','>>','(',')']
                if ok:
                    m = {'AND':'&','OR':'|','XOR':'^','NOT':'~'}
                    self.expression += m.get(ch, ch)
            else:
                if ch == 'π': self.expression += "π"
                elif ch == '√': self.expression += "√("
                else: self.expression += str(ch)
        self.input_var.set(self.expression)

class SpeedtestPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="black", width=480, height=320)
        tb = tk.Frame(self, bg="#111111"); tb.place(x=0, y=0, width=480, height=30)
        tk.Button(tb, text="< BACK", bg="#111111", fg="#39ff14", font=("Helvetica",11,"bold"), bd=0, command=controller.go_back).pack(side="left", fill="y")
        tk.Label(tb, text="SPEEDTEST", bg="#111111", fg="#39ff14", font=("Helvetica",11,"bold")).pack(side="left", expand=True)
        self.lbl_ping = tk.Label(self, text="PING: -- ms", font=("Helvetica",14,"bold"), bg="black", fg="#39ff14"); self.lbl_ping.pack(pady=(20,5))
        self.lbl_down = tk.Label(self, text="DOWNLOAD: -- Mbit/s", font=("Helvetica",14,"bold"), bg="black", fg="#39ff14"); self.lbl_down.pack(pady=5)
        self.lbl_up = tk.Label(self, text="UPLOAD: -- Mbit/s", font=("Helvetica",14,"bold"), bg="black", fg="#39ff14"); self.lbl_up.pack(pady=5)
        self.btn_start = tk.Button(self, text="RUN SPEEDTEST", font=("Helvetica",14,"bold"), bg="#005500", fg="white", command=self.run_speedtest); self.btn_start.pack(pady=20, ipadx=20, ipady=10)
        self.status_lbl = tk.Label(self, text="Press button to start", font=("Helvetica",10), bg="black", fg="yellow"); self.status_lbl.pack()
    def run_speedtest(self):
        self.btn_start.config(state=tk.DISABLED, text="TESTING..."); self.status_lbl.config(text="Connecting...", fg="yellow")
        self.lbl_ping.config(text="PING: -- ms"); self.lbl_down.config(text="DOWNLOAD: -- Mbit/s"); self.lbl_up.config(text="UPLOAD: -- Mbit/s")
        def run():
            try:
                r = subprocess.run("speedtest-cli --simple", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if r.returncode == 0:
                    for line in r.stdout.strip().split('\n'):
                        if "Ping:" in line: self.after(0, lambda l=line: self.lbl_ping.config(text=l.strip().upper()))
                        elif "Download:" in line: self.after(0, lambda l=line: self.lbl_down.config(text=l.strip().upper()))
                        elif "Upload:" in line: self.after(0, lambda l=line: self.lbl_up.config(text=l.strip().upper()))
                    self.after(0, lambda: self.status_lbl.config(text="Test completed.", fg="#39ff14"))
                else: self.after(0, lambda: self.status_lbl.config(text="Error", fg="red"))
            except Exception as e: self.after(0, lambda: self.status_lbl.config(text=f"Error: {str(e)[:30]}", fg="red"))
            finally: self.after(0, lambda: self.btn_start.config(state=tk.NORMAL, text="RUN SPEEDTEST"))
        threading.Thread(target=run, daemon=True).start()

class SnakePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="black", width=480, height=320)
        self.controller = controller
        tb = tk.Frame(self, bg="#111111"); tb.place(x=0, y=0, width=480, height=30)
        tk.Button(tb, text="< BACK", bg="#111111", fg="#39ff14", font=("Helvetica",11,"bold"), bd=0, command=self.exit_game).pack(side="left", fill="y")
        tk.Label(tb, text="SNAKE", bg="#111111", fg="#39ff14", font=("Helvetica",11,"bold")).pack(side="left", expand=True)
        gf = tk.Frame(self, bg="black"); gf.place(x=10, y=35, width=460, height=200)
        self.cs = 20; self.cols = 23; self.rows = 10
        self.canvas = tk.Canvas(gf, width=self.cols*self.cs, height=self.rows*self.cs, bg="#111111", highlightthickness=1, highlightbackground="#39ff14"); self.canvas.pack()
        self.canvas.bind("<ButtonPress-1>", self.ss); self.canvas.bind("<ButtonRelease-1>", self.se)
        self.sx = 0; self.sy = 0
        dp = tk.Frame(self, bg="black"); dp.place(x=0, y=240, width=480, height=50)
        bs = {"bg":"#1a1a1a","fg":"#39ff14","font":("Helvetica",14,"bold"),"bd":1,"relief":"solid","highlightbackground":"#39ff14"}
        tk.Button(dp, text="◀", command=lambda: self.cd(-1,0), **bs).place(x=150, y=0, width=50, height=50)
        tk.Button(dp, text="▲", command=lambda: self.cd(0,-1), **bs).place(x=200, y=0, width=50, height=50)
        tk.Button(dp, text="▼", command=lambda: self.cd(0,1), **bs).place(x=250, y=0, width=50, height=50)
        tk.Button(dp, text="▶", command=lambda: self.cd(1,0), **bs).place(x=300, y=0, width=50, height=50)
        tk.Button(self, text="RESTART", font=("Helvetica",10,"bold"), bg="#aa0000", fg="white", command=self.reset).place(x=10, y=290, width=100, height=25)
        self.running = False; self.reset()
    def on_show(self): self.reset()
    def exit_game(self):
        self.running = False; self.controller.go_back()
    def ss(self, e): self.sx = e.x; self.sy = e.y
    def se(self, e):
        dx = e.x - self.sx; dy = e.y - self.sy
        if abs(dx) < 20 and abs(dy) < 20: return
        if abs(dx) > abs(dy): self.cd(1 if dx>0 else -1, 0)
        else: self.cd(0, 1 if dy>0 else -1)
    def reset(self):
        self.running = False; self.score = 0; self.direction = (1,0); self.next_direction = (1,0)
        sx = self.cols//2; sy = self.rows//2
        self.snake = [(sx,sy),(sx-1,sy),(sx-2,sy)]; self.food = self.get_food()
        self.canvas.delete("all"); self.draw(); self.running = True; self.loop()
    def get_food(self):
        while True:
            f = (random.randint(0,self.cols-1), random.randint(0,self.rows-1))
            if f not in self.snake: return f
    def cd(self, dx, dy):
        if (dx*-1, dy*-1) != self.direction: self.next_direction = (dx, dy)
    def draw(self):
        self.canvas.delete("all")
        fx, fy = self.food
        self.canvas.create_oval(fx*self.cs+2, fy*self.cs+2, (fx+1)*self.cs-2, (fy+1)*self.cs-2, fill="#aa0000")
        for i, (x, y) in enumerate(self.snake):
            c = "#39ff14" if i==0 else "#00aa00"
            self.canvas.create_rectangle(x*self.cs+1, y*self.cs+1, (x+1)*self.cs-1, (y+1)*self.cs-1, fill=c)
        self.canvas.create_text(450, 10, text=f"SCORE: {self.score}", anchor="ne", fill="#39ff14", font=("Helvetica",10,"bold"))
    def loop(self):
        if not self.running: return
        self.direction = self.next_direction
        hx, hy = self.snake[0]; nh = (hx+self.direction[0], hy+self.direction[1])
        if (nh[0]<0 or nh[0]>=self.cols or nh[1]<0 or nh[1]>=self.rows or nh in self.snake):
            self.over(); return
        self.snake.insert(0, nh)
        if nh == self.food: self.score += 10; self.food = self.get_food()
        else: self.snake.pop()
        self.draw(); self.after(150, self.loop)
    def over(self):
        self.running = False
        self.canvas.create_text(self.cols*self.cs//2, self.rows*self.cs//2, text="GAME OVER", fill="#aa0000", font=("Helvetica",24,"bold"))
        self.canvas.create_text(self.cols*self.cs//2, self.rows*self.cs//2+30, text="Press RESTART", fill="white", font=("Helvetica",12))

class MainMenu(tk.Frame):
    APPS = [
        ("OnionShare Chat", "OnionPage"), ("File Receive", "ReceivePage"),
        ("File Send", "SendPage"), ("Nmap", "NmapPage"),
        ("SMS Bomber", "SmsBomberPage"), ("MAC Changer", "_MAC_"),
        ("Dir Scan", "DirScanPage"), ("File Manager", "FileManagerPage"),
        ("WHOIS", "WHOISPage"), ("DNS Lookup", "DNSPage"),
        ("Sub Enum", "SubEnumPage"), ("HTTP Headers", "HTTPHeadersPage"),
        ("SSL Cert", "SSLCertPage"), ("IP Info", "IPInfoPage"),
        ("Reverse IP", "ReverseIPPage"), ("Tech Stack", "TechStackPage"),
        ("Wayback", "WaybackPage"), ("Robots.txt", "RobotsPage"),
        ("Sitemap.xml", "SitemapPage"), ("Sec Headers", "SecHeadersPage"),
        ("Port Check", "PortCheckPage"), ("Clock", "ClockPage"),
        ("Calculator", "CalculatorPage"), ("Speedtest", "SpeedtestPage"),
        ("Snake", "SnakePage"),
    ]

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="black", width=480, height=320)
        self.controller = controller; self.current_page = 0; self.buttons = []
        img = ikon_yukle("ghost", 300, 65)
        if img:
            l = tk.Label(self, image=img, bg="black"); l.image = img; l.place(relx=0.5, y=5, anchor="n")
        tk.Label(self, text="HAYALET", font=("Helvetica",11,"bold"),
                 bg="black", fg="#39ff14").place(x=10, y=14)
        tk.Label(self, text="v1.0", font=("Helvetica",8),
                 bg="black", fg="#888888").place(x=82, y=17)
        self.btn_wifi = tk.Button(self, text="WI-FI", font=("Helvetica",11,"bold"),
                                   bg="#1a1a1a", fg="#39ff14",
                                   command=lambda: controller.show_wifi("MainMenu"))
        self.btn_wifi.place(x=363, y=8, width=115, height=40)
        self.btn_search = tk.Button(self, text="SEARCH", font=("Helvetica",10,"bold"),
                                     bg="#1a1a1a", fg="#39ff14",
                                     command=self.show_search)
        self.btn_search.place(x=8, y=52, width=100, height=26)
        tk.Button(self, text="<", font=("Helvetica",20,"bold"), bg="#1a1a1a", fg="#39ff14", bd=0, command=self.prev_page).place(x=5, y=120, width=35, height=80)
        tk.Button(self, text=">", font=("Helvetica",20,"bold"), bg="#1a1a1a", fg="#39ff14", bd=0, command=self.next_page).place(x=440, y=120, width=35, height=80)
        self.grid_frame = tk.Frame(self, bg="black"); self.grid_frame.place(x=45, y=80, width=390, height=200)
        self.render(); ekle_cikis_butonu(self, controller)

    def show_search(self):
        if hasattr(self, 'search_bg'): return
        self.search_bg = tk.Frame(self, bg="#000000")
        self.search_bg.place(x=0, y=0, width=480, height=320)
        self.search_bg.bind("<Escape>", lambda e: self.close_search())
        top = tk.Frame(self.search_bg, bg="#111111")
        top.place(x=0, y=0, width=480, height=35)
        tk.Button(top, text="X", bg="#aa0000", fg="white", font=("Helvetica",14,"bold"),
                  command=self.close_search, width=3).pack(side="right", fill="y")
        self.search_entry = tk.Entry(top, font=("Helvetica",14), bg="#222", fg="#39ff14",
                                      bd=0, insertbackground="#39ff14")
        self.search_entry.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self._filter_search(self.search_entry.get()))
        self.search_entry.bind("<Return>", lambda e: self._auto_select_first())
        gc = tk.Frame(self.search_bg, bg="black")
        gc.place(x=0, y=35, width=480, height=165)
        self._search_canvas = tk.Canvas(gc, bg="black", highlightthickness=0)
        sb = tk.Scrollbar(gc, command=self._search_canvas.yview)
        self.search_grid_frame = tk.Frame(self._search_canvas, bg="black")
        self.search_grid_frame.bind("<Configure>",
            lambda e: self._search_canvas.configure(scrollregion=self._search_canvas.bbox("all")))
        self._search_canvas.create_window((0, 0), window=self.search_grid_frame, anchor="nw", width=460)
        self._search_canvas.configure(yscrollcommand=sb.set)
        self._search_canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        kb = tk.Frame(self.search_bg, bg="black")
        kb.place(x=0, y=200, width=480, height=120)
        self._create_search_keyboard(kb)
        self._filter_search("")

    def _create_search_keyboard(self, parent):
        for row in ["qwertyuiop", "asdfghjkl"]:
            f = tk.Frame(parent, bg="black"); f.pack(fill="x", expand=True, padx=1, pady=1)
            for ch in row:
                tk.Button(f, text=ch, command=lambda c=ch: self._search_char(c),
                          bg="#222", fg="#39ff14", font=("Helvetica",11,"bold"),
                          bd=1, relief="solid", highlightbackground="#39ff14"
                          ).pack(side="left", fill="both", expand=True, padx=1)
        f = tk.Frame(parent, bg="black"); f.pack(fill="x", expand=True, padx=1, pady=1)
        for ch in "zxcvbnm":
            tk.Button(f, text=ch, command=lambda c=ch: self._search_char(c),
                      bg="#222", fg="#39ff14", font=("Helvetica",11,"bold"),
                      bd=1, relief="solid", highlightbackground="#39ff14"
                      ).pack(side="left", fill="both", expand=True, padx=1)
        tk.Button(f, text="SPACE", command=lambda: self._search_char(" "),
                  bg="#333", fg="white", font=("Helvetica",9,"bold"),
                  bd=1, relief="solid").pack(side="left", fill="both", expand=True, padx=1)
        tk.Button(f, text="DEL", command=self._search_del,
                  bg="#aa0000", fg="white", font=("Helvetica",9,"bold"),
                  bd=1, relief="solid").pack(side="left", fill="both", expand=True, padx=1)

    def _search_char(self, ch):
        self.search_entry.insert(tk.END, ch)
        self._filter_search(self.search_entry.get())

    def _search_del(self):
        cur = self.search_entry.get()
        if cur:
            self.search_entry.delete(len(cur)-1, tk.END)
            self._filter_search(self.search_entry.get())

    def _auto_select_first(self):
        q = self.search_entry.get().lower().strip()
        matches = [app for app in self.APPS if not q or q in app[0].lower()]
        if matches: self._go_to_page(matches[0][1])

    def _filter_search(self, query):
        for w in self.search_grid_frame.winfo_children(): w.destroy()
        q = query.lower().strip()
        matches = [app for app in self.APPS if not q or q in app[0].lower()]
        if not matches:
            tk.Label(self.search_grid_frame, text="No results", bg="black", fg="#555",
                     font=("Helvetica",11)).grid(row=0, column=0, columnspan=3, pady=30)
            return
        for i, (name, page) in enumerate(matches):
            tk.Button(self.search_grid_frame, text=name,
                      font=("Helvetica",9,"bold"), bg="#1a1a1a", fg="#39ff14",
                      bd=1, relief="solid", highlightbackground="#39ff14",
                      highlightthickness=1,
                      command=lambda p=page: self._go_to_page(p)
                      ).grid(row=i//3, column=i%3, padx=2, pady=2, sticky="nsew")
        for i in range(3):
            self.search_grid_frame.grid_columnconfigure(i, weight=1)
        if hasattr(self, '_search_canvas'):
            self._search_canvas.yview_moveto(0)

    def _go_to_page(self, page):
        self.close_search()
        if page == "_MAC_": self.show_mac()
        else: self.controller.show_frame(page)

    def close_search(self):
        if hasattr(self, 'search_bg'):
            self.search_bg.destroy(); del self.search_bg

    def on_show(self):
        r = subprocess.run("iwgetid -r", shell=True, stdout=subprocess.PIPE, text=True)
        s = r.stdout.strip(); self.btn_wifi.config(text=f"WI-FI:\n{s[:8]}" if s else "WI-FI", fg="#39ff14")

    def render(self):
        for b in self.buttons: b.destroy()
        self.buttons.clear()
        for i in range(3):
            self.grid_frame.grid_rowconfigure(i, weight=0)
            self.grid_frame.grid_columnconfigure(i, weight=0)
        if self.current_page == 5:
            for i in range(2): self.grid_frame.grid_rowconfigure(i, weight=1)
            for i in range(3): self.grid_frame.grid_columnconfigure(i, weight=1)
        else:
            for i in range(2): self.grid_frame.grid_rowconfigure(i, weight=1)
            for i in range(2): self.grid_frame.grid_columnconfigure(i, weight=1)
        bs = {"bg":"#1a1a1a","fg":"#39ff14","font":("Helvetica",12,"bold"),"bd":1,"relief":"solid","highlightbackground":"#39ff14","highlightthickness":1}
        sms_style = {"bg":"#330000","fg":"#aa0000","font":("Helvetica",12,"bold"),"bd":1,"relief":"solid","highlightbackground":"#aa0000","highlightthickness":1}
        if self.current_page == 0:
            def onion():
                if self.controller.frames["OnionPage"].process is not None: self.controller.show_frame("OnionPage")
                else: self.controller.show_chat_dialog()
            def recv():
                if self.controller.frames["ReceivePage"].process is not None: self.controller.show_frame("ReceivePage")
                else: self.controller.show_receive_dialog()
            def snd():
                if self.controller.frames["SendPage"].process is not None: self.controller.show_frame("SendPage")
                else: self.controller.show_send_dialog()
            def nmap(): self.controller.show_frame("NmapPage")
            self.cb(0,0,"ONIONSHARE\nCHAT",onion,bs); self.cb(0,1,"FILE\nRECEIVE",recv,bs)
            self.cb(1,0,"FILE\nSEND",snd,bs); self.cb(1,1,"NMAP",nmap,bs)
        elif self.current_page == 1:
            self.cb(0,0,"SMS\nBOMBER",None,sms_style,disabled=True)
            self.cb(0,1,"MAC\nCHANGER",self.show_mac,bs)
            def dirs(): self.controller.show_frame("DirScanPage")
            self.cb(1,0,"DIR\nSCAN",dirs,bs)
            def whois(): self.controller.show_frame("WHOISPage")
            self.cb(1,1,"WHOIS",whois,bs)
        elif self.current_page == 2:
            def dns(): self.controller.show_frame("DNSPage")
            def sub(): self.controller.show_frame("SubEnumPage")
            def http(): self.controller.show_frame("HTTPHeadersPage")
            def ssl(): self.controller.show_frame("SSLCertPage")
            self.cb(0,0,"DNS\nLOOKUP",dns,bs); self.cb(0,1,"SUB\nENUM",sub,bs)
            self.cb(1,0,"HTTP\nHEADERS",http,bs); self.cb(1,1,"SSL\nCERT",ssl,bs)
        elif self.current_page == 3:
            def ipinfo(): self.controller.show_frame("IPInfoPage")
            def revip(): self.controller.show_frame("ReverseIPPage")
            def tech(): self.controller.show_frame("TechStackPage")
            def wayb(): self.controller.show_frame("WaybackPage")
            self.cb(0,0,"IP\nINFO",ipinfo,bs); self.cb(0,1,"REVERSE\nIP",revip,bs)
            self.cb(1,0,"TECH\nSTACK",tech,bs); self.cb(1,1,"WAYBACK",wayb,bs)
        elif self.current_page == 4:
            def robots(): self.controller.show_frame("RobotsPage")
            def sitemap(): self.controller.show_frame("SitemapPage")
            def sech(): self.controller.show_frame("SecHeadersPage")
            def port(): self.controller.show_frame("PortCheckPage")
            self.cb(0,0,"ROBOTS\n.TXT",robots,bs); self.cb(0,1,"SITEMAP\n.XML",sitemap,bs)
            self.cb(1,0,"SEC\nHEADERS",sech,bs); self.cb(1,1,"PORT\nCHECK",port,bs)
        elif self.current_page == 5:
            def fm(): self.controller.show_frame("FileManagerPage")
            def clock(): self.controller.show_frame("ClockPage")
            def calc(): self.controller.show_frame("CalculatorPage")
            def speed(): self.controller.show_frame("SpeedtestPage")
            def snake(): self.controller.show_frame("SnakePage")
            self.cb(0,0,"FILE\nMANAGER",fm,bs); self.cb(0,1,"CLOCK",clock,bs); self.cb(0,2,"CALCULATOR",calc,bs)
            self.cb(1,0,"SPEEDTEST",speed,bs); self.cb(1,1,"SNAKE",snake,bs)

    def cb(self, r, c, t, cmd, style, disabled=False):
        if disabled: b = tk.Button(self.grid_frame, text=t, bg="#111111", fg="#555555", font=style["font"], bd=1, relief="solid", state=tk.DISABLED)
        else:
            b = tk.Button(self.grid_frame, text=t, **style)
            def op(e): b.config(bg="#005500", fg="white")
            def orl(e):
                b.config(bg=style["bg"], fg=style["fg"])
                if cmd: cmd()
            b.bind("<ButtonPress-1>", op); b.bind("<ButtonRelease-1>", orl)
        b.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")
        self.buttons.append(b)

    def next_page(self):
        if self.current_page < 5: self.current_page += 1; self.render()
    def prev_page(self):
        if self.current_page > 0: self.current_page -= 1; self.render()

    def show_mac(self):
        if hasattr(self, 'mac_bg'): return
        self.mac_bg = tk.Frame(self, bg="#050505"); self.mac_bg.place(x=0, y=0, width=480, height=320)
        self.mac_bg.bind("<Button-1>", lambda e: self.close_mac())
        ov = tk.Frame(self.mac_bg, bg="#111111", bd=2, relief="solid", highlightbackground="#39ff14", highlightthickness=2)
        ov.place(relx=0.5, rely=0.5, anchor="center", width=400, height=190)
        ov.bind("<Button-1>", lambda e: "break")
        tk.Label(ov, text="MAC CHANGER", bg="#111111", fg="#39ff14", font=("Helvetica",14,"bold")).pack(pady=(15,5))
        tk.Label(ov, text="Random MAC for wlan0. Wi-Fi will disconnect.", bg="#111111", fg="white", font=("Helvetica",10)).pack(pady=5)
        self.mac_result = tk.StringVar(); self.mac_result.set("")
        tk.Label(ov, textvariable=self.mac_result, bg="#111111", fg="yellow", font=("Helvetica",11,"bold")).pack(pady=10)
        bf = tk.Frame(ov, bg="#111111"); bf.pack(pady=10)
        tk.Button(bf, text="CHANGE", font=("Helvetica",11,"bold"), bg="#005500", fg="white", command=self._do_mac, width=15).pack(side="left", padx=10)
        tk.Button(bf, text="CLOSE", font=("Helvetica",11,"bold"), bg="#aa0000", fg="white", command=self.close_mac, width=10).pack(side="right", padx=10)

    def close_mac(self):
        if hasattr(self, 'mac_bg'): self.mac_bg.destroy(); del self.mac_bg

    def _do_mac(self):
        def run():
            m = "02:%02x:%02x:%02x:%02x:%02x" % tuple(random.randint(0,255) for _ in range(5))
            try:
                subprocess.run("sudo ip link set wlan0 down", shell=True, capture_output=True, timeout=5)
                r = subprocess.run(f"sudo ip link set wlan0 address {m}", shell=True, capture_output=True, text=True, timeout=5)
                subprocess.run("sudo ip link set wlan0 up", shell=True, capture_output=True, timeout=5)
                if r.returncode == 0: self.after(0, lambda: self.mac_result.set(f"New: {m}"))
                else: self.after(0, lambda: self.mac_result.set(f"Err: {r.stderr.strip()[:50]}"))
            except Exception as e: self.after(0, lambda: self.mac_result.set(f"Fail: {str(e)[:40]}"))
        threading.Thread(target=run, daemon=True).start()

class BaseOnionPage(tk.Frame):
    def __init__(self, parent, controller, title):
        tk.Frame.__init__(self, parent, bg="black", width=480, height=320)
        self.controller = controller; self.process = None; self.secili_mod = "PRIVATE"
        self.current_url = None; self.current_key = None
        tb = tk.Frame(self, bg="#111111"); tb.place(x=0, y=0, width=480, height=30)
        tk.Button(tb, text="< BACK", bg="#111111", fg="#39ff14", font=("Helvetica",11,"bold"), bd=0, command=controller.go_back).pack(side="left", fill="y")
        self.mod_lbl = tk.Label(tb, text=f"MODE: {self.secili_mod}", bg="#111111", fg="yellow", font=("Helvetica",11,"bold")); self.mod_lbl.pack(side="left", expand=True)
        tk.Label(tb, text=title, bg="#111111", fg="#39ff14", font=("Helvetica",11,"bold")).pack(side="right", padx=10)
        lf = tk.Frame(self, bg="black"); lf.place(x=0, y=30, width=480, height=260)
        sb = tk.Scrollbar(lf); sb.pack(side="right", fill="y")
        self.log_area = tk.Text(lf, bg="black", fg="#39ff14", font=("Helvetica",11), bd=0, padx=5, pady=5, yscrollcommand=sb.set)
        self.log_area.pack(side="left", fill="both", expand=True); sb.config(command=self.log_area.yview)
        make_readonly_text(self.log_area)
        self.btn_start = tk.Button(self, text="START", font=("Helvetica",11,"bold"), bg="#005500", fg="white", command=self.start_process); self.btn_start.place(x=0, y=290, width=240, height=30)
        self.btn_stop = tk.Button(self, text="STOP", font=("Helvetica",11,"bold"), bg="#aa0000", fg="white", command=self.stop_process); self.btn_stop.place(x=240, y=290, width=240, height=30)
    def set_mod(self, m):
        self.secili_mod = m; self.mod_lbl.config(text=f"MODE: {self.secili_mod}")
        self.log_area.config(state=tk.NORMAL); self.log_area.delete(1.0, tk.END); self.log_area.config(state=tk.DISABLED)
        self.current_url = None; self.current_key = None; self.log(f"Mode: {self.secili_mod}\n")
    def start_process(self): raise NotImplementedError
    def _sureci(self, cmd):
        m, s = pty.openpty()
        env = os.environ.copy(); env.update({"PYTHONUNBUFFERED":"1","TERM":"dumb","LANG":"C.UTF-8","LC_ALL":"C.UTF-8"})
        self.process = subprocess.Popen(cmd, shell=True, stdin=s, stdout=s, stderr=s, env=env, text=True, bufsize=1, start_new_session=True)
        os.close(s)
        def r():
            try:
                while True:
                    try:
                        d = os.read(m, 4096)
                        if not d: break
                        for line in d.decode('utf-8', errors='replace').splitlines():
                            if line.strip(): self.log(line.strip())
                    except OSError: break
            finally:
                try: os.close(m)
                except: pass
        threading.Thread(target=r, daemon=True).start()
    def stop_process(self):
        if self.process:
            self.log("\n[!] Stopping...")
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGINT); self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                try: os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                except: pass
            finally: self.process = None; self.log("[-] Stopped.")
        else: self.log("No process.")
    def save_addr(self, fn):
        if self.current_url:
            c = self.current_url + "\n"
            if self.current_key: c += f"Private Key: {self.current_key}\n"
            try:
                with open(os.path.expanduser(f"~/{fn}"), "w") as f: f.write(c)
                b = "/boot/firmware" if os.path.exists("/boot/firmware") else "/boot"
                subprocess.run(["sudo", "tee", os.path.join(b, fn)], input=c, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except: pass
    def log(self, m):
        t = ansi_temizle(m)
        if not t.strip(): return
        mm = re.search(r'(http://[a-z0-9]{56}\.onion)', t)
        if mm: self.current_url = mm.group(1); self.save_addr()
        km = re.search(r'Private key:\s*([A-Za-z0-9\-_]+)', t, re.IGNORECASE)
        if km: self.current_key = km.group(1); self.save_addr()
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, t+"\n")
        log_sinirla(self.log_area)
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)

class OnionPage(BaseOnionPage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "ONION CHAT"); self.log("Ready.\n")
    def start_process(self):
        if self.process: return
        self.log(f"\n--- {self.secili_mod} CHAT ---\n")
        v = os.getenv("ONIONSHARE_CLI", os.path.expanduser("~/onionshare-env/bin/onionshare-cli"))
        self._sureci(f"PYTHONUNBUFFERED=1 {v} --chat" + (" --public" if self.secili_mod=="PUBLIC" else ""))
    def save_addr(self): super().save_addr("onionshare_chat.txt")

class ReceivePage(BaseOnionPage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "FILE RECEIVE"); self.log("Ready.\n")
    def start_process(self):
        if self.process: return
        self.log(f"\n--- {self.secili_mod} RECEIVE ---\n")
        v = os.getenv("ONIONSHARE_CLI", os.path.abspath("onionshare-env/bin/onionshare-cli"))
        dd = os.path.expanduser(os.getenv("RECEIVE_DIR", "~/received_files"))
        os.makedirs(dd, exist_ok=True)
        self._sureci(f"PYTHONUNBUFFERED=1 {v} --receive --data-dir {dd}" + (" --public" if self.secili_mod=="PUBLIC" else ""))
    def save_addr(self): super().save_addr("onionshare_file_receive.txt")

class SendPage(BaseOnionPage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "FILE SEND"); self.log("Files in ~/send_files\n")
    def start_process(self):
        if self.process: return
        v = os.getenv("ONIONSHARE_CLI", os.path.abspath("onionshare-env/bin/onionshare-cli"))
        sd = os.path.expanduser(os.getenv("SEND_DIR", "~/send_files"))
        os.makedirs(sd, exist_ok=True)
        if not os.listdir(sd): self.log("\n[!] Empty dir!"); return
        self.log(f"\n--- {self.secili_mod} SEND ---\n")
        self._sureci(f"PYTHONUNBUFFERED=1 {v} {sd}" + (" --public" if self.secili_mod=="PUBLIC" else ""))
    def save_addr(self): super().save_addr("onionshare_file_send.txt")

if __name__ == "__main__":
    bagimlilik_kontrol()
    torrc_kontrol_et()
    app = GhostDeckApp()
    app.mainloop()