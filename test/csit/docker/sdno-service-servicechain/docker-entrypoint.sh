#!/bin/bash
#
# This file was auto-generated by gen-all-dockerfiles.sh; do not modify manually.
#
# ./sdno-service-servicechain/docker-entrypoint.sh
#

if [ -z "$SERVICE_IP" ]; then
    export SERVICE_IP=`hostname -i`
fi
echo
echo Environment Variables:
echo "SERVICE_IP=$SERVICE_IP"


if [ -z "$MSB_ADDR" ]; then
    echo "Missing required variable MSB_ADDR: Microservices Service Bus address <ip>:<port>"
    exit 1
fi
echo "MSB_ADDR=$MSB_ADDR"
echo

# Wait for MSB initialization
echo Wait for MSB initialization
for i in {1..20}; do
    curl -sS -m 1 $MSB_ADDR > /dev/null && break
    sleep $i
done

echo

# Configure service based on docker environment variables
./instance-config.sh

# Perform one-time config
if [ ! -e init.log ]; then
    # Generate sshd keys
    /usr/bin/ssh-keygen -A

    # Perform workarounds due to defects in release binary
    ./instance-workaround.sh

    # microservice-specific one-time initialization
    ./instance-init.sh

    date > init.log
fi

# temporarily enable sshd
/usr/sbin/sshd -D &


# Start the microservice
./instance-run.sh

