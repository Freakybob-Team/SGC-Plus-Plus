@echo off

echo Moving executable to SGC++ folder...
cd ..
cd ..
cd ..
if not exist "SGC++" mkdir "SGC++"
move /y "%~dp0dist\SGC++.exe" "SGC++\"

echo Deleting unnecessary files...
cd "%~dp0"
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "SGC++.spec" del /q "SGC++.spec"

echo Done!
