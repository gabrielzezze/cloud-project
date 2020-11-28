#!/bin/bash

# Vars, will be replaced in code
server_private_key="$SERVER_PRIVATE_KEY"
client_public_key="$CLIENT_PUBLIC_KEY"
client_vpn_address="$CLIENT_VPN_ADDRESS"

# Install Wireguard
sudo apt update
sudo apt upgrade -y
sudo apt install wireguard -y

# Enable Ip forwarding
echo 'net.ipv4.ip_forward=1' | sudo tee -a /etc/sysctl.conf
echo 1 > /proc/sys/net/ipv4/ip_forward
sudo sysctl -p
sudo echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward

# Get template files
git clone https://github.com/gabrielzezze/cloud-project.git
cp ./cloud-project/infraestructure/scripts/vpn/gateway_template.conf ./gateway-template.conf
touch ./gateway.conf
sed -e "s~$(echo 'private_key')~${server_private_key}~g" -e "s~$(echo 'client_public_key')~${client_public_key}~g" -e "s~$(echo 'client_vpn_address')~${client_vpn_address}~g" ./gateway-template.conf > ./gateway.conf
sudo cp ./gateway.conf /etc/wireguard/gateway.conf

sudo systemctl enable wg-quick@gateway
sudo wg-quick up gateway
