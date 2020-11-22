#!/bin/bash
########################
#
# Wireguard Config Credits: https://forums.lawrencesystems.com/t/getting-started-building-your-own-wireguard-vpn-server/7425
#
########################

# Get shell parameters
echo "Gateway IP: ${1}"
echo "Application IP: ${2}"
echo "Database IP: ${3}"
echo "SSH Key Password for SCP Transfers (.conf files are transfered to respectivi instances by SCP):"
# read -s password

# Clean Env
sudo rm -rf ./vpn-creation-sandbox

# Create sandbox folder
mkdir ./vpn-creation-sandbox
cd ./vpn-creation-sandbox
mkdir ./gateway
mkdir ./application
mkdir ./database

# Gateway Configs
cd ./gateway
wg genkey | tee privatekey | wg pubkey > publickey
touch ./gateway.conf
sed -e "s~$(echo 'private_key')~$(cat privatekey)~g" ../../gateway_template.conf > ./gateway.conf
cd ..


# Application Configs
cd ./application
wg genkey | tee privatekey | wg pubkey > publickey
touch ./client-temp.conf
sed -e "s~$(echo 'private_key')~$(cat privatekey)~g" ../../client_template.conf > ./client-temp.conf
sed -e "s~$(echo 'server_public_key')~$(cat ../gateway/publickey)~g" client-temp.conf > ./client.conf
rm -rf ./client-temp.conf
cd ..

# Database Configs
cd ./database
wg genkey | tee privatekey | wg pubkey > publickey
touch ./client-temp.conf
sed -e "s~$(echo 'private_key')~$(cat privatekey)~g" ../../client_template.conf > ./client-temp.conf
sed -e "s~$(echo 'server_public_key')~$(cat ../gateway/publickey)~g" client-temp.conf > ./client.conf
rm -rf ./client-temp.conf
cd ..

# Send files to respctive remote instances
sshpass -p "$password" scp ./gateway/* ubuntu@$1:/etc/wireguard/
sshpass -p "$password" scp ./application/* ubuntu@$2:/etc/wireguard/
sshpass -p "$password" scp ./database/* ubuntu@$3:/etc/wireguard/
