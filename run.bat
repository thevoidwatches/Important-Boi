@echo off
:main
echo Starting the Important Boi...
python main.py
echo The Important Boi has crashed. Attempting to restart in 1 minute...
timeout /t 60 /nobreak
goto:main
cmd /k 