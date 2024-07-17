Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c cd /d C:\Users\jacob\projects\asteroids && python asteroids.py --fullscreen", 0
