# Update System
sudo apt update
sudo apt upgrade -y

# Install Node + yarn + npm
# -Node + Npm
sudo apt install nodejs -y
sudo apt install npm -y
# -Yarn
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
sudo apt update
sudo apt install --no-install-recommends yarn -y

git clone https://github.com/gabrielzezze/cloud-project-applications.git ./applications
cd ./applications/backend
yarn install
