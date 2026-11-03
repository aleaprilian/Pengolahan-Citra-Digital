"""
Enhancement Module (Peningkatan Kualitas Citra)
Mengakomodasi:
- Spatial Domain Smoothing: Gaussian Blur, Average/Mean Blur, Median Blur, Bilateral Filter
- Frequency Domain Smoothing: ILPF (Ideal Lowpass), BLPF (Butterworth Lowpass)
- Spatial Domain Sharpening: Laplacian, Unsharp Masking, Highpass, Highboost
- Frequency Domain Sharpening: IHPF (Ideal Highpass), BHPF (Butterworth Highpass)
- Histogram Equalization: Global Equalization, CLAHE
- Histogram Visualization
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt


def _get_frequency_filter(shape: tuple[int, int], cutoff: float, filter_type: str = "ILPF", order: int = 2) -> np.ndarray:
    """
    Helper untuk membangkitkan filter domain frekuensi 2D (ILPF, BLPF, IHPF, BHPF).
    """
    rows, cols = shape
    center_row, center_col = rows / 2.0, cols / 2.0

    u = np.arange(rows) - center_row
    v = np.arange(cols) - center_col
    v_grid, u_grid = np.meshgrid(v, u)

    # Jarak euclidean dari pusat D(u, v)
    d = np.sqrt(u_grid**2 + v_grid**2)
    cutoff = max(1.0, float(cutoff))

    filter_type = filter_type.upper().strip()

    if "ILPF" in filter_type:
        h = np.zeros((rows, cols), dtype=np.float32)
        h[d <= cutoff] = 1.0
    elif "BLPF" in filter_type:
        h = 1.0 / (1.0 + (d / cutoff)**(2 * order))
    elif "IHPF" in filter_type:
        h = np.ones((rows, cols), dtype=np.float32)
        h[d <= cutoff] = 0.0
    elif "BHPF" in filter_type:
        h = 1.0 / (1.0 + (cutoff / (d + 1e-6))**(2 * order))
    else:
        h = np.ones((rows, cols), dtype=np.float32)

    return h


def apply_frequency_filter(img: np.ndarray, filter_name: str = "ILPF", cutoff: float = 30.0, order: int = 2) -> np.ndarray:
    """
    Menerapkan transformasi Fourier (2D FFT) + Filter Frekuensi + IFFT.
    """
    if img is None:
        return None

    # Proses per channel untuk citra RGB
    is_color = len(img.shape) == 3 and img.shape[2] == 3
    channels = cv2.split(img) if is_color else [img]

    processed_channels = []
    rows, cols = channels[0].shape
    h_filter = _get_frequency_filter((rows, cols), cutoff, filter_name, order)

    for ch in channels:
        f = np.fft.fft2(ch.astype(np.float32))
        fshift = np.fft.fftshift(f)
        fshift_filtered = fshift * h_filter
        f_ishift = np.fft.ifftshift(fshift_filtered)
        img_back = np.fft.ifft2(f_ishift)
        img_back = np.abs(img_back)
        processed_channels.append(np.clip(img_back, 0, 255).astype(np.uint8))

    if is_color:
        return cv2.merge(processed_channels)
    return processed_channels[0]


def apply_filtering(img: np.ndarray, method: str = "Gaussian Filter", kernel_size: int = 3, sigma: float = 1.0) -> np.ndarray:
    """
    Penerapan Penghalusan Citra (Smoothing / Blurring):
    - Gaussian Filter
    - Average Filter (Mean Blur)
    - Median Filter
    - Bilateral Filter
    - ILPF (Frequency Domain)
    - BLPF (Frequency Domain)
    """
    if img is None:
        return None

    # Pastikan kernel ganjil positif
    k = max(3, int(kernel_size))
    if k % 2 == 0:
        k += 1

    method_clean = method.lower()

    if "gaussian" in method_clean:
        s = max(0.1, float(sigma))
        return cv2.GaussianBlur(img, (k, k), s)

    elif "average" in method_clean or "mean" in method_clean:
        return cv2.blur(img, (k, k))

    elif "median" in method_clean:
        return cv2.medianBlur(img, k)

    elif "bilateral" in method_clean:
        s_val = max(10.0, float(sigma) * 5.0)
        return cv2.bilateralFilter(img, d=k, sigmaColor=s_val, sigmaSpace=s_val)

    elif "ilpf" in method_clean:
        return apply_frequency_filter(img, "ILPF", cutoff=float(sigma) * 2.0)

    elif "blpf" in method_clean:
        return apply_frequency_filter(img, "BLPF", cutoff=float(sigma) * 2.0)

    return img.copy()


def apply_sharpening(img: np.ndarray, method: str = "Laplacian", strength: float = 1.5) -> np.ndarray:
    """
    Penerapan Penajaman Citra (Sharpening):
    - Laplacian
    - Unsharp Masking
    - Highpass Spatial
    - Highboost Spatial
    - IHPF (Frequency Domain)
    - BHPF (Frequency Domain)
    """
    if img is None:
        return None

    strength = max(0.1, float(strength))
    method_clean = method.lower()

    if "laplacian" in method_clean:
        # Kernel Laplacian 3x3 standar
        kernel = np.array([
            [0, -1, 0],
            [-1, 4 + strength, -1],
            [0, -1, 0]
        ], dtype=np.float32)
        # Normalisasi kernel bila perlu
        kernel_sum = np.sum(kernel)
        if kernel_sum > 0:
            kernel = kernel / kernel_sum
        return cv2.filter2D(img, -1, kernel)

    elif "unsharp" in method_clean:
        # Unsharp masking: Sharp = Original + Strength * (Original - Blurred)
        blurred = cv2.GaussianBlur(img, (5, 5), 1.0)
        sharp = cv2.addWeighted(img, 1.0 + strength, blurred, -strength, 0.0)
        return sharp

    elif "highpass" in method_clean:
        kernel = np.array([
            [-1, -1, -1],
            [-1, 8, -1],
            [-1, -1, -1]
        ], dtype=np.float32)
        highpass = cv2.filter2D(img, cv2.CV_32F, kernel)
        res = img.astype(np.float32) + strength * highpass
        return np.clip(res, 0, 255).astype(np.uint8)

    elif "highboost" in method_clean:
        # Highboost: A * Original - Lowpass = (A - 1)*Original + Highpass
        # A = 1.0 + strength
        blurred = cv2.GaussianBlur(img, (5, 5), 1.0)
        highboost = cv2.addWeighted(img, 1.0 + strength, blurred, -1.0, 0.0)
        return highboost

    elif "ihpf" in method_clean:
        return apply_frequency_filter(img, "IHPF", cutoff=strength * 20.0)

    elif "bhpf" in method_clean:
        return apply_frequency_filter(img, "BHPF", cutoff=strength * 20.0)

    return img.copy()


def apply_equalization(img: np.ndarray, method: str = "Global") -> np.ndarray:
    """
    Ekualisasi Histogram (Perataan Kontras):
    - Global Equalization (cv2.equalizeHist)
    - CLAHE (Contrast Limited Adaptive Histogram Equalization)
    Mendukung citra Grayscale maupun Citra Berwarna (RGB melalui YCrCb channel Y).
    """
    if img is None:
        return None

    is_gray = len(img.shape) == 2 or (len(img.shape) == 3 and img.shape[2] == 1)
    method_clean = method.lower()

    if is_gray:
        gray = img if len(img.shape) == 2 else img[:, :, 0]
        if "clahe" in method_clean:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            res = clahe.apply(gray)
        else:
            res = cv2.equalizeHist(gray)
        return cv2.cvtColor(res, cv2.COLOR_GRAY2RGB)

    else:
        # Citra Berwarna: Konversi ke YCrCb agar warna asli tidak rusak
        ycrcb = cv2.cvtColor(img, cv2.COLOR_RGB2YCrCb)
        y, cr, cb = cv2.split(ycrcb)

        if "clahe" in method_clean:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            y_eq = clahe.apply(y)
        else:
            y_eq = cv2.equalizeHist(y)

        ycrcb_eq = cv2.merge([y_eq, cr, cb])
        return cv2.cvtColor(ycrcb_eq, cv2.COLOR_YCrCb2RGB)


def show_histogram_dialog(original_img: np.ndarray, processed_img: np.ndarray = None, parent=None):
    """
    Menampilkan plot histogram komparatif sebelum dan sesudah ekualisasi menggunakan Matplotlib.
    """
    if original_img is None:
        return

    plt.figure("Analisis Plot Histogram PCD", figsize=(10, 5))
    plt.clf()

    if processed_img is not None:
        plt.subplot(1, 2, 1)
        plt.title("Histogram Citra Asli (Original)")
        plt.xlabel("Intensitas Piksel (0-255)")
        plt.ylabel("Frekuensi")
        if len(original_img.shape) == 3 and original_img.shape[2] == 3:
            colors = ('r', 'g', 'b')
            for i, col in enumerate(colors):
                hist = cv2.calcHist([original_img], [i], None, [256], [0, 256])
                plt.plot(hist, color=col, label=f'Channel {col.upper()}')
            plt.legend(loc="upper right")
        else:
            hist = cv2.calcHist([original_img], [0], None, [256], [0, 256])
            plt.plot(hist, color='black')
        plt.xlim([0, 256])
        plt.grid(True, linestyle="--", alpha=0.5)

        plt.subplot(1, 2, 2)
        plt.title("Histogram Citra Hasil (Processed)")
        plt.xlabel("Intensitas Piksel (0-255)")
        plt.ylabel("Frekuensi")
        if len(processed_img.shape) == 3 and processed_img.shape[2] == 3:
            colors = ('r', 'g', 'b')
            for i, col in enumerate(colors):
                hist = cv2.calcHist([processed_img], [i], None, [256], [0, 256])
                plt.plot(hist, color=col, label=f'Channel {col.upper()}')
            plt.legend(loc="upper right")
        else:
            hist = cv2.calcHist([processed_img], [0], None, [256], [0, 256])
            plt.plot(hist, color='black')
        plt.xlim([0, 256])
        plt.grid(True, linestyle="--", alpha=0.5)

    else:
        plt.title("Histogram Citra")
        plt.xlabel("Intensitas Piksel (0-255)")
        plt.ylabel("Frekuensi")
        if len(original_img.shape) == 3 and original_img.shape[2] == 3:
            colors = ('r', 'g', 'b')
            for i, col in enumerate(colors):
                hist = cv2.calcHist([original_img], [i], None, [256], [0, 256])
                plt.plot(hist, color=col, label=f'Channel {col.upper()}')
            plt.legend(loc="upper right")
        else:
            hist = cv2.calcHist([original_img], [0], None, [256], [0, 256])
            plt.plot(hist, color='black')
        plt.xlim([0, 256])
        plt.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.show()

