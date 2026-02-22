@echo off
:: Vérifie que whisper_key est bien importable
python -X utf8 -c "import whisper_key" >nul 2>&1
if errorlevel 1 (
    echo [whisper-key] Package manquant, reinstallation...
    pip install -e "%~dp0" --break-system-packages --quiet
)
:: Lance
python -X utf8 -m whisper_key.main
