import os
import io
import time
import base64
import socket
from flask import Flask, render_template, request, jsonify
from PIL import Image
import numpy as np
import cv2

# Import algoritma langsung dari modul pcd_modules yang ada
from pcd_modules.basic_ops import (
    adjust_brightness_contrast,
    invert_image,
    convert_colouring,
    rotate_image,
    flip_image,
    zoom_image,
    crop_image,
    arithmetic_operation,
    boolean_operation
)
from pcd_modules.enhancement import (
    apply_filtering,
    apply_sharpening,
    apply_equalization,
    apply_frequency_filter
)
from pcd_modules.noise import generate_noise, restore_noise
from pcd_modules.edge_detection import detect_edges
from pcd_modules.segmentation import segment_and_analyze

app = Flask(__name__)
app.config["SECRET_KEY"] = "pcd-secret-key-2026"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # Maksimum upload 16MB


def b64_to_rgb_array(b64_str: str) -> np.ndarray:
    """Mengubah string data URL base64 menjadi array NumPy RGB uint8"""
    if not b64_str:
        return None
    if "," in b64_str:
        b64_str = b64_str.split(",")[1]
    img_bytes = base64.b64decode(b64_str)
    pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    return np.array(pil_img, dtype=np.uint8)


def rgb_array_to_b64(img_arr: np.ndarray, format: str = "PNG") -> str:
    """Mengubah array NumPy RGB uint8 menjadi string base64 data URL"""
    if img_arr is None:
        return ""
    if len(img_arr.shape) == 2:
        img_arr = cv2.cvtColor(img_arr, cv2.COLOR_GRAY2RGB)
    pil_img = Image.fromarray(img_arr)
    buf = io.BytesIO()
    pil_img.save(buf, format=format)
    encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/{format.lower()};base64,{encoded}"


@app.route("/")
def index():
    """Halaman antarmuka web utama PCD"""
    return render_template("index.html")


@app.route("/api/process", methods=["POST"])
def process_image():
    """Endpoint pemrosesan citra interaktif via AJAX Fetch"""
    data = request.get_json() or {}
    tab = data.get("tab", "basic")
    img_b64 = data.get("image")
    sec_img_b64 = data.get("secondary_image")
    params = data.get("params", {})

    if not img_b64:
        return jsonify({"success": False, "error": "Citra utama belum dimuat!"}), 400

    try:
        start_time = time.time()
        img = b64_to_rgb_array(img_b64)
        result = img.copy()
        info_detail = ""

        # ----------------------------------------------------------------------
        # 1. TAB: BASIC OPERATION
        # ----------------------------------------------------------------------
        if tab == "basic":
            bright = int(params.get("brightness", 0))
            contrast = float(params.get("contrast", 1.0))
            colouring = params.get("colouring", "RGB")
            rotate_str = params.get("rotate", "No Rotate")
            flip_str = params.get("flip", "No Flip")
            do_invert = bool(params.get("invert", False))
            arith = params.get("arithmetic", "None")
            bool_op = params.get("boolean", "None")

            # A. Kecerahan & Kontras
            if bright != 0 or contrast != 1.0:
                result = adjust_brightness_contrast(result, brightness=bright, contrast=contrast)

            # B. Invert (Negative)
            if do_invert:
                result = invert_image(result)

            # C. Colouring
            if colouring != "RGB":
                result = convert_colouring(result, mode=colouring)

            # D. Rotasi & Flip
            angle_map = {"No Rotate": 0, "90° CW": 90, "180°": 180, "270° CW": 270}
            angle = angle_map.get(rotate_str, 0)
            if angle != 0:
                result = rotate_image(result, angle=angle)

            if flip_str != "No Flip":
                result = flip_image(result, mode=flip_str)

            # E. Crop (Pemotongan)
            try:
                x1 = int(params.get("crop_x1", ""))
                y1 = int(params.get("crop_y1", ""))
                x2 = int(params.get("crop_x2", ""))
                y2 = int(params.get("crop_y2", ""))
                if (x2 > x1) and (y2 > y1) and (x1 > 0 or y1 > 0 or x2 < result.shape[1] or y2 < result.shape[0]):
                    result = crop_image(result, x1, y1, x2, y2)
                    info_detail += f"Crop: ({x1},{y1})-({x2},{y2}) | "
            except Exception:
                pass

            # F. Operasi Citra Ganda (Aritmatika & Boolean)
            if sec_img_b64 and (arith != "None" or bool_op != "None"):
                sec_img = b64_to_rgb_array(sec_img_b64)
                if arith != "None":
                    result = arithmetic_operation(result, sec_img, op=arith)
                    info_detail += f"Arithmetic: {arith} | "
                if bool_op != "None":
                    result = boolean_operation(result, sec_img, op=bool_op)
                    info_detail += f"Boolean: {bool_op} | "

            info_detail += f"Brightness: {bright:+d}, Contrast: {contrast:.1f}x, Color: {colouring}"

        # ----------------------------------------------------------------------
        # 2. TAB: ENHANCEMENT
        # ----------------------------------------------------------------------
        elif tab == "enhancement":
            method = params.get("filter_method", "None")
            ksize_str = params.get("kernel_size", "3x3")
            ksize = int(ksize_str.split("x")[0]) if "x" in ksize_str else 3
            sigma = float(params.get("sigma", 1.5))
            sharp = params.get("sharpening", "None")
            strength = float(params.get("strength", 1.5))
            equalize = params.get("equalization", "None")

            # Spatial Smoothing
            if method != "None":
                result = apply_filtering(result, method=method, kernel_size=ksize, sigma=sigma)

            # Spatial Sharpening
            if sharp != "None":
                result = apply_sharpening(result, method=sharp, strength=strength)

            # Equalization
            if equalize != "None":
                result = apply_equalization(result, method=equalize)

            info_detail = f"Filter: {method} ({ksize}x{ksize}), Sharpen: {sharp}, Equalize: {equalize}"

        # ----------------------------------------------------------------------
        # 3. TAB: NOISE
        # ----------------------------------------------------------------------
        elif tab == "noise":
            noise_type = params.get("noise_type", "None")
            ratio = float(params.get("noise_ratio", 0.05))
            resto = params.get("restoration", "None")
            ksize_str = params.get("kernel_size", "3x3")
            ksize = int(ksize_str.split("x")[0]) if "x" in ksize_str else 3

            if noise_type != "None":
                result = generate_noise(result, noise_type=noise_type, ratio=ratio)
            if resto != "None":
                result = restore_noise(result, method=resto, kernel_size=ksize)

            info_detail = f"Noise: {noise_type} ({ratio:.2f}), Resto: {resto} ({ksize}x{ksize})"

        # ----------------------------------------------------------------------
        # 4. TAB: EDGE DETECTION
        # ----------------------------------------------------------------------
        elif tab == "edge":
            op = params.get("operator", "Canny")
            direction = params.get("direction", "Horizontal")
            ksize_str = params.get("kernel_size", "3x3")
            ksize = int(ksize_str.split("x")[0]) if "x" in ksize_str else 3
            low_t = int(params.get("lower_thresh", 10))
            up_t = int(params.get("upper_thresh", 50))

            result = detect_edges(
                result,
                operator=op,
                direction=direction,
                lower_thresh=low_t,
                upper_thresh=up_t,
                ksize=ksize
            )
            info_detail = f"Edge Detection: {op} ({direction}, Kernel: {ksize}x{ksize})"

        # ----------------------------------------------------------------------
        # 5. TAB: SEGMENTATION
        # ----------------------------------------------------------------------
        elif tab == "segmentation":
            method = params.get("method", "Manual")
            thresh_val = int(params.get("thresh_val", 50))
            thresh_type = params.get("thresh_type", "Thresh Binary")
            contour_col = params.get("contour_color", "Green")
            draw_cnt = bool(params.get("draw_contours", True))
            thickness = int(params.get("line_thickness", 2))
            retrieval = params.get("retrieval_mode", "RETR External")
            draw_bb = bool(params.get("draw_bb", True))

            result, opt_thresh, count, ms = segment_and_analyze(
                result,
                binary_method=method,
                thresh_type=thresh_type,
                thresh_val=thresh_val,
                draw_contours=draw_cnt,
                contour_color_name=contour_col,
                retrieval_mode_name=retrieval,
                line_thickness=thickness,
                draw_bounding_boxes=draw_bb
            )
            info_detail = f"Result: {method} T = {opt_thresh} | Detected: {count} Objects"

        elapsed_ms = int((time.time() - start_time) * 1000)
        h, w = result.shape[:2]

        return jsonify({
            "success": True,
            "result_image": rgb_array_to_b64(result),
            "execution_ms": elapsed_ms,
            "dimensions": f"{w}x{h} px",
            "info": info_detail
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def find_available_port(default_port: int = 5050, fallbacks: list = None) -> int:
    """Mencari port jaringan lokal yang bebas dan tidak diblokir oleh sistem operasi Windows"""
    if fallbacks is None:
        fallbacks = [8000, 5500, 8888, 5001]
    for p in [default_port] + fallbacks:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("127.0.0.1", p))
            s.close()
            return p
        except Exception:
            continue
    return default_port


if __name__ == "__main__":
    port = find_available_port(default_port=5050)
    print("=" * 65)
    print(">> Aplikasi Web Pengolahan Citra Digital (Flask Server)")
    print(f">> Server aktif pada port {port}!")
    print(f">> Silakan buka tautan berikut di browser Anda:")
    print(f">> http://127.0.0.1:{port}")
    print("=" * 65)
    app.run(host="127.0.0.1", port=port, debug=True)
