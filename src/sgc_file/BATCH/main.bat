@echo off
setlocal

call exe.bat

call clean.bat

echo ===================================================================
echo For this to work, you need to run this program as Administrator.
echo Don't worry, this script does nothing harmful to your device! :3
echo It simply provides the necessary support for SGC++ (.sgc) files.
echo ===================================================================

pause

openfiles >nul 2>nul
if %errorlevel% neq 0 (
    echo This program requires administrator privileges. Relaunching with admin rights...
    powershell -Command "Start-Process cmd -ArgumentList '/c %~s0' -Verb RunAs"
    exit /b
)

set /p exe_path="Enter the full path to the executable (.exe) for SGC++: "
set /p ico_path="Enter the full path to the icon (.ico) for .sgc files: "

if not exist "%exe_path%" (
    echo ERROR: The specified executable path does not exist! Please check the path and try again.
    pause
    exit /b
)

if not exist "%ico_path%" (
    echo ERROR: The specified icon path does not exist! Please check the path and try again.
    pause
    exit /b
)

assoc .sgc=SGC++
ftype SGC++="%exe_path%" "%%1"
echo File association created for .sgc with "%exe_path%"!

reg add "HKCR\SGC++\DefaultIcon" /ve /t REG_SZ /d "%ico_path%" /f
echo Icon set for .sgc files!

echo ===========================================================
echo All operations completed successfully! You can now open .sgc files with SGC++. Enjoy! :3
echo ===========================================================

pause
endlocal
