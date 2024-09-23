#!/bin/bash

# Ensure the script exits if any command fails
set -e

# Path to your virtual environment
VENV_PATH="../.venv"

# Function to ask for user confirmation and install a package
install_package() {
    read -p "$2 not found. Do you want to install $2 using $1? (y/n): " -n 1 -r
    echo # Move to a new line
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        case $1 in
            apt-get) sudo apt-get update && sudo apt-get install -y $2 ;;
            yum) sudo yum install -y $2 ;;
            dnf) sudo dnf install -y $2 ;;
            pacman) sudo pacman -S --noconfirm $2 ;;
            brew) brew install $2 ;;
        esac
    else
        echo "Installation aborted."
        exit 1
    fi
}

# Function to check if a command exists
check_command() {
    command -v "$1" &> /dev/null
}

# Check if Python3 is installed; if not, determine the package manager and prompt user
if ! check_command python3; then
    echo "Python3 is not installed."
    if check_command apt-get; then
        install_package "apt-get" "python3"
    elif check_command yum; then
        install_package "yum" "python3"
    elif check_command dnf; then
        install_package "dnf" "python3"
    elif check_command pacman; then
        install_package "pacman" "python"
    elif check_command brew; then
        install_package "brew" "python"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "Please install Python manually from https://www.python.org/downloads/windows/"
        exit 1
    else
        echo "No known package manager found. Please install Python manually."
        exit 1
    fi
else
    echo "Python3 is already installed."
fi

# Check if pip is installed; if not, prompt for installation
if ! check_command pip; then
    if check_command apt-get; then
        install_package "apt-get" "python3-pip"
    elif check_command yum; then
        install_package "yum" "python3-pip"
    elif check_command dnf; then
        install_package "dnf" "python3-pip"
    elif check_command pacman; then
        install_package "pacman" "python-pip"
    elif check_command brew; then
        install_package "brew" "pip"
    else
        echo "No known package manager found. Please install pip manually."
        exit 1
    fi
else
    echo "pip is already installed."
fi

# Check if python3-venv is installed (for Debian-based systems)
if ! dpkg -s python3-venv &> /dev/null && check_command apt-get; then
    install_package "apt-get" "python3-venv"
fi

# Create and activate virtual environment if not already present
if [[ ! -d "$VENV_PATH" ]]; then
    echo "Creating virtual environment at $VENV_PATH..."
    python3 -m venv "$VENV_PATH"
fi

echo "Activating virtual environment..."
source "$VENV_PATH/bin/activate"

# Install required packages from requirements.txt (one folder above the current folder)
REQUIREMENTS_FILE="../requirements.txt"
if [[ -f "$REQUIREMENTS_FILE" ]]; then
    echo "Installing packages from $REQUIREMENTS_FILE into the virtual environment..."
    pip install -r "$REQUIREMENTS_FILE"
else
    echo "requirements.txt not found at $REQUIREMENTS_FILE. Please check the file location."
    exit 1
fi

# Path to your main.py file
MAIN_PY_PATH="./server.py"
PORT=5002
FILENAME=$(basename -- "$MAIN_PY_PATH")
BASENAME="${FILENAME%.*}"
WORKERS=4
echo "Starting server on port ${PORT} with ${WORKERS} workers, through file at ${MAIN_PY_PATH}."

# Get the Gunicorn executable path
GUNICORN_PATH="$VENV_PATH/bin/gunicorn"

# Check if the Gunicorn executable exists
if [[ ! -x "$GUNICORN_PATH" ]]; then
    echo "Gunicorn is not installed or not found. Please check your requirements.txt file."
    exit 1
fi

# Run the gunicorn command within the virtual environment
"$GUNICORN_PATH" -w ${WORKERS} -b 0.0.0.0:${PORT} ${BASENAME}:app
