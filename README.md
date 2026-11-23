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
⚙️ Konfigurasi
Semua parameter bisa diubah di config.py. Berikut yang paling sering di-tuning:

Kamera & Resolusi
python
CAMERA_INDEX = 0              # ganti ke 1/2 kalau kamera tidak terdeteksi
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
CAMERA_FPS = 60
Piano Layout
python
KEYBOARD_TOP_RATIO = 0.65     # keyboard mulai di 65% tinggi layar
KEYBOARD_HEIGHT_RATIO = 0.35  # tinggi keyboard 35%
BLACK_KEY_HEIGHT_RATIO = 0.62 # tinggi tuts hitam relatif
BLACK_KEY_WIDTH_RATIO = 0.58  # lebar tuts hitam relatif
Audio
python
AUDIO_VOLUME = 0.35           # volume (0.0 - 1.0)
KEY_COOLDOWN = 0.12           # jeda antar nada sama (detik)
TONE_DURATION = 0.55          # durasi nada (detik)
USE_REAL_PIANO_SAMPLES = False # True = pakai file .wav asli
Hand Tracking
python
MAX_NUM_HANDS = 2
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.6
MODEL_COMPLEXITY = 1          # 0 = cepat, 1 = akurat
PINCH_THRESHOLD = 35          # jarak jempol-telunjuk untuk pinch
Gameplay
python
STARTING_LIVES = 5            # nyawa di Song Mode
SCORE_PER_CORRECT_NOTE = 10   # skor dasar per not benar
COMBO_TIMEOUT = 1.5           # detik sebelum combo reset
NOTE_FALL_SPEED = 380         # kecepatan not jatuh (px/detik)
🎵 Membuat Lagu Sendiri
Lagu disimpan sebagai file .json di assets/songs/. Formatnya:

json
{
  "title": "Lagu Saya",
  "composer": "Nama Kamu",
  "bpm": 100,
  "difficulty": "easy",
  "notes": [
    {"note": "C4", "time": 0.0, "duration": 0.5},
    {"note": "D4", "time": 0.5, "duration": 0.5},
    {"note": "E4", "time": 1.0, "duration": 0.5},
    {"note": "F4", "time": 1.5, "duration": 0.5}
  ]
}
Field:

note: nama nada (C4, C#4, D4, ..., B5)

time: waktu mulai (detik) relatif ke awal lagu

duration: durasi nada (detik)

bpm: opsional (info saja)

difficulty: easy / medium / hard

Langkah:

Simpan file di assets/songs/lagu_saya.json

Jalankan game → lagu otomatis terdeteksi

Tapi karena tombol pilih lagu hanya 1-5, untuk testing pakai kode langsung atau sementara ganti urutan file

🎹 Menggunakan Suara Piano Asli (Opsional)
Kalau suara sintesis terasa kurang natural, bisa pakai file piano sungguhan:

Download sample piano gratis dari:

tonejs-instruments — folder piano/

freesound.org — search "piano C4"

Rename file sesuai format kita: C4.wav, C#4.wav, D4.wav, ..., B5.wav

Simpan ke assets/sounds/ (timpa file sintesis)

Edit config.py: USE_REAL_PIANO_SAMPLES = True

Jalankan ulang

🆘 Troubleshooting
❌ No module named 'cv2' / No module named 'mediapipe'
Penyebab: venv tidak aktif atau library belum terinstall.

Solusi:

bash
venv\Scripts\activate
pip install -r requirements.txt
❌ ERROR: Could not find a version that satisfies the requirement mediapipe==0.10.14
Penyebab: Python kamu bukan 3.12 (kemungkinan 3.13/3.14).

Solusi: Install Python 3.12, lalu buat venv baru dengan py -3.12 -m venv venv.

❌ ModuleNotFoundError: No module named 'distutils.msvccompiler'
Penyebab: Python 3.14 (distutils sudah dihapus).

Solusi: Turun ke Python 3.12.

❌ Kamera tidak terdeteksi
Solusi:

Cek kamera: python -c "import cv2; c=cv2.VideoCapture(0); print(c.isOpened()); c.release()"

Kalau False, ubah CAMERA_INDEX = 1 atau 2 di config.py

Pastikan kamera tidak dipakai aplikasi lain (Zoom, Teams, dll)

Cek izin kamera di Settings Windows → Privacy → Camera

❌ Suara tidak keluar
Solusi:

Cek volume speaker Windows

Edit config.py: naikkan AUDIO_VOLUME = 0.6

Pastikan pygame terinstall: pip list | findstr pygame

Cek file audio: dir assets\sounds — harus ada 24 file .wav

❌ Game lag / FPS rendah
Solusi:

Edit config.py: MODEL_COMPLEXITY = 0

Turunkan resolusi kamera: CAMERA_WIDTH = 640, CAMERA_HEIGHT = 480

Tutup aplikasi lain yang berat (Chrome, Zoom, dll)

Pastikan laptop tidak dalam mode "Power Saving"

❌ Tangan tidak terdeteksi
Solusi:

Perbaiki pencahayaan — tangan harus terlihat jelas

Jangan pakai baju warna sama dengan latar belakang

Naikkan MIN_DETECTION_CONFIDENCE = 0.5 di config

Jauhkan tangan dari wajah (jangan sampai menutupi)

❌ Fullscreen tidak mau keluar
Solusi: Tekan F (toggle) atau Q (keluar). Kalau tetap tidak bisa, tekan Alt+F4.

❌ Tuts piano terpotong
Solusi: Edit config.py:

KEYBOARD_TOP_RATIO = 0.60 (keyboard lebih tinggi)

atau KEYBOARD_HEIGHT_RATIO = 0.40 (tuts lebih tinggi)

🧪 File Test
Proyek ini punya beberapa file test standalone untuk debugging:

bash
python test_audio.py         # test generate & play nada
python test_hand_tracker.py  # test deteksi tangan
python test_renderer.py      # test render tuts piano
python test_game_state.py    # test logika skor & combo
python test_song_loader.py   # test load lagu
Berguna kalau ada bagian yang tidak jalan — test per modul.

🛠️ Teknologi
Library	Fungsi
OpenCV	Capture kamera, rendering, drawing
MediaPipe	Hand tracking (21 landmark per tangan)
NumPy	Array operations, generate gelombang audio
Pygame	Audio playback (mixer)
📊 Performa
Hardware	FPS (estimasi)
Laptop modern (i5/Ryzen 5+)	50-60
Laptop mid-range	35-50
Laptop lama (i3, 4GB RAM)	20-35
Tips performa:

MODEL_COMPLEXITY = 0 → +30% FPS

Resolusi kamera 640x480 → +40% FPS

Tutup aplikasi berat lain

🎯 Roadmap
Fitur yang mungkin ditambahkan:

□ Mode Record & Playback (rekam permainan, putar ulang)
□ Leaderboard lokal (top 10 skor)
□ Song Editor (bikin lagu via UI)
□ Tema warna (neon, light, dark)
□ Packaging jadi .exe standalone via PyInstaller
□ Multi-bahasa (ID/EN)
□ Efek partikel lebih kaya saat tuts ditekan
□ Metronom untuk latihan timing
📝 Lisensi
Proyek ini untuk pembelajaran pribadi. Bebas dimodifikasi dan digunakan.

Library yang dipakai:

OpenCV: Apache 2.0

MediaPipe: Apache 2.0

Pygame: LGPL

NumPy: BSD

🙏 Kredit
MediaPipe oleh Google — hand tracking

OpenCV — computer vision

Pygame — audio

Melodi lagu bawaan: public domain / traditional

📞 Kontak & Dukungan
Kalau ada bug atau pertanyaan:

Cek bagian Troubleshooting di atas dulu

Cek file log: logs/air_piano.log

Jalankan file test yang relevan untuk isolasi masalah

Selamat bermain! 🎹🎵

"Musik adalah bahasa universal — dan sekarang kamu bisa memainkannya di udara."

text

---

## 📋 Ringkasan Isi README

| Bagian | Isi |
|--------|-----|
| **Judul & Badge** | Info proyek + versi library |
| **Fitur** | 10 fitur utama |
| **Prasyarat** | Python 3.12, webcam, speaker |
| **Instalasi** | Step-by-step dari nol |
| **Cara Menjalankan** | 1 perintah |
| **Kontrol** | Tabel tombol keyboard |
| **Cara Bermain** | Free Play & Song Mode |
| **Struktur Proyek** | Tree folder lengkap |
| **Konfigurasi** | Parameter yang bisa di-tuning |
| **Bikin Lagu** | Format JSON + langkah |
| **Suara Piano Asli** | Cara pakai sample |
| **Troubleshooting** | 9 masalah umum + solusi |
| **File Test** | 5 script test |
| **Teknologi** | 4 library utama |
| **Performa** | Estimasi FPS per hardware |
| **Roadmap** | 8 fitur masa depan |
| **Lisensi** | Info lisensi |
| **Kredit** | Ucapan terima kasih |

---

## ✅ Langkah Selanjutnya

1. **Buat file `README.md`** di root folder `air_piano_pro/`
2. Copy semua isi di atas
3. Simpan
4. Cek di File Explorer — file `README.md` muncul dengan icon markdown
5. (Opsional) Buka di VS Code / Notepad++ untuk lihat preview

---