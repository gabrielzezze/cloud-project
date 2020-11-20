#!/bin/bash
# Create workspace folder
rm -rf ./temp_openvpn_workspace
mkdir ./temp_openvpn_workspace
cd ./temp_openvpn_workspace
mkdir ./CA
mkdir ./gateway

# Get EasyRSA package for CA and server
wget  https://github.com/OpenVPN/easy-rsa/releases/download/v3.0.8/EasyRSA-3.0.8.tgz

# Unpack EasyRSA package
tar xvf ./EasyRSA-3.0.8.tgz
cp ./EasyRSA-3.0.8/* ./CA/
cp ./EasyRSA-3.0.8/* ./gateway/

# Clone repo for needed files
git clone https://github.com/gabrielzezze/cloud-project.git

# Build CA
cp ./cloud-project/infraestructure/scripts/openvpn/vars ./CA/
cd ./CA
./easyrsa init-pki
./easyrsa build-ca nopass << EOD 
CA
EOD

# Generate server certs
cd ../gateway
./easyrsa init-pki
./easyrsa gen-req gateway nopass << EOD
gateway
EOD

# Import REQ in CA
cd ../CA
./easyrsa import-req ../gateway/pki/reqs/gateway.req gateway
./easyrsa sign-req server gateway << EOD
yes
EOD








