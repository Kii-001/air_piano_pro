# 🎹 Air Piano Pro

Game piano virtual futuristik dengan **hand tracking** — mainkan piano tanpa menyentuh apa pun, hanya dengan gerakan tangan di depan kamera.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.11-green)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.14-orange)
![Pygame](https://img.shields.io/badge/Pygame-2.6.1-red)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)

---

## ✨ Fitur

- 🖐️ **Hand Tracking 2 Tangan** — deteksi ujung telunjuk via MediaPipe, smoothing posisi biar halus
- 🎹 **Piano 2 Oktaf** — 14 tuts putih + 10 tuts hitam, layout standar piano
- 🎵 **Audio Sintesis** — generate nada piano dengan harmonik + envelope ADSR (atau pakai sample piano asli)
- 🎮 **2 Mode Game**:
  - **Free Play** — main bebas, skor & combo bertambah
  - **Song Mode** — not jatuh dari atas (Piano Tiles style), pukul dengan timing tepat
- 🎼 **5 Lagu Bawaan** — Twinkle Twinkle, Ode to Joy, Happy Birthday, Mary Had a Little Lamb, Jingle Bells
- 🏆 **Highscore Tersimpan** — best score, best combo, akurasi terbaik disimpan ke `highscore.json`
- 🎨 **Visual Cantik** — background gradient + bintang, tuts gradient, glow saat ditekan, trail jari bercahaya
- 🖥️ **Auto-Fit Layar** — deteksi resolusi layar otomatis, fullscreen support
- ⏸️ **Pause / Restart** — kontrol lengkap saat main
- 📝 **Logging** — log ke file `logs/air_piano.log` untuk debugging

---

## 📋 Prasyarat

- **Python 3.11 atau 3.12** (⚠️ **JANGAN** pakai 3.13 atau 3.14 — MediaPipe & Pygame belum stabil)
- **Webcam** (built-in laptop atau eksternal)
- **Speaker / headphone**
- **OS**: Windows 10/11 (direkomendasikan), Mac, Linux

### Cek Python Kamu

```bash

py -3.12 --version

Kalau belum ada Python 3.12, download dari python.org — pilih Windows installer (64-bit), centang "Add python.exe to PATH" dan "py launcher" saat install.

💡 Python versi lain boleh terpasang, kita akan pakai py -3.12 untuk panggil versi 3.12.

🚀 Instalasi
1. Clone / Download Proyek
bash
cd Desktop
mkdir air_piano_pro
cd air_piano_pro
Atau copy folder proyek ini ke lokasi yang diinginkan.

2. Buat Virtual Environment
Windows:

bash
py -3.12 -m venv venv
venv\Scripts\activate
Mac/Linux:

bash
python3.12 -m venv venv
source venv/bin/activate
Setelah aktif, prompt akan ada (venv) di depan.

3. Install Dependensi
Buat file requirements.txt di root folder:

txt
opencv-python==4.10.0.84
mediapipe==0.10.14
numpy==1.26.4
pygame==2.6.1
Install:

bash
pip install -r requirements.txt
4. Verifikasi Instalasi
bash
python -c "import cv2, mediapipe, numpy, pygame; print('cv2:', cv2.__version__); print('mediapipe:', mediapipe.__version__); print('numpy:', numpy.__version__); print('pygame:', pygame.version.ver)"
Ekspektasi output:

text
cv2: 4.10.0
mediapipe: 0.10.14
numpy: 1.26.4
pygame: 2.6.1
Cek kamera:

bash
python -c "import cv2; c=cv2.VideoCapture(0); print('Kamera:', c.isOpened()); c.release()"
Harus Kamera: True. Kalau False, coba ubah CAMERA_INDEX = 1 atau 2 di config.py.

🎮 Cara Menjalankan
bash
python main.py
Jendela game akan terbuka fullscreen dengan:

HUD di atas (skor, combo, mode, FPS)

Area kamera di tengah (video diri kamu)

Tuts piano di bawah (2 oktaf)

🕹️ Kontrol
Tombol	Fungsi
Q	Keluar dari game
F	Toggle fullscreen
M	Ganti mode (Free Play ↔ Song Mode)
P	Pause / Resume
R	Restart sesi
L	Toggle skeleton tangan (debug)
1 - 5	Pilih lagu (khusus Song Mode)
SPACE	Mulai lagu (khusus Song Mode)
🎯 Cara Bermain
🎹 Free Play
Jalankan game — mode default adalah Free Play

Angkat satu atau dua tangan ke depan kamera

Arahkan ujung telunjuk ke tuts piano

Sentuh tuts → nada berbunyi + efek glow + trail

Coba main lagu seperti Twinkle Twinkle:

text
C C G G A A G  F F E E D D C
🎼 Song Mode (Piano Tiles)
Tekan M untuk masuk Song Mode

Pilih lagu dengan tombol 1-5

1 = Happy Birthday

2 = Jingle Bells

3 = Mary Had a Little Lamb

4 = Ode to Joy

5 = Twinkle Twinkle Little Star

Tekan SPACE untuk mulai — ada countdown 3 detik

Not jatuh dari atas layar — pukul dengan jari saat not menyentuh keyboard

Timing tepat = hit (skor + combo), timing salah = miss (nyawa berkurang)

Game berakhir kalau nyawa habis atau lagu selesai

📁 Struktur Proyek
text
air_piano_pro/
│
├── venv/                     # virtual environment
├── requirements.txt          # daftar dependensi
├── README.md                 # file ini
├── main.py                   # entry point game
├── config.py                 # konfigurasi terpusat
├── highscore.json            # highscore tersimpan (auto-generate)
│
├── core/
│   ├── __init__.py
│   ├── audio_engine.py       # generate & play nada piano
│   ├── hand_tracker.py       # deteksi tangan MediaPipe
│   ├── piano_renderer.py     # render tuts + efek
│   ├── game_state.py         # skor, combo, nyawa, mode
│   └── song_loader.py        # load lagu dari JSON
│
├── assets/
│   ├── sounds/               # cache 24 file .wav (auto-generate)
│   │   ├── C4.wav
│   │   ├── D4.wav
│   │   └── ... (sampai B5.wav)
│   └── songs/                # file lagu JSON
│       ├── twinkle.json
│       ├── ode_to_joy.json
│       ├── happy_birthday.json
│       ├── mary_lamb.json
│       └── jingle_bells.json
│
└── logs/
    └── air_piano.log         # log aktivitas game

