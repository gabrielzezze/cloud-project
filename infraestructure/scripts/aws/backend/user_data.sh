#!/bin/bash
mkdir /home/ubuntu/wireguard
git clone https://github.com/gabrielzezze/cloud-project.git
chmod +x ./cloud-project/infraestructure/scripts/aws/backend/init.sh
./cloud-project/infraestructure/scripts/aws/backend/init.sh
cd ./applications/backend
DATABASE_IP=$DATABASE_IP DATABASE_PASSWORD=$DATABASE_PASSWORD yarn run prod
