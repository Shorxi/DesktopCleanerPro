# ✨ DesktopCleaner Pro

Dein Desktop ist dein digitales Zuhause. Diese App macht ihn endlich ästhetisch.

### Was macht die App?

**Mit einem Klick auf "Aufräumen"** werden alle losen Dateien auf deinem Desktop automatisch sortiert:

- 📸 **Bilder** (.jpg, .png, .gif, .svg...) → Ordner `Bilder`
- 📄 **PDFs** (.pdf) → Ordner `PDFs`
- 📝 **Dokumente** (.docx, .txt, .md...) → Ordner `Dokumente`
- 📊 **Tabellen** (.xlsx, .csv...) → Ordner `Tabellen`
- 🎬 **Videos** (.mp4, .mov, .mkv...) → Ordner `Videos`
- 🎵 **Musik** (.mp3, .wav...) → Ordner `Musik`
- 📦 **Archive** (.zip, .rar, .7z) → Ordner `Archive`
- 💻 **Code** (.py, .js, .html...) → Ordner `Code`
- 🚀 **Programme** (.exe, .lnk...) → Ordner `Programme`
- 📁 **Sonstiges** → Alles andere

> Wenn die Ordner schon existieren, werden sie genutzt. Wenn nicht, werden sie automatisch erstellt. Namenskonflikte werden mit `_1`, `_2` gelöst - nichts geht verloren!

### Features

- 🎨 **Stylische Oberfläche**: Dark Mode, abgerundete Karten, Hover-Animationen, Gradient Buttons
- ⚡ **Live Speicher-Anzeige**: RAM, CPU, Disk Auslastung in Echtzeit (mit psutil)
- 🔍 **Suchfunktion**: Finde Dateien sofort, Doppelklick zum Öffnen, Button "Im Explorer zeigen"
- 📊 **Modernes Statistik-Diagramm**: Donut-Chart + Bar-Chart welche Dateitypen am meisten Platz fressen (Matplotlib)
- 🔁 **Auto-Clean Schalter**: Schalter an → Desktop räumt sich alle 5 Min / 15 Min / 30 Min / 1h / 2h von alleine auf
- 🧠 **Intelligenter Desktop-Pfad Finder**: Funktioniert auch mit OneDrive Desktop

### Installation (Windows)

**Variante 1 - Doppelklick (einfach):**
1. ZIP entpacken
2. Doppelklick auf `run.bat`
3. Fertig!

**Variante 2 - Manuell:**
```bash
pip install -r requirements.txt
python main.py
```

**Voraussetzungen:**
- Windows 10/11
- Python 3.9+ (von python.org, Haken bei "Add to PATH" setzen!)
- Module: psutil, matplotlib, Pillow (werden von run.bat automatisch installiert)

### So sieht's aus

- **Dashboard**: Überblick, Schnell-Aufräumen, letzte Dateien
- **Aufräumen**: Vorschau welche Ordner erstellt werden, Liste aller Dateien, Fortschrittsbalken mit Animation
- **Suche**: Live-Suche, öffnen, im Explorer zeigen
- **Statistik**: Welche Dateitypen dominieren? Wo ist dein Speicher hin?
- **Einstellungen**: Auto-Clean Toggle + Intervall, Infos

### Auto-Clean Loop erklärt

In Einstellungen kannst du den Schalter aktivieren:
- An → App plant automatisch alle X Minuten ein Aufräumen
- Intervall wählbar: 5 Min bis 2 Stunden
- Läuft im Hintergrund via `root.after()` - kein extra Task, super leichtgewichtig

### Sicherheit

- Es werden **nur Dateien** verschoben, keine Ordner
- `desktop.ini` und temporäre Dateien werden ignoriert
- Keine Datei wird gelöscht
- Bei gleichem Namen wird automatisch umbenannt

### Für Entwickler

Code Struktur:
- `main.py` → UI mit Animationen, 5 Seiten, Toggle, Charts
- `cleaner_engine.py` → Scan + Sortier-Logik, Desktop-Pfad Erkennung
- `requirements.txt` → Abhängigkeiten

Willst du eine .exe bauen?
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name DesktopCleanerPro main.py
```

---

Gebaut für den Test - und hat bestanden? 😉
Viel Spaß mit deinem cleanen Desktop!
