#!/bin/bash

count=1
volume_size=50
prefix=group-3-shahab
openstack \
server create --block-device uuid=b229a221-e685-4376-98a6-295d502bb41e,source_type=image,volume_size=$volume_size,boot_index=0,delete_on_termination=true \
--flavor ssc.small --key-name db1 --security-group default \
--network ee482b5f-f68a-4404-a5d8-076eb1200cca \
--wait --min $count --max $count $prefix

floating_ip="$(openstack  floating ip create 9187404b-b24b-4ee5-b5f4-22d9a15dc4e2 | grep floating_ip_address | awk '{print $4}')"
echo $floating_ip > floating_ip.txt

openstack server add floating ip $prefix $floating_ip