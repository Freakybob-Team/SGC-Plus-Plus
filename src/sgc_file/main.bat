@echo off
setlocal

echo For this to work, place this program in the same folder as your main.py file. We promise you that we are doing nothing bad to your device! All this does is give you the right support to SigmaGreg :3

pause

set /p py_path="Enter the path to the main.py file: "
set exe_path=%py_path:.py=SGC++.exe%
set ico_path=%py_path%\..\sgc\logo.ico%

pyinstaller --onefile --name "SGC++" %py_path%

assoc .sgc=SGC++File
ftype SGC++File="%exe_path%" "%%1"
echo File association created for .sgc with %exe_path%!

reg add "HKCR\SGC++File\DefaultIcon" /ve /t REG_SZ /d "%ico_path%" /f
echo Icon set for .sgc files!

echo All operations completed successfully! Enjoy your new support for SGC files :3
pause
endlocal
