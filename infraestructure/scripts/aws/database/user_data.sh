#!/bin/bash
mkdir /home/ubuntu/wireguard
git clone https://github.com/gabrielzezze/cloud-project.git
chmod +x ./cloud-project/infraestructure/scripts/aws/database/init.sh
./cloud-project/infraestructure/scripts/aws/database/init.sh
sudo docker run --name zezze-cloud-mysql-database -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD --restart always -p 80:3306 zezze-custom-mysql
