#!/bin/bash

# Vars, will be replaced in code
server_private_key="$SERVER_PRIVATE_KEY"
application_public_key="$APPLICATION_PUBLIC_KEY"
database_public_key="$DATABASE_PUBLIC_KEY"

# Install Wireguard
sudo apt update
sudo apt upgrade -y
sudo apt install wireguard -y

# Enable Ip forwarding
echo 'net.ipv4.ip_forward=1' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Get template files
git clone https://github.com/gabrielzezze/cloud-project.git
cp ./cloud-project/infraestructure/scripts/vpn/gateway_template.conf ./gateway-template.conf
touch ./gateway.conf
sed -e "s~$(echo 'private_key')~${server_private_key}~g" -e "s~$(echo 'application_public_key')~${application_public_key}~g" -e "s~$(echo 'database_public_key')~${database_public_key}~g" ./gateway-template.conf > ./gateway.conf
sudo cp ./gateway.conf /etc/wireguard/gateway.conf

sudo systemctl enable wg-quick@gateway
sudo wg-quick up gateway
