"""
Edge Detection Module (Deteksi Tepi & Garis Kontur Struktural)
Mengakomodasi:
- 1'st Differential Gradient: Sobel, Prewitt, Robert
- 2'nd Differential Gradient: Laplacian, Laplacian of Gaussian (LoG), Canny
- Compass Edge Detection (8 Direction Compass: N, NE, E, SE, S, SW, W, NW)
"""

import cv2
import numpy as np


def detect_edges(
    img: np.ndarray,
    operator: str = "Canny",
    direction: str = "Magnitude",
    lower_thresh: int = 10,
    upper_thresh: int = 50,
    ksize: int = 3
) -> np.ndarray:
    """
    Mengekstraksi garis tepi objek:
    - operator: Canny, Sobel, Prewitt, Robert, Laplacian, LoG, Compass
    - direction: Horizontal, Vertical, Magnitude (Combined)
    - lower_thresh & upper_thresh: Ambang batas histeresis Canny
    - ksize: Ukuran kernel aperture (1, 3, 5, 7)
    """
    if img is None:
        return None

    # Pastikan citra berformat Grayscale 1-channel untuk komputasi gradien
    if len(img.shape) == 3 and img.shape[2] == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        gray = img.copy()

    # Kernel size sanitasi (harus 1, 3, 5, 7)
    k = max(1, int(ksize))
    if k % 2 == 0:
        k += 1

    op_clean = operator.lower()
    dir_clean = direction.lower()

    if "canny" in op_clean:
        # Canny edge detector: threshold1 = lower, threshold2 = upper
        t_low = min(lower_thresh, upper_thresh)
        t_high = max(lower_thresh, upper_thresh)
        edges = cv2.Canny(gray, threshold1=t_low, threshold2=t_high, apertureSize=min(7, max(3, k)))
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)

    elif "sobel" in op_clean:
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=k)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=k)

        if "horiz" in dir_clean:
            grad = np.abs(sobel_x)
        elif "vert" in dir_clean:
            grad = np.abs(sobel_y)
        else:
            grad = cv2.magnitude(sobel_x, sobel_y)

        edges = np.uint8(np.clip(grad, 0, 255))
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)

    elif "prewitt" in op_clean:
        # Prewitt Kernel 3x3
        kernel_x = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float32)
        kernel_y = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], dtype=np.float32)

        prewitt_x = cv2.filter2D(gray.astype(np.float32), -1, kernel_x)
        prewitt_y = cv2.filter2D(gray.astype(np.float32), -1, kernel_y)

        if "horiz" in dir_clean:
            grad = np.abs(prewitt_x)
        elif "vert" in dir_clean:
            grad = np.abs(prewitt_y)
        else:
            grad = np.sqrt(prewitt_x**2 + prewitt_y**2)

        edges = np.uint8(np.clip(grad, 0, 255))
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)

    elif "robert" in op_clean:
        # Roberts Cross 2x2
        kernel_x = np.array([[1, 0], [0, -1]], dtype=np.float32)
        kernel_y = np.array([[0, 1], [-1, 0]], dtype=np.float32)

        robert_x = cv2.filter2D(gray.astype(np.float32), -1, kernel_x)
        robert_y = cv2.filter2D(gray.astype(np.float32), -1, kernel_y)

        if "horiz" in dir_clean:
            grad = np.abs(robert_x)
        elif "vert" in dir_clean:
            grad = np.abs(robert_y)
        else:
            grad = np.sqrt(robert_x**2 + robert_y**2)

        edges = np.uint8(np.clip(grad, 0, 255))
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)

    elif "laplacian" in op_clean and "gaussian" not in op_clean and "log" not in op_clean:
        # 2nd derivative Laplacian
        lap = cv2.Laplacian(gray, cv2.CV_64F, ksize=min(7, max(1, k)))
        edges = np.uint8(np.clip(np.abs(lap), 0, 255))
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)

    elif "log" in op_clean or "gaussian" in op_clean:
        # Laplacian of Gaussian (LoG)
        blurred = cv2.GaussianBlur(gray, (5, 5), 1.0)
        lap = cv2.Laplacian(blurred, cv2.CV_64F, ksize=min(7, max(1, k)))
        edges = np.uint8(np.clip(np.abs(lap), 0, 255))
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)

    elif "compass" in op_clean:
        # Kirsch Compass Masks (8 arah mata angin: N, NW, W, SW, S, SE, E, NE)
        kirsch_masks = [
            np.array([[-3, -3, 5], [-3, 0, 5], [-3, -3, 5]], dtype=np.float32),   # East
            np.array([[-3, 5, 5], [-3, 0, 5], [-3, -3, -3]], dtype=np.float32),  # North-East
            np.array([[5, 5, 5], [-3, 0, -3], [-3, -3, -3]], dtype=np.float32),   # North
            np.array([[5, 5, -3], [5, 0, -3], [-3, -3, -3]], dtype=np.float32),  # North-West
            np.array([[5, -3, -3], [5, 0, -3], [5, -3, -3]], dtype=np.float32),   # West
            np.array([[-3, -3, -3], [5, 0, -3], [5, 5, -3]], dtype=np.float32),  # South-West
            np.array([[-3, -3, -3], [-3, 0, -3], [5, 5, 5]], dtype=np.float32),   # South
            np.array([[-3, -3, -3], [-3, 0, 5], [-3, 5, 5]], dtype=np.float32),  # South-East
        ]
        responses = [cv2.filter2D(gray.astype(np.float32), -1, mask) for mask in kirsch_masks]
        max_response = np.max(np.array(responses), axis=0)
        edges = np.uint8(np.clip(max_response, 0, 255))
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)

    return cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)

