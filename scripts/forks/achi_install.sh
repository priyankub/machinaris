#!/bin/env bash
#
# Installs Achi as per https://github.com/Achi-Coin/achi-blockchain
#

ACHI_BRANCH=$1
# On 2024-02-08
HASH=e3ca475efb3d7267d3a2eedef8b4897d129aeb5d

if [ -z ${ACHI_BRANCH} ]; then
    echo 'Skipping Achi install as not requested.'
else
    sudo apt update
    sudo apt upgrade -y
    sudo apt install -y build-essential cmake git python3 python3-pip python3-venv libssl-dev libboost-all-dev libgmp-dev clang rustc pkg-config cargo

    git clone --branch ${ACHI_BRANCH} --recurse-submodules https://github.com/priyankub/achi-blockchain.git /achi-blockchain
    git clone https://github.com/priyankub/alvm.git
    git clone https://github.com/priyankub/alvm_rs.git
    git clone https://github.com/priyankub/alvm_tools.git
    git clone https://github.com/priyankub/achipos.git
    git clone https://github.com/priyankub/achibip158.git
    git clone https://github.com/priyankub/achivdf.git
    git clone https://github.com/priyankub/blspy.git

    cd /achi-blockchain
    git submodule update --init mozilla-ca 
    git checkout $HASH

    python3 -m venv venv
    source venv/bin/activate
    ln -s venv/bin/activate .
    
    pip install maturin

    pip install ../achibip158/
    pip install ../achipos/
    pip install ../alvm/
    pip install ../alvm_tools/
    maturin develop --release -m ../alvm_rs/Cargo.toml
    pip install ../achivdf/
    pip install ../blspy/

    pip install -e .

    if [ ! -d /chia-blockchain/venv ]; then
        cd /
        rmdir /chia-blockchain
        ln -s /achi-blockchain /chia-blockchain
        ln -s /achi-blockchain/venv/bin/achi /chia-blockchain/venv/bin/chia
    fi

    #Cleanup
    rm -rf ../alvm ../alvm_rs ../alvm_tools ../achipos ../achibip158 ../achivdf ../blspy
fi
