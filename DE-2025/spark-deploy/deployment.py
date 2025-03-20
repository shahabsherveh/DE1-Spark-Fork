import os
import fire
import random
import time
import requests

from utils.instance import create_instance, delete_instance
from utils.configs import parse_configs, write_configs
from utils.keygen import generate_keypair, read_public_key

def deploy_headnode(name_prefix, configs, ssh_keys):
    """A module to create the headnode and send config files."""

    cloud_cfg = parse_configs(config_path=configs["instance_configs"])
    configs["instance_configs"] = "__temp_dir__/temp_headnode_cfg.yaml"
    
    # Append new key for all users
    for user in cloud_cfg["users"]:
        if "ssh_authorized_keys" in user.keys():
            user["ssh_authorized_keys"].extend(ssh_keys)  
        else:
            user["ssh_authorized_keys"] = ssh_keys

    # # Write GIT access token to a 
    # # local file on the head node
    # cloud_cfg["write_files"] = [{
    #     "content": github_access_token,
    #     "path": "/crawlerdata/GITHUB_ACCESS_TOKEN.txt",
    #     "permissions": "0644",
    # }]

    os.makedirs("__temp_dir__", exist_ok=True)
    write_configs(configs["instance_configs"], cloud_cfg)

    # Prepend the head comment: #cloud-config 
    # to newly created yaml file
    with open(configs["instance_configs"], "r+") as f:
        content = f.read()
        f.seek(0, 0)
        f.write("#cloud-config" + "\n\n" + content)

    # Create the headnode and obtain ip address
    ip_addr = create_instance(name=f"{name_prefix}-spark-headnode", configs=configs)

    return ip_addr

def launch_workernodes(name_prefix, num_nodes, head_ip, configs, ssh_keys):

    # Update cloud configurations in order to write
    # the head ip address to a temporary file at
    # worker node
    old_cfg_path = configs["instance_configs"]
    configs["instance_configs"] = "__temp_dir__/temp_worknode_cfg.yaml"

    # If head_ip is None we assume that
    # the user is adding nodes to the
    # existing swarm, which in turn means
    # that the temporary configuration files
    # already exist from initial launch.
    if head_ip is not None:
        cloud_cfg = parse_configs(config_path=old_cfg_path)
        
        # Append new key for all users
        for user in cloud_cfg["users"]:
            if "ssh_authorized_keys" in user and user["ssh_authorized_keys"] is not None:
                user["ssh_authorized_keys"].extend(ssh_keys)  
            else:
                user["ssh_authorized_keys"] = ssh_keys

        # Write head ip to a file
        cloud_cfg["write_files"] = [{
            "content": f"{head_ip}",
            "path": "/HEAD-IP.txt",
            "permissions": "0644",
        }]
        os.makedirs("__temp_dir__", exist_ok=True)
        write_configs(configs["instance_configs"], cloud_cfg)

        # Prepend the head comment: #cloud-config 
        # to newly created yaml file
        with open(configs["instance_configs"], "r+") as f:
            content = f.read()
            f.seek(0, 0)
            f.write("#cloud-config" + "\n\n" + content)

    # Deploy all nodes
    ip_addresses = []
    for i in range(num_nodes):
        # Create the headnode and obtain ip address
        ip_addresses += [create_instance(name=f"{name_prefix}-spark-worker-{i+1}", configs=configs)]
        print(f"Worker-{i+1} deployed at {ip_addresses[-1]} ...")

    # Retrun worker ip addresses
    return ip_addresses

def add_workernodes(num_nodes, head_ip = None, config_file="configs/instance-cfg.yaml", keypair_path="__temp_dir__/keypair", keyname="id_rsa", ipaddr_path="__temp_dir__/cluster_ips.txt"):
    # Open the configurations file
    print("Parsing provided configurations file... ")
    configs = parse_configs(config_path=config_file)

    # Produce a random identifier
    identifier = random.randint(1000,9999)

    # Read existing public key
    # ssh_key = read_public_key(keypath=keypair_path, keyname=keyname)

    # Obtain the swarm token
    print("\nDeploying worker nodes ... ")
    worker_ips = launch_workernodes(name_prefix=f"{configs['instances']['name_prefix']}-{identifier}", num_nodes=num_nodes, head_ip=head_ip, configs=configs["instances"]["workernodes"]["workercfgs"], ssh_keys=None)

    with open(ipaddr_path, "a") as f:
        [f.write(f"{worker_ip}\n") for worker_ip in worker_ips]

def del_workernodes(num_nodes, manager_port = 5200, ipaddr_path="__temp_dir__/cluster_ips.txt"):
    ip_addresses = open(ipaddr_path).readlines()
    count = 0
    for ip_addr in reversed(ip_addresses.copy()):
        if (count >= num_nodes): break
        #response = requests.post(f"http://{ip_addr.strip()}:{manager_port}/drain-node", timeout=300)
        #if response.status_code == 200:
        delete_instance(search_opts={"ip": ip_addr.strip()})
        ip_addresses.remove(ip_addr)
        count += 1
        #else:
        #    print(response.status_code, response.content)

    # Update the instance ip address list
    open(ipaddr_path, "w").writelines(ip_addresses)

def full_deployment(config_file = "configs/instance-cfg.yaml", keypair_path="__temp_dir__/keypair", keyname="id_rsa", ipaddr_path="__temp_dir__/cluster_ips.txt"):
    # Open the configurations file
    print("Parsing provided configurations file... ")
    configs = parse_configs(config_path=config_file)

    # Produce a random identifier
    identifier = random.randint(1000,9999)

    # Generate a new private/public keypair
    new_ssh_key = generate_keypair(keypath=keypair_path, keyname=keyname)
    ssh_keys = [new_ssh_key] + (configs["ssh_authorized_keys"] if ("ssh_authorized_keys" in configs.keys() and configs["ssh_authorized_keys"] is not None) else [])

    # Perform deployment of headnode
    # rest all will be handled by headnode
    print("Deploying head node ... ")
    head_ip = deploy_headnode(name_prefix=f"{configs['instances']['name_prefix']}-{identifier}", configs=configs["instances"]["headnode"], ssh_keys=ssh_keys)
    print(f"Head node deployed at {head_ip} ...")
    
    # Should have a 3-4 minutes of wait here!!!
    time.sleep(120)

    # Obtain the swarm token
    # docker swarm join-token manager -q
    print("\nDeploying worker nodes ... ")
    worker_ips = launch_workernodes(name_prefix=f"{configs['instances']['name_prefix']}-{identifier}", num_nodes=configs["instances"]["workernodes"]["numworkers"], head_ip=head_ip, configs=configs["instances"]["workernodes"]["workercfgs"], ssh_keys=ssh_keys)

    with open(ipaddr_path, "w") as f:
        f.write(f"{head_ip}\n")
        [f.write(f"{worker_ip}\n") for worker_ip in worker_ips]

if __name__ == "__main__":
    fire.Fire({
        "--full": full_deployment,
        "--add-nodes": add_workernodes,
        "--del-nodes": del_workernodes,
    })
