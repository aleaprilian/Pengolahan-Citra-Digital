# Aplikasi Pengolahan Citra Digital (Flask Web Application)

Aplikasi web interaktif untuk mata kuliah **Pengolahan Citra Digital (PCD)** yang dibangun menggunakan Python, Flask microframework, OpenCV, Pillow, dan antarmuka web modern (HTML5/CSS3/JavaScript). Aplikasi ini mendukung visualisasi komparatif citra (mode tunggal dan ganda), manipulasi piksel, perbaikan kualitas citra, analisis noise & restorasi, deteksi tepi, hingga segmentasi citra secara asinkron (*real-time*).

---

## 👥 Tim Pengembang (Developers)
* **Ale Aprilian Putra Anton** (Ketua / Integrasi Kode & Sistem) - NIM: 2407114008
* **Raditya Yhori Pratama** (Perancangan Antar Muka & Dokumentasi) - NIM: 2407110797
* **Wan Nabil Muzakhy** (Algoritma PCD & Analisis Data) - NIM: 2407127390

**Dosen Pengampu:**
* T. Yudi Hadiwandra, S.Kom, M.Kom
* Khairul Umam Syaliman, S.T., M.Kom

---

## 🚀 Fitur Utama & Struktur Menu

Aplikasi dirancang mengacu pada perancangan wireframe UI (`PCD WIREFRAME.pdf`) yang mencakup 7 menu utama:

1. **File:**
   * Browse File Citra Utama
   * Open Secondary Image (untuk operasi Aritmatika & Boolean)
   * Save Image & Save As (mengunduh citra hasil olahan)
   * Exit / Reset Sesi
2. **Basic Operation (Operasi Dasar & Mode Dual Canvas):**
   * Pengaturan Kecerahan (*Brightness*) & Kontras (*Contrast*)
   * Inversi Warna (*Negative*)
   * Konversi Ruang Warna (RGB, Grayscale, Binary, HSV, CMY, YUV, YIQ, Pseudo Color)
   * Transformasi Geometri (Rotasi sudut, Flip Horizontal/Vertikal, Zooming)
   * Seleksi Pemotongan Interaktif pada Kanvas (*Interactive Crop on Canvas*) dengan koordinat X1, Y1, X2, Y2
   * Operasi Aritmatika Citra Ganda (Add, Subtract, Multiply, Divide)
   * Operasi Logika Citra Ganda (AND, OR, XOR, NOT)
3. **Enhancement (Peningkatan Kualitas Citra):**
   * Spatial Smoothing: Gaussian Filter, Average Filter, Median Filter, Bilateral Filter
   * Spatial Sharpening: Highpass, Highboost, Laplacian, Unsharp Masking
   * Perataan Kontras: Global Histogram Equalization & CLAHE
   * Visualisasi Modal Pop-up Grafik Distribusi Histogram
4. **Noise & Restoration:**
   * Pembangkitan Noise: Salt & Pepper, Gaussian, Rayleigh, Erlang, Exponential, Uniform
   * Filter Restorasi: Median Filter, Mean Filter, Gaussian Filter, Bilateral Filter dengan variasi ukuran kernel
5. **Edge Detection:**
   * Gradient Orde Pertama & Kedua: Canny, Sobel, Prewitt, Robert, Laplacian, LoG
   * Deteksi Kompas 8 Arah (Kirsch Compass)
   * Pengaturan arah gradien (Horizontal, Vertical, Magnitude) dan ambang histeresis
6. **Segmentation:**
   * Binarisasi: Manual Thresholding, Otsu's Auto Thresholding, Adaptive Mean, Adaptive Gaussian
   * Ekstraksi Kontur & Penghitungan Jumlah Objek (*Object Counting*)
   * Pelabelan Bounding Box persegi & Analisis Waktu Komputasi
7. **About:**
   * Informasi Tim Pengembang
   * Tautan Repositori GitHub & Video Tutorial YouTube

---

## 💻 Persyaratan Sistem & Instalasi

### 1. Kebutuhan Perangkat Lunak
* Python 3.10 atau versi lebih baru
* Modul dependensi:
  ```bash
  pip install flask pillow opencv-python numpy matplotlib
  ```

### 2. Cara Menjalankan Server Web
Buka terminal pada direktori proyek, lalu jalankan:
```bash
python web_app.py
```
Setelah server aktif, buka peramban (*browser*) Anda di:
👉 **http://127.0.0.1:5050**

---

## 📁 Struktur Direktori
```text
├── web_app.py                          # Server backend Flask & REST API pemrosesan citra
├── templates/
│   └── index.html                      # Antarmuka web responsif (HTML5, Modern CSS, Fetch API)
├── pcd_modules/                        # Pustaka algoritma pengolahan citra digital
│   ├── __init__.py
│   ├── basic_ops.py                    # Operasi dasar piksel, geometri, aritmatika, boolean
│   ├── enhancement.py                  # Penghalusan, penajaman, ekualisasi histogram
│   ├── noise.py                        # Pembangkitan noise & filter restorasi
│   ├── edge_detection.py               # Deteksi tepi gradient & kompas Kirsch
│   └── segmentation.py                 # Thresholding Otsu, kontur, bounding box
├── .gitignore                          # Konfigurasi file yang diabaikan Git
└── README.md                           # Dokumentasi resmi repositori
```
