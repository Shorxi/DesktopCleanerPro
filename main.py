
import os
import sys
import time
import json
import threading
from pathlib import Path
import webbrowser
from datetime import datetime

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    TK_AVAILABLE = True
except ImportError:
    TK_AVAILABLE = False
    sys.exit(1)

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from cleaner_engine import get_desktop_path, scan_desktop, clean_desktop, get_categories, get_fallback_name
from languages import TRANSLATIONS

COLORS = {
    "bg": "#0A0A0F",
    "bg_card": "#15151E",
    "bg_card_hover": "#1E1E2A",
    "bg_input": "#1A1A27",
    "primary": "#7C3AED",
    "primary_hover": "#8B5CF6",
    "secondary": "#06B6D4",
    "accent": "#F59E0B",
    "success": "#10B981",
    "danger": "#EF4444",
    "text": "#F8FAFC",
    "text_muted": "#94A3B8",
    "text_dim": "#64748B",
    "border": "#262637",
    "chart": ["#7C3AED", "#06B6D4", "#F59E0B", "#10B981", "#EF4444", "#8B5CF6", "#EC4899", "#14B8A6", "#F97316", "#6366F1", "#A3E635"]
}

FONTS = {
    "title": ("Segoe UI", 24, "bold"),
    "subtitle": ("Segoe UI", 14, "bold"),
    "body": ("Segoe UI", 10),
    "body_bold": ("Segoe UI", 10, "bold"),
    "small": ("Segoe UI", 9),
    "mono": ("Consolas", 10)
}

class AnimatedButton(tk.Canvas):
    def __init__(self, parent, text, command, width=200, height=45, bg_color=COLORS["primary"], fg_color=COLORS["text"], **kwargs):
        super().__init__(parent, width=width, height=height, bg=COLORS["bg_card"], highlightthickness=0, **kwargs)
        self.command = command
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.text = text
        self.width = width
        self.height = height
        self.is_hovered = False
        self.is_pressed = False
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.draw_button(bg_color)
        
    def draw_button(self, color):
        self.delete("all")
        self.create_oval(2, 2, 20, self.height-2, fill=color, outline=color)
        self.create_oval(self.width-20, 2, self.width-2, self.height-2, fill=color, outline=color)
        self.create_rectangle(10, 2, self.width-10, self.height-2, fill=color, outline=color)
        self.create_text(self.width//2, self.height//2, text=self.text, fill=self.fg_color, font=FONTS["body_bold"])
        if self.is_hovered:
            self.create_oval(4, 4, 22, self.height-4, fill="", outline=color, width=2)
            self.create_oval(self.width-22, 4, self.width-4, self.height-4, fill="", outline=color, width=2)
    
    def set_text(self, new_text):
        self.text = new_text
        self.draw_button(COLORS["primary_hover"] if self.is_hovered else self.bg_color)
    
    def on_enter(self, e):
        self.is_hovered = True
        self.draw_button(COLORS["primary_hover"])
        self.config(cursor="hand2")
    def on_leave(self, e):
        self.is_hovered = False
        self.draw_button(self.bg_color)
    def on_click(self, e):
        self.is_pressed = True
        self.draw_button("#6D28D9")
    def on_release(self, e):
        self.is_pressed = False
        self.draw_button(COLORS["primary_hover"] if self.is_hovered else self.bg_color)
        if self.command:
            self.command()

class ToggleSwitch(tk.Canvas):
    def __init__(self, parent, command=None, width=50, height=26, **kwargs):
        super().__init__(parent, width=width, height=height, bg=COLORS["bg_card"], highlightthickness=0, **kwargs)
        self.command = command
        self.state = False
        self.width = width
        self.height = height
        self.bind("<Button-1>", self.toggle)
        self.draw()
    def draw(self):
        self.delete("all")
        bg = COLORS["success"] if self.state else COLORS["border"]
        self.create_oval(0, 0, self.height, self.height, fill=bg, outline=bg)
        self.create_oval(self.width-self.height, 0, self.width, self.height, fill=bg, outline=bg)
        self.create_rectangle(self.height//2, 0, self.width-self.height//2, self.height, fill=bg, outline=bg)
        x = self.width - self.height + 2 if self.state else 2
        self.create_oval(x, 2, x+self.height-4, self.height-2, fill="white", outline="white")
    def toggle(self, e=None):
        self.state = not self.state
        self.draw()
        if self.command:
            self.command(self.state)
    def set(self, value):
        self.state = bool(value)
        self.draw()

class DesktopCleanerApp:
    def __init__(self, root):
        self.root = root
        self.config_path = Path(__file__).parent / "config.json"
        self.current_lang = self.load_language()
        
        self.root.title(self.tr("app_title"))
        self.root.geometry("1150x780")
        self.root.configure(bg=COLORS["bg"])
        self.root.minsize(1000, 650)
        
        self.desktop_path = get_desktop_path()
        self.scan_data = None
        self.auto_clean_enabled = False
        self.auto_clean_interval = 30
        self.auto_job = None
        
        # Pre-init refs
        self.search_tree = None
        self.clean_tree = None
        self.recent_list = None
        
        self.setup_ui()
        self.refresh_scan()
        self.update_system_stats()
    
    def load_language(self):
        try:
            if self.config_path.exists():
                data = json.loads(self.config_path.read_text(encoding="utf-8"))
                lang = data.get("language", "de")
                if lang in TRANSLATIONS:
                    return lang
        except:
            pass
        return "de"
    
    def save_language(self):
        try:
            self.config_path.write_text(json.dumps({"language": self.current_lang}, ensure_ascii=False, indent=2), encoding="utf-8")
        except:
            pass
    
    def tr(self, key, **kwargs):
        template = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["de"]).get(key, key)
        try:
            return template.format(**kwargs) if kwargs else template
        except:
            return template
    
    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg=COLORS["bg"], height=70)
        header.pack(fill="x", padx=20, pady=(15,0))
        header.pack_propagate(False)
        
        left_header = tk.Frame(header, bg=COLORS["bg"])
        left_header.pack(side="left", fill="y")
        
        self.header_title_label = tk.Label(left_header, text="✨ DesktopCleaner Pro", font=FONTS["title"], bg=COLORS["bg"], fg=COLORS["text"])
        self.header_title_label.pack(anchor="w")
        self.path_label = tk.Label(left_header, text=f"📁 {self.desktop_path}", font=FONTS["small"], bg=COLORS["bg"], fg=COLORS["text_muted"])
        self.path_label.pack(anchor="w", pady=(2,0))
        
        right_header = tk.Frame(header, bg=COLORS["bg"])
        right_header.pack(side="right")
        
        self.file_count_label = tk.Label(right_header, text="0", font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["secondary"], padx=12, pady=6)
        self.file_count_label.pack()
        
        # Main
        main = tk.Frame(self.root, bg=COLORS["bg"])
        main.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Sidebar
        sidebar = tk.Frame(main, bg=COLORS["bg_card"], width=190)
        sidebar.pack(side="left", fill="y", padx=(0,15))
        sidebar.pack_propagate(False)
        
        self.nav_buttons = {}
        nav_items = [
            ("nav_dashboard", "dashboard"),
            ("nav_clean", "clean"),
            ("nav_search", "search"),
            ("nav_stats", "stats"),
            ("nav_settings", "settings")
        ]
        self.current_page = "dashboard"
        for key, page in nav_items:
            btn = tk.Button(sidebar, text=self.tr(key), font=FONTS["body"], bg=COLORS["bg_card"], fg=COLORS["text_muted"],
                           activebackground=COLORS["bg_card_hover"], activeforeground=COLORS["text"],
                           bd=0, relief="flat", anchor="w", padx=20, pady=12,
                           command=lambda k=page: self.switch_page(k))
            btn.pack(fill="x", pady=2, padx=5)
            self.nav_buttons[page] = btn
        self.nav_buttons["dashboard"].config(bg=COLORS["primary"], fg="white")
        
        # System stats
        sidebar_bottom = tk.Frame(sidebar, bg=COLORS["bg_card"])
        sidebar_bottom.pack(side="bottom", fill="x", padx=10, pady=15)
        
        self.sidebar_system_label = tk.Label(sidebar_bottom, text=self.tr("system_section"), font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text"])
        self.sidebar_system_label.pack(anchor="w", pady=(0,8))
        
        self.ram_label = tk.Label(sidebar_bottom, text="RAM: --%", font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["text_muted"])
        self.ram_label.pack(anchor="w")
        self.ram_bar = ttk.Progressbar(sidebar_bottom, length=160, mode='determinate')
        self.ram_bar.pack(pady=(2,10))
        
        self.cpu_label = tk.Label(sidebar_bottom, text="CPU: --%", font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["text_muted"])
        self.cpu_label.pack(anchor="w")
        self.cpu_bar = ttk.Progressbar(sidebar_bottom, length=160, mode='determinate')
        self.cpu_bar.pack(pady=(2,10))
        
        self.disk_label = tk.Label(sidebar_bottom, text="Disk: --%", font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["text_muted"])
        self.disk_label.pack(anchor="w")
        self.disk_bar = ttk.Progressbar(sidebar_bottom, length=160, mode='determinate')
        self.disk_bar.pack(pady=(2,5))
        
        # Content
        self.content = tk.Frame(main, bg=COLORS["bg"])
        self.content.pack(side="right", fill="both", expand=True)
        
        self.pages = {}
        for key in ["dashboard", "clean", "search", "stats", "settings"]:
            frame = tk.Frame(self.content, bg=COLORS["bg"])
            self.pages[key] = frame
        
        self.setup_dashboard()
        self.setup_clean_page()
        self.setup_search_page()
        self.setup_stats_page()
        self.setup_settings_page()
        
        self.pages["dashboard"].pack(fill="both", expand=True)
    
    def switch_page(self, page_key):
        for k, btn in self.nav_buttons.items():
            btn.config(bg=COLORS["bg_card"], fg=COLORS["text_muted"])
        self.nav_buttons[page_key].config(bg=COLORS["primary"], fg="white")
        for f in self.pages.values():
            f.pack_forget()
        self.current_page = page_key
        self.pages[page_key].pack(fill="both", expand=True)
        if page_key == "stats":
            self.update_charts()
        elif page_key == "dashboard":
            self.refresh_scan()
    
    def setup_dashboard(self):
        page = self.pages["dashboard"]
        welcome = tk.Frame(page, bg=COLORS["bg_card"], bd=0)
        welcome.pack(fill="x", pady=(0,15))
        self.dashboard_welcome_title_label = tk.Label(welcome, text=self.tr("welcome_title"), font=FONTS["subtitle"], bg=COLORS["bg_card"], fg=COLORS["text"])
        self.dashboard_welcome_title_label.pack(anchor="w", padx=20, pady=(15,5))
        self.dashboard_welcome_sub_label = tk.Label(welcome, text=self.tr("welcome_sub"), font=FONTS["body"], bg=COLORS["bg_card"], fg=COLORS["text_muted"])
        self.dashboard_welcome_sub_label.pack(anchor="w", padx=20, pady=(0,15))
        
        grid = tk.Frame(page, bg=COLORS["bg"])
        grid.pack(fill="x", pady=5)
        
        self.stat_cards = {}
        self.stat_title_labels = {}
        stats = [
            ("stat_total_files", "0", COLORS["secondary"]),
            ("stat_storage", "0 MB", COLORS["accent"]),
            ("stat_categories", f"{len(get_categories(self.current_lang))+1}", COLORS["primary"]),
            ("stat_last_scan", self.tr("just_now"), COLORS["success"])
        ]
        for i, (title_key, value, color) in enumerate(stats):
            card = tk.Frame(grid, bg=COLORS["bg_card"], width=200, height=90)
            card.grid(row=0, column=i, padx=(0,12) if i<3 else 0, sticky="ew")
            card.grid_propagate(False)
            grid.columnconfigure(i, weight=1)
            title_lbl = tk.Label(card, text=self.tr(title_key), font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["text_dim"])
            title_lbl.pack(anchor="w", padx=15, pady=(12,2))
            val_label = tk.Label(card, text=value, font=("Segoe UI", 18, "bold"), bg=COLORS["bg_card"], fg=color)
            val_label.pack(anchor="w", padx=15)
            tk.Frame(card, bg=color, height=3).pack(fill="x", side="bottom", pady=(10,0))
            self.stat_cards[title_key] = val_label
            self.stat_title_labels[title_key] = title_lbl
        
        middle = tk.Frame(page, bg=COLORS["bg"])
        middle.pack(fill="both", expand=True, pady=15)
        
        left = tk.Frame(middle, bg=COLORS["bg_card"])
        left.pack(side="left", fill="both", expand=True, padx=(0,10))
        
        self.quick_clean_title_label = tk.Label(left, text=self.tr("quick_clean_title"), font=FONTS["subtitle"], bg=COLORS["bg_card"], fg=COLORS["text"])
        self.quick_clean_title_label.pack(anchor="w", padx=20, pady=(20,10))
        self.quick_clean_desc_label = tk.Label(left, text=self.tr("quick_clean_desc"), font=FONTS["body"], bg=COLORS["bg_card"], fg=COLORS["text_muted"], wraplength=350, justify="left")
        self.quick_clean_desc_label.pack(anchor="w", padx=20)
        
        btn_frame = tk.Frame(left, bg=COLORS["bg_card"])
        btn_frame.pack(pady=25)
        self.dashboard_clean_btn = AnimatedButton(btn_frame, self.tr("quick_clean_btn"), self.start_cleaning, width=260, height=50, bg_color=COLORS["primary"])
        self.dashboard_clean_btn.pack()
        
        self.dashboard_progress = ttk.Progressbar(left, mode='determinate', length=300)
        self.dashboard_progress.pack(pady=(15,5))
        self.dashboard_status = tk.Label(left, text=self.tr("ready_to_clean"), font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["text_muted"])
        self.dashboard_status.pack()
        
        right = tk.Frame(middle, bg=COLORS["bg_card"])
        right.pack(side="right", fill="both", expand=True, padx=(5,0))
        self.recent_title_label = tk.Label(right, text=self.tr("recent_files_title"), font=FONTS["subtitle"], bg=COLORS["bg_card"], fg=COLORS["text"])
        self.recent_title_label.pack(anchor="w", padx=20, pady=(20,10))
        
        list_frame = tk.Frame(right, bg=COLORS["bg_card"])
        list_frame.pack(fill="both", expand=True, padx=15, pady=(0,15))
        self.recent_list = tk.Listbox(list_frame, bg=COLORS["bg_input"], fg=COLORS["text"], bd=0, highlightthickness=0, font=FONTS["small"], selectbackground=COLORS["primary"])
        self.recent_list.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.recent_list.yview, bg=COLORS["bg_card"])
        scrollbar.pack(side="right", fill="y")
        self.recent_list.config(yscrollcommand=scrollbar.set)
    
    def setup_clean_page(self):
        page = self.pages["clean"]
        self.clean_center_title_label = tk.Label(page, text=self.tr("clean_center_title"), font=FONTS["title"], bg=COLORS["bg"], fg=COLORS["text"])
        self.clean_center_title_label.pack(anchor="w", pady=(0,5))
        self.clean_center_desc_label = tk.Label(page, text=self.tr("clean_center_desc"), font=FONTS["body"], bg=COLORS["bg"], fg=COLORS["text_muted"])
        self.clean_center_desc_label.pack(anchor="w", pady=(0,20))
        
        preview_frame = tk.Frame(page, bg=COLORS["bg_card"])
        preview_frame.pack(fill="x", pady=(0,15))
        self.target_folders_label = tk.Label(preview_frame, text=self.tr("target_folders_label"), font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text"])
        self.target_folders_label.pack(anchor="w", padx=20, pady=(15,10))
        self.category_flow = tk.Frame(preview_frame, bg=COLORS["bg_card"])
        self.category_flow.pack(fill="x", padx=20, pady=(0,15))
        
        list_container = tk.Frame(page, bg=COLORS["bg_card"])
        list_container.pack(fill="both", expand=True, pady=(0,15))
        header = tk.Frame(list_container, bg=COLORS["bg_card"])
        header.pack(fill="x", padx=20, pady=(15,10))
        self.files_to_sort_title_label = tk.Label(header, text=self.tr("files_to_sort_label"), font=FONTS["subtitle"], bg=COLORS["bg_card"], fg=COLORS["text"])
        self.files_to_sort_title_label.pack(side="left")
        self.clean_count_label = tk.Label(header, text="0", font=FONTS["body"], bg=COLORS["bg_card"], fg=COLORS["secondary"])
        self.clean_count_label.pack(side="right")
        
        tree_frame = tk.Frame(list_container, bg=COLORS["bg_card"])
        tree_frame.pack(fill="both", expand=True, padx=15, pady=(0,15))
        columns = ("name", "category", "size", "ext")
        self.clean_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        self.clean_tree.heading("name", text=self.tr("col_filename"))
        self.clean_tree.heading("category", text=self.tr("col_target"))
        self.clean_tree.heading("size", text=self.tr("col_size"))
        self.clean_tree.heading("ext", text=self.tr("col_type"))
        self.clean_tree.column("name", width=350)
        self.clean_tree.column("category", width=120)
        self.clean_tree.column("size", width=80)
        self.clean_tree.column("ext", width=60)
        self.clean_tree.pack(side="left", fill="both", expand=True)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.clean_tree.yview)
        vsb.pack(side="right", fill="y")
        self.clean_tree.configure(yscrollcommand=vsb.set)
        
        action_bar = tk.Frame(page, bg=COLORS["bg"])
        action_bar.pack(fill="x")
        self.clean_progress = ttk.Progressbar(action_bar, mode='determinate', length=400)
        self.clean_progress.pack(side="left", padx=(0,15))
        self.clean_btn = AnimatedButton(action_bar, self.tr("clean_start_btn"), self.start_cleaning, width=220, height=45)
        self.clean_btn.pack(side="left")
        self.clean_log = tk.Label(action_bar, text="", font=FONTS["small"], bg=COLORS["bg"], fg=COLORS["text_muted"])
        self.clean_log.pack(side="left", padx=15)
    
    def setup_search_page(self):
        page = self.pages["search"]
        self.search_title_label = tk.Label(page, text=self.tr("search_title"), font=FONTS["title"], bg=COLORS["bg"], fg=COLORS["text"])
        self.search_title_label.pack(anchor="w", pady=(0,10))
        
        # Results FIRST
        results_frame = tk.Frame(page, bg=COLORS["bg_card"])
        results_frame.pack(fill="both", expand=True, side="bottom")
        self.search_results_title_label = tk.Label(results_frame, text=self.tr("search_results_title"), font=FONTS["subtitle"], bg=COLORS["bg_card"], fg=COLORS["text"])
        self.search_results_title_label.pack(anchor="w", padx=20, pady=(15,10))
        tree_frame = tk.Frame(results_frame, bg=COLORS["bg_card"])
        tree_frame.pack(fill="both", expand=True, padx=15, pady=(0,15))
        columns = ("name", "category", "size", "path")
        self.search_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.search_tree.heading("name", text=self.tr("col_name"))
        self.search_tree.heading("category", text=self.tr("col_category"))
        self.search_tree.heading("size", text=self.tr("col_size"))
        self.search_tree.heading("path", text=self.tr("col_path"))
        self.search_tree.column("name", width=250)
        self.search_tree.column("category", width=100)
        self.search_tree.column("size", width=80)
        self.search_tree.column("path", width=400)
        self.search_tree.pack(side="left", fill="both", expand=True)
        self.search_tree.bind("<Double-1>", self.open_selected_file)
        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.search_tree.yview)
        sb.pack(side="right", fill="y")
        self.search_tree.configure(yscrollcommand=sb.set)
        
        search_bar = tk.Frame(page, bg=COLORS["bg_card"], height=60)
        search_bar.pack(fill="x", pady=(0,15), side="top")
        search_bar.pack_propagate(False)
        tk.Label(search_bar, text="🔎", font=("Segoe UI", 16), bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(side="left", padx=(20,10), pady=15)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_bar, textvariable=self.search_var, font=FONTS["body"], bg=COLORS["bg_input"], fg=COLORS["text"], bd=0, insertbackground=COLORS["text"], relief="flat")
        self.search_entry.pack(side="left", fill="both", expand=True, pady=15, padx=(0,20))
        self.search_entry.insert(0, self.tr("search_placeholder"))
        self.search_entry.bind("<FocusIn>", lambda e: self.search_entry.delete(0, 'end') if self.search_entry.get() == self.tr("search_placeholder") else None)
        self.search_var.trace_add("write", self.on_search)
        
        search_actions = tk.Frame(page, bg=COLORS["bg"])
        search_actions.pack(fill="x", pady=10, side="bottom")
        self.search_show_btn = tk.Button(search_actions, text=self.tr("search_show_explorer"), command=self.show_in_explorer, bg=COLORS["bg_card"], fg=COLORS["text"], bd=0, padx=12, pady=6)
        self.search_show_btn.pack(side="left", padx=5)
        self.search_open_btn = tk.Button(search_actions, text=self.tr("search_open"), command=self.open_selected_file, bg=COLORS["bg_card"], fg=COLORS["text"], bd=0, padx=12, pady=6)
        self.search_open_btn.pack(side="left", padx=5)
    
    def setup_stats_page(self):
        page = self.pages["stats"]
        self.stats_title_label = tk.Label(page, text=self.tr("stats_title"), font=FONTS["title"], bg=COLORS["bg"], fg=COLORS["text"])
        self.stats_title_label.pack(anchor="w", pady=(0,15))
        if not MATPLOTLIB_AVAILABLE:
            tk.Label(page, text="Matplotlib missing - pip install matplotlib", bg=COLORS["bg"], fg=COLORS["danger"]).pack()
            return
        chart_container = tk.Frame(page, bg=COLORS["bg"])
        chart_container.pack(fill="both", expand=True)
        left_chart = tk.Frame(chart_container, bg=COLORS["bg_card"])
        left_chart.pack(side="left", fill="both", expand=True, padx=(0,10))
        self.stats_dist_title_label = tk.Label(left_chart, text=self.tr("stats_dist_title"), font=FONTS["subtitle"], bg=COLORS["bg_card"], fg=COLORS["text"])
        self.stats_dist_title_label.pack(anchor="w", padx=20, pady=(15,5))
        self.fig1 = Figure(figsize=(5,4), dpi=100, facecolor=COLORS["bg_card"])
        self.ax1 = self.fig1.add_subplot(111)
        self.ax1.set_facecolor(COLORS["bg_card"])
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=left_chart)
        self.canvas1.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        right_chart = tk.Frame(chart_container, bg=COLORS["bg_card"])
        right_chart.pack(side="right", fill="both", expand=True, padx=(5,0))
        self.stats_storage_title_label = tk.Label(right_chart, text=self.tr("stats_storage_title"), font=FONTS["subtitle"], bg=COLORS["bg_card"], fg=COLORS["text"])
        self.stats_storage_title_label.pack(anchor="w", padx=20, pady=(15,5))
        self.fig2 = Figure(figsize=(5,4), dpi=100, facecolor=COLORS["bg_card"])
        self.ax2 = self.fig2.add_subplot(111)
        self.ax2.set_facecolor(COLORS["bg_card"])
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=right_chart)
        self.canvas2.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def setup_settings_page(self):
        page = self.pages["settings"]
        self.settings_title_label = tk.Label(page, text=self.tr("settings_title"), font=FONTS["title"], bg=COLORS["bg"], fg=COLORS["text"])
        self.settings_title_label.pack(anchor="w", pady=(0,15))
        
        # Language Card - NEW
        lang_card = tk.Frame(page, bg=COLORS["bg_card"])
        lang_card.pack(fill="x", pady=(0,15))
        self.lang_title_label = tk.Label(lang_card, text=self.tr("lang_title"), font=FONTS["subtitle"], bg=COLORS["bg_card"], fg=COLORS["text"])
        self.lang_title_label.pack(anchor="w", padx=20, pady=(15,5))
        self.lang_desc_label = tk.Label(lang_card, text=self.tr("lang_desc"), font=FONTS["body"], bg=COLORS["bg_card"], fg=COLORS["text_muted"], wraplength=600, justify="left")
        self.lang_desc_label.pack(anchor="w", padx=20, pady=(0,15))
        lang_row = tk.Frame(lang_card, bg=COLORS["bg_card"])
        lang_row.pack(fill="x", padx=20, pady=(0,20))
        self.lang_label_label = tk.Label(lang_row, text=self.tr("lang_label"), font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text"])
        self.lang_label_label.pack(side="left")
        self.lang_var = tk.StringVar(value=self.tr("lang_de") if self.current_lang=="de" else self.tr("lang_en"))
        lang_combo = ttk.Combobox(lang_row, textvariable=self.lang_var, values=[self.tr("lang_de"), self.tr("lang_en")], width=15, state="readonly")
        lang_combo.pack(side="left", padx=15)
        lang_combo.bind("<<ComboboxSelected>>", self.on_language_change)
        
        # Auto Clean Card
        auto_card = tk.Frame(page, bg=COLORS["bg_card"])
        auto_card.pack(fill="x", pady=(0,15))
        self.auto_clean_title_label = tk.Label(auto_card, text=self.tr("auto_clean_title"), font=FONTS["subtitle"], bg=COLORS["bg_card"], fg=COLORS["text"])
        self.auto_clean_title_label.pack(anchor="w", padx=20, pady=(15,5))
        self.auto_clean_desc_label = tk.Label(auto_card, text=self.tr("auto_clean_desc"), font=FONTS["body"], bg=COLORS["bg_card"], fg=COLORS["text_muted"], wraplength=600, justify="left")
        self.auto_clean_desc_label.pack(anchor="w", padx=20, pady=(0,15))
        toggle_row = tk.Frame(auto_card, bg=COLORS["bg_card"])
        toggle_row.pack(fill="x", padx=20, pady=(0,20))
        self.auto_clean_enable_label = tk.Label(toggle_row, text=self.tr("auto_clean_enable"), font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text"])
        self.auto_clean_enable_label.pack(side="left")
        self.auto_toggle = ToggleSwitch(toggle_row, command=self.on_auto_toggle)
        self.auto_toggle.pack(side="left", padx=15)
        self.interval_label = tk.Label(toggle_row, text=self.tr("interval_label"), font=FONTS["body"], bg=COLORS["bg_card"], fg=COLORS["text_muted"])
        self.interval_label.pack(side="left", padx=(30,10))
        self.interval_var = tk.StringVar(value=self.tr("interval_30m"))
        self.interval_combo = ttk.Combobox(toggle_row, textvariable=self.interval_var, values=[self.tr("interval_5m"), self.tr("interval_15m"), self.tr("interval_30m"), self.tr("interval_1h"), self.tr("interval_2h")], width=15, state="readonly")
        self.interval_combo.pack(side="left")
        self.interval_combo.bind("<<ComboboxSelected>>", self.on_interval_change)
        self.auto_status_label = tk.Label(auto_card, text=self.tr("auto_disabled"), font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["text_dim"])
        self.auto_status_label.pack(anchor="w", padx=20, pady=(0,15))
        
        # Info Card
        info_card = tk.Frame(page, bg=COLORS["bg_card"])
        info_card.pack(fill="x", pady=(0,15))
        self.about_title_label = tk.Label(info_card, text=self.tr("about_title"), font=FONTS["subtitle"], bg=COLORS["bg_card"], fg=COLORS["text"])
        self.about_title_label.pack(anchor="w", padx=20, pady=(15,10))
        self.about_text_label = tk.Label(info_card, text=self.tr("about_text"), font=FONTS["body"], bg=COLORS["bg_card"], fg=COLORS["text_muted"], justify="left", wraplength=650)
        self.about_text_label.pack(anchor="w", padx=20, pady=(0,15))
    
    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def refresh_scan(self):
        self.scan_data = scan_desktop(self.desktop_path, lang=self.current_lang)
        files = self.scan_data["files"]
        by_type = self.scan_data["by_type"]
        total_size = self.scan_data["total_size"]
        
        self.file_count_label.config(text=self.tr("file_count_header", count=len(files), size=self.format_size(total_size)))
        
        if "stat_total_files" in self.stat_cards:
            self.stat_cards["stat_total_files"].config(text=str(len(files)))
            self.stat_cards["stat_storage"].config(text=self.format_size(total_size))
            self.stat_cards["stat_last_scan"].config(text=datetime.now().strftime("%H:%M:%S"))
        
        if self.recent_list is not None:
            try:
                self.recent_list.delete(0, tk.END)
                for f in sorted(files, key=lambda x: x["modified"], reverse=True)[:20]:
                    self.recent_list.insert(tk.END, f" {f['category'][:4]} | {f['name'][:40]}")
            except:
                pass
        
        if self.clean_tree is not None:
            try:
                self.clean_tree.delete(*self.clean_tree.get_children())
                for f in files:
                    self.clean_tree.insert("", "end", values=(f["name"], f["category"], self.format_size(f["size"]), f["ext"]))
            except:
                pass
        
        if hasattr(self, 'clean_count_label'):
            self.clean_count_label.config(text=self.tr("files_to_sort_count", count=len(files)))
        
        if hasattr(self, 'category_flow'):
            for widget in self.category_flow.winfo_children():
                widget.destroy()
            for cat, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
                lbl = tk.Label(self.category_flow, text=f"{cat} ({count})", bg=COLORS["primary"], fg="white", font=FONTS["small"], padx=8, pady=4, bd=0)
                lbl.pack(side="left", padx=4, pady=4)
        
        self.on_search()
    
    def update_system_stats(self):
        if PSUTIL_AVAILABLE:
            try:
                vm = psutil.virtual_memory()
                self.ram_label.config(text=self.tr("ram_label", percent=vm.percent))
                self.ram_bar["value"] = vm.percent
                cpu = psutil.cpu_percent(interval=0.1)
                self.cpu_label.config(text=self.tr("cpu_label", percent=int(cpu)))
                self.cpu_bar["value"] = cpu
                disk = psutil.disk_usage(str(self.desktop_path))
                disk_percent = (disk.used / disk.total) * 100
                self.disk_label.config(text=self.tr("disk_label", percent=f"{disk_percent:.1f}"))
                self.disk_bar["value"] = disk_percent
            except:
                pass
        self.root.after(2000, self.update_system_stats)
    
    def update_charts(self):
        if not MATPLOTLIB_AVAILABLE or not self.scan_data:
            return
        by_type = self.scan_data["by_type"]
        if not by_type:
            return

        self.ax1.clear()
        labels = list(by_type.keys())
        sizes = list(by_type.values())

        wedges, texts = self.ax1.pie(
            sizes,
            colors=COLORS["chart"],
            startangle=90
        )

        self.ax1.legend(
            wedges,
            labels,
            title="Dateitypen",
            loc="lower center",
            bbox_to_anchor=(0.5, -0.15),
            ncol=3,
            facecolor=COLORS["bg_card"],
            labelcolor=COLORS["text"]
        )

        self.ax1.axis('equal')
        self.ax1.set_title(self.tr("stats_dist_title"), color=COLORS["text"], fontsize=12, pad=10)
        self.fig1.tight_layout()
        self.canvas1.draw()

        self.ax2.clear()
        size_per_cat = {}
        for f in self.scan_data["files"]:
            cat = f["category"]
            size_per_cat[cat] = size_per_cat.get(cat, 0) + f["size"]
        cats = list(size_per_cat.keys())
        sizes_mb = [s / (1024*1024) for s in size_per_cat.values()]
        colors = [COLORS["chart"][i % len(COLORS["chart"])] for i in range(len(cats))]
        self.ax2.bar(cats, sizes_mb, color=colors[:len(cats)], edgecolor=COLORS["bg_card"])
        self.ax2.set_title(self.tr("stats_storage_mb_title"), color=COLORS["text"], fontsize=12, pad=10)
        self.ax2.tick_params(axis='x', rotation=45, colors=COLORS["text_muted"], labelsize=8)
        self.ax2.tick_params(axis='y', colors=COLORS["text_muted"], labelsize=8)
        self.ax2.set_facecolor(COLORS["bg_card"])
        for spine in self.ax2.spines.values():
            spine.set_color(COLORS["border"])
        self.fig2.tight_layout()
        self.canvas2.draw()


    def start_cleaning(self):
        if not self.scan_data or not self.scan_data["files"]:
            messagebox.showinfo(self.tr("nothing_title"), self.tr("nothing_msg"))
            return
        self.dashboard_clean_btn.config(state="disabled")
        def progress_callback(current, total, filename):
            percent = (current / total) * 100
            self.root.after(0, lambda: self.update_clean_progress(percent, filename))
        def clean_thread():
            result = clean_desktop(self.desktop_path, lang=self.current_lang, progress_callback=progress_callback)
            self.root.after(0, lambda: self.on_clean_finished(result))
        threading.Thread(target=clean_thread, daemon=True).start()
    
    def update_clean_progress(self, percent, filename):
        self.dashboard_progress["value"] = percent
        self.clean_progress["value"] = percent
        short = filename[:30]
        self.dashboard_status.config(text=self.tr("moving_file", name=short))
        self.clean_log.config(text=self.tr("moving_file", name=short))
    
    def on_clean_finished(self, result):
        self.dashboard_progress["value"] = 100
        self.clean_progress["value"] = 100
        moved = result["moved"]
        total = result["total"]
        if moved > 0:
            messagebox.showinfo(self.tr("done_title"), self.tr("done_msg", moved=moved, total=total))
            self.dashboard_status.config(text=self.tr("sorted_files", count=moved))
            self.clean_log.config(text=self.tr("sorted_files", count=moved))
        else:
            self.dashboard_status.config(text=self.tr("already_sorted"))
            self.clean_log.config(text=self.tr("nothing_msg"))
        self.root.after(3000, lambda: (self.dashboard_progress.config(value=0), self.clean_progress.config(value=0)))
        self.refresh_scan()
    
    def on_search(self, *args):
        if self.search_tree is None:
            return
        try:
            query = self.search_var.get().lower() if hasattr(self, 'search_var') else ""
        except:
            query = ""
        if query == self.tr("search_placeholder").lower() or not query:
            query = ""
        try:
            self.search_tree.delete(*self.search_tree.get_children())
        except:
            return
        if not self.scan_data:
            return
        for f in self.scan_data["files"]:
            if query in f["name"].lower() or query in f["category"].lower() or query in f["ext"].lower():
                try:
                    self.search_tree.insert("", "end", values=(f["name"], f["category"], self.format_size(f["size"]), str(f["path"])))
                except:
                    pass
    
    def open_selected_file(self, event=None):
        if self.search_tree is None:
            return
        selection = self.search_tree.selection()
        if not selection:
            return
        item = self.search_tree.item(selection[0])
        path = item["values"][3]
        try:
            os.startfile(path)
        except AttributeError:
            webbrowser.open(path)
        except Exception as e:
            messagebox.showerror("Error", self.tr("error_open", error=e))
    
    def show_in_explorer(self):
        if self.search_tree is None:
            return
        selection = self.search_tree.selection()
        if not selection:
            return
        item = self.search_tree.item(selection[0])
        path = Path(item["values"][3]).parent
        try:
            os.startfile(path)
        except:
            webbrowser.open(str(path))
    
    def on_auto_toggle(self, state):
        self.auto_clean_enabled = state
        if state:
            interval_text = self.interval_var.get()
            self.auto_status_label.config(text=self.tr("auto_active", interval=interval_text), fg=COLORS["success"])
            self.schedule_auto_clean()
        else:
            self.auto_status_label.config(text=self.tr("auto_disabled"), fg=COLORS["text_dim"])
            if self.auto_job:
                self.root.after_cancel(self.auto_job)
    
    def on_interval_change(self, event=None):
        mapping_de = {"5 Minuten": 5, "15 Minuten": 15, "30 Minuten": 30, "1 Stunde": 60, "2 Stunden": 120}
        mapping_en = {"5 Minutes": 5, "15 Minutes": 15, "30 Minutes": 30, "1 Hour": 60, "2 Hours": 120}
        mapping = mapping_en if self.current_lang=="en" else mapping_de
        val = self.interval_var.get()
        self.auto_clean_interval = mapping.get(val, 30)
        if self.auto_clean_enabled:
            self.auto_status_label.config(text=self.tr("auto_active", interval=val))
            if self.auto_job:
                self.root.after_cancel(self.auto_job)
            self.schedule_auto_clean()
    
    def schedule_auto_clean(self):
        if not self.auto_clean_enabled:
            return
        interval_ms = self.auto_clean_interval * 60 * 1000
        self.auto_job = self.root.after(interval_ms, self.auto_clean_run)
    
    def auto_clean_run(self):
        if self.auto_clean_enabled:
            self.start_cleaning()
            self.schedule_auto_clean()
    
    def on_language_change(self, event=None):
        selected = self.lang_var.get()
        # Determine lang from display text
        if "Deutsch" in selected or "German" in selected:
            new_lang = "de"
        else:
            new_lang = "en"
        if new_lang != self.current_lang:
            self.current_lang = new_lang
            self.save_language()
            self.apply_language()
    
    def apply_language(self):
        # Update window title
        self.root.title(self.tr("app_title"))
        # Nav
        self.nav_buttons["dashboard"].config(text=self.tr("nav_dashboard"))
        self.nav_buttons["clean"].config(text=self.tr("nav_clean"))
        self.nav_buttons["search"].config(text=self.tr("nav_search"))
        self.nav_buttons["stats"].config(text=self.tr("nav_stats"))
        self.nav_buttons["settings"].config(text=self.tr("nav_settings"))
        # Header not translated (brand)
        # Sidebar system
        self.sidebar_system_label.config(text=self.tr("system_section"))
        # Dashboard
        self.dashboard_welcome_title_label.config(text=self.tr("welcome_title"))
        self.dashboard_welcome_sub_label.config(text=self.tr("welcome_sub"))
        for key in self.stat_title_labels:
            self.stat_title_labels[key].config(text=self.tr(key))
        self.quick_clean_title_label.config(text=self.tr("quick_clean_title"))
        self.quick_clean_desc_label.config(text=self.tr("quick_clean_desc"))
        self.dashboard_clean_btn.set_text(self.tr("quick_clean_btn"))
        self.recent_title_label.config(text=self.tr("recent_files_title"))
        self.dashboard_status.config(text=self.tr("ready_to_clean"))
        # Clean page
        self.clean_center_title_label.config(text=self.tr("clean_center_title"))
        self.clean_center_desc_label.config(text=self.tr("clean_center_desc"))
        self.target_folders_label.config(text=self.tr("target_folders_label"))
        self.files_to_sort_title_label.config(text=self.tr("files_to_sort_label"))
        self.clean_tree.heading("name", text=self.tr("col_filename"))
        self.clean_tree.heading("category", text=self.tr("col_target"))
        self.clean_tree.heading("size", text=self.tr("col_size"))
        self.clean_tree.heading("ext", text=self.tr("col_type"))
        self.clean_btn.set_text(self.tr("clean_start_btn"))
        # Search page
        self.search_title_label.config(text=self.tr("search_title"))
        self.search_results_title_label.config(text=self.tr("search_results_title"))
        # Update placeholder if needed
        if self.search_entry.get() == TRANSLATIONS["de"]["search_placeholder"] or self.search_entry.get() == TRANSLATIONS["en"]["search_placeholder"]:
            self.search_entry.delete(0, 'end')
            self.search_entry.insert(0, self.tr("search_placeholder"))
        self.search_tree.heading("name", text=self.tr("col_name"))
        self.search_tree.heading("category", text=self.tr("col_category"))
        self.search_tree.heading("size", text=self.tr("col_size"))
        self.search_tree.heading("path", text=self.tr("col_path"))
        self.search_show_btn.config(text=self.tr("search_show_explorer"))
        self.search_open_btn.config(text=self.tr("search_open"))
        # Stats
        self.stats_title_label.config(text=self.tr("stats_title"))
        self.stats_dist_title_label.config(text=self.tr("stats_dist_title"))
        self.stats_storage_title_label.config(text=self.tr("stats_storage_title"))
        # Settings
        self.settings_title_label.config(text=self.tr("settings_title"))
        self.lang_title_label.config(text=self.tr("lang_title"))
        self.lang_desc_label.config(text=self.tr("lang_desc"))
        self.lang_label_label.config(text=self.tr("lang_label"))
        self.auto_clean_title_label.config(text=self.tr("auto_clean_title"))
        self.auto_clean_desc_label.config(text=self.tr("auto_clean_desc"))
        self.auto_clean_enable_label.config(text=self.tr("auto_clean_enable"))
        self.interval_label.config(text=self.tr("interval_label"))
        # Update interval combo values
        new_intervals = [self.tr("interval_5m"), self.tr("interval_15m"), self.tr("interval_30m"), self.tr("interval_1h"), self.tr("interval_2h")]
        self.interval_combo['values'] = new_intervals
        # Keep selection if possible, else default to 30m
        if self.interval_var.get() not in new_intervals:
            self.interval_var.set(self.tr("interval_30m"))
        # Update lang combo values
        self.lang_var.set(self.tr("lang_de") if self.current_lang=="de" else self.tr("lang_en"))
        # Need to update combo values for language too
        # About
        self.about_title_label.config(text=self.tr("about_title"))
        self.about_text_label.config(text=self.tr("about_text"))
        # Auto status
        if self.auto_clean_enabled:
            self.auto_status_label.config(text=self.tr("auto_active", interval=self.interval_var.get()))
        else:
            self.auto_status_label.config(text=self.tr("auto_disabled"))
        
        # Refresh data with new language categories
        self.refresh_scan()
        self.update_charts()

def main():
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TProgressbar", thickness=8, troughcolor=COLORS["bg_input"], background=COLORS["primary"], bordercolor=COLORS["bg_card"], lightcolor=COLORS["primary"], darkcolor=COLORS["primary"])
    style.configure("Treeview", background=COLORS["bg_input"], foreground=COLORS["text"], fieldbackground=COLORS["bg_input"], borderwidth=0, rowheight=28)
    style.configure("Treeview.Heading", background=COLORS["bg_card"], foreground=COLORS["text"], relief="flat", font=FONTS["body_bold"])
    style.map("Treeview", background=[('selected', COLORS["primary"])])
    app = DesktopCleanerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
