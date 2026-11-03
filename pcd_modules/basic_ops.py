"""
Basic Operations Module (Operasi Dasar PCD)
Mengakomodasi:
- Brightness & Contrast
- Invert (Negative)
- Colouring (RGB, Grayscale, Binary, HSV, CMY, YUV, YIQ, Pseudo Color)
- Geometrics (Rotation, Flipping, Zooming, Cropping, Translation)
- Arithmetic (Add, Subtract, Multiply, Divide)
- Boolean (AND, OR, XOR, NOT)
"""

import cv2
import numpy as np


def adjust_brightness_contrast(img: np.ndarray, brightness: int = 0, contrast: float = 1.0) -> np.ndarray:
    """
    Menyesuaikan kecerahan dan kontras: Y = alpha * X + beta
    alpha = contrast (0.1 - 3.0)
    beta = brightness (-255 - 255)
    """
    return cv2.convertScaleAbs(img, alpha=contrast, beta=brightness)


def invert_image(img: np.ndarray) -> np.ndarray:
    """
    Membalik nilai intensitas piksel (Negative image): s = 255 - r
    """
    return cv2.bitwise_not(img)


def convert_colouring(img: np.ndarray, mode: str = "RGB") -> np.ndarray:
    """
    Konversi ruang warna (Colouring):
    - RGB, Grayscale, Binary, HSV, CMY, YUV, YIQ, Pseudo
    Semua output dikembalikan dalam format 3-channel uint8 (RGB) agar seragam ditampilkan di canvas GUI.
    """
    if img is None:
        return None

    # Pastikan citra berformat RGB 3-channel
    if len(img.shape) == 2:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    else:
        img_rgb = img.copy()

    mode = mode.upper().strip()

    if mode == "RGB":
        return img_rgb

    elif mode == "GRAYSCALE":
        gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)

    elif mode == "BINARY":
        gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
        return cv2.cvtColor(binary, cv2.COLOR_GRAY2RGB)

    elif mode == "HSV":
        # Konversi RGB -> HSV
        hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
        return hsv

    elif mode == "CMY":
        # CMY: C = 255 - R, M = 255 - G, Y = 255 - B
        cmy = 255 - img_rgb
        return cmy

    elif mode == "YUV":
        yuv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2YUV)
        return yuv

    elif mode == "YIQ":
        # Matriks transformasi NTSC standard:
        # [Y]   [0.299  0.587  0.114] [R]
        # [I] = [0.596 -0.274 -0.322] [G]
        # [Q]   [0.211 -0.523  0.312] [B]
        r = img_rgb[:, :, 0].astype(np.float32)
        g = img_rgb[:, :, 1].astype(np.float32)
        b = img_rgb[:, :, 2].astype(np.float32)

        y = 0.299 * r + 0.587 * g + 0.114 * b
        i = 0.596 * r - 0.274 * g - 0.322 * b
        q = 0.211 * r - 0.523 * g + 0.312 * b

        # Normalisasi ke 0-255 untuk visualisasi
        i_norm = np.clip(i + 128, 0, 255)
        q_norm = np.clip(q + 128, 0, 255)
        yiq_vis = np.stack([np.clip(y, 0, 255), i_norm, q_norm], axis=-1).astype(np.uint8)
        return yiq_vis

    elif mode == "PSEUDO":
        gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        pseudo = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
        return cv2.cvtColor(pseudo, cv2.COLOR_BGR2RGB)

    return img_rgb


def rotate_image(img: np.ndarray, angle: float = 0.0) -> np.ndarray:
    """
    Rotasi citra berdasarkan derajat sudut (clockwise).
    """
    if img is None:
        return None

    angle = float(angle) % 360
    if angle == 0:
        return img.copy()
    elif angle == 90:
        return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    elif angle == 180:
        return cv2.rotate(img, cv2.ROTATE_180)
    elif angle == 270:
        return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

    h, w = img.shape[:2]
    center = (w // 2, h // 2)
    m = cv2.getRotationMatrix2D(center, -angle, 1.0)
    return cv2.warpAffine(img, m, (w, h), borderMode=cv2.BORDER_REFLECT)


def flip_image(img: np.ndarray, mode: str = "No Flip") -> np.ndarray:
    """
    Pencerminan citra (Flip):
    - Horizontal, Vertical, Both
    """
    if img is None or mode == "No Flip" or mode == "None":
        return img.copy()

    if mode == "Horizontal":
        return cv2.flip(img, 1)
    elif mode == "Vertical":
        return cv2.flip(img, 0)
    elif mode == "Both":
        return cv2.flip(img, -1)
    return img.copy()


def zoom_image(img: np.ndarray, zoom_factor: float = 1.0) -> np.ndarray:
    """
    Zoom citra (scaling / resizing)
    """
    if img is None:
        return None

    if zoom_factor <= 0:
        zoom_factor = 1.0

    h, w = img.shape[:2]
    new_w = max(1, int(w * zoom_factor))
    new_h = max(1, int(h * zoom_factor))
    return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)


def crop_image(img: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> np.ndarray:
    """
    Memotong citra berdasarkan koordinat kotak pembatas (Bounding Box).
    """
    if img is None:
        return None

    h, w = img.shape[:2]
    # Sanitasi koordinat
    x_min = max(0, min(x1, x2))
    x_max = min(w, max(x1, x2))
    y_min = max(0, min(y1, y2))
    y_max = min(h, max(y1, y2))

    if x_max - x_min < 2 or y_max - y_min < 2:
        return img.copy()

    return img[y_min:y_max, x_min:x_max].copy()


def translate_image(img: np.ndarray, dx: int = 0, dy: int = 0) -> np.ndarray:
    """
    Translasi citra (pergeseran koordinat): x' = x + dx, y' = y + dy
    """
    if img is None:
        return None

    h, w = img.shape[:2]
    m = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(img, m, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))


def match_image_sizes(img1: np.ndarray, img2: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Memastikan citra 1 dan citra 2 memiliki dimensi yang sama sebelum operasi matriks.
    """
    if img1 is None or img2 is None:
        return img1, img2

    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]

    # Pastikan kedua citra 3-channel
    if len(img1.shape) == 2:
        img1 = cv2.cvtColor(img1, cv2.COLOR_GRAY2RGB)
    if len(img2.shape) == 2:
        img2 = cv2.cvtColor(img2, cv2.COLOR_GRAY2RGB)

    if (h1, w1) != (h2, w2):
        img2 = cv2.resize(img2, (w1, h1), interpolation=cv2.INTER_LINEAR)

    return img1, img2


def arithmetic_operation(img1: np.ndarray, img2: np.ndarray, op: str = "Add (+)", weight: float = 0.5) -> np.ndarray:
    """
    Operasi Aritmatika pada 2 Citra:
    - Add (+), Subtract (-), Multiply (*), Divide (/)
    """
    if img1 is None:
        return None
    if img2 is None:
        return img1.copy()

    i1, i2 = match_image_sizes(img1, img2)

    op_clean = op.lower()

    if "add" in op_clean:
        # Blended weighted addition: alpha * img1 + beta * img2
        alpha = weight
        beta = 1.0 - weight
        return cv2.addWeighted(i1, alpha, i2, beta, 0.0)

    elif "sub" in op_clean:
        # Pengurangan piksel
        return cv2.subtract(i1, i2)

    elif "mul" in op_clean:
        # Perkalian piksel ternormalisasi
        f1 = i1.astype(np.float32)
        f2 = i2.astype(np.float32)
        res = (f1 * f2) / 255.0
        return np.clip(res, 0, 255).astype(np.uint8)

    elif "div" in op_clean:
        # Pembagian piksel ternormalisasi
        f1 = i1.astype(np.float32)
        f2 = i2.astype(np.float32) + 1.0  # Hindari division by zero
        res = (f1 / f2) * 255.0
        return np.clip(res, 0, 255).astype(np.uint8)

    return i1.copy()


def boolean_operation(img1: np.ndarray, img2: np.ndarray, op: str = "AND") -> np.ndarray:
    """
    Operasi Logika Boolean:
    - AND, OR, XOR, NOT
    """
    if img1 is None:
        return None

    op_clean = op.upper().strip()

    if op_clean == "NOT":
        return cv2.bitwise_not(img1)

    if img2 is None:
        return img1.copy()

    i1, i2 = match_image_sizes(img1, img2)

    if op_clean == "AND":
        return cv2.bitwise_and(i1, i2)
    elif op_clean == "OR":
        return cv2.bitwise_or(i1, i2)
    elif op_clean == "XOR":
        return cv2.bitwise_xor(i1, i2)

    return i1.copy()

