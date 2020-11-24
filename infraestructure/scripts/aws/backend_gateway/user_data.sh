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
echo 1 > /proc/sys/net/ipv4/ip_forward
sudo sysctl -p
sudo echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward

# Get template files
git clone https://github.com/gabrielzezze/cloud-project.git
cp ./cloud-project/infraestructure/scripts/vpn/gateway_template.conf ./gateway-template.conf
touch ./gateway.conf
sed -e "s~$(echo 'private_key')~${server_private_key}~g" -e "s~$(echo 'application_public_key')~${application_public_key}~g" -e "s~$(echo 'database_public_key')~${database_public_key}~g" ./gateway-template.conf > ./gateway.conf
sudo cp ./gateway.conf /etc/wireguard/gateway.conf

sudo systemctl enable wg-quick@gateway
sudo wg-quick up gateway



iptables -t nat -A PREROUTING -p tcp --dport 3000 -j DNAT --to-destination 14.0.0.2:80
iptables -t nat -A POSTROUTING -p tcp -d 14.0.0.2 --dport 80 -j SNAT --to-source 14.0.0.1

iptables -t nat -D PREROUTING -p tcp --dport 3000 -j DNAT --to-destination 14.0.0.2:80
iptables -t nat -D POSTROUTING -p tcp -d 14.0.0.2 --dport 80 -j SNAT --to-source 14.0.0.1
