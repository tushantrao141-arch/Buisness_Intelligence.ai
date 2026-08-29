$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

if (-not (Test-Path -LiteralPath ".venv\Scripts\python.exe")) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3.11 -m venv .venv 2>$null
        if (-not (Test-Path -LiteralPath ".venv\Scripts\python.exe")) {
            & py -3 -m venv .venv
        }
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        & python -m venv .venv
    } else {
        throw "Python 3.11 or newer is required. Install Python, then run this script again."
    }
}

& ".venv\Scripts\python.exe" -m pip install -r requirements.txt
& ".venv\Scripts\python.exe" scripts\generate_demo.py
& ".venv\Scripts\python.exe" scripts\init_database.py
& ".venv\Scripts\python.exe" -m streamlit run app.py

