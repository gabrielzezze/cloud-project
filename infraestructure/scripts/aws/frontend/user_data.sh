#!/bin/bash
# Vars to be replaced by code
frontend_outway_ip=$FRONTEND_OUTWAY_IP

sudo apt update
sudo apt upgrade -y
cd /home/ubuntu
# Clone repo
git clone https://github.com/gabrielzezze/cloud-project.git

# Run application
chmod +x ./cloud-project/infraestructure/scripts/aws/frontend/init.sh
./cloud-project/infraestructure/scripts/aws/frontend/init.sh

# Instal caddy
echo "deb [trusted=yes] https://apt.fury.io/caddy/ /" | sudo tee -a /etc/apt/sources.list.d/caddy-fury.list
sudo apt update
sudo apt install caddy -y

cp ./cloud-project/infraestructure/scripts/aws/frontend/Caddyfile-template ./Caddyfile-template
touch ./Caddyfile
sed -e "s~$(echo 'frontend-outway-ip')~${frontend_outway_ip}~g" Caddyfile-template > ./Caddyfile
sudo caddy start
