# Aplikasi Pengolahan Citra Digital (Desktop GUI)

Aplikasi desktop GUI interaktif untuk mata kuliah **Pengolahan Citra Digital (PCD)** yang dibangun menggunakan Python, Tkinter, dan Pillow. Aplikasi ini mendukung visualisasi komparatif citra (mode tunggal dan ganda), manipulasi piksel, perbaikan kualitas citra, analisis noise & restorasi, deteksi tepi, hingga segmentasi citra.

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

Aplikasi dirancang dengan mengacu pada panduan praktikum dan wireframe UI yang mencakup 7 menu utama:

1. **File:**
   * Open / Browse File Citra Utama
   * Open Secondary Image (untuk operasi Aritmatika & Boolean)
   * Save & Save As citra hasil olahan
   * Exit
2. **Basic Operation (Operasi Dasar & Mode Dual Canvas):**
   * Pengaturan Kecerahan (*Brightness*) & Kontras (*Contrast*)
   * Inversi Warna (*Negative*)
   * Konversi Ruang Warna (RGB, Grayscale, Binary, HSV, CMY, YUV, YIQ, Pseudo Color)
   * Transformasi Geometri (Rotasi, Flip Horizontal/Vertikal, Zooming, dan Interactive Crop on Canvas)
   * Operasi Aritmatika Citra Ganda (Add, Subtract, Multiply, Divide)
   * Operasi Logika Citra Ganda (AND, OR, XOR, NOT)
3. **Enhancement (Peningkatan Kualitas Citra):**
   * Spatial Smoothing: Gaussian Filter, Average Filter, Median Filter, Bilateral Filter
   * Frequency Domain Smoothing: ILPF (Ideal Lowpass), BLPF (Butterworth Lowpass)
   * Spatial Sharpening: Highpass, Highboost, Laplacian, Unsharp Masking
   * Frequency Domain Sharpening: IHPF (Ideal Highpass), BHPF (Butterworth Highpass)
   * Perataan Kontras: Global Histogram Equalization & CLAHE
   * Visualisasi Grafik Distribusi Histogram
4. **Noise & Restoration:**
   * Pembangkitan Noise: Gaussian, Rayleigh, Erlang (Gamma), Exponential, Uniform, Salt & Pepper (Impulse)
   * Filter Restorasi: Median Filter, Mean Filter, Gaussian Filter, Bilateral Filter dengan variasi ukuran kernel
5. **Edge Detection:**
   * Gradient Orde Pertama: Sobel, Prewitt, Robert
   * Gradient Orde Kedua: Laplacian, Laplacian of Gaussian (LoG), Canny
   * Deteksi Kompas 8 Arah (Kirsch Compass)
6. **Segmentation:**
   * Binarisasi: Manual Thresholding, Otsu's Auto Thresholding, Adaptive Thresholding
   * Ekstraksi Kontur & Penghitungan Jumlah Objek (*Object Counting*)
   * Pelabelan Bounding Box & Analisis Waktu Eksekusi
7. **About:**
   * Informasi Tim Pengembang
   * Tautan Repositori GitHub & Video Tutorial YouTube

---

## 💻 Persyaratan Sistem & Instalasi

### 1. Kebutuhan Perangkat Lunak
* Python 3.10 atau versi lebih baru
* Modul dependensi:
  ```bash
  pip install pillow opencv-python numpy matplotlib
  ```

### 2. Cara Menjalankan Aplikasi
Buka terminal pada direktori proyek, lalu jalankan:
```bash
python main.py
```
Atau dapat dijalankan melalui Jupyter Notebook pada sel Bagian D di:
```bash
GUI_app.ipynb
```

---

## 📁 Struktur Direktori
```text
├── main.py                             # File utama aplikasi desktop GUI (Tkinter & Pillow)
├── GUI_app.ipynb                       # Notebook panduan praktikum & testing modul
├── pcd_modules/                        # Modul algoritma pengolahan citra digital
│   ├── __init__.py
│   ├── basic_ops.py                    # Operasi dasar piksel, geometri, aritmatika, boolean
│   ├── enhancement.py                  # Penghalusan, penajaman, ekualisasi histogram
│   ├── noise.py                        # Pembangkitan noise & filter restorasi
│   ├── edge_detection.py               # Deteksi tepi gradient & kompas Kirsch
│   └── segmentation.py                 # Thresholding Otsu, kontur, bounding box
├── .gitignore                          # Konfigurasi file yang diabaikan Git
└── README.md                           # Dokumentasi proyek
```

