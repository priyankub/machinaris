#!/bin/env bash
#
# Installs Ballcoin as per https://github.com/ball-network/ballcoin-blockchain
#

BALLCOIN_BRANCH=$1
# On 2025-02-12
HASH=1acf07d752ecc8a1350efaf62b031ca3e93a8883

if [ -z ${BALLCOIN_BRANCH} ]; then
    echo 'Skipping Ballcoin install as not requested.'
else
    rm -rf /root/.cache
    git clone --branch ${BALLCOIN_BRANCH} --single-branch https://github.com/ball-network/ballcoin-blockchain.git /ballcoin-blockchain
    cd /ballcoin-blockchain
    git submodule update --init mozilla-ca
    chmod +x install.sh
    /usr/bin/sh ./install.sh

    if [ ! -d /chia-blockchain/venv ]; then
        cd /
        rmdir /chia-blockchain
        ln -s /ballcoin-blockchain /chia-blockchain
        ln -s /ballcoin-blockchain/venv/bin/ballcoin /chia-blockchain/venv/bin/chia
    fi
fi
