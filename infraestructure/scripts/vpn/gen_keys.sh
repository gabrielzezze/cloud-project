#!/bin/bash
wg genkey | tee privatekey | wg pubkey > publickey
echo -e "$(cat privatekey)~$(cat publickey)"
