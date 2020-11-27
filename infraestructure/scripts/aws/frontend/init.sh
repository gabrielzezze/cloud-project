rm -rf ./applications
# Install yarn
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
sudo apt update
sudo apt install yarn -y

# Clone application
git clone https://github.com/gabrielzezze/cloud-project-applications.git ./applications
cd ./applications/frontend
git checkout vpn-version
yarn install
sudo yarn run deploy-prod
