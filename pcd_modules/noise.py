"""
Noise & Restoration Module (Pembangkitan Derau & Pemulihan Citra)
Mengakomodasi:
- Noise Generation:
  1. Salt & Pepper (Impulse Noise)
  2. Gaussian Noise
  3. Rayleigh Noise
  4. Erlang (Gamma) Noise
  5. Exponential Noise
  6. Uniform Noise
- Noise Restoration (Denoising Filters):
  1. Median Filter
  2. Mean / Average Filter
  3. Gaussian Filter
  4. Bilateral Filter
"""

import cv2
import numpy as np


def generate_noise(img: np.ndarray, noise_type: str = "Salt & Pepper", ratio: float = 0.05) -> np.ndarray:
    """
    Menambahkan derau matematis ke dalam citra:
    - Salt & Pepper, Gaussian, Rayleigh, Erlang (Gamma), Exponential, Uniform
    ratio mengontrol intensitas / densitas derau (0.01 - 0.50).
    """
    if img is None:
        return None

    noisy = img.copy().astype(np.float32)
    noise_clean = noise_type.lower()
    ratio = max(0.001, min(1.0, float(ratio)))

    if "salt" in noise_clean or "pepper" in noise_clean or "impulse" in noise_clean:
        # Salt and Pepper Noise
        h, w = img.shape[:2]
        num_pixels = int(ratio * h * w)

        # Pepper (hitam / 0)
        num_pepper = num_pixels // 2
        coords_y = np.random.randint(0, h, num_pepper)
        coords_x = np.random.randint(0, w, num_pepper)
        noisy[coords_y, coords_x] = 0

        # Salt (putih / 255)
        num_salt = num_pixels - num_pepper
        coords_y = np.random.randint(0, h, num_salt)
        coords_x = np.random.randint(0, w, num_salt)
        noisy[coords_y, coords_x] = 255

        return np.clip(noisy, 0, 255).astype(np.uint8)

    elif "gaussian" in noise_clean:
        # Gaussian Noise: N(mean=0, sigma)
        sigma = ratio * 100.0
        gauss = np.random.normal(0, sigma, img.shape)
        noisy = noisy + gauss
        return np.clip(noisy, 0, 255).astype(np.uint8)

    elif "rayleigh" in noise_clean:
        # Rayleigh Noise: scale
        scale = ratio * 50.0
        rayleigh = np.random.rayleigh(scale=scale, size=img.shape)
        noisy = noisy + rayleigh - (scale * np.sqrt(np.pi / 2))
        return np.clip(noisy, 0, 255).astype(np.uint8)

    elif "erlang" in noise_clean or "gamma" in noise_clean:
        # Erlang / Gamma Noise: shape k=2, scale theta
        scale = ratio * 25.0
        gamma = np.random.gamma(shape=2.0, scale=scale, size=img.shape)
        noisy = noisy + gamma - (2.0 * scale)
        return np.clip(noisy, 0, 255).astype(np.uint8)

    elif "exponential" in noise_clean:
        # Exponential Noise: scale
        scale = ratio * 40.0
        expo = np.random.exponential(scale=scale, size=img.shape)
        noisy = noisy + expo - scale
        return np.clip(noisy, 0, 255).astype(np.uint8)

    elif "uniform" in noise_clean:
        # Uniform Noise: U(-a, a)
        a = ratio * 80.0
        uniform = np.random.uniform(-a, a, img.shape)
        noisy = noisy + uniform
        return np.clip(noisy, 0, 255).astype(np.uint8)

    return img.copy()


def restore_noise(img: np.ndarray, method: str = "Median Filter", kernel_size: int = 3) -> np.ndarray:
    """
    Merestorasi / mereduksi derau menggunakan filter spasial:
    - Median Filter (Paling efektif mengatasi Salt & Pepper)
    - Mean / Average Filter
    - Gaussian Filter
    - Bilateral Filter
    """
    if img is None:
        return None

    k = max(3, int(kernel_size))
    if k % 2 == 0:
        k += 1

    method_clean = method.lower()

    if "median" in method_clean:
        return cv2.medianBlur(img, k)

    elif "mean" in method_clean or "average" in method_clean:
        return cv2.blur(img, (k, k))

    elif "gaussian" in method_clean:
        return cv2.GaussianBlur(img, (k, k), 0)

    elif "bilateral" in method_clean:
        return cv2.bilateralFilter(img, d=k, sigmaColor=75, sigmaSpace=75)

    return img.copy()

