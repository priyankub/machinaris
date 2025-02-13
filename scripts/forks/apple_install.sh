#!/bin/env bash
#
# Installs Apple as per https://github.com/Apple-Network/apple-blockchain
#

APPLE_BRANCH=$1
# On 2025-02-12
HASH=95d460a01cfdc79f64b69d2b32393cb8dcaabb1a

if [ -z ${APPLE_BRANCH} ]; then
    echo 'Skipping Apple install as not requested.'
else
    rm -rf /root/.cache
    git clone --branch ${APPLE_BRANCH} --single-branch https://github.com/Apple-Network/apple-blockchain.git /apple-blockchain
    cd /apple-blockchain 
    git submodule update --init mozilla-ca 
    git checkout $HASH
    chmod +x install.sh

    /usr/bin/sh ./install.sh

    if [ ! -d /chia-blockchain/venv ]; then
        cd /
        rmdir /chia-blockchain
        ln -s /apple-blockchain /chia-blockchain
        ln -s /apple-blockchain/venv/bin/apple /chia-blockchain/venv/bin/chia
    fi
fi
