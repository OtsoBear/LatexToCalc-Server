#!/bin/bash

# Ensure the script exits if any command fails
set -e

# Path to your virtual environment
VENV_PATH="../.venv"

# Function to ask for user confirmation and install packages
install_packages() {
    read -p "$2 not found. Do you want to install $2 using $1? (y/n): " -n 1 -r
    echo # Move to a new line
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if ! $1 install -y $3; then
            echo "Failed to install $2. Please install it manually."
            exit 1
        fi
    else
        echo "Installation aborted."
        exit 1
    fi
}

# Function to check and install Python
check_python() {
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        echo "Python is not installed."
        if command -v apt-get &> /dev/null; then
            install_packages "apt-get" "python3" "python3"
        elif command -v yum &> /dev/null; then
            install_packages "yum" "python3" "python3"
        elif command -v dnf &> /dev/null; then
            install_packages "dnf" "python3" "python3"
        elif command -v pacman &> /dev/null; then
            install_packages "pacman" "python" "python"
        elif command -v brew &> /dev/null; then
            install_packages "brew" "python" "python"
        elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
            echo "Please install Python manually from https://www.python.org/downloads/windows/"
            exit 1
        else
            echo "No known package manager found. Please install Python manually."
            exit 1
        fi
    else
        echo "Python is already installed."
    fi
}

# Function to check and install pip
check_pip() {
    if ! command -v pip &> /dev/null; then
        echo "pip not found. Installing pip..."
        if command -v apt-get &> /dev/null; then
            install_packages "apt-get" "pip" "python3-pip"
        elif command -v yum &> /dev/null; then
            install_packages "yum" "pip" "python3-pip"
        elif command -v dnf &> /dev/null; then
            install_packages "dnf" "pip" "python3-pip"
        elif command -v pacman &> /dev/null; then
            install_packages "pacman" "pip" "python-pip"
        elif command -v brew &> /dev/null; then
            install_packages "brew" "pip" "pip"
        else
            echo "No known package manager found. Please install pip manually."
            exit 1
        fi
    else
        echo "pip is already installed."
    fi
}

# Function to check and install venv
check_venv() {
    if command -v dpkg &> /dev/null && ! dpkg -s python3-venv &> /dev/null; then
        install_packages "apt-get" "python3-venv" "python3-venv"
    fi
}

# Check for Python, pip, and venv
check_python
check_pip
check_venv

# Create and activate virtual environment if not already present
if [[ ! -d "$VENV_PATH" ]]; then
    echo "Creating virtual environment at $VENV_PATH..."
    if ! python3 -m venv "$VENV_PATH"; then
        echo "Failed to create virtual environment."
        exit 1
    fi
fi

# Activate the virtual environment (Windows vs Unix)
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source "$VENV_PATH/Scripts/activate"
else
    source "$VENV_PATH/bin/activate"
fi

# Install required packages from requirements.txt
REQUIREMENTS_FILE="../requirements.txt"
if [[ -f "$REQUIREMENTS_FILE" ]]; then
    echo "Installing packages from $REQUIREMENTS_FILE..."
    if ! pip install -r "$REQUIREMENTS_FILE"; then
        echo "Failed to install packages from $REQUIREMENTS_FILE."
        exit 1
    fi
else
    echo "requirements.txt not found at $REQUIREMENTS_FILE."
    exit 1
fi

# Start server with gunicorn
MAIN_PY_PATH="./server.py"
PORT=5002
WORKERS=4
GUNICORN_PATH="$VENV_PATH/bin/gunicorn"

if [[ ! -x "$GUNICORN_PATH" ]]; then
    echo "Gunicorn not installed. Please check your requirements.txt."
    exit 1
fi

echo "Starting server on port $PORT with $WORKERS workers..."
if ! "$GUNICORN_PATH" -w $WORKERS -b 0.0.0.0:$PORT "$(basename "$MAIN_PY_PATH" .py):app"; then
    echo "Failed to start the server."
    exit 1
fi
