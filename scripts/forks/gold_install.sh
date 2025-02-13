#!/bin/env bash
#
# Installs Gold as per https://github.com/goldcoin-gl/gold-blockchain
#

GOLD_BRANCH=$1
# On 2025-02-12
HASH=50879493c84486dc73055850e5267c484f630809

if [ -z ${GOLD_BRANCH} ]; then
    echo 'Skipping Gold install as not requested.'
else
    rm -rf /root/.cache
    git clone --branch ${GOLD_BRANCH} --single-branch https://github.com/goldcoin-gl/gold-blockchain.git /gold-blockchain
    cd /gold-blockchain 
    git submodule update --init mozilla-ca 
    git checkout $HASH
    chmod +x install.sh

    /usr/bin/sh ./install.sh

    if [ ! -d /chia-blockchain/venv ]; then
        cd /
        rmdir /chia-blockchain
        ln -s /gold-blockchain /chia-blockchain
        ln -s /gold-blockchain/venv/bin/gold /chia-blockchain/venv/bin/chia
    fi
fi
