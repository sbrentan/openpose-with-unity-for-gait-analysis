@echo off
REM Move into the application folder
cd "FastAPI Application"

REM Check if the virtual environment exists
if not exist .venv (
    echo Virtual environment not found, creating it...
    python -m venv .venv
    if errorlevel 1 (
        echo Failed to create the virtual environment
        exit /b 1
    )
)

REM Activate the virtual environment
call .venv\Scripts\activate

REM Check if uvicorn is installed
set UVICORN_INSTALLED=NO
for /f "delims=" %%i in ('pip show uvicorn 2^>nul') do (
    set UVICORN_INSTALLED=YES
    goto :UVICORN_CHECK_DONE
)

:UVICORN_CHECK_DONE
IF "%UVICORN_INSTALLED%"=="NO" (
    echo Uvicorn is not installed in the virtual environment, installing requirements...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install requirements
        exit /b 1
    )
)

REM Move into the src folder
cd "src"

REM Run the FastAPI application with uvicorn
start uvicorn main:app --workers 4
IF %ERRORLEVEL% NEQ 0 (
    echo Uvicorn is not installed in the virtual environment
    exit /b 1
)

REM Wait a few seconds to ensure the server starts
timeout /t 5 /nobreak

REM Open the default URL in the default web browser
start http://127.0.0.1:8000