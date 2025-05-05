#!/bin/bash

DEPS=mkcert


install_apt() {
    echo "Detected Debian-based system."
    echo "Updating package lists..."
    sudo apt update
    echo "Installing packages: $*"
    sudo apt install -y "$@"
}

install_pacman() {
    echo "Detected Arch-based system."
    echo "Updating package lists..."
    sudo pacman -Syu --noconfirm
    echo "Installing packages: $*"
    sudo pacman -S --noconfirm "$@"
}


# Detect OS and call the correct function
if grep -qi 'ID_LIKE=arch' /etc/os-release; then
    install_pacman "$DEPS"
elif grep -Eqi 'ID=(debian|ubuntu|linuxmint)' /etc/os-release; then
    install_apt "$DEPS"
else
    echo "Unsupported OS."
    exit 1
fi

# Install the local CA in the system trust store.
mkcert -install -ecdsa

# Create certificates for localhost
mkcert -ecdsa localhost 127.0.0.1

# Copy rootCA in `pwd`
ROOT_CA="$(mkcert -CAROOT)/rootCA.pem"
cp "$ROOT_CA" .

# Rename certs
mv "localhost+1.pem" "localhost.pem"
mv "localhost+1-key.pem" "localhost-key.pem"

echo -e "\e[1;32mInstalled certificates successfully\e[0m"