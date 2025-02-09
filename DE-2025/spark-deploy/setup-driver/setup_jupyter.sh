#!/bin/bash

auth_certificate_path="/home/ubuntu/auth-certs"

# Check for root access
if [[ $EUID -eq 0 ]];
then
    # Rerun the script with elevated priviledge
    exec sudo -u ubuntu bash "$0" "$@"

    exit "$?";
fi

# Skipping the annoying prompts of kernel restart
export NEEDRESTART_MODE=a
sed -i "s/#\$nrconf{kernelhints} = -1;/\$nrconf{kernelhints} = -1;/g" /etc/needrestart/needrestart.conf

# Install dependencies
python3 -m pip install -r requirements.txt

# Create 30 day validity certificate
mkdir $auth_certificate_path
openssl req -x509 -nodes -days 30 -newkey rsa:2048 -keyout $auth_certificate_path/mykey.key -out $auth_certificate_path/mycert.pem -subj "/C=SE/ST=UPPSALA"

# Setup jupyter notebook password
jupyter server password

# Generate Jupyter configurations file
jupyter server --generate-config -y

# Setup authentication related values
echo "c.ServerApp.certfile = u'$auth_certificate_path/mycert.pem'" >> /home/ubuntu/.jupyter/jupyter_server_config.py
echo "c.ServerApp.keyfile = u'$auth_certificate_path/mykey.key'" >> /home/ubuntu/.jupyter/jupyter_server_config.py
echo "c.ServerApp.ip = '*'" >> /home/ubuntu/.jupyter/jupyter_server_config.py
echo "c.ServerApp.open_browser = False" >> /home/ubuntu/.jupyter/jupyter_server_config.py
echo "c.ServerApp.port = 8888" >> /home/ubuntu/.jupyter/jupyter_server_config.py

# Setup Java path on the driver
echo "export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64" >> /home/ubuntu/.bashrc 
