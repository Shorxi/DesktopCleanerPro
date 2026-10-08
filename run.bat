@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo DesktopCleaner Pro - Starter v1.2
echo ==========================================
echo Directory: %CD%
echo.

set "PYTHON_CMD="
set "PYTHON_TYPE="

net session >nul 2>&1
if %errorlevel%==0 (
    echo [WARNING] Running as admin - PyInstaller may block this
    echo Please run without admin rights
    echo.
)

py -3 --version >nul 2>&1
if %errorlevel%==0 (
    set "PYTHON_CMD=py -3"
    set "PYTHON_TYPE=PY"
    echo [OK] Python found via py launcher
    goto :menu
)

python --version >nul 2>&1
if %errorlevel%==0 (
    set "PYTHON_CMD=python"
    set "PYTHON_TYPE=PY"
    echo [OK] Python found in PATH
    goto :menu
)

python3 --version >nul 2>&1
if %errorlevel%==0 (
    set "PYTHON_CMD=python3"
    set "PYTHON_TYPE=PY"
    echo [OK] Python3 found
    goto :menu
)

for %%P in (
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "%ProgramFiles%\Python313\python.exe"
    "%ProgramFiles%\Python312\python.exe"
    "%ProgramFiles%\Python311\python.exe"
    "C:\Python313\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
) do (
    if exist %%P (
        set "PYTHON_CMD=%%~P"
        set "PYTHON_TYPE=EXE"
        echo [OK] Python found at %%P
        goto :menu
    )
)

echo [ERROR] Python not found - install from python.org
pause
exit /b

:menu
echo.
echo What do you want to do?
echo [1] Build EXE to dist\DesktopCleanerPro.exe
echo [2] Run directly with Python
echo.
set /p CHOICE=Choice [1/2, Enter=2]:
if "%CHOICE%"=="" set "CHOICE=2"
if "%CHOICE%"=="1" goto :build
goto :run

:build
echo.
echo ==========================================
echo Building EXE - please wait 1-2 minutes
echo ==========================================

if not exist "%CD%\main.py" (
    echo [ERROR] main.py not found at %CD%\main.py
    dir "%CD%"
    pause
    exit /b
)

if "%PYTHON_TYPE%"=="EXE" (
    "%PYTHON_CMD%" -m pip install pyinstaller --quiet --disable-pip-version-check
) else (
    %PYTHON_CMD% -m pip install pyinstaller --quiet --disable-pip-version-check
)

echo Building EXE from: %CD%\main.py

if exist "%CD%\assets\icon.png" (
    echo Using icon: %CD%\assets\icon.png
    if "%PYTHON_TYPE%"=="EXE" (
        "%PYTHON_CMD%" -m PyInstaller --onefile --windowed --name DesktopCleanerPro --icon "%CD%\assets\icon.png" --distpath "%CD%\dist" --workpath "%CD%\build" --specpath "%CD%" --clean "%CD%\main.py"
    ) else (
        %PYTHON_CMD% -m PyInstaller --onefile --windowed --name DesktopCleanerPro --icon "%CD%\assets\icon.png" --distpath "%CD%\dist" --workpath "%CD%\build" --specpath "%CD%" --clean "%CD%\main.py"
    )
) else (
    echo No icon found - building without icon
    if "%PYTHON_TYPE%"=="EXE" (
        "%PYTHON_CMD%" -m PyInstaller --onefile --windowed --name DesktopCleanerPro --distpath "%CD%\dist" --workpath "%CD%\build" --specpath "%CD%" --clean "%CD%\main.py"
    ) else (
        %PYTHON_CMD% -m PyInstaller --onefile --windowed --name DesktopCleanerPro --distpath "%CD%\dist" --workpath "%CD%\build" --specpath "%CD%" --clean "%CD%\main.py"
    )
)

if exist "%CD%\dist\DesktopCleanerPro.exe" (
    echo.
    echo [DONE] EXE built: %CD%\dist\DesktopCleanerPro.exe
    echo.
    set /p RUNEXE=Run EXE now? [Y/N]:
    if /i "%RUNEXE%"=="Y" (
        start "" "%CD%\dist\DesktopCleanerPro.exe"
        exit /b
    )
) else (
    echo [ERROR] Build failed - check errors above
    pause
)
goto :run

:run
echo.
echo Starting DesktopCleaner Pro with Python...
if "%PYTHON_TYPE%"=="EXE" (
    "%PYTHON_CMD%" -m pip install -r "%CD%\requirements.txt" --quiet --disable-pip-version-check
    "%PYTHON_CMD%" "%CD%\main.py"
) else (
    %PYTHON_CMD% -m pip install -r "%CD%\requirements.txt" --quiet --disable-pip-version-check
    %PYTHON_CMD% "%CD%\main.py"
)

if %errorlevel% neq 0 (
    echo Error starting app
    pause
)
endlocal