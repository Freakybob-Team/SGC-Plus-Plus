@echo off

pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller is not installed... Installing now...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo Couldn't install PyInstaller... Please check your Python installation!
        pause
        exit /b
    )
)

set /p pythonPath=Enter the full path to the main.py file: 
set /p icoPath=Enter the full path to the icon file: 

if not exist "%pythonPath%" (
    echo The specified Python file does not exist... Please check the path :3
    pause
    exit /bat
)

if not exist "%icoPath%" (
    echo The specified icon file does not exist... Please check the path :3
    pause
    exit /b
)

echo Running PyInstaller... Please wait.
(
    powershell -Command "pyinstaller --name SGC++ --onefile --icon='%icoPath%' '%pythonPath%'"
) && (
    echo PyInstaller has completed successfully.
) || (
    echo The exe was not created. Maybe try to reinstall PyInstaller? (pip install pyinstaller)
    pause
    exit /b
)

echo ===========================================================
echo All operations completed successfully! The exe is now in the "dist" folder.
echo ===========================================================

pause
exit /b
