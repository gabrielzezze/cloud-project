# Update System
sudo apt update
sudo apt upgrade -y

# Install docker
sudo apt remove docker docker-engine docker.io containerd runc
sudo apt install apt-transport-https ca-certificates curl gnupg-agent software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt update
sudo apt nstall docker-ce docker-ce-cli containerd.io

# Build Custom docker file
sudo docker build -t zezze-custom-mysql ../database
sudo docker run --name cloud-mysql-database -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD --restart always -p 80:3306 zezze-custom-mysql

