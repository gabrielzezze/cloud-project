#!/bin/bash
########################
#
# Wireguard Config Credits: https://forums.lawrencesystems.com/t/getting-started-building-your-own-wireguard-vpn-server/7425
#
########################

# Update System
sudo apt update
sudo apt upgrade -y

# Enable IP Forwading
echo 'net.ipv4.ip_forward=1' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Install wireguard
sudo apt install wireguard -y

# Configure Keys
git clone https://github.com/gabrielzezze/cloud-project.git
sudo cp ./cloud-project/infraestructure/scripts/vpn/wg0.conf /etc/wireguard/
sudo su << EOD
cd /etc/wireguard
umask 077; wg genkey | tee privatekey | wg pubKey > publickey
sed -e "s/\${private_key}"cat privatekey"/" wg0.conf
EOD
