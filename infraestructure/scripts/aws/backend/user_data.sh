#!/bin/bash
# Vars, will be replaced by code
application_private_key="$APPLICATION_PRIVATE_KEY"
gateway_public_key="$GATEWAY_PUBLIC_KEY"
vpn_address="$VPN_ADDRESS"
gateway_public_ip="$GATEWAY_PUBLIC_IP"

# Update System
sudo apt update
sudo apt upgrade -y

# Install Wireguard
sudo apt install wireguard -y

# Get Files from repo
git clone https://github.com/gabrielzezze/cloud-project.git

# Wireguard config
cp ./cloud-project/infraestructure/scripts/vpn/client_template.conf ./client-template.conf
touch ./client.conf
sed -e "s~$(echo 'private_key')~${application_private_key}~g" -e "s~$(echo 'server_public_key')~${gateway_public_key}~g" -e "s~$(echo 'vpn_address')~${vpn_address}~g" -e "s~$(echo 'server_public_ip')~${gateway_public_ip}~g"  ./client-template.conf > ./client.conf
sudo cp ./client.conf /etc/wireguard/client.conf
# sudo systemctl enable wg-quick@client
# sudo wg-quick up client

# # Application config
# chmod +x ./cloud-project/infraestructure/scripts/aws/backend/init.sh
# ./cloud-project/infraestructure/scripts/aws/backend/init.sh
# cd ./applications/backend
# DATABASE_IP=$DATABASE_IP DATABASE_PASSWORD=$DATABASE_PASSWORD yarn run prod
