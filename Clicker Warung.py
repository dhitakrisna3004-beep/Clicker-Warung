# ============================================================
#  🏪 CLICKER WARUNG v0.5
#  Copyright (c) 2025 Clicker Warung. All rights reserved.
#  Dibuat dengan Python + tkinter + pygame
#  Install: pip install pygame numpy
# ============================================================

import tkinter as tk
from tkinter import font as tkfont, messagebox, simpledialog
import json, os, time, threading, random, shutil

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR   = os.path.join(BASE_DIR, "saves")
os.makedirs(SAVE_DIR, exist_ok=True)
SAVE_SLOT  = [os.path.join(SAVE_DIR, f"slot{i}.json") for i in range(3)]
AUTO_SAVE  = os.path.join(SAVE_DIR, "autosave.json")

# ── AUDIO ─────────────────────────────────────────────────────────────────────
HAS_AUDIO = False
try:
    import numpy as np
    import pygame
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.mixer.init()
    HAS_AUDIO = True
except: pass

SR = 44100

def buat_nada(hz, dur, vol=0.28, shape="square"):
    if not HAS_AUDIO: return None
    n = int(SR * dur)
    if n == 0: return None
    t = np.linspace(0, dur, n, endpoint=False)
    if   shape == "square": w = np.sign(np.sin(2*np.pi*hz*t))
    elif shape == "tri":    w = 2*np.abs(2*(t*hz - np.floor(t*hz+0.5)))-1
    elif shape == "pulse":  w = ((np.sin(2*np.pi*hz*t))>0.2).astype(float)*2-1
    else:                   w = np.sin(2*np.pi*hz*t)
    a = min(int(0.008*SR), n//4); d = min(int(0.04*SR), n//4)
    env = np.ones(n); env[:a]=np.linspace(0,1,a); env[-d:]=np.linspace(1,0,d)
    data = (w * env * vol * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(data)

def play(snd):
    if snd and HAS_AUDIO:
        try: snd.play()
        except: pass

_sfx = {}
def init_sfx():
    if not HAS_AUDIO: return
    _sfx["klik"]  = buat_nada(880,  0.04, 0.18, "square")
    _sfx["beli1"] = buat_nada(523,  0.07, 0.25, "square")
    _sfx["beli2"] = buat_nada(659,  0.07, 0.25, "square")
    _sfx["beli3"] = buat_nada(784,  0.12, 0.25, "square")
    _sfx["ach1"]  = buat_nada(523,  0.09, 0.30, "tri")
    _sfx["ach2"]  = buat_nada(659,  0.09, 0.30, "tri")
    _sfx["ach3"]  = buat_nada(784,  0.09, 0.30, "tri")
    _sfx["ach4"]  = buat_nada(1047, 0.18, 0.30, "tri")
    _sfx["boost1"]= buat_nada(440,  0.06, 0.25, "pulse")
    _sfx["boost2"]= buat_nada(554,  0.06, 0.25, "pulse")
    _sfx["boost3"]= buat_nada(659,  0.06, 0.25, "pulse")
    _sfx["boost4"]= buat_nada(880,  0.12, 0.25, "pulse")
    _sfx["combo"] = buat_nada(1318, 0.08, 0.22, "square")
    _sfx["rebirth"]= buat_nada(440, 0.12, 0.35, "tri")
    _sfx["menu"]  = buat_nada(660,  0.10, 0.20, "square")

def sfx(name):
    if not musik_on: return
    s = _sfx.get(name)
    if s: threading.Thread(target=play, args=(s,), daemon=True).start()

def sfx_seq(names, gap=0.08):
    def _do():
        for n in names:
            if not musik_on: return
            sfx(n); time.sleep(gap)
    threading.Thread(target=_do, daemon=True).start()

def suara_klik():   sfx("klik")
def suara_beli():   sfx_seq(["beli1","beli2","beli3"], 0.08)
def suara_prest():  sfx_seq(["ach1","ach2","ach3","ach4"], 0.10)
def suara_boost():  sfx_seq(["boost1","boost2","boost3","boost4"], 0.07)
def suara_combo():  sfx("combo")
def suara_rebirth():sfx_seq(["rebirth","ach1","ach2","ach3","ach4","combo"], 0.12)
def suara_menu():   sfx("menu")

BGM = [
    (659,165,0.18,"square"),(698,175,0.18,"square"),(784,196,0.18,"square"),(880,220,0.25,"square"),
    (784,196,0.12,"square"),(698,175,0.12,"square"),(659,165,0.18,"square"),(587,147,0.25,"square"),
    (523,131,0.18,"square"),(587,147,0.12,"square"),(659,165,0.12,"square"),(523,131,0.25,"square"),
    (587,147,0.18,"square"),(523,131,0.12,"square"),(494,123,0.12,"square"),(440,110,0.30,"square"),
    (784,196,0.10,"pulse"),(659,165,0.10,"pulse"),(523,131,0.10,"pulse"),(659,165,0.10,"pulse"),
    (784,196,0.10,"pulse"),(880,220,0.10,"pulse"),(784,196,0.10,"pulse"),(659,165,0.10,"pulse"),
    (698,175,0.10,"pulse"),(587,147,0.10,"pulse"),(494,123,0.10,"pulse"),(587,147,0.10,"pulse"),
    (698,175,0.10,"pulse"),(784,196,0.10,"pulse"),(698,175,0.10,"pulse"),(587,147,0.10,"pulse"),
    (523,131,0.20,"tri"),(440,110,0.20,"tri"),(494,123,0.20,"tri"),(523,131,0.20,"tri"),
    (587,147,0.20,"tri"),(659,165,0.20,"tri"),(698,175,0.20,"tri"),(784,196,0.30,"tri"),
    (659,165,0.15,"tri"),(587,147,0.15,"tri"),(523,131,0.15,"tri"),(494,123,0.15,"tri"),
    (440,110,0.30,"tri"),(523,131,0.10,"tri"),(523,131,0.20,"tri"),(523,131,0.30,"tri"),
    (784,196,0.18,"square"),(880,220,0.12,"square"),(784,196,0.12,"square"),(698,175,0.18,"square"),
    (659,165,0.18,"square"),(784,196,0.12,"square"),(659,165,0.12,"square"),(587,147,0.18,"square"),
    (523,131,0.18,"square"),(659,165,0.12,"square"),(784,196,0.12,"square"),(523,131,0.18,"square"),
    (587,147,0.12,"square"),(523,131,0.12,"square"),(494,123,0.12,"square"),(523,131,0.35,"square"),
]

_bgm_idx=0; _bgm_run=False; _bgm_cache={}

def _prebake_bgm():
    if not HAS_AUDIO: return
    for i,(mel,bas,dur,sh) in enumerate(BGM):
        if dur==0: _bgm_cache[i]=None; continue
        m=buat_nada(mel,dur,0.20,sh)
        b=buat_nada(bas,dur,0.10,"tri") if bas else None
        if m and b:
            try:
                ma=np.frombuffer(pygame.sndarray.array(m),dtype=np.int16).astype(np.float32)
                ba=np.frombuffer(pygame.sndarray.array(b),dtype=np.int16).astype(np.float32)
                mn=len(min([ma,ba],key=len))
                mix=np.clip(ma[:mn]+ba[:mn],-32767,32767).astype(np.int16)
                _bgm_cache[i]=pygame.sndarray.make_sound(mix)
            except: _bgm_cache[i]=m
        else: _bgm_cache[i]=m

def _loop_bgm():
    global _bgm_idx
    while _bgm_run:
        if not musik_on: time.sleep(0.1); continue
        mel,bas,dur,sh=BGM[_bgm_idx%len(BGM)]
        snd=_bgm_cache.get(_bgm_idx%len(BGM))
        if snd:
            try: snd.play()
            except: pass
        _bgm_idx+=1; time.sleep(dur if dur>0 else 0.1)

def mulai_bgm():
    global _bgm_run
    if not HAS_AUDIO or _bgm_run: return
    _bgm_run=True
    threading.Thread(target=_prebake_bgm,daemon=True).start()
    threading.Thread(target=_loop_bgm,daemon=True).start()

def stop_bgm():
    global _bgm_run; _bgm_run=False
    if HAS_AUDIO:
        try: pygame.mixer.stop()
        except: pass

# ── STATE ─────────────────────────────────────────────────────────────────────
musik_on      = True
uang          = 0.0
uang_per_klik = 1
uang_per_detik= 0.0
total_uang    = 0.0
total_klik    = 0
waktu_mulai   = time.time()
is_fullscreen = False
tab_aktif     = "upgrade"
combo_count   = 0
combo_timer_id= None
COMBO_BATAS   = 10
_partikel     = []

# REBIRTH
rebirth_count    = 0          # berapa kali sudah rebirth
rebirth_bonus    = 1.0        # multiplier permanent dari rebirth
REBIRTH_SYARAT   = 1_000_000  # uang total minimum untuk rebirth pertama
REBIRTH_MULTIPLIER = 0.25     # tiap rebirth +25% permanent ke semua income

# ── DATA ──────────────────────────────────────────────────────────────────────
upgrades = [
    {"nama":"☕ Es Teh",         "harga":10,       "harga0":10,       "ups":1,      "dibeli":0,"tipe":"klik","desc":"+1/klik"},
    {"nama":"🍜 Mie Ayam",      "harga":50,       "harga0":50,       "ups":5,      "dibeli":0,"tipe":"klik","desc":"+5/klik"},
    {"nama":"🧃 Jus Buah",      "harga":120,      "harga0":120,      "ups":10,     "dibeli":0,"tipe":"klik","desc":"+10/klik"},
    {"nama":"🍗 Ayam Goreng",   "harga":350,      "harga0":350,      "ups":25,     "dibeli":0,"tipe":"klik","desc":"+25/klik"},
    {"nama":"🛵 Ojek Antar",    "harga":100,      "harga0":100,      "ups":2,      "dibeli":0,"tipe":"auto","desc":"+2/det"},
    {"nama":"👨‍🍳 Karyawan",      "harga":300,      "harga0":300,      "ups":8,      "dibeli":0,"tipe":"auto","desc":"+8/det"},
    {"nama":"📺 Papan Iklan",   "harga":800,      "harga0":800,      "ups":20,     "dibeli":0,"tipe":"auto","desc":"+20/det"},
    {"nama":"🏪 Cabang Baru",   "harga":2000,     "harga0":2000,     "ups":60,     "dibeli":0,"tipe":"auto","desc":"+60/det"},
    {"nama":"🏬 Mall Mini",     "harga":8000,     "harga0":8000,     "ups":200,    "dibeli":0,"tipe":"auto","desc":"+200/det"},
    {"nama":"🏭 Pabrik",        "harga":25000,    "harga0":25000,    "ups":600,    "dibeli":0,"tipe":"auto","desc":"+600/det"},
    {"nama":"🚀 Ekspor Global", "harga":100000,   "harga0":100000,   "ups":2000,   "dibeli":0,"tipe":"auto","desc":"+2.000/det"},
    {"nama":"🤖 AI Warung",     "harga":500000,   "harga0":500000,   "ups":8000,   "dibeli":0,"tipe":"auto","desc":"+8.000/det"},
    {"nama":"🌐 Franchise",     "harga":2000000,  "harga0":2000000,  "ups":30000,  "dibeli":0,"tipe":"auto","desc":"+30.000/det"},
    {"nama":"🏙️ Kota Warung",   "harga":10000000, "harga0":10000000, "ups":120000, "dibeli":0,"tipe":"auto","desc":"+120.000/det"},
    {"nama":"🌍 Warung Dunia",  "harga":50000000, "harga0":50000000, "ups":500000, "dibeli":0,"tipe":"auto","desc":"+500.000/det"},
]

boosters = [
    {"nama":"⚡ Klik x2",   "harga":500,   "efek":"klik_x2", "durasi":30, "desc":"Klik 2× lipat (30 detik)"},
    {"nama":"💨 Klik x5",   "harga":3000,  "efek":"klik_x5", "durasi":20, "desc":"Klik 5× lipat (20 detik)"},
    {"nama":"🔥 Klik x10",  "harga":20000, "efek":"klik_x10","durasi":15, "desc":"Klik 10× lipat (15 detik)"},
    {"nama":"🌟 Auto x3",   "harga":5000,  "efek":"auto_x3", "durasi":30, "desc":"Auto income 3× (30 detik)"},
    {"nama":"⏩ Turbo x5",  "harga":15000, "efek":"turbo",   "durasi":60, "desc":"Auto income 5× (60 detik)"},
    {"nama":"💎 Jackpot",   "harga":10000, "efek":"jackpot", "durasi":0,  "desc":"Dapat uang acak besar!"},
    {"nama":"🎰 Lucky Spin","harga":2000,  "efek":"spin",    "durasi":0,  "desc":"Spin hadiah acak!"},
]
booster_aktif = {}

def total_dibeli(): return sum(u["dibeli"] for u in upgrades)

PRESTASI = [
    {"id":"k10",    "nama":"🖱️ Pelanggan Pertama","desc":"Klik 10×",            "f":lambda:total_klik>=10,              "unlock":False},
    {"id":"k100",   "nama":"💪 Jari Besi",         "desc":"Klik 100×",           "f":lambda:total_klik>=100,             "unlock":False},
    {"id":"k1k",    "nama":"🦾 Legenda Klik",      "desc":"Klik 1.000×",         "f":lambda:total_klik>=1000,            "unlock":False},
    {"id":"k10k",   "nama":"🔥 Tangan Api",        "desc":"Klik 10.000×",        "f":lambda:total_klik>=10000,           "unlock":False},
    {"id":"combo",  "nama":"⚡ Combo Master",       "desc":"Raih combo 10×",      "f":lambda:combo_count>=10,             "unlock":False},
    {"id":"u1rb",   "nama":"💰 Kantong Tebal",     "desc":"Kumpul Rp 1.000",     "f":lambda:total_uang>=1000,            "unlock":False},
    {"id":"u100rb", "nama":"🤑 Sultan Warung",     "desc":"Kumpul Rp 100.000",   "f":lambda:total_uang>=100000,          "unlock":False},
    {"id":"u1jt",   "nama":"👑 Raja Kuliner",      "desc":"Kumpul Rp 1 Juta",    "f":lambda:total_uang>=1_000_000,       "unlock":False},
    {"id":"u100jt", "nama":"🏆 Konglomerat",       "desc":"Kumpul Rp 100 Juta",  "f":lambda:total_uang>=100_000_000,     "unlock":False},
    {"id":"u1M",    "nama":"💫 Taipan Nusantara",  "desc":"Kumpul Rp 1 Miliar",  "f":lambda:total_uang>=1_000_000_000,   "unlock":False},
    {"id":"upg1",   "nama":"🛒 Pembeli Pertama",   "desc":"Beli 1 upgrade",      "f":lambda:total_dibeli()>=1,           "unlock":False},
    {"id":"upg20",  "nama":"🏗️ Pengembang Ulung", "desc":"Beli 20 upgrade",     "f":lambda:total_dibeli()>=20,          "unlock":False},
    {"id":"auto1k", "nama":"⚙️ Mesin Uang",        "desc":"Auto 1.000/detik",    "f":lambda:uang_per_detik>=1000,        "unlock":False},
    {"id":"rb1",    "nama":"♻️ Lahir Kembali",     "desc":"Lakukan Rebirth 1×",  "f":lambda:rebirth_count>=1,            "unlock":False},
    {"id":"rb5",    "nama":"🌟 Phoenix",            "desc":"Lakukan Rebirth 5×",  "f":lambda:rebirth_count>=5,            "unlock":False},
]

# ── WARNA ─────────────────────────────────────────────────────────────────────
C = {
    "bg":     "#0A0A0A","panel":  "#131313","card":   "#1C1812",
    "card2":  "#222018","border": "#3A2E18","orange": "#FF7A00",
    "gold":   "#FFD700","green":  "#39D353","red":    "#FF4444",
    "blue":   "#4FC3F7","purple": "#CE93D8","gray":   "#4A4A4A",
    "txt":    "#F0E6D3","txt2":   "#B8A88A","header": "#150A00",
    "rebirth":"#AA44FF","menu_bg":"#080808",
}

# ── FORMAT ────────────────────────────────────────────────────────────────────
def fmt(n):
    n=int(n)
    if n>=1_000_000_000_000: return f"Rp {n/1_000_000_000_000:.2f}T"
    if n>=1_000_000_000:     return f"Rp {n/1_000_000_000:.2f}M"
    if n>=1_000_000:         return f"Rp {n/1_000_000:.2f}jt"
    if n>=1_000:             return f"Rp {n/1_000:.1f}rb"
    return f"Rp {n}"

# ── SAVE / LOAD ───────────────────────────────────────────────────────────────
def _buat_data():
    return {
        "uang":uang,"upk":uang_per_klik,"upd":uang_per_detik,
        "tu":total_uang,"tk":total_klik,"wm":waktu_mulai,
        "rb_count":rebirth_count,"rb_bonus":rebirth_bonus,
        "upg":[{"h":u["harga"],"d":u["dibeli"]} for u in upgrades],
        "pst":[p["unlock"] for p in PRESTASI],
        "timestamp": time.time(),
    }

def simpan_ke(path):
    with open(path,"w") as f: json.dump(_buat_data(),f,indent=2)

def simpan(): simpan_ke(AUTO_SAVE)

def simpan_slot(slot):
    simpan_ke(SAVE_SLOT[slot])
    notif(f"💾 Slot {slot+1} Tersimpan", f"Progress disimpan ke Slot {slot+1}")

def muat_dari(path):
    global uang,uang_per_klik,uang_per_detik,total_uang,total_klik,waktu_mulai,rebirth_count,rebirth_bonus
    if not os.path.exists(path): return False
    try:
        with open(path) as f: d=json.load(f)
        uang=d.get("uang",0); uang_per_klik=d.get("upk",1)
        uang_per_detik=d.get("upd",0); total_uang=d.get("tu",0)
        total_klik=d.get("tk",0); waktu_mulai=d.get("wm",time.time())
        rebirth_count=d.get("rb_count",0); rebirth_bonus=d.get("rb_bonus",1.0)
        for i,u in enumerate(d.get("upg",[])):
            if i<len(upgrades): upgrades[i]["harga"]=u["h"]; upgrades[i]["dibeli"]=u["d"]
        for i,v in enumerate(d.get("pst",[])):
            if i<len(PRESTASI): PRESTASI[i]["unlock"]=v
        return True
    except: return False

def muat(): muat_dari(AUTO_SAVE)

def info_slot(slot):
    p=SAVE_SLOT[slot]
    if not os.path.exists(p): return None
    try:
        with open(p) as f: d=json.load(f)
        ts=d.get("timestamp",0)
        tgl=time.strftime("%d/%m %H:%M", time.localtime(ts))
        return {"uang":d.get("uang",0),"tu":d.get("tu",0),"tk":d.get("tk",0),
                "rb":d.get("rb_count",0),"tgl":tgl}
    except: return None

def reset_game(konfirm=True):
    if konfirm and not messagebox.askyesno("Reset","Reset semua progress?\nTidak bisa dibatalkan!"): return
    global uang,uang_per_klik,uang_per_detik,total_uang,total_klik,waktu_mulai,rebirth_count,rebirth_bonus
    uang=0;uang_per_klik=1;uang_per_detik=0;total_uang=0;total_klik=0
    waktu_mulai=time.time();rebirth_count=0;rebirth_bonus=1.0
    for u in upgrades: u["dibeli"]=0; u["harga"]=u["harga0"]
    for p in PRESTASI: p["unlock"]=False
    booster_aktif.clear()

def auto_save():
    simpan(); root.after(15000, auto_save)

# ── REBIRTH ───────────────────────────────────────────────────────────────────
def rebirth_syarat_terpenuhi():
    syarat=int(REBIRTH_SYARAT * (2 ** rebirth_count))
    return int(total_uang) >= syarat

def rebirth_syarat_berikut():
    return int(REBIRTH_SYARAT * (2 ** rebirth_count))

def lakukan_rebirth():
    global uang,uang_per_klik,uang_per_detik,waktu_mulai,rebirth_count,rebirth_bonus
    if not rebirth_syarat_terpenuhi():
        notif("❌ Belum bisa Rebirth",f"Butuh total {fmt(rebirth_syarat_berikut())}",C["red"])
        return
    bonus_baru = round(1.0 + (rebirth_count+1)*REBIRTH_MULTIPLIER, 2)
    if not messagebox.askyesno("♻️ REBIRTH",
        f"Reset progress tapi dapat bonus permanent!\n\n"
        f"Rebirth ke-{rebirth_count+1}\n"
        f"Bonus sekarang: {rebirth_bonus:.2f}×\n"
        f"Bonus baru:     {bonus_baru:.2f}×\n\n"
        f"Lanjutkan?"): return
    # reset tapi pertahankan total_uang, total_klik, prestasi, rebirth
    uang=0; uang_per_klik=1; uang_per_detik=0
    waktu_mulai=time.time()
    rebirth_count+=1
    rebirth_bonus=bonus_baru
    for u in upgrades: u["dibeli"]=0; u["harga"]=u["harga0"]
    booster_aktif.clear()
    suara_rebirth()
    notif(f"♻️ REBIRTH ke-{rebirth_count}!",f"Bonus permanent: {rebirth_bonus:.2f}×",C["rebirth"])
    cek_prestasi(); refresh_ui(); refresh_tab()

# ── COMBO ─────────────────────────────────────────────────────────────────────
def reset_combo():
    global combo_count
    combo_count=0
    if 'lbl_combo' in globals(): lbl_combo.config(text="")

def tambah_combo():
    global combo_count,combo_timer_id
    combo_count+=1
    if combo_timer_id: root.after_cancel(combo_timer_id)
    combo_timer_id=root.after(1500,reset_combo)
    if combo_count>=COMBO_BATAS:
        lbl_combo.config(text=f"🔥 COMBO ×{combo_count}!",fg=C["gold"]); suara_combo()
    elif combo_count>=5:
        lbl_combo.config(text=f"⚡ ×{combo_count}",fg=C["orange"])
    else:
        lbl_combo.config(text=f"×{combo_count}",fg=C["txt2"])

# ── PARTIKEL ──────────────────────────────────────────────────────────────────
WP=["#FFD700","#FF8C00","#FF4500","#FFFFFF","#FF7A00","#AA44FF"]
def spawn_partikel(x,y):
    for _ in range(10):
        _partikel.append([x,y,random.uniform(-3,3),random.uniform(-4,-1),random.choice(WP),14])

def update_partikel():
    mati=[]
    for p in _partikel:
        p[0]+=p[2];p[1]+=p[3];p[3]+=0.3;p[5]-=1
        if p[5]<=0: mati.append(p)
    for p in mati: _partikel.remove(p)
    canvas_klik.delete("partikel")
    for p in _partikel:
        r=max(1,p[5]//4)
        canvas_klik.create_oval(p[0]-r,p[1]-r,p[0]+r,p[1]+r,fill=p[4],outline="",tags="partikel")
    root.after(30,update_partikel)

# ── MULTIPLIER ────────────────────────────────────────────────────────────────
def klik_mult():
    m=rebirth_bonus
    if "klik_x2"  in booster_aktif: m*=2
    if "klik_x5"  in booster_aktif: m*=5
    if "klik_x10" in booster_aktif: m*=10
    if combo_count>=COMBO_BATAS: m*=2
    return m

def auto_mult():
    m=rebirth_bonus
    if "auto_x3" in booster_aktif: m*=3
    if "turbo"   in booster_aktif: m*=5
    return m

# ── GAME LOGIC ────────────────────────────────────────────────────────────────
def klik_warung(event=None):
    global uang,total_uang,total_klik
    dp=uang_per_klik*klik_mult()
    uang+=dp;total_uang+=dp;total_klik+=1
    suara_klik(); animasi_klik(); tambah_combo()
    cx=canvas_klik.winfo_width()//2; cy=canvas_klik.winfo_height()//2
    spawn_partikel(cx,cy-20)
    cek_prestasi(); refresh_ui()

def beli_upgrade(i):
    global uang,uang_per_klik,uang_per_detik
    u=upgrades[i]
    if int(uang)<u["harga"]: return
    uang-=u["harga"]; u["dibeli"]+=1; u["harga"]=int(u["harga"]*1.5)
    if u["tipe"]=="klik": uang_per_klik+=u["ups"]
    else: uang_per_detik+=u["ups"]
    suara_beli(); cek_prestasi(); refresh_ui(); refresh_tab()

def pakai_booster(i):
    global uang,total_uang
    b=boosters[i]
    if int(uang)<b["harga"]: return
    uang-=b["harga"]; ef=b["efek"]
    if ef=="jackpot":
        h=random.randint(5000,50000); uang+=h; total_uang+=h
        notif("💎 JACKPOT!",f"Dapat {fmt(h)}!",C["gold"])
    elif ef=="spin": lucky_spin()
    else:
        booster_aktif[ef]=b["durasi"]
        notif(f"🚀 {b['nama']} AKTIF!",f"{b['durasi']} detik",C["blue"])
        hitung_mundur()
    suara_boost(); cek_prestasi(); refresh_ui(); refresh_tab()

def hitung_mundur():
    for k in list(booster_aktif):
        booster_aktif[k]-=1
        if booster_aktif[k]<=0: del booster_aktif[k]
    if booster_aktif: root.after(1000,hitung_mundur)
    update_booster_bar()

def update_booster_bar():
    parts=[f"{k}({v}s)" for k,v in booster_aktif.items()]
    lbl_booster.config(text=" | ".join(parts) if parts else "")

def lucky_spin():
    global uang,total_uang
    opts=[("😅 Zonk",0),("💵 Kecil",random.randint(100,2000)),
          ("💰 Besar",random.randint(5000,30000)),("🎰 JACKPOT",random.randint(80000,300000))]
    r=random.choices(opts,weights=[45,35,15,5],k=1)[0]
    uang+=r[1];total_uang+=r[1]
    notif("🎰 Lucky Spin!",f"{r[0]}"+(f" +{fmt(r[1])}" if r[1] else ""),C["purple"])

def auto_income():
    global uang,total_uang
    if uang_per_detik>0:
        inc=(uang_per_detik*auto_mult())/10
        uang+=inc;total_uang+=inc;cek_prestasi()
    refresh_ui()
    root.after(100,auto_income)

def animasi_klik():
    lbl_warung_emoji.config(fg=C["gold"])
    root.after(120,lambda:lbl_warung_emoji.config(fg=C["orange"]))

# ── NOTIF ────────────────────────────────────────────────────────────────────
_nq=[];_nb=False
def notif(j,p,w=None):
    _nq.append((j,p,w or C["gold"]))
    if not _nb: _proc_notif()

def _proc_notif():
    global _nb
    if not _nq: _nb=False; return
    _nb=True; j,p,w=_nq.pop(0)
    pop=tk.Toplevel(root); pop.overrideredirect(True); pop.attributes("-topmost",True)
    pop.configure(bg=C["panel"])
    brd=tk.Frame(pop,bg=w,padx=2,pady=2); brd.pack(fill="both",expand=True)
    inn=tk.Frame(brd,bg=C["panel"],padx=14,pady=8); inn.pack(fill="both",expand=True)
    tk.Label(inn,text=j,font=fnt_btn, bg=C["panel"],fg=w).pack(anchor="w")
    tk.Label(inn,text=p,font=fnt_kecil,bg=C["panel"],fg=C["txt2"]).pack(anchor="w")
    pop.update_idletasks()
    sw=root.winfo_screenwidth(); pw=pop.winfo_width()
    pop.geometry(f"+{sw-pw-20}+20")
    root.after(2200,lambda:(pop.destroy(),root.after(250,_proc_notif)))

def cek_prestasi():
    for p in PRESTASI:
        if not p["unlock"] and p["f"]():
            p["unlock"]=True; notif(f"🏆 {p['nama']}",p["desc"])
            suara_prest()
            if tab_aktif=="prestasi": refresh_tab()

# ── UI REFRESH ────────────────────────────────────────────────────────────────
_last_ui=-1
def refresh_ui():
    global _last_ui
    v=int(uang)
    if v==_last_ui: return
    _last_ui=v
    lbl_uang.config(text=fmt(uang))
    lbl_kps.config(text=f"▲ {fmt(uang_per_klik*klik_mult())} / klik")
    lbl_aps.config(text=f"⚙ {fmt(uang_per_detik*auto_mult())} / detik")
    dur=int(time.time()-waktu_mulai); h,r=divmod(dur,3600); m,s=divmod(r,60)
    lbl_waktu.config(text=f"⏱ {h:02d}:{m:02d}:{s:02d}")
    lbl_stat.config(text=f"Total {fmt(total_uang)}  •  {total_klik:,} klik")
    un=sum(1 for p in PRESTASI if p["unlock"])
    lbl_pst_ct.config(text=f"🏆 {un}/{len(PRESTASI)}")
    lbl_rebirth.config(text=f"♻️ Rebirth ×{rebirth_count}  |  Bonus {rebirth_bonus:.2f}×")
    # warna rebirth label kalau sudah bisa rebirth
    clr=C["rebirth"] if rebirth_syarat_terpenuhi() else C["gray"]
    lbl_rebirth.config(fg=clr)

def ganti_tab(nama):
    global tab_aktif; tab_aktif=nama
    for k,b in tab_btns.items():
        b.config(bg=C["orange"] if k==nama else C["card2"],
                 fg="#000" if k==nama else C["txt2"])
    refresh_tab()

def refresh_tab():
    for w in frame_content.winfo_children(): w.destroy()
    {"upgrade":build_upgrade,"toko":build_toko,
     "rebirth":build_rebirth,"prestasi":build_prestasi,
     "tentang":build_tentang}[tab_aktif]()

def _scrollable(parent):
    c=tk.Canvas(parent,bg=C["panel"],highlightthickness=0)
    sb=tk.Scrollbar(parent,orient="vertical",command=c.yview,
                    bg=C["card"],troughcolor=C["bg"],width=8)
    c.configure(yscrollcommand=sb.set)
    sb.pack(side="right",fill="y"); c.pack(fill="both",expand=True)
    f=tk.Frame(c,bg=C["panel"]); c.create_window((0,0),window=f,anchor="nw")
    f.bind("<Configure>",lambda e:c.configure(scrollregion=c.bbox("all")))
    def _scroll(e): c.yview_scroll(int(-1*(e.delta/120)),"units")
    c.bind("<MouseWheel>",_scroll); f.bind("<MouseWheel>",_scroll)
    return f,c

def _kartu(parent,wl=None,bg=None):
    brd=tk.Frame(parent,bg=wl or C["border"],padx=3,pady=0)
    brd.pack(fill="x",padx=8,pady=3)
    inn=tk.Frame(brd,bg=bg or C["card"],padx=10,pady=7)
    inn.pack(fill="both",expand=True)
    return inn

def build_upgrade():
    tk.Label(frame_content,text="🛒  UPGRADE WARUNG",font=fnt_sek,
             bg=C["panel"],fg=C["orange"]).pack(anchor="w",padx=12,pady=(8,4))
    f,c=_scrollable(frame_content)
    for i,u in enumerate(upgrades):
        mampu=int(uang)>=u["harga"]
        wl=C["green"] if mampu else C["border"]
        k=_kartu(f,wl)
        k.columnconfigure(0,weight=1)
        tk.Label(k,text=u["nama"],font=fnt_btn,bg=C["card"],fg=C["txt"],anchor="w").grid(row=0,column=0,sticky="w")
        tk.Label(k,text=u["desc"],font=fnt_kecil,bg=C["card"],fg=C["txt2"]).grid(row=1,column=0,sticky="w")
        tk.Label(k,text=f"[{u['dibeli']}×]",font=fnt_kecil,bg=C["card"],fg=C["gold"]).grid(row=0,column=1,padx=8)
        clr=C["green"] if mampu else C["gray"]
        btn=tk.Button(k,text=fmt(u["harga"]),font=fnt_btn,
                  bg=clr,fg="white",width=9,cursor="hand2",relief="flat",
                  state="normal" if mampu else "disabled",
                  command=lambda idx=i:(beli_upgrade(idx),refresh_tab()))
        btn.grid(row=0,column=2,rowspan=2,padx=4)
        # scroll binding
        for w in [k,btn]:
            w.bind("<MouseWheel>",lambda e,cv=c:cv.yview_scroll(int(-1*(e.delta/120)),"units"))

def build_toko():
    tk.Label(frame_content,text="🎯  TOKO BOOSTER",font=fnt_sek,
             bg=C["panel"],fg=C["blue"]).pack(anchor="w",padx=12,pady=(8,4))
    if booster_aktif:
        bar=tk.Frame(frame_content,bg=C["card2"],padx=10,pady=5)
        bar.pack(fill="x",padx=8,pady=(0,6))
        tk.Label(bar,text="AKTIF: "+" | ".join(f"{k}({v}s)" for k,v in booster_aktif.items()),
                 font=fnt_kecil,bg=C["card2"],fg=C["blue"]).pack(anchor="w")
    f,c=_scrollable(frame_content)
    for i,b in enumerate(boosters):
        mampu=int(uang)>=b["harga"]
        wl=C["blue"] if mampu else C["border"]
        k=_kartu(f,wl)
        k.columnconfigure(0,weight=1)
        tk.Label(k,text=b["nama"],font=fnt_btn,bg=C["card"],fg=C["txt"],anchor="w").grid(row=0,column=0,sticky="w")
        tk.Label(k,text=b["desc"],font=fnt_kecil,bg=C["card"],fg=C["txt2"]).grid(row=1,column=0,sticky="w")
        clr=C["blue"] if mampu else C["gray"]
        btn=tk.Button(k,text=fmt(b["harga"]),font=fnt_btn,
                  bg=clr,fg="white",width=9,cursor="hand2",relief="flat",
                  state="normal" if mampu else "disabled",
                  command=lambda idx=i:(pakai_booster(idx),refresh_tab()))
        btn.grid(row=0,column=1,rowspan=2,padx=8)
        for w in [k,btn]:
            w.bind("<MouseWheel>",lambda e,cv=c:cv.yview_scroll(int(-1*(e.delta/120)),"units"))

def build_rebirth():
    syarat=rebirth_syarat_berikut()
    bisa=rebirth_syarat_terpenuhi()
    tk.Label(frame_content,text="♻️  REBIRTH",font=fnt_sek,
             bg=C["panel"],fg=C["rebirth"]).pack(anchor="w",padx=12,pady=(8,4))

    info=tk.Frame(frame_content,bg=C["card2"],padx=16,pady=14)
    info.pack(fill="x",padx=8,pady=4)
    tk.Label(info,text=f"Rebirth ke-{rebirth_count+1}",font=fnt_btn,
             bg=C["card2"],fg=C["rebirth"]).pack(anchor="w")
    tk.Label(info,text=f"Syarat total uang: {fmt(syarat)}",font=fnt_info,
             bg=C["card2"],fg=C["txt2"]).pack(anchor="w",pady=2)
    tk.Label(info,text=f"Total uang kamu:   {fmt(total_uang)}",font=fnt_info,
             bg=C["card2"],fg=C["green"] if bisa else C["red"]).pack(anchor="w")
    tk.Label(info,text=f"Bonus sekarang:    {rebirth_bonus:.2f}×",font=fnt_info,
             bg=C["card2"],fg=C["txt"]).pack(anchor="w",pady=2)
    bonus_baru=round(1.0+(rebirth_count+1)*REBIRTH_MULTIPLIER,2)
    tk.Label(info,text=f"Bonus setelah:     {bonus_baru:.2f}×",font=fnt_btn,
             bg=C["card2"],fg=C["gold"]).pack(anchor="w")

    tk.Frame(frame_content,bg=C["border"],height=1).pack(fill="x",padx=8,pady=8)

    penjelasan=[
        "Apa itu Rebirth?",
        "Rebirth mereset semua upgrade dan uang kamu,",
        "tapi memberikan bonus PERMANENT ke semua income.",
        "",
        "• Setiap rebirth: +25% bonus permanent",
        "• Total klik & prestasi tetap tersimpan",
        "• Makin banyak rebirth = makin cepat kaya!",
        "",
        f"Riwayat rebirth: {rebirth_count}×",
    ]
    for t in penjelasan:
        fg=C["orange"] if t.startswith("Apa") else (C["txt2"] if t.startswith("•") else C["txt"])
        tk.Label(frame_content,text=t,font=fnt_info if t else fnt_kecil,
                 bg=C["panel"],fg=fg,anchor="w").pack(anchor="w",padx=16,pady=1)

    tk.Frame(frame_content,bg=C["border"],height=1).pack(fill="x",padx=8,pady=12)

    clr=C["rebirth"] if bisa else C["gray"]
    tk.Button(frame_content,text=f"♻️  LAKUKAN REBIRTH ke-{rebirth_count+1}",
              font=fnt_btn,bg=clr,fg="white",relief="flat",cursor="hand2",
              padx=20,pady=10,
              state="normal" if bisa else "disabled",
              command=lakukan_rebirth).pack(pady=4)
    if not bisa:
        butuh=syarat-int(total_uang)
        tk.Label(frame_content,text=f"Butuh {fmt(butuh)} lagi",
                 font=fnt_kecil,bg=C["panel"],fg=C["gray"]).pack()

def build_prestasi():
    tk.Label(frame_content,text="🏆  PRESTASI",font=fnt_sek,
             bg=C["panel"],fg=C["gold"]).pack(anchor="w",padx=12,pady=(8,4))
    un=sum(1 for p in PRESTASI if p["unlock"])
    tk.Label(frame_content,text=f"{un} / {len(PRESTASI)} terbuka",
             font=fnt_kecil,bg=C["panel"],fg=C["txt2"]).pack(anchor="w",padx=12)
    bar=tk.Canvas(frame_content,bg=C["card2"],height=8,highlightthickness=0)
    bar.pack(fill="x",padx=12,pady=(4,8))
    bar.update_idletasks()
    bw=bar.winfo_width() or 400
    bar.create_rectangle(0,0,int(bw*(un/len(PRESTASI))),8,fill=C["gold"],outline="")
    f,_=_scrollable(frame_content)
    for p in PRESTASI:
        wl=C["gold"] if p["unlock"] else C["border"]
        bg2=C["card2"] if p["unlock"] else C["card"]
        k=_kartu(f,wl,bg2)
        fg1=C["gold"] if p["unlock"] else C["gray"]
        fg2=C["txt"]  if p["unlock"] else C["gray"]
        tk.Label(k,text=p["nama"],font=fnt_btn,  bg=bg2,fg=fg1).pack(anchor="w")
        tk.Label(k,text=p["desc"],font=fnt_kecil,bg=bg2,fg=fg2).pack(anchor="w")
        if p["unlock"]: tk.Label(k,text="✓ TERBUKA",font=fnt_kecil,bg=bg2,fg=C["green"]).pack(anchor="e")

def build_tentang():
    f,_=_scrollable(frame_content)
    baris=[
        ("🏪 CLICKER WARUNG",fnt_judul,C["orange"]),
        ("v  0 . 5",fnt_sek,C["gold"]),("","",""),
        ("Idle clicker bertema warung Indonesia.",fnt_info,C["txt"]),
        ("Klik, upgrade, rebirth, jadi sultan!",fnt_info,C["txt2"]),("","",""),
        ("━"*38,fnt_kecil,C["border"]),("","",""),
        ("© 2025  CLICKER WARUNG",fnt_btn,C["gold"]),
        ("Hak cipta dilindungi undang-undang.",fnt_kecil,C["txt2"]),
        ("Dibuat dengan ❤️  Python + tkinter",fnt_kecil,C["txt2"]),
        ("Music: 8-bit synthesizer via pygame",fnt_kecil,C["txt2"]),("","",""),
        ("━"*38,fnt_kecil,C["border"]),("","",""),
        ("KONTROL",fnt_btn,C["orange"]),
        ("  SPASI      →  Klik warung",fnt_info,C["txt"]),
        ("  F11        →  Fullscreen",fnt_info,C["txt"]),
        ("  Ctrl+S     →  Simpan",fnt_info,C["txt"]),
        ("  Ctrl+M     →  Toggle musik",fnt_info,C["txt"]),("","",""),
        ("━"*38,fnt_kecil,C["border"]),("","",""),
        ("TIPS",fnt_btn,C["orange"]),
        ("  • Combo 10× → bonus klik 2×!",fnt_info,C["txt"]),
        ("  • Rebirth setelah 1 juta untuk bonus permanent",fnt_info,C["txt"]),
        ("  • Gunakan 3 slot save untuk backup progress",fnt_info,C["txt"]),
        ("  • Lucky Spin punya 5% chance jackpot!",fnt_info,C["txt"]),("","",""),
        ("Python 3 • tkinter • pygame • numpy",fnt_kecil,C["gray"]),
    ]
    for t,fn,fg in baris:
        if not t: tk.Frame(f,bg=C["panel"],height=4).pack(); continue
        tk.Label(f,text=t,font=fn,bg=C["panel"],fg=fg,anchor="w",justify="left").pack(anchor="w",padx=12,pady=1)

# ── WINDOW HELPERS ────────────────────────────────────────────────────────────
def toggle_fs():
    global is_fullscreen; is_fullscreen=not is_fullscreen
    root.attributes("-fullscreen",is_fullscreen)
    btn_fs.config(text="🗗 Window" if is_fullscreen else "⛶ Full")

def toggle_musik():
    global musik_on; musik_on=not musik_on
    if not musik_on: stop_bgm()
    else: mulai_bgm()
    btn_mus.config(text="🔊 ON" if musik_on else "🔇 OFF")

def on_close(): simpan(); root.destroy()

# ═══════════════════════════════════════════════════════════════════════════════
#  MENU UTAMA
# ═══════════════════════════════════════════════════════════════════════════════
def buka_menu():
    menu=tk.Toplevel(); menu.title("🏪 Clicker Warung v0.5")
    menu.configure(bg=C["menu_bg"]); menu.resizable(False,False)
    menu.geometry("480x600")
    menu.grab_set()   # modal
    # center
    menu.update_idletasks()
    sw=menu.winfo_screenwidth(); sh=menu.winfo_screenheight()
    x=(sw-480)//2; y=(sh-600)//2
    menu.geometry(f"480x600+{x}+{y}")

    # judul
    tk.Label(menu,text="🏪",font=tkfont.Font(size=52),bg=C["menu_bg"],fg=C["orange"]).pack(pady=(30,0))
    tk.Label(menu,text="CLICKER WARUNG",font=tkfont.Font(family="Courier",size=22,weight="bold"),
             bg=C["menu_bg"],fg=C["orange"]).pack()
    tk.Label(menu,text="v 0.5",font=tkfont.Font(family="Courier",size=11),
             bg=C["menu_bg"],fg=C["gold"]).pack()
    tk.Label(menu,text="─"*40,bg=C["menu_bg"],fg=C["border"]).pack(pady=8)

    def mbtn(txt,cmd,clr=None,w=28):
        b=tk.Button(menu,text=txt,font=tkfont.Font(family="Courier",size=11,weight="bold"),
                    bg=clr or C["card"],fg=C["txt"],relief="flat",cursor="hand2",
                    width=w,pady=8,command=cmd)
        b.pack(pady=4,padx=40,fill="x")
        b.bind("<Enter>",lambda e:b.config(bg=clr or C["card2"] if not clr else clr))
        return b

    def mulai_baru():
        reset_game(konfirm=False); menu.destroy(); buka_game()

    def lanjut():
        ok=muat()
        if not ok:
            messagebox.showinfo("Info","Tidak ada save ditemukan.\nMulai game baru.",parent=menu)
            mulai_baru(); return
        menu.destroy(); buka_game()

    def muat_slot(slot):
        ok=muat_dari(SAVE_SLOT[slot])
        if not ok:
            messagebox.showinfo("Info",f"Slot {slot+1} kosong!",parent=menu)
            return
        menu.destroy(); buka_game()

    def simpan_slot_menu(slot):
        # simpan state saat ini ke slot (state mungkin masih kosong, tapi ok)
        simpan_slot(slot)

    def buka_save_manager():
        sm=tk.Toplevel(menu); sm.title("💾 Save Manager")
        sm.configure(bg=C["panel"]); sm.resizable(False,False)
        sm.geometry("400x400"); sm.grab_set()
        sm.update_idletasks()
        sx=(menu.winfo_screenwidth()-400)//2; sy=(menu.winfo_screenheight()-400)//2
        sm.geometry(f"400x400+{sx}+{sy}")
        tk.Label(sm,text="💾 SAVE MANAGER",font=tkfont.Font(family="Courier",size=13,weight="bold"),
                 bg=C["panel"],fg=C["gold"]).pack(pady=12)
        for i in range(3):
            info=info_slot(i)
            sf=tk.Frame(sm,bg=C["card"],padx=12,pady=8); sf.pack(fill="x",padx=12,pady=4)
            if info:
                tk.Label(sf,text=f"SLOT {i+1}  —  {info['tgl']}",font=tkfont.Font(family="Courier",size=9,weight="bold"),
                         bg=C["card"],fg=C["orange"]).pack(anchor="w")
                tk.Label(sf,text=f"Uang: {fmt(info['uang'])}   Total: {fmt(info['tu'])}   Klik: {info['tk']:,}   Rebirth: {info['rb']}×",
                         font=tkfont.Font(family="Courier",size=8),bg=C["card"],fg=C["txt2"]).pack(anchor="w")
            else:
                tk.Label(sf,text=f"SLOT {i+1}  —  (kosong)",font=tkfont.Font(family="Courier",size=9,weight="bold"),
                         bg=C["card"],fg=C["gray"]).pack(anchor="w")
            bf=tk.Frame(sf,bg=C["card"]); bf.pack(anchor="e")
            tk.Button(bf,text="📂 Load",font=tkfont.Font(size=8),bg=C["blue"],fg="white",
                      relief="flat",cursor="hand2",padx=6,pady=2,
                      command=lambda s=i:(sm.destroy(),menu.destroy(),muat_dari(SAVE_SLOT[s]) and buka_game() or buka_game())).pack(side="left",padx=2)
            tk.Button(bf,text="💾 Save",font=tkfont.Font(size=8),bg=C["green"],fg="white",
                      relief="flat",cursor="hand2",padx=6,pady=2,
                      command=lambda s=i:simpan_slot(s)).pack(side="left",padx=2)
            if info:
                tk.Button(bf,text="🗑",font=tkfont.Font(size=8),bg=C["red"],fg="white",
                          relief="flat",cursor="hand2",padx=6,pady=2,
                          command=lambda s=i:(os.remove(SAVE_SLOT[s]),sm.destroy(),buka_save_manager())).pack(side="left",padx=2)
        tk.Button(sm,text="✖ Tutup",font=tkfont.Font(size=9),bg=C["card2"],fg=C["txt2"],
                  relief="flat",cursor="hand2",padx=10,pady=4,
                  command=sm.destroy).pack(pady=10)

    # cek apakah ada autosave
    has_save=os.path.exists(AUTO_SAVE)

    mbtn("▶  MULAI BARU", mulai_baru, "#1A3A00")
    if has_save:
        mbtn("⏩  LANJUTKAN", lanjut, "#003A2A")
    mbtn("💾  SAVE MANAGER", buka_save_manager, C["card"])
    tk.Label(menu,text="─"*40,bg=C["menu_bg"],fg=C["border"]).pack(pady=6)
    tk.Label(menu,text="© 2025 Clicker Warung  •  Python + tkinter",
             font=tkfont.Font(family="Courier",size=8),bg=C["menu_bg"],fg=C["gray"]).pack(pady=(0,10))

    menu.protocol("WM_DELETE_WINDOW",lambda:(root.destroy()))

# ═══════════════════════════════════════════════════════════════════════════════
#  GAME WINDOW
# ═══════════════════════════════════════════════════════════════════════════════
def buka_game():
    global frame_content, tab_btns, canvas_klik, lbl_warung_emoji
    global lbl_uang, lbl_kps, lbl_aps, lbl_waktu, lbl_stat, lbl_pst_ct
    global lbl_combo, lbl_booster, lbl_rebirth, btn_fs, btn_mus

    # bersihkan root
    for w in root.winfo_children(): w.destroy()

    # ── HEADER ────────────────────────────────────────────────
    hdr=tk.Frame(root,bg=C["header"],pady=6); hdr.pack(fill="x")
    tk.Label(hdr,text="▶ CLICKER WARUNG  v0.5",font=fnt_sek,
             bg=C["header"],fg=C["orange"]).pack(side="left",padx=14)

    def hbtn(txt,cmd,clr=None):
        b=tk.Button(hdr,text=txt,font=fnt_kecil,bg=clr or "#2A1A00",fg=C["txt2"],
                    relief="flat",cursor="hand2",padx=8,pady=3,command=cmd)
        b.pack(side="right",padx=3); return b

    btn_fs  = hbtn("⛶ Full",toggle_fs)
    btn_mus = hbtn("🔊 ON", toggle_musik)
    hbtn("💾 Simpan",lambda:(simpan(),notif("💾 Tersimpan","Autosave ✓")))

    # slot cepat
    for i in range(3):
        hbtn(f"S{i+1}",lambda s=i: simpan_slot(s))

    hbtn("☰ Menu",lambda:(simpan(),_balik_menu()),"#3A2000")
    hbtn("🗑 Reset",reset_game,"#3A0000")

    # ── BODY ──────────────────────────────────────────────────
    body=tk.Frame(root,bg=C["bg"]); body.pack(fill="both",expand=True)
    body.columnconfigure(0,weight=0,minsize=255)
    body.columnconfigure(1,weight=1); body.rowconfigure(0,weight=1)

    # ── PANEL KIRI ────────────────────────────────────────────
    pl=tk.Frame(body,bg=C["panel"],width=255); pl.grid(row=0,column=0,sticky="nsew")
    pl.pack_propagate(False)

    uf=tk.Frame(pl,bg=C["card"],padx=12,pady=10); uf.pack(fill="x",padx=8,pady=(10,4))
    tk.Label(uf,text="UANG",font=fnt_kecil,bg=C["card"],fg=C["txt2"]).pack(anchor="w")
    lbl_uang=tk.Label(uf,text="Rp 0",font=fnt_uang,bg=C["card"],fg=C["orange"]); lbl_uang.pack(anchor="w")
    lbl_kps=tk.Label(uf,text="▲ +1 / klik",font=fnt_kecil,bg=C["card"],fg=C["green"]); lbl_kps.pack(anchor="w")
    lbl_aps=tk.Label(uf,text="⚙ 0 / detik",font=fnt_kecil,bg=C["card"],fg=C["txt2"]); lbl_aps.pack(anchor="w")

    canvas_klik=tk.Canvas(pl,bg=C["panel"],height=170,highlightthickness=0)
    canvas_klik.pack(fill="x",padx=8,pady=4)

    lbl_warung_emoji=tk.Label(pl,text="🏪",font=tkfont.Font(size=48),
                               bg=C["panel"],fg=C["orange"],cursor="hand2")
    lbl_warung_emoji.place(in_=canvas_klik,relx=0.5,rely=0.45,anchor="center")
    lbl_warung_emoji.bind("<Button-1>",klik_warung)
    canvas_klik.bind("<Button-1>",klik_warung)

    lbl_combo  =tk.Label(pl,text="",font=fnt_combo,bg=C["panel"],fg=C["gold"]); lbl_combo.pack()
    lbl_booster=tk.Label(pl,text="",font=fnt_kecil,bg=C["panel"],fg=C["blue"],wraplength=240); lbl_booster.pack()
    tk.Label(pl,text="[SPASI] untuk klik",font=fnt_kecil,bg=C["panel"],fg=C["gray"]).pack(pady=2)

    sf=tk.Frame(pl,bg=C["card2"],padx=10,pady=8); sf.pack(fill="x",padx=8,pady=(6,2))
    lbl_waktu=tk.Label(sf,text="⏱ 00:00:00",font=fnt_kecil,bg=C["card2"],fg=C["txt2"]); lbl_waktu.pack(anchor="w")
    lbl_stat =tk.Label(sf,text="Total Rp 0  •  0 klik",font=fnt_kecil,bg=C["card2"],fg=C["txt2"],wraplength=230); lbl_stat.pack(anchor="w")
    lbl_pst_ct=tk.Label(sf,text=f"🏆 0/{len(PRESTASI)}",font=fnt_kecil,bg=C["card2"],fg=C["gold"]); lbl_pst_ct.pack(anchor="w")

    # rebirth info
    rf=tk.Frame(pl,bg=C["card"],padx=10,pady=6); rf.pack(fill="x",padx=8,pady=(2,4))
    lbl_rebirth=tk.Label(rf,text="♻️ Rebirth ×0  |  Bonus 1.00×",font=fnt_kecil,
                          bg=C["card"],fg=C["gray"],wraplength=230); lbl_rebirth.pack(anchor="w")
    tk.Button(rf,text="♻️ Rebirth",font=fnt_kecil,bg=C["rebirth"],fg="white",
              relief="flat",cursor="hand2",padx=6,pady=2,
              command=lambda:(ganti_tab("rebirth"))).pack(anchor="e")

    if not HAS_AUDIO:
        tk.Label(pl,text="⚠ pip install pygame numpy",
                 font=fnt_kecil,bg=C["panel"],fg=C["red"],wraplength=230).pack(padx=8,pady=2)

    # ── PANEL KANAN ───────────────────────────────────────────
    pr=tk.Frame(body,bg=C["bg"]); pr.grid(row=0,column=1,sticky="nsew")
    pr.rowconfigure(1,weight=1); pr.columnconfigure(0,weight=1)

    tf=tk.Frame(pr,bg=C["bg"]); tf.grid(row=0,column=0,sticky="ew",padx=6,pady=6)
    tab_btns={}
    tabs=[("upgrade","🛒 Upgrade"),("toko","🎯 Toko"),
          ("rebirth","♻️ Rebirth"),("prestasi","🏆 Prestasi"),("tentang","ℹ Tentang")]
    for nama,label in tabs:
        b=tk.Button(tf,text=label,font=fnt_btn,
                    bg=C["orange"] if nama=="upgrade" else C["card2"],
                    fg="#000" if nama=="upgrade" else C["txt2"],
                    relief="flat",cursor="hand2",padx=10,pady=5,
                    command=lambda n=nama:ganti_tab(n))
        b.pack(side="left",padx=2); tab_btns[nama]=b

    brd=tk.Frame(pr,bg=C["orange"],padx=1); brd.grid(row=1,column=0,sticky="nsew",padx=6,pady=(0,6))
    frame_content=tk.Frame(brd,bg=C["panel"]); frame_content.pack(fill="both",expand=True)

    # ── KEYBIND ───────────────────────────────────────────────
    root.bind("<space>",    klik_warung)
    root.bind("<F11>",      lambda e:toggle_fs())
    root.bind("<Control-s>",lambda e:(simpan(),notif("💾 Tersimpan","Autosave ✓")))
    root.bind("<Control-m>",lambda e:toggle_musik())

    refresh_ui(); refresh_tab()
    root.after(100,auto_income)
    root.after(15000,auto_save)
    root.after(30,update_partikel)
    if HAS_AUDIO: root.after(800,mulai_bgm)

def _balik_menu():
    stop_bgm()
    for w in root.winfo_children(): w.destroy()
    buka_menu()

# ── ROOT ──────────────────────────────────────────────────────────────────────
root=tk.Tk()
root.title("🏪 Clicker Warung v0.5")
root.configure(bg=C["bg"])
root.geometry("1100x700")
root.resizable(True,True)
root.protocol("WM_DELETE_WINDOW",lambda:(simpan(),root.destroy()))

fnt_judul=tkfont.Font(family="Courier",size=18,weight="bold")
fnt_sek  =tkfont.Font(family="Courier",size=11,weight="bold")
fnt_uang =tkfont.Font(family="Courier",size=24,weight="bold")
fnt_btn  =tkfont.Font(family="Courier",size=10,weight="bold")
fnt_info =tkfont.Font(family="Courier",size=10)
fnt_kecil=tkfont.Font(family="Courier",size=8)
fnt_combo=tkfont.Font(family="Courier",size=13,weight="bold")

init_sfx()
buka_menu()
root.mainloop()
