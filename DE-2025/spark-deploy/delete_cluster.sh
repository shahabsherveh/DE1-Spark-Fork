#!/bin/bash
prefix=group-3-spark
floating_ip="$(cat floating_ip.txt)"

instances="$(openstack  server list | grep $prefix-* | awk '{print $2}')"
openstack server delete $instances