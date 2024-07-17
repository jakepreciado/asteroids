@echo off
echo Launching Pygame in fullscreen mode...

REM Launch VBScript to run Pygame without displaying the terminal
start /min "" wscript.exe "%~dp0\play_game.vbs"
