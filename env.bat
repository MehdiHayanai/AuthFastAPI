@echo off
setlocal enabledelayedexpansion

REM Read the project name from pyproject.toml
for /f "tokens=2 delims== " %%i in ('findstr /r /c:"^name = " pyproject.toml') do (
    set "ENV_NAME=%%i"
    set "ENV_NAME=!ENV_NAME:~1,-1!"
    goto :found
)
:found
echo Project name: !ENV_NAME!


REM Check if the virtual environment directory exists
if not exist .\.venv\Scripts (
    echo .\.venv\Scripts not found. Installing uv and creating virtual environment...
    pip install uv
    if %ERRORLEVEL% neq 0 (
        if %ERRORLEVEL% equ 2 (
            echo uv is already installed.
        ) else (
            echo Failed to install uv. Exiting...
            exit /b %ERRORLEVEL%
        )
    )
    uv venv .venv --prompt !ENV_NAME!
    if %ERRORLEVEL% neq 0 (
        echo Failed to create virtual environment. Exiting...
        exit /b %ERRORLEVEL%
    )
)

endlocal

REM Check if the virtual environment is already activated
if defined VIRTUAL_ENV (
    REM Deactivate the virtual environment
    echo deactivate
    call .\.venv\Scripts\deactivate.bat
    if %ERRORLEVEL% neq 0 (
        echo Failed to deactivate virtual environment. Exiting...
        exit /b %ERRORLEVEL%
    )
) else (
    REM Activate the virtual environment
    echo activate
    call .\.venv\Scripts\activate.bat
    if %ERRORLEVEL% neq 0 (
        echo Failed to activate virtual environment. Exiting...
        exit /b %ERRORLEVEL%
    )
)

