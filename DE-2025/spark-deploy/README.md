# Instructions

## Setup OpenStack API

- Setup the environment variable for authentication according to here https://docs.openstack.org/api-quick-start/api-quick-start.html#authentication-and-api-request-workflow

## Configure the Master and Worker VMs

- Go to `./configs`
- Edit the `instance-cfg.yaml`
  - Head Node
    - just modify the `authorized_keys` to your key pair created in openstack cloud
    - You can modify other parameters for the instance or you can just keep it that way
  - Worker Node
    - modify the `numWorkers` to your needs.
    - change the `authorized_keys` to your key pair created in openstack cloud

## Initiate the Cluster

- Run `chmod +x ./deploy-full.sh` to make it executable
- Run `./deploy-full.sh`

## Access the cluster through your driver

- Add the private key to the driver
  - Copy the private ssh to your driver

  `scp ./__temp_dir__/keypair/id_rsa <user>:<driver ip>://.ssh/`
  
  - Start ssh-agent on the driver
  
  `eval "$(ssh-agent -s)"`

  - Add the key to the agent

  `ssh-add .ssh/id_rsa`
- Now it is possible to ssh to master and worker nodes through our driver.
