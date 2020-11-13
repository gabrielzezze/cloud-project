#!/bin/bash
git clone https://github.com/gabrielzezze/cloud-project.git
chmod +x ./cloud-project/infraestructure/scripts/aws/database.sh
export MYSQL_ROOT_PASSWORD= __password-placeholder__
./cloud-project/infraestructure/scripts/aws/database/init.sh  