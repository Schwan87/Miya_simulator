# Archery - Precision Challenge 🎯

Game 2D Desktop Target Shooting / Archery modern, minimalis, dan bertema gelap (*dark-themed*) yang dibangun dengan Python dan Pygame. Game ini terinspirasi dari arcade archery dengan fokus pada responsivitas gameplay, estetika futuristik neon, physics anak panah yang halus, dan sistem skoring presisi berbasis jarak (*distance-based collision*).

![Python](https://img.shields.io/badge/Python-3.13%20%7C%203.14-blue)
![Pygame](https://img.shields.io/badge/Pygame--CE-2.5%2B-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-darkgrey)

---

## ✨ Fitur Utama

- **Modern Minimalist Dark UI**: Tampilan visual elegan dengan background *deep void*, garis grid halus, pencahayaan aksen cyan neon & gold, serta partikel atmosfer melayang (*ambient floating dust*).
- **Interactive Mouse Aiming**: Busur berputar halus mengikuti pergerakan kursor mouse dengan batasan sudut realistis (-75° hingga +75°) dan preview lintasan tembak (*trajectory projection*).
- **Continuous Collision Detection (CCD)**: Mendeteksi titik potong anak panah tepat pada bidang target lingkaran, menjamin tembakan kecepatan tinggi tidak terlewat (*anti-tunneling*) dan memberikan skor bullseye yang akurat.
- **Dynamic Concentric Rings**: Target lingkaran konsentris dengan nilai skor proporsional:
  - 🎯 **Bullseye (Pusat)**: 100 Poin
  - 🟠 **Inner Ring**: 50 Poin
  - 🔵 **Middle Ring**: 25 Poin
  - ⚪ **Outer Ring**: 10 Poin
- **Tantangan Berperingkat (Rounds Progression)**: 5 ronde permainan dengan kecepatan gerak dan osilasi target vertikal yang semakin menantang di setiap rondenya.
- **Streak & Combo Multiplier**: Tembakan berturut-turut yang mengenai target memberikan bonus poin multiplier bertingkat.
- **Visual Feedback & Effects**:
  - Teks pop-up dinamis: `"HIT!"`, `"BULLSEYE!"`, `"MISS"`, dan bonus skor.
  - Efek pecahan partikel (*spark burst*) dan gelombang cincin (*shockwave*).
  - Animasi flash pada target dan guncangan layar halus (*screen shake*).
  - Jejak terbang neon (*motion trail*) pada setiap anak panah.
- **Built-in Procedural Audio Synthesizer**: Menghasilkan efek suara retro-futuristik (`shoot.wav`, `hit.wav`, `bullseye.wav`, `miss.wav`, `click.wav`) secara otomatis menggunakan modul standar Python tanpa perlu mengunduh file eksternal secara manual. Dilengkapi fallback aman sehingga game tidak pernah crash jika audio device bermasalah.
- **State Management Lengkap**:
  - `MAIN MENU` (Play, How To Play, Quit)
  - `HOW TO PLAY` (Petunjuk kontrol & tabel poin)
  - `PLAYING` (Gameplay utama & HUD)
  - `PAUSED` (Resume, Restart, Menu)
  - `GAME OVER` (Statistik Final Score, Target Hits, Accuracy %, dan Max Streak)

---

## 🎮 Kontrol Game

| Aksi | Kontrol | Keterangan |
| :--- | :--- | :--- |
| **Arahkan Busur** | Gerakkan Mouse | Sudut busur mengikuti kursor secara dinamis |
| **Tarik & Lepas / Tembak** | Klik Kiri Mouse | Menembakkan anak panah ke arah target |
| **Jeda / Pause** | Tombol `ESC` | Membuka menu jeda saat sedang bermain |
| **Kembali ke Menu** | Tombol `ESC` | Kembali dari layar How To Play |

---

## 🚀 Cara Install dan Menjalankan

### 1. Prasyarat
Pastikan Anda telah menginstal **Python 3.10+** (disarankan Python 3.13 / 3.14).

Periksa versi Python:
```bash
python --version
```

### 2. Install Dependensi
Game ini hanya memerlukan `pygame` (atau `pygame-ce`):
```bash
pip install pygame-ce
```
*(atau `pip install pygame`)*

### 3. Jalankan Game
Buka terminal / command prompt di direktori project ini, lalu jalankan:
```bash
python main.py
```

---

## 📁 Struktur Project

```text
Miya_simulator/
│
├── main.py               # Entrypoint aplikasi dan loop utama (60 FPS)
├── settings.py           # Konfigurasi resolusi, palet warna, fisika, & aturan
├── README.md             # Dokumentasi panduan lengkap
│
├── game/
│   ├── __init__.py
│   ├── game.py           # Game Manager, state machine, kalkulasi ronde & skor
│   ├── player.py         # Entity busur, aiming mouse, trajectory guide
│   ├── arrow.py          # Fisika proyektil panah, motion trail, koordinat tip
│   ├── target.py         # Target konsentris, kalkulasi tabrakan, pergerakan osilasi
│   ├── effects.py        # Partikel, shockwaves, floating text, screen shake
│   └── audio.py          # Procedural sound synthesizer & safe audio manager
│
├── ui/
│   ├── __init__.py
│   ├── buttons.py        # Komponen tombol modern dengan efek hover & border glow
│   ├── hud.py            # Status bar atas (Score, Round, Arrows, Accuracy, Streak)
│   └── menu.py           # Layar Menu Utama, How To Play, Game Over, dan Pause
│
└── assets/
    └── sounds/           # File audio sintetis WAV (dihasilkan otomatis)
```

---

## 🎯 Gameplay Tips

1. **Gunakan Trajectory Guide**: Titik-titik cyan bercahaya menunjukkan perkiraan lintasan panah dengan memperhitungkan gravitasi ringan.
2. **Kalkulasikan Gerakan Target**: Di ronde-ronde akhir, target bergerak vertikal lebih cepat. Tembak sedikit di depan arah gerak target (*lead your shot*).
3. **Pertahankan Combo Streak**: Setiap tembakan berturut-turut yang mengenai sasaran akan meningkatkan pengali skor combo!
