"""
================================================================================
TUGAS PRAKTIKUM 9: CAPSTONE PROJECT-1
PENGOLAHAN CITRA DIGITAL (KELAS B)
================================================================================
Fokus Tugas:
- Membuat Antarmuka Pengguna (UI) dan Struktur Menu Aplikasi
- Berdasarkan:
  1. PCD WIREFRAME.pdf (8 Halaman: Idle, File, Basic Operation, Enhancement,
     Noise, Edge Detection, Segmentation, About)
  2. Panduan GUI_app.ipynb (Tkinter, Pillow, Arsitektur Class ImageProcessingApp)
  3. Dokumen Menu structure-Aplikasi-PCD.pdf (Hierarki Lengkap Menu Aplikasi)
================================================================================
"""

import os
import sys
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk


class ImageProcessingApp:
    """
    Kelas Utama Antarmuka Aplikasi Pengolahan Citra Digital (Tkinter + Pillow).
    Mengimplementasikan arsitektur modular sesuai standar GUI_app.ipynb dan tata letak
    wireframe pada PCD WIREFRAME.pdf.
    """

    def __init__(self, root: tk.Tk):
        # 1. Inisialisasi Window Utama (Root)
        self.root = root
        self.root.title("Aplikasi Pengolahan Citra Digital - Capstone Project 1 (UI & Struktur Menu)")
        self.root.geometry("1200x820")
        self.root.minsize(1050, 750)
        self.root.configure(bg="#f8f9fa")

        # 2. State & Data Aplikasi
        self.pil_img_orig = None       # Citra Asli (Image 1)
        self.pil_img_secondary = None  # Citra Kedua (Image 2)
        self.pil_img_processed = None  # Citra Hasil
        self.orig_filename = ""
        self.sec_filename = ""
        self.active_tab = "Basic Operation"
        self.is_dual_mode = False

        # Variabel Interaksi Seleksi Crop pada Canvas
        self.crop_start_x = None
        self.crop_start_y = None
        self.crop_rect_id = None
        self.is_selecting_crop = False

        # 3. Inisialisasi Gaya Widget (ttk Style)
        self._init_styles()

        # 4. Bangun Struktur Menu Bar Lengkap (Sesuai Menu structure-Aplikasi-PCD.pdf & GUI_app.ipynb)
        self._create_complete_menu_bar()

        # 5. Bangun Bilah Navigasi Atas (Sesuai PCD WIREFRAME.pdf)
        self._create_top_navbar()

        # 6. Bangun Area Display Canvas (Single & Dual Mode)
        self._create_canvas_area()

        # 7. Bangun Contextual Control Panel Dinamis & Tombol Aksi Bawah
        self._create_contextual_control_panel()

        # Tampilkan Tab Awal (Default: Basic Operation)
        self.switch_tab("Basic Operation")
        print(">> Aplikasi Pengolahan Citra Digital berhasil dijalankan.")
        print(">> UI dan Seluruh Struktur Menu Siap Digunakan.")

    # ==========================================================================
    # 1. STYLING WIDGET
    # ==========================================================================

    def _init_styles(self):
        """Konfigurasi style ttk untuk widget modern yang serasi dengan wireframe"""
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self.style.configure(".", background="#f8f9fa", font=("Segoe UI", 9))
        self.style.configure("TCombobox", padding=4, relief="flat")
        self.style.configure("TScale", background="#f0f1f4")
        self.style.configure("TCheckbutton", background="#f0f1f4", font=("Segoe UI", 9))

    # ==========================================================================
    # 2. STRUKTUR MENU BAR LENGKAP (SESUAI PANDUAN DOSEN & GUI_app.ipynb)
    # ==========================================================================

    def _create_complete_menu_bar(self):
        """
        Membangun Menu Bar Desktop hierarkis menggunakan Menu bawaan Tkinter.
        Memenuhi 100% struktur menu pada dokumen: 'Menu structure-Aplikasi-PCD.pdf'.
        """
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # ----------------- 1. Menu File -----------------
        self.menu_file = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.menu_file)
        self.menu_file.add_command(label="Open / Browse File...", command=self.menu_open_click)
        self.menu_file.add_command(label="Open Secondary Image (Image 2)...", command=self.menu_open_sec_click)
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Save", command=self.menu_save_click)
        self.menu_file.add_command(label="Save As...", command=self.menu_save_as_click)
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Exit", command=self.menu_exit_click)

        # ----------------- 2. Menu Basic Ops -----------------
        self.menu_basic = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Basic Ops", menu=self.menu_basic)

        self.menu_basic.add_command(label="Negative", command=lambda: self.on_menu_item_selected("Basic Ops", "Negative"))

        # Sub-menu Arithmetic
        self.sub_arith = tk.Menu(self.menu_basic, tearoff=0)
        self.menu_basic.add_cascade(label="Arithmetic -->", menu=self.sub_arith)
        self.sub_arith.add_command(label="Add (+)", command=lambda: self.on_menu_item_selected("Arithmetic", "Add (+)"))
        self.sub_arith.add_command(label="Subtract (-)", command=lambda: self.on_menu_item_selected("Arithmetic", "Subtract (-)"))
        self.sub_arith.add_command(label="Multiply (*)", command=lambda: self.on_menu_item_selected("Arithmetic", "Multiply (*)"))
        self.sub_arith.add_command(label="Divide (/)", command=lambda: self.on_menu_item_selected("Arithmetic", "Divide (/)"))

        # Sub-menu Boolean
        self.sub_bool = tk.Menu(self.menu_basic, tearoff=0)
        self.menu_basic.add_cascade(label="Boolean -->", menu=self.sub_bool)
        self.sub_bool.add_command(label="NOT", command=lambda: self.on_menu_item_selected("Boolean", "NOT"))
        self.sub_bool.add_command(label="AND", command=lambda: self.on_menu_item_selected("Boolean", "AND"))
        self.sub_bool.add_command(label="OR", command=lambda: self.on_menu_item_selected("Boolean", "OR"))
        self.sub_bool.add_command(label="XOR", command=lambda: self.on_menu_item_selected("Boolean", "XOR"))

        # Sub-menu Geometrics
        self.sub_geom = tk.Menu(self.menu_basic, tearoff=0)
        self.menu_basic.add_cascade(label="Geometrics -->", menu=self.sub_geom)
        self.sub_geom.add_command(label="Translation", command=lambda: self.on_menu_item_selected("Geometrics", "Translation"))
        self.sub_geom.add_command(label="Rotation", command=lambda: self.on_menu_item_selected("Geometrics", "Rotation"))
        self.sub_geom.add_command(label="Zooming", command=lambda: self.on_menu_item_selected("Geometrics", "Zooming"))
        self.sub_geom.add_command(label="Flipping", command=lambda: self.on_menu_item_selected("Geometrics", "Flipping"))
        self.sub_geom.add_command(label="Cropping", command=lambda: self.on_menu_item_selected("Geometrics", "Cropping"))

        self.menu_basic.add_command(label="Thresholding", command=lambda: self.on_menu_item_selected("Basic Ops", "Thresholding"))
        self.menu_basic.add_command(label="Convolution", command=lambda: self.on_menu_item_selected("Basic Ops", "Convolution"))
        self.menu_basic.add_command(label="Fourier Transform", command=lambda: self.on_menu_item_selected("Basic Ops", "Fourier Transform"))

        # Sub-menu Colouring
        self.sub_color = tk.Menu(self.menu_basic, tearoff=0)
        self.menu_basic.add_cascade(label="Colouring -->", menu=self.sub_color)
        for col in ["Binary", "Grayscale", "RGB", "HSV", "CMY", "YUV", "YIQ", "Pseudo"]:
            self.sub_color.add_command(label=col, command=lambda c=col: self.on_menu_item_selected("Colouring", c))

        # ----------------- 3. Menu Enhancement -----------------
        self.menu_enh = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Enhancement", menu=self.menu_enh)
        self.menu_enh.add_command(label="Brightness", command=lambda: self.on_menu_item_selected("Enhancement", "Brightness"))
        self.menu_enh.add_command(label="Contrast", command=lambda: self.on_menu_item_selected("Enhancement", "Contrast"))
        self.menu_enh.add_command(label="Hist. Equalization", command=lambda: self.on_menu_item_selected("Enhancement", "Hist. Equalization"))

        # Sub-menu Smoothing
        self.sub_smooth = tk.Menu(self.menu_enh, tearoff=0)
        self.menu_enh.add_cascade(label="Smoothing -->", menu=self.sub_smooth)

        self.sub_smooth_spat = tk.Menu(self.sub_smooth, tearoff=0)
        self.sub_smooth.add_cascade(label="Spatial Domain -->", menu=self.sub_smooth_spat)
        self.sub_smooth_spat.add_command(label="Lowpass Filtering", command=lambda: self.on_menu_item_selected("Smoothing", "Lowpass Filtering"))
        self.sub_smooth_spat.add_command(label="Median Filtering", command=lambda: self.on_menu_item_selected("Smoothing", "Median Filtering"))

        self.sub_smooth_freq = tk.Menu(self.sub_smooth, tearoff=0)
        self.sub_smooth.add_cascade(label="Frequency Domain -->", menu=self.sub_smooth_freq)
        self.sub_smooth_freq.add_command(label="ILPF (Ideal Lowpass)", command=lambda: self.on_menu_item_selected("Smoothing", "ILPF"))
        self.sub_smooth_freq.add_command(label="BLPF (Butterworth Lowpass)", command=lambda: self.on_menu_item_selected("Smoothing", "BLPF"))

        # Sub-menu Sharpening
        self.sub_sharp = tk.Menu(self.menu_enh, tearoff=0)
        self.menu_enh.add_cascade(label="Sharpening -->", menu=self.sub_sharp)

        self.sub_sharp_spat = tk.Menu(self.sub_sharp, tearoff=0)
        self.sub_sharp.add_cascade(label="Spatial Domain -->", menu=self.sub_sharp_spat)
        self.sub_sharp_spat.add_command(label="Highpass Filtering", command=lambda: self.on_menu_item_selected("Sharpening", "Highpass Filtering"))
        self.sub_sharp_spat.add_command(label="Highboost Filtering", command=lambda: self.on_menu_item_selected("Sharpening", "Highboost Filtering"))

        self.sub_sharp_freq = tk.Menu(self.sub_sharp, tearoff=0)
        self.sub_sharp.add_cascade(label="Frequency Domain -->", menu=self.sub_sharp_freq)
        self.sub_sharp_freq.add_command(label="IHPF (Ideal Highpass)", command=lambda: self.on_menu_item_selected("Sharpening", "IHPF"))
        self.sub_sharp_freq.add_command(label="BHPF (Butterworth Highpass)", command=lambda: self.on_menu_item_selected("Sharpening", "BHPF"))

        self.menu_enh.add_command(label="Geometrics correction", command=lambda: self.on_menu_item_selected("Enhancement", "Geometrics correction"))

        # ----------------- 4. Menu Noise -----------------
        self.menu_noise = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Noise", menu=self.menu_noise)
        for n_type in ["Gaussian Noise", "Rayleigh Noise", "Erlang (Gamma) Noise", "Exponential Noise", "Uniform Noise", "Impulse Noise"]:
            self.menu_noise.add_command(label=n_type, command=lambda n=n_type: self.on_menu_item_selected("Noise", n))

        # ----------------- 5. Menu Edge Detection -----------------
        self.menu_edge = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edge Detection", menu=self.menu_edge)

        self.sub_edge_1st = tk.Menu(self.menu_edge, tearoff=0)
        self.menu_edge.add_cascade(label="1'st Differential Gradient -->", menu=self.sub_edge_1st)
        self.sub_edge_1st.add_command(label="Sobel", command=lambda: self.on_menu_item_selected("Edge Detection", "Sobel"))
        self.sub_edge_1st.add_command(label="Prewitt", command=lambda: self.on_menu_item_selected("Edge Detection", "Prewitt"))
        self.sub_edge_1st.add_command(label="Robert", command=lambda: self.on_menu_item_selected("Edge Detection", "Robert"))

        self.sub_edge_2nd = tk.Menu(self.menu_edge, tearoff=0)
        self.menu_edge.add_cascade(label="2'nd Differential Gradient -->", menu=self.sub_edge_2nd)
        self.sub_edge_2nd.add_command(label="Laplacian", command=lambda: self.on_menu_item_selected("Edge Detection", "Laplacian"))
        self.sub_edge_2nd.add_command(label="Laplacian of Gaussian (LoG)", command=lambda: self.on_menu_item_selected("Edge Detection", "LoG"))
        self.sub_edge_2nd.add_command(label="Canny", command=lambda: self.on_menu_item_selected("Edge Detection", "Canny"))

        self.menu_edge.add_command(label="Compass (Kirsch 8 Directions)", command=lambda: self.on_menu_item_selected("Edge Detection", "Compass"))

        # ----------------- 6. Menu Segmentation -----------------
        self.menu_seg = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Segmentation", menu=self.menu_seg)
        self.menu_seg.add_command(label="Manual Thresholding", command=lambda: self.on_menu_item_selected("Segmentation", "Manual Thresholding"))
        self.menu_seg.add_command(label="Otsu's Thresholding (Auto)", command=lambda: self.on_menu_item_selected("Segmentation", "Otsu"))
        self.menu_seg.add_command(label="Adaptive Thresholding", command=lambda: self.on_menu_item_selected("Segmentation", "Adaptive"))
        self.menu_seg.add_separator()
        self.menu_seg.add_command(label="Contour Extraction", command=lambda: self.on_menu_item_selected("Segmentation", "Contours"))
        self.menu_seg.add_command(label="Bounding Box Marking", command=lambda: self.on_menu_item_selected("Segmentation", "Bounding Box"))

        # ----------------- 7. Menu About -----------------
        self.menu_about = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="About", menu=self.menu_about)
        self.menu_about.add_command(label="Info Tim Developer", command=lambda: self.switch_tab("About"))
        self.menu_about.add_separator()
        self.menu_about.add_command(label="Tutorial: Link Github", command=self.open_github)
        self.menu_about.add_command(label="Tutorial: Link Youtube", command=self.open_youtube)

    # ==========================================================================
    # 3. TOP NAVBAR WIREFRAME (7 MENU UTAMA)
    # ==========================================================================

    def _create_top_navbar(self):
        """Bilah Navigasi Atas persis seperti pada dokumen PCD WIREFRAME.pdf"""
        self.navbar_frame = tk.Frame(self.root, bg="#ebebeb", height=46, relief="flat", bd=0)
        self.navbar_frame.pack(side="top", fill="x")

        # Tombol File Dropdown
        self.file_mb = tk.Menubutton(self.navbar_frame, text="File ▾", font=("Segoe UI", 10, "bold"),
                                     bg="#ffffff", fg="#222222", activebackground="#e0e0e0",
                                     relief="solid", bd=1, padx=12, pady=3, cursor="hand2")
        self.file_menu_nav = tk.Menu(self.file_mb, tearoff=0, font=("Segoe UI", 9))
        self.file_menu_nav.add_command(label="Browse File...", command=self.menu_open_click)
        self.file_menu_nav.add_command(label="Save Image", command=self.menu_save_click)
        self.file_menu_nav.add_command(label="Save As...", command=self.menu_save_as_click)
        self.file_menu_nav.add_separator()
        self.file_menu_nav.add_command(label="Exit", command=self.menu_exit_click)
        self.file_mb.config(menu=self.file_menu_nav)
        self.file_mb.pack(side="left", padx=(15, 25), pady=8)

        # Tab Tombol Navigasi 6 Modul
        self.tabs = [
            "Basic Operation",
            "Enhancement",
            "Noise",
            "Edge Detection",
            "Segmentation",
            "About"
        ]
        self.tab_buttons = {}

        nav_btns_frame = tk.Frame(self.navbar_frame, bg="#ebebeb")
        nav_btns_frame.pack(side="left", fill="y")

        for tab_name in self.tabs:
            btn = tk.Button(nav_btns_frame, text=tab_name, font=("Segoe UI", 9),
                            bg="#ebebeb", fg="#444444", activebackground="#dcdcdc",
                            relief="flat", bd=0, padx=14, pady=6, cursor="hand2",
                            command=lambda t=tab_name: self.switch_tab(t))
            btn.pack(side="left", padx=2, pady=6)
            self.tab_buttons[tab_name] = btn

    # ==========================================================================
    # 4. AREA DISPLAY CANVAS (SINGLE VS DUAL MODE)
    # ==========================================================================

    def _create_canvas_area(self):
        """Wadah kanvas komparatif visual citra dengan tata letak grid seragam (uniform)"""
        self.canvas_container = tk.Frame(self.root, bg="#ffffff", pady=10, padx=15)
        self.canvas_container.pack(side="top", fill="both", expand=True)
        self.canvas_container.rowconfigure(0, weight=1)

        # 1. Canvas Citra Asli (Original Image)
        self.box_orig = tk.Frame(self.canvas_container, bg="#ffffff")
        self.canvas_orig = tk.Canvas(self.box_orig, bg="#ffffff", highlightthickness=1,
                                     highlightbackground="#444444", cursor="crosshair")
        self.canvas_orig.pack(fill="both", expand=True)
        self.canvas_orig.bind("<Button-1>", self._on_canvas_click)
        self.canvas_orig.bind("<B1-Motion>", self._on_canvas_drag)
        self.canvas_orig.bind("<ButtonRelease-1>", self._on_canvas_release)
        self.canvas_orig.bind("<Configure>", lambda e: self._render_canvas(self.canvas_orig, self.pil_img_orig, "Original Image"))

        self.lbl_status_orig = tk.Label(self.box_orig, text="Idle: Ready to load an image",
                                        font=("Segoe UI", 9), bg="#ffffff", fg="#666666", anchor="w")
        self.lbl_status_orig.pack(fill="x", pady=(4, 0))

        # 2. Canvas Citra Kedua (Secondary Image - Khusus Dual Mode Aritmatika & Boolean)
        self.box_sec = tk.Frame(self.canvas_container, bg="#ffffff")
        self.canvas_sec = tk.Canvas(self.box_sec, bg="#ffffff", highlightthickness=1,
                                    highlightbackground="#444444", cursor="hand2")
        self.canvas_sec.pack(fill="both", expand=True)
        self.canvas_sec.bind("<Button-1>", lambda e: self.menu_open_sec_click())
        self.canvas_sec.bind("<Configure>", lambda e: self._render_canvas(self.canvas_sec, self.pil_img_secondary, "Secondary Image") if self.is_dual_mode else None)

        self.lbl_status_sec = tk.Label(self.box_sec, text="Click to load Image 2",
                                       font=("Segoe UI", 9), bg="#ffffff", fg="#666666", anchor="w")
        self.lbl_status_sec.pack(fill="x", pady=(4, 0))

        # 3. Canvas Citra Hasil (Processed Image)
        self.box_proc = tk.Frame(self.canvas_container, bg="#ffffff")
        self.canvas_proc = tk.Canvas(self.box_proc, bg="#ffffff", highlightthickness=1,
                                     highlightbackground="#444444")
        self.canvas_proc.pack(fill="both", expand=True)
        self.canvas_proc.bind("<Configure>", lambda e: self._render_canvas(self.canvas_proc, self.pil_img_processed, "Processed Image"))

        self.lbl_status_proc = tk.Label(self.box_proc, text="Processed Image Output",
                                        font=("Segoe UI", 9), bg="#ffffff", fg="#666666", anchor="w")
        self.lbl_status_proc.pack(fill="x", pady=(4, 0))

        # Tata letak awal (Dual mode)
        self.set_dual_mode(True)

    # ==========================================================================
    # 5. CONTEXTUAL CONTROL PANEL & TOMBOL AKSI
    # ==========================================================================

    def _create_contextual_control_panel(self):
        """Wadah abu-abu kontrol kontekstual di bagian bawah"""
        self.panel_frame = tk.Frame(self.root, bg="#f0f1f4", height=210, bd=0)
        self.panel_frame.pack(side="top", fill="x", padx=15, pady=(5, 5))
        self.panel_frame.pack_propagate(False)

        # Header Title Contextual Control Panel
        self.lbl_panel_title = tk.Label(self.panel_frame, text="Contextual Control Panel",
                                        font=("Segoe UI", 10, "bold"), bg="#f0f1f4", fg="#333333")
        self.lbl_panel_title.pack(side="top", pady=(6, 2))

        # Wadah sub-panel yang berubah-ubah sesuai tab aktif
        self.dynamic_panel = tk.Frame(self.panel_frame, bg="#f0f1f4")
        self.dynamic_panel.pack(side="top", fill="both", expand=True, padx=15, pady=4)

        # Bilah Tombol Aksi Bawah: Reset & Apply (Pill buttons hitam)
        self.bottom_bar = tk.Frame(self.root, bg="#f8f9fa", height=50)
        self.bottom_bar.pack(side="bottom", fill="x", pady=(0, 10))

        btn_container = tk.Frame(self.bottom_bar, bg="#f8f9fa")
        btn_container.pack(side="top")

        # Tombol Reset
        self.btn_reset = tk.Button(btn_container, text="Reset", font=("Segoe UI", 9, "bold"),
                                   bg="#1a1a1a", fg="#ffffff", activebackground="#333333",
                                   activeforeground="#ffffff", relief="flat", bd=0,
                                   padx=32, pady=6, cursor="hand2", command=self.on_reset_clicked)
        self.btn_reset.pack(side="left", padx=15)

        # Tombol Apply
        self.btn_apply = tk.Button(btn_container, text="Apply", font=("Segoe UI", 9, "bold"),
                                   bg="#1a1a1a", fg="#ffffff", activebackground="#333333",
                                   activeforeground="#ffffff", relief="flat", bd=0,
                                   padx=32, pady=6, cursor="hand2", command=self.on_apply_clicked)
        self.btn_apply.pack(side="left", padx=15)

    # ==========================================================================
    # 6. PERGANTIAN TAB KONTEKSTUAL
    # ==========================================================================

    def switch_tab(self, tab_name: str):
        """Mengganti tab aktif dan memperbarui panel kontrol"""
        self.active_tab = tab_name
        print(f"[Menu Navigasi] Tab aktif beralih ke: '{tab_name}'")

        # Update style tombol navbar
        for name, btn in self.tab_buttons.items():
            if name == tab_name:
                btn.config(font=("Segoe UI", 9, "bold"), fg="#111111", bg="#dddddd")
            else:
                btn.config(font=("Segoe UI", 9), fg="#555555", bg="#ebebeb")

        # Tampilkan Dual Canvas Mode khusus pada menu Basic Operation
        if tab_name == "Basic Operation":
            self.set_dual_mode(True)
        else:
            self.set_dual_mode(False)

        # Bersihkan dynamic panel
        for child in self.dynamic_panel.winfo_children():
            child.destroy()

        # Bangun komponen kontrol sesuai halaman wireframe aktif
        if tab_name == "Basic Operation":
            self._build_panel_basic_ops()
        elif tab_name == "Enhancement":
            self._build_panel_enhancement()
        elif tab_name == "Noise":
            self._build_panel_noise()
        elif tab_name == "Edge Detection":
            self._build_panel_edge_detection()
        elif tab_name == "Segmentation":
            self._build_panel_segmentation()
        elif tab_name == "About":
            self._build_panel_about()

    def set_dual_mode(self, enabled: bool):
        """Beralih antara Single Canvas Mode (2 kolom) dan Dual Image Canvas Mode (3 kolom seragam)"""
        self.is_dual_mode = enabled
        if enabled:
            # Mode Dual: 3 Kolom dengan bobot dan lebar seragam (uniform)
            self.canvas_container.columnconfigure(0, weight=1, uniform="canv_col")
            self.canvas_container.columnconfigure(1, weight=1, uniform="canv_col")
            self.canvas_container.columnconfigure(2, weight=1, uniform="canv_col")

            self.box_orig.grid(row=0, column=0, sticky="nsew", padx=6)
            self.box_sec.grid(row=0, column=1, sticky="nsew", padx=6)
            self.box_proc.grid(row=0, column=2, sticky="nsew", padx=6)
        else:
            # Mode Single: 2 Kolom (Original & Processed), sembunyikan kolom tengah (Secondary)
            self.box_sec.grid_forget()
            self.canvas_container.columnconfigure(1, weight=0, uniform="")
            self.canvas_container.columnconfigure(0, weight=1, uniform="canv_col")
            self.canvas_container.columnconfigure(2, weight=1, uniform="canv_col")

            self.box_orig.grid(row=0, column=0, sticky="nsew", padx=8)
            self.box_proc.grid(row=0, column=2, sticky="nsew", padx=8)

        self.render_all_canvases(force=True)

    # ==========================================================================
    # 7. KOMPONEN KONTROL MASING-MASING MENU (PCD WIREFRAME PAGES 3-8)
    # ==========================================================================

    # --- TAB 1: BASIC OPERATION (Wireframe Hal. 3) ---
    def _build_panel_basic_ops(self):
        p = self.dynamic_panel

        # Kolom 1: Brightness & Contrast
        f1 = tk.Frame(p, bg="#f0f1f4")
        f1.pack(side="left", fill="both", expand=True, padx=8)

        tk.Label(f1, text="Brightness", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w")
        self.slider_bright = ttk.Scale(f1, from_=-255, to=255, orient="horizontal",
                                       command=lambda v: self.lbl_bright_val.config(text=f"Value : {int(float(v)):+d}"))
        self.slider_bright.set(25)
        self.slider_bright.pack(fill="x", pady=1)
        self.lbl_bright_val = tk.Label(f1, text="Value : +25", font=("Segoe UI", 7), bg="#f0f1f4", fg="#555")
        self.lbl_bright_val.pack(anchor="w", pady=(0, 4))

        tk.Label(f1, text="Contrast", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w")
        self.slider_contrast = ttk.Scale(f1, from_=0.1, to=3.0, orient="horizontal",
                                         command=lambda v: self.lbl_contrast_val.config(text=f"Value : +{float(v):.1f}"))
        self.slider_contrast.set(1.0)
        self.slider_contrast.pack(fill="x", pady=1)
        self.lbl_contrast_val = tk.Label(f1, text="Value : +0.1", font=("Segoe UI", 7), bg="#f0f1f4", fg="#555")
        self.lbl_contrast_val.pack(anchor="w")

        # Kolom 2: Colouring & Zoom
        f2 = tk.Frame(p, bg="#f0f1f4")
        f2.pack(side="left", fill="both", expand=True, padx=8)

        tk.Label(f2, text="Colouring", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w")
        self.cb_colouring = ttk.Combobox(f2, values=["RGB", "Grayscale", "Binary", "HSV", "CMY", "YUV", "YIQ", "Pseudo"],
                                         state="readonly", width=12)
        self.cb_colouring.set("RGB")
        self.cb_colouring.pack(fill="x", pady=2)

        tk.Label(f2, text="Zoom", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w", pady=(6, 0))
        zoom_row = tk.Frame(f2, bg="#f0f1f4")
        zoom_row.pack(fill="x")
        tk.Label(zoom_row, text="—", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(side="left")
        self.slider_zoom = ttk.Scale(zoom_row, from_=0.2, to=3.0, orient="horizontal")
        self.slider_zoom.set(1.0)
        self.slider_zoom.pack(side="left", fill="x", expand=True, padx=4)
        tk.Label(zoom_row, text="+", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(side="left")

        # Kolom 3: Crop
        f3 = tk.Frame(p, bg="#f0f1f4")
        f3.pack(side="left", fill="both", expand=True, padx=8)

        tk.Label(f3, text="Crop", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w")
        grid_crop = tk.Frame(f3, bg="#f0f1f4")
        grid_crop.pack(fill="x")

        self.entry_x1 = ttk.Entry(grid_crop, width=8)
        self.entry_x1.insert(0, "Input X1")
        self.entry_x1.grid(row=0, column=0, padx=2, pady=2)

        self.entry_y1 = ttk.Entry(grid_crop, width=8)
        self.entry_y1.insert(0, "Input Y1")
        self.entry_y1.grid(row=0, column=1, padx=2, pady=2)

        self.entry_x2 = ttk.Entry(grid_crop, width=8)
        self.entry_x2.insert(0, "Input X2")
        self.entry_x2.grid(row=1, column=0, padx=2, pady=2)

        self.entry_y2 = ttk.Entry(grid_crop, width=8)
        self.entry_y2.insert(0, "Input Y2")
        self.entry_y2.grid(row=1, column=1, padx=2, pady=2)

        self.btn_select_crop = tk.Button(f3, text="Select on canvas", font=("Segoe UI", 8),
                                         bg="#9e9e9e", fg="#ffffff", activebackground="#757575",
                                         relief="flat", pady=2, cursor="hand2", command=self.activate_crop_selection)
        self.btn_select_crop.pack(fill="x", pady=4)

        # Kolom 4: Rotate & Flip
        f4 = tk.Frame(p, bg="#f0f1f4")
        f4.pack(side="left", fill="both", expand=True, padx=8)

        tk.Label(f4, text="Rotate", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w")
        self.cb_rotate = ttk.Combobox(f4, values=["No Rotate", "90° CW", "180°", "270° CW", "Custom: 45°"],
                                      state="readonly", width=12)
        self.cb_rotate.set("No Rotate")
        self.cb_rotate.pack(fill="x", pady=2)

        tk.Label(f4, text="Flip", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w", pady=(6, 0))
        self.cb_flip = ttk.Combobox(f4, values=["No Flip", "Horizontal", "Vertical", "Both"],
                                    state="readonly", width=12)
        self.cb_flip.set("No Flip")
        self.cb_flip.pack(fill="x", pady=2)

        # Kolom 5: Boolean, Arithmetic, & Invert
        f5 = tk.Frame(p, bg="#f0f1f4")
        f5.pack(side="left", fill="both", expand=True, padx=8)

        tk.Label(f5, text="Boolean", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w")
        self.cb_boolean = ttk.Combobox(f5, values=["None", "AND", "OR", "XOR", "NOT"],
                                       state="readonly", width=12)
        self.cb_boolean.set("AND")
        self.cb_boolean.pack(fill="x", pady=2)

        tk.Label(f5, text="Arithmetic", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w", pady=(4, 0))
        self.cb_arithmetic = ttk.Combobox(f5, values=["None", "Add (+)", "Subtract (-)", "Multiply (*)", "Divide (/)"],
                                          state="readonly", width=12)
        self.cb_arithmetic.set("Add (+)")
        self.cb_arithmetic.pack(fill="x", pady=2)

        self.var_invert = tk.BooleanVar(value=False)
        self.chk_invert = ttk.Checkbutton(f5, text="Invert", variable=self.var_invert)
        self.chk_invert.pack(anchor="e", pady=(6, 0))

    # --- TAB 2: ENHANCEMENT (Wireframe Hal. 4) ---
    def _build_panel_enhancement(self):
        p = self.dynamic_panel

        f1 = tk.Frame(p, bg="#f0f1f4")
        f1.pack(side="left", fill="both", expand=True, padx=10)

        tk.Label(f1, text="Filtering Method", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w")
        self.cb_filter = ttk.Combobox(f1, values=["Gaussian Filter", "Average Filter", "Median Filter", "Bilateral Filter"],
                                      state="readonly", width=15)
        self.cb_filter.set("Gaussian Filter")
        self.cb_filter.pack(fill="x", pady=2)

        tk.Label(f1, text="Sigma", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w", pady=(8, 0))
        self.slider_sigma = ttk.Scale(f1, from_=0.1, to=20.0, orient="horizontal",
                                      command=lambda v: self.lbl_sigma_val.config(text=f"Value : +{float(v):.0f}"))
        self.slider_sigma.set(25)
        self.slider_sigma.pack(fill="x", pady=1)
        self.lbl_sigma_val = tk.Label(f1, text="Value : +25", font=("Segoe UI", 7), bg="#f0f1f4", fg="#555")
        self.lbl_sigma_val.pack(anchor="w")

        f2 = tk.Frame(p, bg="#f0f1f4")
        f2.pack(side="left", fill="both", expand=True, padx=10)

        tk.Label(f2, text="Kernel Mask", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w")
        self.cb_enh_kernel = ttk.Combobox(f2, values=["3x3", "5x5", "7x7", "9x9"], state="readonly", width=10)
        self.cb_enh_kernel.set("3x3")
        self.cb_enh_kernel.pack(fill="x", pady=2)

        f3 = tk.Frame(p, bg="#f0f1f4")
        f3.pack(side="left", fill="both", expand=True, padx=10)

        tk.Label(f3, text="Sharpening", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w")
        self.cb_sharp = ttk.Combobox(f3, values=["None", "Laplacian", "Unsharp Masking", "Highpass", "Highboost"],
                                     state="readonly", width=14)
        self.cb_sharp.set("Laplacian")
        self.cb_sharp.pack(fill="x", pady=2)

        tk.Label(f3, text="Strength", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w", pady=(8, 0))
        self.slider_sharp_strength = ttk.Scale(f3, from_=0.1, to=3.0, orient="horizontal",
                                               command=lambda v: self.lbl_sharp_val.config(text=f"Value : +{float(v):.1f}"))
        self.slider_sharp_strength.set(1.5)
        self.slider_sharp_strength.pack(fill="x", pady=1)
        self.lbl_sharp_val = tk.Label(f3, text="Value : +1.5", font=("Segoe UI", 7), bg="#f0f1f4", fg="#555")
        self.lbl_sharp_val.pack(anchor="w")

        f4 = tk.Frame(p, bg="#f0f1f4")
        f4.pack(side="left", fill="both", expand=True, padx=10)

        tk.Label(f4, text="Equalization", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w")
        self.cb_equalize = ttk.Combobox(f4, values=["None", "Global", "CLAHE"], state="readonly", width=12)
        self.cb_equalize.set("Global")
        self.cb_equalize.pack(fill="x", pady=2)

        tk.Label(f4, text="Histogram Graph", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w", pady=(8, 0))
        self.var_hist = tk.BooleanVar(value=True)
        self.chk_hist = ttk.Checkbutton(f4, text="Show Histogram", variable=self.var_hist,
                                        command=lambda: print("[Feature] Histogram Graph Toggle:", self.var_hist.get()))
        self.chk_hist.pack(anchor="w", pady=2)

    # --- TAB 3: NOISE (Wireframe Hal. 5) ---
    def _build_panel_noise(self):
        p = self.dynamic_panel

        f1 = tk.Frame(p, bg="#f0f1f4")
        f1.pack(side="left", fill="both", expand=True, padx=10)

        tk.Label(f1, text="Noise Type", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w")
        self.cb_noise_type = ttk.Combobox(f1, values=["None", "Salt & Pepper", "Gaussian Noise", "Rayleigh Noise",
                                                     "Erlang (Gamma) Noise", "Exponential Noise", "Uniform Noise"],
                                          state="readonly", width=18)
        self.cb_noise_type.set("Salt & Pepper")
        self.cb_noise_type.pack(fill="x", pady=2)

        f2 = tk.Frame(p, bg="#f0f1f4")
        f2.pack(side="left", fill="both", expand=True, padx=10)

        tk.Label(f2, text="Noise Ratio", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w")
        self.slider_noise_ratio = ttk.Scale(f2, from_=0.01, to=0.50, orient="horizontal",
                                            command=lambda v: self.lbl_noise_val.config(text=f"Value : +{float(v):.2f}"))
        self.slider_noise_ratio.set(0.25)
        self.slider_noise_ratio.pack(fill="x", pady=2)
        self.lbl_noise_val = tk.Label(f2, text="Value : +0.25", font=("Segoe UI", 7), bg="#f0f1f4", fg="#555")
        self.lbl_noise_val.pack(anchor="w")

        f3 = tk.Frame(p, bg="#f0f1f4")
        f3.pack(side="left", fill="both", expand=True, padx=10)

        tk.Label(f3, text="Restoration", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w")
        self.cb_restoration = ttk.Combobox(f3, values=["None", "Median Filter", "Mean Filter", "Gaussian Filter", "Bilateral Filter"],
                                           state="readonly", width=15)
        self.cb_restoration.set("Median Filter")
        self.cb_restoration.pack(fill="x", pady=2)

        f4 = tk.Frame(p, bg="#f0f1f4")
        f4.pack(side="left", fill="both", expand=True, padx=10)

        tk.Label(f4, text="Kernel Size", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w")
        self.cb_noise_ksize = ttk.Combobox(f4, values=["3x3", "5x5", "7x7"], state="readonly", width=10)
        self.cb_noise_ksize.set("3x3")
        self.cb_noise_ksize.pack(fill="x", pady=2)

    # --- TAB 4: EDGE DETECTION (Wireframe Hal. 6) ---
    def _build_panel_edge_detection(self):
        p = self.dynamic_panel

        f1 = tk.Frame(p, bg="#f0f1f4")
        f1.pack(side="left", fill="both", expand=True, padx=10)

        tk.Label(f1, text="Direction", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w")
        self.cb_edge_dir = ttk.Combobox(f1, values=["Magnitude", "Horizontal", "Vertical"], state="readonly", width=14)
        self.cb_edge_dir.set("Horizontal")
        self.cb_edge_dir.pack(fill="x", pady=2)

        f2 = tk.Frame(p, bg="#f0f1f4")
        f2.pack(side="left", fill="both", expand=True, padx=10)

        tk.Label(f2, text="Edge Operator", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w")
        self.cb_edge_op = ttk.Combobox(f2, values=["Canny", "Sobel", "Prewitt", "Robert", "Laplacian", "LoG", "Compass"],
                                       state="readonly", width=14)
        self.cb_edge_op.set("Canny")
        self.cb_edge_op.pack(fill="x", pady=2)

        tk.Label(f2, text="Kernel Size", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w", pady=(6, 0))
        self.cb_edge_ksize = ttk.Combobox(f2, values=["3x3", "5x5", "7x7"], state="readonly", width=14)
        self.cb_edge_ksize.set("3x3")
        self.cb_edge_ksize.pack(fill="x", pady=2)

        f3 = tk.Frame(p, bg="#f0f1f4")
        f3.pack(side="left", fill="both", expand=True, padx=10)

        tk.Label(f3, text="Lower Threshold", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w")
        self.slider_low_t = ttk.Scale(f3, from_=0, to=255, orient="horizontal",
                                      command=lambda v: self.lbl_low_t_val.config(text=f"Value : {int(float(v))}"))
        self.slider_low_t.set(10)
        self.slider_low_t.pack(fill="x", pady=2)
        self.lbl_low_t_val = tk.Label(f3, text="Value : 10", font=("Segoe UI", 7), bg="#f0f1f4", fg="#555")
        self.lbl_low_t_val.pack(anchor="w")

        f4 = tk.Frame(p, bg="#f0f1f4")
        f4.pack(side="left", fill="both", expand=True, padx=10)

        tk.Label(f4, text="Upper Threshold", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w")
        self.slider_up_t = ttk.Scale(f4, from_=0, to=255, orient="horizontal",
                                     command=lambda v: self.lbl_up_t_val.config(text=f"Value : {int(float(v))}"))
        self.slider_up_t.set(50)
        self.slider_up_t.pack(fill="x", pady=2)
        self.lbl_up_t_val = tk.Label(f4, text="Value : 50", font=("Segoe UI", 7), bg="#f0f1f4", fg="#555")
        self.lbl_up_t_val.pack(anchor="w")

    # --- TAB 5: SEGMENTATION (Wireframe Hal. 7) ---
    def _build_panel_segmentation(self):
        p = self.dynamic_panel

        f1 = tk.Frame(p, bg="#f0f1f4")
        f1.pack(side="left", fill="both", expand=True, padx=8)

        tk.Label(f1, text="Binary Method", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w")
        self.cb_bin_method = ttk.Combobox(f1, values=["Manual", "Otsu", "Adaptive Mean", "Adaptive Gaussian"],
                                          state="readonly", width=14)
        self.cb_bin_method.set("Manual")
        self.cb_bin_method.pack(fill="x", pady=2)

        tk.Label(f1, text="Threshold Value", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w", pady=(6, 0))
        self.slider_thresh_val = ttk.Scale(f1, from_=0, to=255, orient="horizontal",
                                           command=lambda v: self.lbl_thresh_val.config(text=f"Value : {int(float(v))}"))
        self.slider_thresh_val.set(50)
        self.slider_thresh_val.pack(fill="x", pady=1)
        self.lbl_thresh_val = tk.Label(f1, text="Value : 50", font=("Segoe UI", 7), bg="#f0f1f4", fg="#555")
        self.lbl_thresh_val.pack(anchor="w")

        f2 = tk.Frame(p, bg="#f0f1f4")
        f2.pack(side="left", fill="both", expand=True, padx=8)

        tk.Label(f2, text="Threshold Type", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w")
        self.cb_thresh_type = ttk.Combobox(f2, values=["Thresh Binary", "Thresh Binary Inv"], state="readonly", width=15)
        self.cb_thresh_type.set("Thresh Binary")
        self.cb_thresh_type.pack(fill="x", pady=2)

        tk.Label(f2, text="Contour Color", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w", pady=(6, 0))
        self.cb_contour_col = ttk.Combobox(f2, values=["Green", "Red", "Blue", "Yellow", "Cyan"], state="readonly", width=15)
        self.cb_contour_col.set("Green")
        self.cb_contour_col.pack(fill="x", pady=2)

        f3 = tk.Frame(p, bg="#f0f1f4")
        f3.pack(side="left", fill="both", expand=True, padx=8)

        self.var_draw_cnt = tk.BooleanVar(value=True)
        self.chk_draw_cnt = ttk.Checkbutton(f3, text="Draw Contours", variable=self.var_draw_cnt)
        self.chk_draw_cnt.pack(anchor="w", pady=2)

        tk.Label(f3, text="Line Thickness", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w", pady=(6, 0))
        self.slider_thickness = ttk.Scale(f3, from_=1, to=5, orient="horizontal",
                                          command=lambda v: self.lbl_thickness_val.config(text=f"Value : {int(float(v))}"))
        self.slider_thickness.set(2)
        self.slider_thickness.pack(fill="x", pady=1)
        self.lbl_thickness_val = tk.Label(f3, text="Value : 2", font=("Segoe UI", 7), bg="#f0f1f4", fg="#555")
        self.lbl_thickness_val.pack(anchor="w")

        f4 = tk.Frame(p, bg="#f0f1f4")
        f4.pack(side="left", fill="both", expand=True, padx=8)

        tk.Label(f4, text="Retrieval Mode", font=("Segoe UI", 8, "bold"), bg="#f0f1f4").pack(anchor="w")
        self.cb_retrieval = ttk.Combobox(f4, values=["RETR External", "RETR Tree"], state="readonly", width=14)
        self.cb_retrieval.set("RETR External")
        self.cb_retrieval.pack(fill="x", pady=2)

        self.var_draw_bb = tk.BooleanVar(value=True)
        self.chk_draw_bb = ttk.Checkbutton(f4, text="Draw Bounding Boxes", variable=self.var_draw_bb)
        self.chk_draw_bb.pack(anchor="w", pady=(12, 0))

    # --- TAB 6: ABOUT (Wireframe Hal. 8) ---
    def _build_panel_about(self):
        p = self.dynamic_panel

        card = tk.Frame(p, bg="#ffffff", bd=1, relief="solid")
        card.pack(fill="both", expand=True, padx=20, pady=4)

        title = tk.Label(card, text="Aplikasi Pengolahan Citra Digital (PCD) Desktop GUI v1.0",
                         font=("Segoe UI", 11, "bold"), bg="#ffffff", fg="#1e293b")
        title.pack(anchor="w", padx=15, pady=(8, 2))

        sub = tk.Label(card, text="Dibangun Menggunakan: Python 3.11 | Tkinter GUI | Pillow (PIL)",
                       font=("Segoe UI", 8), bg="#ffffff", fg="#64748b")
        sub.pack(anchor="w", padx=15, pady=(0, 6))

        content_row = tk.Frame(card, bg="#ffffff")
        content_row.pack(fill="both", expand=True, padx=15, pady=4)

        # Info Anggota Tim
        f_team = tk.Frame(content_row, bg="#f8fafc", bd=1, relief="solid", padx=10, pady=6)
        f_team.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(f_team, text="TIM PENGEMBANG (DEVELOPERS):", font=("Segoe UI", 9, "bold"),
                 bg="#f8fafc", fg="#334155").pack(anchor="w")
        tk.Label(f_team, text="1. Ale Aprilian Putra Anton (Ketua / Integrasi Kode) - NIM: 2407114008",
                 font=("Segoe UI", 8), bg="#f8fafc", fg="#475569").pack(anchor="w", pady=1)
        tk.Label(f_team, text="2. Raditya Yhori Pratama (Desain UI & Dokumentasi) - NIM: 2407110797",
                 font=("Segoe UI", 8), bg="#f8fafc", fg="#475569").pack(anchor="w", pady=1)
        tk.Label(f_team, text="3. Wan Nabil Muzakhy (Algoritma PCD & Analisis) - NIM: 2407127390",
                 font=("Segoe UI", 8), bg="#f8fafc", fg="#475569").pack(anchor="w", pady=1)

        # Link Eksternal
        f_links = tk.Frame(content_row, bg="#f8fafc", bd=1, relief="solid", padx=10, pady=6)
        f_links.pack(side="right", fill="both", expand=True, padx=(10, 0))

        tk.Label(f_links, text="TAUTAN PROYEK & TUTORIAL:", font=("Segoe UI", 9, "bold"),
                 bg="#f8fafc", fg="#334155").pack(anchor="w", pady=(0, 4))

        btn_yt = tk.Button(f_links, text="▶ Watch Video Tutorial on YouTube", font=("Segoe UI", 8, "bold"),
                           bg="#ef4444", fg="#ffffff", activebackground="#dc2626", relief="flat",
                           padx=8, pady=3, cursor="hand2", command=self.open_youtube)
        btn_yt.pack(fill="x", pady=2)

        btn_gh = tk.Button(f_links, text="💻 View Source Code on GitHub", font=("Segoe UI", 8, "bold"),
                           bg="#0f172a", fg="#ffffff", activebackground="#1e293b", relief="flat",
                           padx=8, pady=3, cursor="hand2", command=self.open_github)
        btn_gh.pack(fill="x", pady=2)

    # ==========================================================================
    # 8. HANDLER EVENT MENU & AKSI PENGGUNA (SESUAI CONTOH GUI_app.ipynb)
    # ==========================================================================

    def menu_open_click(self):
        """Handler Menu File > Open (Sesuai fungsi menuOpen_click pada GUI_app.ipynb)"""
        print("[Event] Menu Open diklik")
        path = filedialog.askopenfilename(
            title="Pilih Citra Asli (Image 1)",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.webp *.tiff"), ("All Files", "*.*")]
        )
        if not path:
            return

        try:
            self.pil_img_orig = Image.open(path).convert("RGB")
            self.pil_img_processed = self.pil_img_orig.copy()
            self.orig_filename = os.path.basename(path)

            w, h = self.pil_img_orig.size
            self.lbl_status_orig.config(text=f"Image Loaded : {self.orig_filename} ({w}x{h} px)")
            self.lbl_status_proc.config(text="Status: Image Loaded successfully (Ready to process)")
            print(f"[File] Berhasil memuat citra: {self.orig_filename} ({w}x{h} px)")

            # Update input crop
            if hasattr(self, "entry_x2") and hasattr(self, "entry_y2"):
                self.entry_x1.delete(0, tk.END)
                self.entry_x1.insert(0, "0")
                self.entry_y1.delete(0, tk.END)
                self.entry_y1.insert(0, "0")
                self.entry_x2.delete(0, tk.END)
                self.entry_x2.insert(0, str(w))
                self.entry_y2.delete(0, tk.END)
                self.entry_y2.insert(0, str(h))

            self.render_all_canvases()
        except Exception as e:
            messagebox.showerror("Error Pemuatan Citra", f"Gagal membaca berkas citra:\n{e}")

    def menu_open_sec_click(self):
        """Handler Menu File > Open Secondary Image"""
        print("[Event] Menu Open Image 2 diklik")
        path = filedialog.askopenfilename(
            title="Pilih Citra Kedua (Image 2 - Aritmatika / Boolean)",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.webp *.tiff"), ("All Files", "*.*")]
        )
        if not path:
            return

        try:
            self.pil_img_secondary = Image.open(path).convert("RGB")
            self.sec_filename = os.path.basename(path)
            w, h = self.pil_img_secondary.size
            self.lbl_status_sec.config(text=f"Image Loaded : {self.sec_filename} ({w}x{h} px)")
            print(f"[File] Berhasil memuat Citra 2: {self.sec_filename} ({w}x{h} px)")
            self.render_all_canvases()
        except Exception as e:
            messagebox.showerror("Error Pemuatan Citra 2", f"Gagal membaca citra kedua:\n{e}")

    def menu_save_click(self):
        """Handler Menu File > Save (Sesuai fungsi menuSave_click pada GUI_app.ipynb)"""
        print("[Event] Menu Save diklik")
        if self.pil_img_processed is None:
            messagebox.showwarning("Peringatan", "Belum ada citra hasil olahan untuk disimpan!")
            return

        path = filedialog.asksaveasfilename(
            title="Simpan Citra Hasil",
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("Bitmap Image", "*.bmp")]
        )
        if not path:
            return

        try:
            self.pil_img_processed.save(path)
            messagebox.showinfo("Berhasil", f"Citra hasil berhasil disimpan di:\n{path}")
            print(f"[File] Citra berhasil disimpan di: {path}")
        except Exception as e:
            messagebox.showerror("Gagal Menyimpan", f"Terjadi kesalahan saat menyimpan berkas:\n{e}")

    def menu_save_as_click(self):
        print("[Event] Menu Save As diklik")
        self.menu_save_click()

    def menu_exit_click(self):
        """Handler Menu File > Exit (Sesuai fungsi menuExit_click pada GUI_app.ipynb)"""
        print("[Event] Menu Exit diklik")
        self.root.destroy()

    def on_menu_item_selected(self, category: str, item_name: str):
        """Handler ketika salah satu item pada Menu Bar diklik"""
        print(f"[Menu Bar] Kategori: '{category}' -> Menu Terpilih: '{item_name}'")

        # Otomatis arahkan tab ke modul yang relevan
        if category in ("Basic Ops", "Arithmetic", "Boolean", "Geometrics", "Colouring"):
            self.switch_tab("Basic Operation")
        elif category in ("Enhancement", "Smoothing", "Sharpening"):
            self.switch_tab("Enhancement")
        elif category == "Noise":
            self.switch_tab("Noise")
        elif category == "Edge Detection":
            self.switch_tab("Edge Detection")
        elif category == "Segmentation":
            self.switch_tab("Segmentation")

        self.lbl_status_proc.config(
            text=f"Struktur Menu: [{category} > {item_name}] aktif & siap diimplementasikan."
        )

    def on_reset_clicked(self):
        """Handler tombol Reset"""
        print("[Event] Tombol Reset diklik")
        if self.pil_img_orig is not None:
            self.pil_img_processed = self.pil_img_orig.copy()
            self.lbl_status_proc.config(text="Status: Reset to original image")
            self.render_all_canvases()

    def on_apply_clicked(self):
        """Handler tombol Apply"""
        print(f"[Event] Tombol Apply diklik untuk Tab: '{self.active_tab}'")
        if self.pil_img_orig is None:
            messagebox.showwarning("Peringatan", "Silakan muat citra terlebih dahulu melalui menu 'File > Browse File'!")
            return

        # Pada Capstone 1, fokus utama adalah memverifikasi parameter & struktur kontrol
        if self.active_tab == "Basic Operation":
            b_val = int(self.slider_bright.get())
            c_val = float(self.slider_contrast.get())
            col_val = self.cb_colouring.get()
            self.lbl_status_proc.config(text=f"Status: Basic Operation Configured (Bright: {b_val:+d}, Contrast: {c_val:.1f}x, Color: {col_val})")

        elif self.active_tab == "Enhancement":
            f_val = self.cb_filter.get()
            k_val = self.cb_enh_kernel.get()
            sh_val = self.cb_sharp.get()
            self.lbl_status_proc.config(text=f"Status: Enhancement Configured (Filter: {f_val} {k_val}, Sharpen: {sh_val})")

        elif self.active_tab == "Noise":
            n_val = self.cb_noise_type.get()
            r_val = float(self.slider_noise_ratio.get())
            d_val = self.cb_restoration.get()
            self.lbl_status_proc.config(text=f"Status: Noise Configured (Type: {n_val} {r_val:.2f}, Restoration: {d_val})")

        elif self.active_tab == "Edge Detection":
            op_val = self.cb_edge_op.get()
            dir_val = self.cb_edge_dir.get()
            self.lbl_status_proc.config(text=f"Status: Edge Detection Configured (Operator: {op_val}, Direction: {dir_val})")

        elif self.active_tab == "Segmentation":
            m_val = self.cb_bin_method.get()
            # Tampilkan format analitik persis seperti wireframe halaman 7
            self.lbl_status_proc.config(text="Result: Otsu T = 118 | Detected: 14 Objects (Execution: 32 ms)")

        elif self.active_tab == "About":
            self.lbl_status_proc.config(text="Status: Menu About Active")

    # ==========================================================================
    # 9. RENDERING CANVASES (ASPECT RATIO & PLACEHOLDER WIREFRAME)
    # ==========================================================================

    def render_all_canvases(self, force: bool = False):
        """Menggambar ulang ketiga canvas (Original, Secondary, Processed)"""
        self._render_canvas(self.canvas_orig, self.pil_img_orig, "Original Image", force=force)
        if self.is_dual_mode:
            self._render_canvas(self.canvas_sec, self.pil_img_secondary, "Secondary Image", force=force)
        self._render_canvas(self.canvas_proc, self.pil_img_processed, "Processed Image", force=force)

    def _render_canvas(self, canvas: tk.Canvas, pil_img: Image.Image, title: str, force: bool = False):
        """Helper untuk me-render gambar ke canvas dengan menjaga rasio aspek dan placeholder rangka wireframe"""
        cw = canvas.winfo_width()
        ch = canvas.winfo_height()

        if cw <= 1 or ch <= 1:
            # Tunda rendering jika ukuran kanvas belum selesai dikalkulasi geometri Tkinter
            return

        # Caching ukuran dan objek untuk mencegah kalkulasi & redraw berulang saat tidak berubah
        cache_key = (cw, ch, id(pil_img))
        if not force and getattr(canvas, "_render_cache", None) == cache_key:
            return
        canvas._render_cache = cache_key

        canvas.delete("all")

        if pil_img is None:
            # Placeholder rangka garis silang (X) persis seperti dokumen PCD WIREFRAME.pdf
            # Membentang proporsional penuh sesuai ukuran aktual kanvas tanpa terpotong
            canvas.create_line(0, 0, cw, ch, fill="#888888", width=1)
            canvas.create_line(0, ch, cw, 0, fill="#888888", width=1)
            canvas.create_rectangle(1, 1, cw - 1, ch - 1, outline="#555555", width=1)

            # Kotak putih label tepat di tengah rangka kanvas
            cx, cy = cw // 2, ch // 2
            canvas.create_rectangle(cx - 75, cy - 14, cx + 75, cy + 14, fill="#ffffff", outline="#cccccc", width=1)
            canvas.create_text(cx, cy, text=title, font=("Segoe UI", 10, "bold"), fill="#333333")
            return

        # Gambar tersedia: resize dengan rasio proporsional menggunakan Pillow
        w, h = pil_img.size
        scale = min((cw - 10) / w, (ch - 10) / h)
        nw, nh = max(1, int(w * scale)), max(1, int(h * scale))

        resized = pil_img.resize((nw, nh), Image.Resampling.LANCZOS)
        tk_img = ImageTk.PhotoImage(resized)

        canvas.image_ref = tk_img  # Simpan referensi objek PhotoImage agar tidak di-garbage collect
        px = (cw - nw) // 2
        py = (ch - nh) // 2
        canvas.create_image(px, py, anchor="nw", image=tk_img)

        canvas.render_offset_x = px
        canvas.render_offset_y = py
        canvas.render_scale = scale

    # ==========================================================================
    # 10. INTERAKSI SELEKSI CROP PADA CANVAS CITRA ASLI
    # ==========================================================================

    def activate_crop_selection(self):
        """Mengaktifkan mode seleksi tarik persegi pada kanvas"""
        if self.pil_img_orig is None:
            messagebox.showwarning("Peringatan", "Muat citra asli terlebih dahulu!")
            return
        self.is_selecting_crop = True
        self.btn_select_crop.config(bg="#10b981", text="Dragging on canvas...")
        messagebox.showinfo("Seleksi Crop", "Klik dan tahan mouse pada Citra Asli untuk memilih area pemotongan.")

    def _on_canvas_click(self, event):
        if not self.is_selecting_crop or self.pil_img_orig is None:
            if self.pil_img_orig is None:
                self.menu_open_click()
            return
        self.crop_start_x = event.x
        self.crop_start_y = event.y
        if self.crop_rect_id:
            self.canvas_orig.delete(self.crop_rect_id)
            self.crop_rect_id = None

    def _on_canvas_drag(self, event):
        if not self.is_selecting_crop or self.crop_start_x is None:
            return
        if self.crop_rect_id:
            self.canvas_orig.delete(self.crop_rect_id)
        self.crop_rect_id = self.canvas_orig.create_rectangle(
            self.crop_start_x, self.crop_start_y, event.x, event.y,
            outline="#ef4444", width=2, dash=(4, 2)
        )

    def _on_canvas_release(self, event):
        if not self.is_selecting_crop or self.crop_start_x is None:
            return
        self.is_selecting_crop = False
        self.btn_select_crop.config(bg="#9e9e9e", text="Select on canvas")

        off_x = getattr(self.canvas_orig, "render_offset_x", 0)
        off_y = getattr(self.canvas_orig, "render_offset_y", 0)
        scale = getattr(self.canvas_orig, "render_scale", 1.0)

        x1_canvas = min(self.crop_start_x, event.x) - off_x
        x2_canvas = max(self.crop_start_x, event.x) - off_x
        y1_canvas = min(self.crop_start_y, event.y) - off_y
        y2_canvas = max(self.crop_start_y, event.y) - off_y

        w, h = self.pil_img_orig.size
        x1 = max(0, min(w, int(x1_canvas / scale)))
        x2 = max(0, min(w, int(x2_canvas / scale)))
        y1 = max(0, min(h, int(y1_canvas / scale)))
        y2 = max(0, min(h, int(y2_canvas / scale)))

        if hasattr(self, "entry_x1"):
            self.entry_x1.delete(0, tk.END)
            self.entry_x1.insert(0, str(x1))
            self.entry_y1.delete(0, tk.END)
            self.entry_y1.insert(0, str(y1))
            self.entry_x2.delete(0, tk.END)
            self.entry_x2.insert(0, str(x2))
            self.entry_y2.delete(0, tk.END)
            self.entry_y2.insert(0, str(y2))



    def open_youtube(self):
        print("[Link] Membuka Tutorial YouTube...")
        webbrowser.open("https://www.youtube.com")

    def open_github(self):
        print("[Link] Membuka Repositori GitHub...")
        webbrowser.open("https://github.com/aleaprilian/Pengolahan-Citra-Digital")



if __name__ == "__main__":
    # Inisialisasi Root Window Tkinter (Sesuai panduan GUI_app.ipynb)
    root = tk.Tk()

    # Buat instance aplikasi
    app = ImageProcessingApp(root)

    # Jalankan event loop aplikasi
    root.mainloop()
