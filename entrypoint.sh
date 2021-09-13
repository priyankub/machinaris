#
#  Configure and start plotting and farming services.
#

# Always launch Chia - required blockchain
/usr/bin/bash /machinaris/scripts/chia_launch.sh

# Optionally launch forked blockchains for multi-farming
if [[ ${blockchains} =~ flax ]]; then
  /usr/bin/bash /machinaris/scripts/flax_launch.sh
fi

# Launch Machinaris web server and other services
/machinaris/scripts/start_machinaris.sh

# Build bladebit plotter on first run of container (quietly)
/usr/bin/bash /machinaris/scripts/bladebit_make.sh 2>&1 >/tmp/bladebit_make.log

while true; do sleep 30; done;
