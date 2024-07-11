@echo off
REM Get the directory where the script is located
SET SCRIPT_DIR=%~dp0

echo Activating virtual environment...
call "%SCRIPT_DIR%venv\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo Failed to activate venv
    exit /b %errorlevel%
)

echo Running Streamlit app...
cd %SCRIPT_DIR%

REM Optionally remove existing 'db' directory
IF EXIST "%SCRIPT_DIR%db" (
    rmdir /s /q "%SCRIPT_DIR%db"
)

streamlit run app/app.py --server.headless True
