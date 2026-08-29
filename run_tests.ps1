$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

if (-not (Test-Path -LiteralPath ".venv\Scripts\python.exe")) {
    throw "Run .\run_app.ps1 once to create the project environment."
}

& ".venv\Scripts\python.exe" -W ignore::DeprecationWarning -W ignore::FutureWarning -m unittest discover -s tests -v
& ".venv\Scripts\python.exe" scripts\evaluate_demo.py

