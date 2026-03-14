#!/bin/bash

# =================================================================
# KNO v6.0 - AI-Native OS System Setup Script
# Description: Automated environment provisioning for VirtualBox/Ubuntu
# Author: KNO Principal Systems Engineer
# =================================================================

set -e # Exit on error

echo "🚀 Starting KNO v6.0 System Provisioning..."

# 1. Update & Upgrade System
sudo apt-get update && sudo apt-get upgrade -y

# 2. Install Essential Dependencies
echo "📦 Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    sqlite3 \
    git \
    curl \
    libasound2-dev \
    libportaudio2 \
    libportaudiocpp0 \
    portaudio19-dev \
    ffmpeg \
    xvfb \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0

# 3. Setup Project Directory
PROJECT_DIR="/opt/KNO"
sudo mkdir -p $PROJECT_DIR
sudo chown $USER:$USER $PROJECT_DIR
cd $PROJECT_DIR

# 4. Virtual Environment Setup
echo "🐍 Setting up Python Virtual Environment..."
python3 -m venv venv
source venv/bin/activate

# 5. Install Python Packages
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
# Installing core components for AI-Native OS
pip install \
    numpy \
    pandas \
    chromadb \
    openai-whisper \
    customtkinter \
    pyaudio \
    asyncio \
    psutil

# 6. Database Initialization
echo "🗄️ Initializing SQLite and Vector DB paths..."
mkdir -p data/vector_db
sqlite3 data/kno_core.db "VACUUM;"

# 7. eDEX-UI Provisioning (Integrated Interface)
echo "🖥️ Preparing eDEX-UI environment..."
if [ ! -d "eDEX-ui" ]; then
    echo "eDEX-UI directory not found, skipping extraction. Ensure it is moved to $PROJECT_DIR."
fi

# 8. Set Permissions
chmod +x agent.py
chmod +x botgui_new.py

echo "✅ KNO v6.0 System Setup Complete!"
echo "📍 Project Root: $PROJECT_DIR"
echo "💡 To start KNO, use: systemctl start kno_os.service"
