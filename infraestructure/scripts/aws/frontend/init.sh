rm -rf ./applications
git clone https://github.com/gabrielzezze/cloud-project-applications.git ./applications
cd ./applications/frontend
git checkout vpn-version
yarn install
yarn run deploy-prod
