#!/bin/bash
sudo apt update
sudo apt upgrade -y
cd /home/ubuntu
# Clone repo
git clone https://github.com/gabrielzezze/cloud-project.git

# Build application
chmod +x ./cloud-project/infraestructure/scripts/aws/frontend/init.sh
./cloud-project/infraestructure/scripts/aws/frontend/init.sh

# Config Caddy
cp ./cloud-project/infraestructure/scripts/aws/frontend/Caddyfile-template ./Caddyfile

# Install docker
sudo apt remove docker docker-engine docker.io containerd runc -y
sudo apt install apt-transport-https ca-certificates curl gnupg-agent software-properties-common -y
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io -y

# Pull caddy image
sudo docker pull caddy

# Run application serving container.
sudo docker run -d -p 8080:80 \
    -v /home/ubuntu/applications/frontend/build/:/usr/share/caddy/ \
    -v caddy_data:/data \
    --name frontend-serving \
    caddy

# Create and run the reverse proxy container.
sudo docker run -d -p 80:80 \
-v /home/ubuntu/Caddyfile:/etc/caddy/Caddyfile \
-v /home/ubuntu/caddy_data:/data \
--name=frontend-caddy-reverse-proxy \
--network=host \
caddy