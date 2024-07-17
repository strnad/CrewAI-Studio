@echo off
echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Failed to create venv
    exit /b %errorlevel%
)

echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Failed to activate venv
    exit /b %errorlevel%
)

echo Installing requirements...
pip install -r requirements.txt --no-cache
if %errorlevel% neq 0 (
    echo Failed to install requirements
    exit /b %errorlevel%
)
set /p install_agentops="Do you want to install agentops? (y/n): "
if /i "%install_agentops%"=="y" (
    echo Installing agentops...
    pip install agentops
    if %errorlevel% neq 0 (
        echo Failed to install agentops
        exit /b %errorlevel%
    )
)
:: Check if .env file exists, if not copy .env_example to .env
if not exist "%SCRIPT_DIR%.env" (
    echo .env file does not exist. Copying .env_example to .env...
    copy "%SCRIPT_DIR%.env_example" "%SCRIPT_DIR%.env"
)


echo Installation completed successfully. Do not forget to update the .env file with your credentials. Then run run_venv.bat to start the app.

