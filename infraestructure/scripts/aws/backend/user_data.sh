#!/bin/bash

# Update System
sudo apt update
sudo apt upgrade -y

# Get Files from repo
git clone https://github.com/gabrielzezze/cloud-project.git

# Application config
chmod +x ./cloud-project/infraestructure/scripts/aws/backend/init.sh
./cloud-project/infraestructure/scripts/aws/backend/init.sh
cd ./applications/backend
DATABASE_IP=$DATABASE_IP DATABASE_PASSWORD=$DATABASE_PASSWORD yarn run prod
