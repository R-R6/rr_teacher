@echo off
chcp 65001 >nul
REM High School Chemistry Teaching Assistant - Quick Start Script

echo ========================================
echo   Chemistry Teaching Assistant - Start
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.11+
    pause
    exit /b 1
)

REM Enter backend directory
cd /d "%~dp0backend"

REM Check virtual environment
if not exist "venv" (
    echo [1/4] Creating virtual environment...
    python -m venv venv
)

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/4] Installing dependencies...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

REM Check .env file
if not exist ".env" (
    echo [4/4] Creating config file...
    copy .env.example .env
    echo.
    echo [NOTE] Please edit backend\.env file to configure database
    echo        Set DB_PASSWORD to your MySQL password
    echo.
    pause
)

echo.
echo [DONE] Setup complete!
echo.
echo Next steps:
echo   1. Start MySQL and create database: CREATE DATABASE chem_teacher;
echo   2. Edit backend\.env file, set DB_PASSWORD
echo   3. Run: python init_database.py
echo   4. Start: uvicorn app.main:app --reload
echo   5. Visit: http://localhost:8000/docs
echo.
pause
