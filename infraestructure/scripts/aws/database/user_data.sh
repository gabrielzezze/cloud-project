#!/bin/bash
# Update System
sudo apt update
sudo apt upgrade -y

# Clone repo for files
git clone https://github.com/gabrielzezze/cloud-project.git

# Run DB container
chmod +x ./cloud-project/infraestructure/scripts/aws/database/init.sh
./cloud-project/infraestructure/scripts/aws/database/init.sh
sudo docker run --name zezze-cloud-mysql-database -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD --restart always -p 80:3306 zezze-custom-mysql
