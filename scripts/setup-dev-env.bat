@echo off
REM Development environment setup for Windows

echo 🔧 Setting up SecureWipe development environment...

REM Check Python version
python --version >nul 2>&1 || (
    echo ❌ Python 3.8+ required
    exit /b 1
)

REM Create virtual environment
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install global development dependencies
echo 📥 Installing development dependencies...
pip install -r requirements-dev.txt

REM Install component dependencies
echo 📥 Installing desktop-app dependencies...
cd desktop-app && pip install -r requirements.txt && cd ..

echo 📥 Installing bootable-iso dependencies...
cd bootable-iso && pip install -r requirements.txt && cd ..

echo 📥 Installing shared test dependencies...
cd shared\tests && pip install -r requirements.txt && cd ..\..

REM Run initial validation
echo 🧪 Running certificate compatibility tests...
python scripts\validate-certificates.py

echo ✅ Development environment setup complete!
echo 💡 Activate with: venv\Scripts\activate.bat