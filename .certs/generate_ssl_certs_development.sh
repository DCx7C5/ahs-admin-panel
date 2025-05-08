#!/bin/bash

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

echo -e "\e[1;32mInstalling ssl certificates for localhost and 127.0.0.1\e[0m"

if ! command -v mkcert &>/dev/null; then
  # Detect OS and call the correct function
  if grep -qi 'ID_LIKE=arch' /etc/os-release; then
      install_pacman mkcert
  elif grep -Eqi 'ID_LIKE=(debian|ubuntu|linuxmint)' /etc/os-release; then
      install_apt mkcert
  else
      echo -e "\e[1;31mUnsupported OS.\e[0m"
      exit 1
  fi
fi

# Install the local CA in the system trust store.
mkcert -install -ecdsa

# Create certificates for localhost
mkcert -ecdsa localhost 127.0.0.1

echo -e "\e[1;32mRenaming key and cert file...\e[0m"

for f in localhost+*-key.pem; do
  [ -f "$f" ] && mv "$f" "localhost-key.pem"
done

for f in localhost+*.pem; do
  [[ "$f" != "localhost-key.pem" ]] && [ -f "$f" ] && mv "$f" "localhost.pem"
done

# Copy rootCA in `pwd`
ROOT_CA="$(mkcert -CAROOT)/rootCA.pem"
cp "$ROOT_CA" .
find . -type f -name "*.pem" | sed 's|^\./||'

echo -e "\e[1;32mInstalled certificates successfully\e[0m"
