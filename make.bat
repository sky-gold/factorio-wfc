@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ROOT=%~dp0"
set "BUILD_DIR=%ROOT%build"
set "PYTHONPATH=%ROOT%gui\src;%BUILD_DIR%\Release"

if /I "%~1"=="clean" goto clean
if /I "%~1"=="build" goto build
if /I "%~1"=="test" goto test
if /I "%~1"=="run" goto run

echo Usage: make build^|test^|run^|clean
exit /b 1

:clean
if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"
exit /b 0

:build
call :setup_vs
if errorlevel 1 exit /b !ERRORLEVEL!

if not exist "%BUILD_DIR%\CMakeCache.txt" (
    call :configure
    if errorlevel 1 exit /b !ERRORLEVEL!
)

cmake --build "%BUILD_DIR%"
exit /b !ERRORLEVEL!

:test
call :build
if errorlevel 1 exit /b !ERRORLEVEL!

ctest --test-dir "%BUILD_DIR%" --output-on-failure
if errorlevel 1 exit /b !ERRORLEVEL!

call :run_python -m pytest "%ROOT%gui\tests" -v
exit /b !ERRORLEVEL!

:run
call :build
if errorlevel 1 exit /b !ERRORLEVEL!

call :run_python -u "%ROOT%gui\src\main.py"
exit /b !ERRORLEVEL!

:setup_vs
if defined VSCMD_VER exit /b 0

set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
if not exist "%VSWHERE%" goto vs_missing

for /f "usebackq delims=" %%i in (`"%VSWHERE%" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do set "VSINSTALL=%%i"
if not defined VSINSTALL goto vs_missing

call "%VSINSTALL%\Common7\Tools\VsDevCmd.bat" -no_logo -arch=amd64
exit /b !ERRORLEVEL!

:configure
set "NINJA=%VSINSTALL%\Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja\ninja.exe"
if exist "%NINJA%" (
    cmake -S "%ROOT%." -B "%BUILD_DIR%" -G Ninja -DCMAKE_BUILD_TYPE=Release "-DCMAKE_MAKE_PROGRAM=%NINJA%"
) else (
    cmake -S "%ROOT%." -B "%BUILD_DIR%" -G Ninja -DCMAKE_BUILD_TYPE=Release
)
exit /b !ERRORLEVEL!

:run_python
where python >nul 2>&1
if not errorlevel 1 (
    python %*
    exit /b !ERRORLEVEL!
)

where py >nul 2>&1
if not errorlevel 1 (
    py -3.13 %*
    exit /b !ERRORLEVEL!
)

where python3.13 >nul 2>&1
if not errorlevel 1 (
    python3.13 %*
    exit /b !ERRORLEVEL!
)

echo [make] ERROR: Python not found. Install Python 3.13 and ensure python or py is on PATH.
exit /b 1

:vs_missing
echo Visual Studio with C++ tools not found.
echo Install workload "Desktop development with C++".
exit /b 1
