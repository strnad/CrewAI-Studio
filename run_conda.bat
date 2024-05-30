@echo off

:: Set the script directory
set SCRIPT_DIR=%~dp0

:: Path to your Miniconda installation
set CONDA_PATH=%SCRIPT_DIR%miniconda

:: Initialize Conda for this script session only
call "%CONDA_PATH%\Scripts\activate.bat"

:: Activate the conda environment
call conda activate crewai_env || (
    echo Failed to activate conda environment
    exit /b 1
)

cd %SCRIPT_DIR%

:: Run the Streamlit application
streamlit run app/app.py --server.headless True
