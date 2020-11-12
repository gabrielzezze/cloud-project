git clone https://github.com/gabrielzezze/cloud-project.git

sudo docker build -t zezze-custom-mysql ./cloud-project/infraestructure/scripts/database/
sudo docker run --name cloud-mysql-database -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD --restart always -p 80:3306 zezze-custom-mysql
