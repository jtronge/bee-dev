## BEE Development Docker Image

This is a short document that will explain how to build and then run
this BEE Development Docker Image.

Note: Since this is using Docker you may have to run many of the commands below
with sudo.

To start out with untar the image file and make sure that you are in the
image directory. Take a look at the CONF file with a text editor. You should see
the contents that look something this:

```
# BEE Development Configuration Variables

# Directory to be mounted rw at /data

# DATA and LOG will need to be updated for your system

DATA=/run/media/jaket/794df44c-3015-465e-9e13-54253fed5855/data/BEE/

# Log file relative to the host system

LOG=/run/media/jaket/794df44c-3015-465e-9e13-54253fed5855/data/BEE/log/startup.log

# Repository directy _relative_ to the directy mounted at /data

BEE_REPO_DIR=BEE_Private
```

Make sure that you have a clean directory where you have cloned the BEE\_Private
repo. Set the DATA directory to the location of this directory. This will be
mounted read-write within the image. You'll also want to set the LOG variable to
a location on the host system for debugging purposes. This will store all output
from running the `./start` script, which will initialize the container.

When you have configured that properly you can run this command to build the image:

```
./build
```

This will take some time if Docker doesn't already have parts of the image
cached.

Now you can start the container with the following command. The first time you
run this it will create a new virtualenv for BEE and install all of the
dependencies. This may fail if the BEE\_REPO\_DIR variable is not specified to
a directory relative to /data within the image.

```
./start
```

When that completes you should be able to run this to launch a shell into the
container:

```
./launch-shell
```

Before running BEE you should set up your BEE config file. The config must be
stored in one of the following locations on these systems:

Linux:

- /etc/beeflow/bee.conf
- ~/.config/beeflow/bee.conf

MacOS:

- /Library/Application Support/beeflow/bee.conf
- ~/Library/Application Support/beeflow/bee.conf

Windows:

- %APPDATA%\beeflow\bee.conf

Here is an example initial BEE configuration file. You will need to modify
a couple of parameters, including the location of the Neo4j image file.

```
# BEE CONFIGURATION FILE #

[graphdb]

hostname = localhost

dbpass = password

bolt\_port = 7687

http\_port = 7474

https\_port = 7473

gdb\_image = /data/bee-dev/neo4j-ch.tar.gz

gdb\_image\_mntdir = /tmp

[workflow\_manager]

listen\_port = 5000


[task\_manager]

listen\_port = 5050
```

After updating this configuration file you should be ready to run BEE within
the container. You can use tmux or GNU screen to open several shell sessions.
You will need one window for the BEE Task Manager, one for the BEE Workflow
Manager, one for the neo4j image and one left over for running the client.

Note: The steps below may change depending on the development of the new
BEEStart script

Now you first need to run the startup.py script to start the Neo4j container.
Note that the location of the Neo4j image file will be taken from the bee config
file and should be accessible within the container.

```
python -m beeflow.server.startup
```

Now you can start the workflow manager. You will need to first change
into the server directory.

```
cd beeflow/server

python server.py
```

In another shell window you can then start the task manger:

```
cd beeflow/task\_manager

python task\_manager.py
```

If any of these commands fail to run you may need to take a look at the bee
config file and make sure that everything is correct.

Given that all of those commands are running you can now run the client to
submit a job. The client runs as an interpreter which can be used to submit
and start workflows, query workflows and also pause or resume workflows.
Submitting a workflow will send it to the workflow manager that will then
store this in the Neo4j database. By starting the workflow from the client
the task manager will start submitting jobs for steps in the workflow. 

```
cd beeflow/client

python client.py
```

After finishing up work on BEE, in order to stop running the container you
can exit from the shell within the container and run this command to shutdown
the container

```
./kill
```

