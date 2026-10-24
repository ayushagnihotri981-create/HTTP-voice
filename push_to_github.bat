@echo off
title Push VoiceOps to GitHub
cd /d "%~dp0"
echo ========================================================
echo Pushing VoiceOps repository to GitHub...
echo Remote: https://github.com/ayushagnihotri981-create/HTTP-voice.git
echo ========================================================
echo.
"C:\Users\ASHUTOSH\AppData\Local\Programs\Git\cmd\git.exe" push -u origin main
echo.
pause
