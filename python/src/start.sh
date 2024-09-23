#!/bin/bash

# Ensure the script exits if any command fails
set -e

# Path to your virtual environment
VENV_PATH="../.venv"

# Function to ask for user confirmation and install pip or python3-venv
install_package() {
    read -p "$2 not found. Do you want to install $2 using $1? (y/n): " -n 1 -r
    echo # Move to a new line
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        case $1 in
            apt-get) sudo apt-get update && sudo apt-get install -y $2 ;;
            yum) sudo yum install -y $2 ;;
            brew) brew install $2 ;;
        esac
    else
        echo "Installation aborted."
        exit 1
    fi
}

# Check if pip is installed; if not, determine the package manager and prompt user
if ! command -v pip &> /dev/null; then
    if command -v apt-get &> /dev/null; then
        install_package "apt-get" "python3-pip"
    elif command -v yum &> /dev/null; then
        install_package "yum" "python3-pip"
    elif command -v brew &> /dev/null; then
        install_package "brew" "python3"
    else
        echo "No known package manager found. Please install pip manually."
        exit 1
    fi
else
    echo "pip is already installed."
fi

# Check if python3-venv is installed
if ! dpkg -s python3-venv &> /dev/null && command -v apt-get &> /dev/null; then
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
