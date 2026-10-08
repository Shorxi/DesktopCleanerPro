
import os
import shutil
from pathlib import Path

CATEGORIES_DE = {
    "Bilder": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff", ".heic"],
    "PDFs": [".pdf"],
    "Dokumente": [".docx", ".doc", ".txt", ".rtf", ".odt", ".md", ".pages"],
    "Tabellen": [".xlsx", ".xls", ".csv", ".ods", ".numbers"],
    "Präsentationen": [".pptx", ".ppt", ".ppsx", ".key"],
    "Videos": [".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm"],
    "Musik": [".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".wma"],
    "Archive": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "Code": [".py", ".js", ".html", ".css", ".cpp", ".c", ".java", ".json", ".xml", ".cs", ".php", ".ts", ".go", ".rs"],
    "Programme": [".exe", ".msi", ".bat", ".lnk", ".appimage"],
}

CATEGORIES_EN = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff", ".heic"],
    "PDFs": [".pdf"],
    "Documents": [".docx", ".doc", ".txt", ".rtf", ".odt", ".md", ".pages"],
    "Spreadsheets": [".xlsx", ".xls", ".csv", ".ods", ".numbers"],
    "Presentations": [".pptx", ".ppt", ".ppsx", ".key"],
    "Videos": [".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm"],
    "Music": [".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".wma"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "Code": [".py", ".js", ".html", ".css", ".cpp", ".c", ".java", ".json", ".xml", ".cs", ".php", ".ts", ".go", ".rs"],
    "Programs": [".exe", ".msi", ".bat", ".lnk", ".appimage"],
}

# For backward compatibility
CATEGORIES = CATEGORIES_DE

def get_categories(lang="de"):
    return CATEGORIES_EN if lang == "en" else CATEGORIES_DE

def get_fallback_name(lang="de"):
    return "Others" if lang == "en" else "Sonstiges"

def get_desktop_path():
    home = Path.home()
    candidates = [
        home / "Desktop",
        home / "OneDrive" / "Desktop",
        home / "OneDrive - Personal" / "Desktop",
        Path(os.environ.get("USERPROFILE", "")) / "Desktop",
        Path(os.environ.get("USERPROFILE", "")) / "OneDrive" / "Desktop",
    ]
    for p in candidates:
        if p.exists() and p.is_dir():
            return p
    return home / "Desktop"

def get_category_for_extension(ext, lang="de"):
    ext = ext.lower()
    cats = get_categories(lang)
    for cat, exts in cats.items():
        if ext in exts:
            return cat
    return get_fallback_name(lang)

def scan_desktop(desktop_path=None, lang="de"):
    if desktop_path is None:
        desktop_path = get_desktop_path()
    
    if not desktop_path.exists():
        return {"files": [], "by_type": {}, "total_size": 0, "path": desktop_path}
    
    files = []
    by_type = {}
    total_size = 0
    # Category folders to ignore (both languages)
    category_folders = set(CATEGORIES_DE.keys()) | set(CATEGORIES_EN.keys()) | {"Sonstiges", "Others"}
    
    try:
        for item in desktop_path.iterdir():
            if item.is_file():
                if item.name.startswith("desktop.ini") or item.name.startswith("~"):
                    continue
                try:
                    size = item.stat().st_size
                except:
                    size = 0
                ext = item.suffix.lower()
                cat = get_category_for_extension(ext, lang)
                files.append({
                    "name": item.name,
                    "path": item,
                    "ext": ext or ("(none)" if lang=="en" else "(keine)"),
                    "category": cat,
                    "size": size,
                    "modified": item.stat().st_mtime if item.exists() else 0
                })
                by_type[cat] = by_type.get(cat, 0) + 1
                total_size += size
    except Exception as e:
        print(f"Scan error: {e}")
    
    return {"files": files, "by_type": by_type, "total_size": total_size, "path": desktop_path}

def clean_desktop(desktop_path=None, lang="de", progress_callback=None):
    if desktop_path is None:
        desktop_path = get_desktop_path()
    
    scan = scan_desktop(desktop_path, lang=lang)
    files = scan["files"]
    
    moved = 0
    errors = []
    
    for idx, f in enumerate(files):
        try:
            target_folder = desktop_path / f["category"]
            target_folder.mkdir(exist_ok=True)
            
            src = f["path"]
            dest = target_folder / f["name"]
            
            counter = 1
            while dest.exists():
                stem = src.stem
                suffix = src.suffix
                dest = target_folder / f"{stem}_{counter}{suffix}"
                counter += 1
            
            shutil.move(str(src), str(dest))
            moved += 1
            
            if progress_callback:
                progress_callback(idx+1, len(files), f["name"])
                
        except Exception as e:
            errors.append(f"{f['name']}: {e}")
    
    return {"moved": moved, "total": len(files), "errors": errors, "remaining": scan_desktop(desktop_path, lang=lang)}
