@echo off
REM Crypto Quant Hedge Fund Simulator Startup Script for Windows

echo 🚀 Starting Crypto Quant Hedge Fund Simulator...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 16 or higher.
    pause
    exit /b 1
)

REM Install Python dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

REM Install Node.js dependencies
echo 📦 Installing Node.js dependencies...
cd frontend
npm install
cd ..

REM Start the backend
echo 🔧 Starting FastAPI backend...
cd backend
start "Backend" python main.py
cd ..

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start the frontend
echo 🎨 Starting React frontend...
cd frontend
start "Frontend" npm start
cd ..

echo ✅ Crypto Quant Simulator is running!
echo 📊 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit...
pause >nul
