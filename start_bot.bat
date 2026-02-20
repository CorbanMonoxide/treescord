@echo off
TITLE Treescord Bot
cd /d "%~dp0"
echo Starting Treescord...
call venv\Scripts\activate
python treescord.py
echo.
echo Bot has stopped.
pause
