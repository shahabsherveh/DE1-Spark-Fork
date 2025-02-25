#!/bin/bash

config_file="configs/instance-cfg.yaml"
[ ! -z "$1" ] && config_file="$1"

# Start deployment
python3 deployment.py --full --config_file=${config_file}