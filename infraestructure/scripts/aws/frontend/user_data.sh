#!/bin/bash
git clone https://github.com/gabrielzezze/cloud-project.git
chmod +x ./cloud-project/infraestructure/scripts/aws/frontend/init.sh
./cloud-project/infraestructure/scripts/aws/frontend/init.sh
REACT_APP_BACKEND_IP=$BACKEND_ELASTIC_IP yarn run prod
