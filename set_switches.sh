#!/bin/bash

RATE_P3=$1
RATE_P4=$2

if [ -z "$RATE_P3" ] || [ -z "$RATE_P4" ]; then
    echo "Error: no port rates defined"
    echo "Usage: $0 <rate_port_3> <rate_port_4>"
    exit 1
fi

python3 initiate_rules.py

simple_switch_CLI --thrift-port 9090 <<< 'set_queue_depth 200'
simple_switch_CLI --thrift-port 9090 <<< "set_queue_rate $RATE_P3 3"
simple_switch_CLI --thrift-port 9090 <<< "set_queue_rate $RATE_P4 4"

# simple_switch_CLI --thrift-port 9090 <<< 'set_queue_depth 200'
# simple_switch_CLI --thrift-port 9090 <<< 'set_queue_rate 200 3'
# simple_switch_CLI --thrift-port 9090 <<< 'set_queue_rate 200 4'

# simple_switch_CLI --thrift-port 9091 <<< 'set_queue_depth 200'
# simple_switch_CLI --thrift-port 9091 <<< 'set_queue_rate 293 3'
# simple_switch_CLI --thrift-port 9091 <<< 'set_queue_rate 18 4'

# simple_switch_CLI --thrift-port 9092 <<< 'set_queue_depth 200'
# simple_switch_CLI --thrift-port 9092 <<< 'set_queue_rate 60 3'
# simple_switch_CLI --thrift-port 9092 <<< 'set_queue_rate 48 4'

python3 receive_queues.py
