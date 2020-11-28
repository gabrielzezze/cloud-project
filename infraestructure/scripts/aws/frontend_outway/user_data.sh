#!/bin/bash

# Vars, will be replaced in code
client_private_key="$CLIENT_PRIVATE_KEY"
client_vpn_address="$CLIENT_VPN_ADDRESS"
server_public_key="$SERVER_PUBLIC_KEY"
backend_gateway_ip="$BACKEND_GATEWAY_IP"

# Install Wireguard
sudo apt update
sudo apt upgrade -y
sudo apt install wireguard -y

# Enable forwarding
echo 'net.ipv4.ip_forward=1' | sudo tee -a /etc/sysctl.conf
sudo echo 1 > /proc/sys/net/ipv4/ip_forward
sudo sysctl -p
sudo echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward

# Get template files
git clone https://github.com/gabrielzezze/cloud-project.git

# Wireguard Config
cp ./cloud-project/infraestructure/scripts/vpn/client_template.conf ./client-template.conf
touch ./client.conf
sed -e "s~$(echo 'private_key')~${client_private_key}~g" -e "s~$(echo 'server_public_key')~${server_public_key}~g" -e "s~$(echo 'server_public_ip')~${backend_gateway_ip}~g" -e "s~$(echo 'vpn_address')~${client_vpn_address}~g" ./client-template.conf > ./client.conf
sudo cp ./client.conf /etc/wireguard/client.conf

# Start Wireguard
sudo systemctl enable wg-quick@client
sudo wg-quick up client

# Instal caddy
echo "deb [trusted=yes] https://apt.fury.io/caddy/ /" | sudo tee -a /etc/apt/sources.list.d/caddy-fury.list
sudo apt update
sudo apt install caddy -y

cp ./cloud-project/infraestructure/scripts/aws/frontend_outway/Caddyfile-template ./Caddyfile
sudo caddy run
