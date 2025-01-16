#!/bin/bash

set -o errexit
set -o nounset

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

shutdown_hook() {
  echo -e "${GREEN}Shutting down ${RED}NODE${GREEN} redis database...${NC}"
  sleep 2
}

trap 'shutdown_hook' SIGTERM SIGINT

# Check Django project dir is mounted
#if [ ! -f manage.py ]; then
#  echo -e "${RED}Project root is missing...${NC}"
#  echo -e "${RED}Dropping into emergency shell...${NC}"
#  exec /bin/bash
#else
#  echo -e "${GREEN}Project root found!${NC}"
#  # Install devcontainer.json
#  npm -D install
#fi

echo -e "${GREEN}Initialisation successfull!${NC}"
"${@}" &
wait $!
shutdown_hook