@echo off
:: Check for Python
python --version >nul 2>&1 || (
    echo Installing Python... (This may take 5 minutes)
    winget install --silent Python.Python.3.10
    timeout /t 5
)

:: Install requirements
python -m pip install --upgrade pip
python -m pip install streamlit pandas numpy

:: Launch app
start "" streamlit run Home.py