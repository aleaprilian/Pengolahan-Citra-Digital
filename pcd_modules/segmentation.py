"""
Segmentation Module (Segmentasi Citra Biner, Kontur, & Analisis Objek)
Mengakomodasi:
- Thresholding: Manual, Otsu's Thresholding, Adaptive Mean, Adaptive Gaussian
- Threshold Types: THRESH_BINARY, THRESH_BINARY_INV
- Contour Extraction: cv2.findContours, cv2.drawContours
- Contour Hierarchy: RETR_EXTERNAL, RETR_TREE
- Bounding Box Marking: cv2.boundingRect
- Object Count & Execution Time Analytics
"""

import time
import cv2
import numpy as np


COLOR_MAP = {
    "GREEN": (0, 255, 0),
    "RED": (255, 0, 0),
    "BLUE": (0, 0, 255),
    "YELLOW": (255, 255, 0),
    "CYAN": (0, 255, 255),
    "MAGENTA": (255, 0, 255),
    "WHITE": (255, 255, 255)
}


def segment_and_analyze(
    img: np.ndarray,
    binary_method: str = "Otsu",
    thresh_type: str = "Thresh Binary",
    thresh_val: int = 128,
    draw_contours: bool = True,
    contour_color_name: str = "Green",
    retrieval_mode_name: str = "RETR External",
    line_thickness: int = 2,
    draw_bounding_boxes: bool = True
) -> tuple[np.ndarray, int, int, float]:
    """
    Menjalankan proses segmentasi biner, ekstraksi kontur, dan analisis kuantitatif objek.
    Mengembalikan: (result_image, optimal_threshold, object_count, execution_time_ms)
    """
    if img is None:
        return None, 0, 0, 0.0

    start_time = time.perf_counter()

    # Pastikan citra berformat RGB untuk visualisasi garis kontur berwarna
    if len(img.shape) == 2:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        gray = img.copy()
    else:
        img_rgb = img.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Pra-pembersihan noise halus dengan Gaussian Blur agar kontur tidak cacat
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Tentukan Tipe Threshold
    is_inv = "inv" in thresh_type.lower()
    cv_thresh_type = cv2.THRESH_BINARY_INV if is_inv else cv2.THRESH_BINARY

    method_clean = binary_method.lower()
    optimal_thresh_val = thresh_val

    # 1. Tahap Binerisasi
    if "otsu" in method_clean:
        opt_t, binary = cv2.threshold(blurred, 0, 255, cv_thresh_type + cv2.THRESH_OTSU)
        optimal_thresh_val = int(opt_t)

    elif "adaptive" in method_clean:
        adaptive_method = cv2.ADAPTIVE_THRESH_GAUSSIAN_C if "gauss" in method_clean else cv2.ADAPTIVE_THRESH_MEAN_C
        binary = cv2.adaptiveThreshold(blurred, 255, adaptive_method, cv_thresh_type, 11, 2)
        optimal_thresh_val = int(np.mean(blurred))

    else:
        # Manual Thresholding
        t_val = max(0, min(255, int(thresh_val)))
        optimal_thresh_val = t_val
        _, binary = cv2.threshold(blurred, t_val, 255, cv_thresh_type)

    # Buat salinan kanvas hasil untuk digambar kontur
    output_img = img_rgb.copy()

    # 2. Tahap Ekstraksi Kontur
    object_count = 0
    if draw_contours or draw_bounding_boxes:
        mode = cv2.RETR_TREE if "tree" in retrieval_mode_name.lower() else cv2.RETR_EXTERNAL
        # Untuk kontur, cari komponen putih pada latar hitam
        # Jika binary_inv dipilih, binary sudah putih pada objek.
        contours, _ = cv2.findContours(binary, mode, cv2.CHAIN_APPROX_SIMPLE)

        # Filter kontur yang memiliki area minimal agar noise piksel tunggal tidak dihitung
        valid_contours = [c for c in contours if cv2.contourArea(c) > 25]
        object_count = len(valid_contours)

        # Ambil kode warna RGB
        col_rgb = COLOR_MAP.get(contour_color_name.upper().strip(), (0, 255, 0))
        thickness = max(1, min(10, int(line_thickness)))

        if draw_contours and object_count > 0:
            cv2.drawContours(output_img, valid_contours, -1, col_rgb, thickness)

        if draw_bounding_boxes and object_count > 0:
            for cnt in valid_contours:
                x, y, w, h = cv2.boundingRect(cnt)
                # Gambar kotak pembatas berwarna biru muda / cyan
                cv2.rectangle(output_img, (x, y), (x + w, y + h), (0, 180, 255), max(1, thickness - 1))

    else:
        # Jika kontur tidak diaktifkan, tampilkan citra biner hitam-putih
        output_img = cv2.cvtColor(binary, cv2.COLOR_GRAY2RGB)

    end_time = time.perf_counter()
    execution_time_ms = round((end_time - start_time) * 1000.0, 1)

    return output_img, optimal_thresh_val, object_count, execution_time_ms

