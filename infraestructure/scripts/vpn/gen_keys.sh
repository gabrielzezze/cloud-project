#!/bin/bash
mkdir ./temp-keys-workspace
cd ./temp-keys-workspace
wg genkey | tee privatekey | wg pubkey > publickey
echo -e "$(cat privatekey)~$(cat publickey)"
cd ..
rm -rf ./temp-keys-workspace
