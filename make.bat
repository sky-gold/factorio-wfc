@echo off
if not defined VSCMD_VER for /f "usebackq delims=" %%i in (`"%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe" -latest -property installationPath`) do call "%%i\Common7\Tools\VsDevCmd.bat" -no_logo -arch=amd64

if "%1"=="build" goto build
if "%1"=="test" goto test
if "%1"=="run" goto run
echo Usage: make build^|test^|run
exit /b 1

:build
if not exist build\CMakeCache.txt cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build
exit /b %ERRORLEVEL%

:test
call :build
if errorlevel 1 exit /b %ERRORLEVEL%
cd build
ctest --output-on-failure
set TEST_ERR=%ERRORLEVEL%
cd ..
if not %TEST_ERR%==0 exit /b %TEST_ERR%
set PYTHONPATH=%CD%\build\Release
python3.13 -m pytest tests/ -v
exit /b %ERRORLEVEL%

:run
call :build
if errorlevel 1 exit /b %ERRORLEVEL%
set PYTHONPATH=%CD%\build\Release
python3.13 src_py\main.py
exit /b %ERRORLEVEL%
