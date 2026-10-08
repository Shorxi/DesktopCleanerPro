# DesktopCleaner Pro 

### ✨ Your smart desktop organizer - Dein smarter Desktop Aufräumer

---

## DEUTSCH

### Was ist das?
DesktopCleaner Pro räumt deinen überfüllten Desktop automatisch auf. Es scannt alle Dateien und sortiert sie in Kategorien wie Bilder, PDFs, Videos, Code, Programme usw.

### Features
- **Dashboard:** Überblick über Dateien, Speicher, Kategorien, RAM/CPU/Disk Anzeige
- **Aufräumen:** Zeigt alle Dateien mit Zielordner, sortiert per Knopfdruck
- **Suche:** Live-Suche mit Explorer Integration (Rechtsklick Öffnen / Im Explorer zeigen)
- **Statistik:** 
  - **NEU - Pie Chart Fix:** Keine überlappenden Texte mehr im Kreisdiagramm! Stattdessen saubere Legende **unten** mit farbigen Quadraten. Jede Farbe = ein Dateityp, 100% überschneidungsfrei.
  - Balkendiagramm Speicher nach Kategorie (MB)
- **Einstellungen:** Sprache DE/EN umschaltbar, Auto-Clean Intervall (5m/15m/30m/1h/2h)

### Installation
```bat
pip install -r requirements.txt
```
Benötigt: Python 3.9+, tkinter, psutil, matplotlib, Pillow

### Starten
**Empfohlen - run.bat:**
- Doppelklick auf `run.bat` (NICHT als Admin!)
- Auto-Erkennung deines Python (py Launcher, PATH, Standardpfade)
- Menü:
  ```
  [1] Build EXE to dist\DesktopCleanerPro.exe
  [2] Run directly with Python
  ```
- Auch mit Leerzeichen im Pfad wie `Desktop aufräumen` funktioniert
- EXE liegt danach in `dist\DesktopCleanerPro.exe`

**Alternativ:**
```bat
python main.py
py -3 main.py
```

### Projektstruktur
```
DesktopCleanerPro/
├── main.py              # GUI (Tkinter + Matplotlib)
├── cleaner_engine.py    # Scan & Sort Logik
├── languages.py         # DE/EN Übersetzungen
├── requirements.txt
├── run.bat              # Starter mit Auto-Erkennung & Build-Menü
├── assets/icon.png      # Optional Icon für EXE
└── config.json          # Sprache wird hier gespeichert
```

### Sprachen
Im Programm unter Einstellungen umschaltbar. Wird in `config.json` gespeichert. Alle Kategorien und UI Texte sind zweisprachig.

### Hinweise
- **Nicht als Admin starten!** PyInstaller blockt Admin ab v7.0
- EXE Build braucht ca. 1-2 Minuten
- `assets/icon.png` optional, wenn vorhanden wird es ins EXE eingebettet

## Author Emanuel Schaaf
Mit ❤️ entwickelt: Muse Spark, der Paket-Assistent 🧰 – Copilot Auron, der Windows wie seine Westentasche kennt 😎 – und Gemini Lyra, die kreative Inspiration 🎨

---

## ENGLISH

### What is it?
DesktopCleaner Pro cleans your cluttered desktop automatically. It scans all files and sorts them into categories like Images, PDFs, Videos, Code, Programs etc.

### Features
- **Dashboard:** Overview of files, storage, categories, RAM/CPU/Disk stats
- **Clean:** Shows all files with target folder, sorts with one click
- **Search:** Live search with Explorer integration (Open / Show in Explorer)
- **Statistics:**
  - **NEW - Pie Chart Fix:** No more overlapping texts in pie chart! Clean legend **below** with colored squares. Each color = one file type, 100% overlap-free.
  - Bar chart storage per category (MB)
- **Settings:** Language DE/EN switchable, Auto-Clean interval (5m/15m/30m/1h/2h)

### Installation
```bat
pip install -r requirements.txt
```
Requires: Python 3.9+, tkinter, psutil, matplotlib, Pillow

### Starting
**Recommended - run.bat:**
- Double-click `run.bat` (NOT as admin!)
- Auto-detection of your Python (py launcher, PATH, common install paths)
- Menu:
  ```
  [1] Build EXE to dist\DesktopCleanerPro.exe
  [2] Run directly with Python
  ```
- Works even with spaces in path like `Desktop aufräumen`
- EXE will be in `dist\DesktopCleanerPro.exe`

**Alternative:**
```bat
python main.py
py -3 main.py
```

### Project Structure
```
DesktopCleanerPro/
├── main.py              # GUI (Tkinter + Matplotlib)
├── cleaner_engine.py    # Scan & Sort logic
├── languages.py         # DE/EN translations
├── requirements.txt
├── run.bat              # Starter with auto-detection & build menu
├── assets/icon.png      # Optional icon for EXE
└── config.json          # Language is saved here
```

### Languages
Switchable in app under Settings. Saved in `config.json`. All categories and UI texts are bilingual.

### Notes
- **Do not run as admin!** PyInstaller blocks admin from v7.0
- EXE build takes ~1-2 minutes
- `assets/icon.png` optional, if present it will be embedded in EXE

---

## Changelog 
- **Fixed:** Pie chart overlapping texts -> moved to legend below with colored squares
- **Added:** run.bat with Python auto-detection + build menu [1] Build EXE [2] Skip
- **Added:** Bilingual README, proper path handling for spaces, no-admin warning
- **Improved:** Chart titles use `tr()` for DE/EN

## Author Emanuel Schaaf
Developed with ❤️: Muse Spark, the package wizard 🧰 – Copilot Auron, who knows Windows like the back of his hand 😎 – and Gemini Lyra, the creative inspiration 🎨
