# Spark deploy instructions

Your Spark applications will run in the cluster, but the 'driver' application will run on your machine.
Recommend 2GB+ RAM and 1 CPU cores for your driver VM.

A Spark/HDFS cluster has been deployed for you. To use it, first you will configure ports and security.

## Step 1: Setup Local Machine

The web GUIs for Spark and HDFS are not open publicly, you will need to configure some port forwarding so that you can access them via the TCP ports.

To do this, create or modify the file ~/.ssh/config on your local (laptop) computer by adding a section like the one shown below:
(This is unix-like systems and (Windows Subsystem for Linux) WSL, you may have to modify the instructions if you are using some other system).

Replace 130.238.x.y and ~/.ssh/id_rsa with your floating IP and key path appropriately:
```
Host 130.238.x.y
KexAlgorithms +diffie-hellman-group1-sha1
        User ubuntu
        # modify this to match the name of your key
        IdentityFile ~/.ssh/id_rsa
        # Spark master web GUI
        LocalForward 8080 192.168.2.251:8080
        # HDFS namenode web gui
        LocalForward 9870 192.168.2.251:9870
        # Python notebook
        LocalForward 8888 localhost:8888
        # Spark applications
        LocalForward 4040 localhost:4040
        LocalForward 4041 localhost:4041
        LocalForward 4042 localhost:4042
        LocalForward 4043 localhost:4043
        LocalForward 4044 localhost:4044
        LocalForward 4045 localhost:4045
        LocalForward 4046 localhost:4046
        LocalForward 4047 localhost:4047
        LocalForward 4048 localhost:4048
        LocalForward 4049 localhost:4049
        LocalForward 4050 localhost:4050
        LocalForward 4051 localhost:4051
        LocalForward 4052 localhost:4052
        LocalForward 4053 localhost:4053
        LocalForward 4054 localhost:4054
        LocalForward 4055 localhost:4055
        LocalForward 4056 localhost:4056
        LocalForward 4057 localhost:4057
        LocalForward 4058 localhost:4058
        LocalForward 4059 localhost:4059
        LocalForward 4060 localhost:4060
```

> [!NOTE]
> - The 'IdentityFile' line follows the same syntax whether you are using a .pem key file, or an OpenSSH key file (without an extension), as shown above. For a .pem, write something like this:
      IdentityFile ~/.ssh/my_key.pem
> - If you are using Windows Subsystem for Linux (WSL), the path to the identity file needs to be relative to the root of the filesystem for Ubuntu.
> - You may get a warning about an "UNPROTECTED PRIVATE KEY FILE!" - to fix this, change the permissions on your key file to 400.
chmod 400 ~/.ssh/mykey.pem
> - If you are using Windows Subsystem for Linux (WSL), you may need to copy your SSH key into the Ubuntu filesystem to be able to modify the permissions.

## Step 2: Verify Local Machine Setup
With these settings, you can connect to your host like this (without any additional parameters):

```
ssh 130.238.x.y
```

And when you access `localhost:8080` in your browser, it will be forwarded to `192.168.2.251:8080` - the Web GUI of the Spark master.

Check the Spark and HDFS cluster is operating by opening these links in your browser
- http://localhost:8080
- http://localhost:9870


All needed ports have been added in the default security group, but in case of special uses, you should create new security group with new rules and assign to your instance. Do NOT modify the default security group. For HDFS, try Utilities > Browse to see the files on the cluster.


## Step 3: Install dependencies on Driver VM

To setup the driver VM perform the following installations:

```
# Update apt repo metadata: 
sudo apt update

# Install java: 
sudo apt install -y openjdk-17-jdk

# Env variable so the workers know which Python to use...
echo "export PYSPARK_PYTHON=python3" >> ~/.bashrc
source ~/.bashrc

# Install git
sudo apt install -y git

# Install python packages manager: 
sudo apt install -y python3-pip

# Check the version:
python3 -m pip --version

# Install pyspark (version must be matched as the Spark cluster), and some other useful deps
python3 -m pip install pyspark==3.5.4 --user
python3 -m pip install pandas --user
python3 -m pip install matplotlib --user

# Clone the examples from the lectures, so you have a copy to experiment with
git clone https://github.com/usamazf/DE1-Spark.git

# Install jupyterlab
python3 -m pip install jupyterlab --user

```


## Step 4: Setup hotnames in /etc/hosts file

Manually define a hostname for all the hosts on the de1 project. this will ensure connections of spark between difference instances: 

```
sudo /bin/bash -c 'for ((i = 1 ; i <= 255 ; i++)); do echo "192.168.2.${i} de1-spark-host-${i}" >> /etc/hosts; done'
```

> [!NOTE] 
> If you have added entries to /etc/hosts yourself, you need to remove those.



## Step 5: Submit Spark applications
In order to start submitting spark applications via jupyter notebooks first run the jupyter instance according to instructions provided in Lab / Assignment 1 of the course (including password setup, authentication certificates etc.).

```
jupyter lab
```

- Now you can run the examples from the lectures in your own notebook. Using the Jupyter Notebook, navigate into the directory you just cloned from GitHub.

- Start with `DE-2025/examples/Lecture1_Example0_with_spark.ipynb`

- Ensure the host is set correctly for the Spark master, and HDFS namenode, to: `192.168.2.251`


When working on your own notebooks, save them in your own repository (for example which you created in A1, do a git clone) and make sure to commit and push changes often (for backup purposes).

When you start your application, you'll see it running in the Spark master web GUI (link at the top). If you hover over the link to your application, you'll see the port number for the Web GUI for your application. It will be 4040, 4041,... You can open the GUI in your web browser like this (e.g.): http://localhost:4040


## General Guidelines:

You need to share the Spark cluster with the other students, hence keep the following general principles in mind:

1. Start your application with dynamic allocation enabled, a timeout of no more than 30 seconds, and a cap on CPU cores (4 cores max per application): (fixed driver/blockManager port for security group)

        spark_session = SparkSession\
                .builder\
                .master("spark://192.168.2.251:7077") \
                .appName("your_application_name")\
                .config("spark.dynamicAllocation.enabled", True)\
                .config("spark.dynamicAllocation.shuffleTracking.enabled",True)\
                .config("spark.shuffle.service.enabled", False)\
                .config("spark.dynamicAllocation.executorIdleTimeout","30s")\
                .config("spark.executor.cores",2)\
                .config("spark.driver.port",9999)\
                .config("spark.blockManager.port",10005)\
                .getOrCreate()

2. Put your name in the name of your application.
3. Kill your application when your have finished with it.
4. Don't interfere with any of the virtual machines in the cluster.
5. Run one app at a time.
6. When the lab is not running, you can use more resources, but keep an eye on other people using the system.
