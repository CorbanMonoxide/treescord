@echo off
TITLE Treescord Bot
cd /d "%~dp0"
:loop
echo Starting Treescord...
call venv\Scripts\activate
python treescord.py
echo.
echo Bot crashed! Restarting in 5 seconds...
timeout /t 5
goto loop
