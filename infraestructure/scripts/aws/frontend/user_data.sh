#!/bin/bash

sudo apt update
sudo apt upgrade -y
# Clone repo
git clone https://github.com/gabrielzezze/cloud-project.git

# Instal caddy
echo "deb [trusted=yes] https://apt.fury.io/caddy/ /" \
    | sudo tee -a /etc/apt/sources.list.d/caddy-fury.list
sudo apt update
sudo apt install caddy

cp ./cloud-project/infraestructure/scripts/aws/frontend/Caddyfile ./
caddy run &

# Run application
chmod +x ./cloud-project/infraestructure/scripts/aws/frontend/init.sh
./cloud-project/infraestructure/scripts/aws/frontend/init.sh
