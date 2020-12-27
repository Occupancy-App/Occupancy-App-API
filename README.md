# OccupancyApp API Endpoint App

## Installation

### Ubuntu 20.04

#### Set up DNS record

Need a DNS A record to point to IP address where you're installing in order 
to get a certificate assigned for that host.

#### Open Firewall For Certificate Request

Open incoming connections to TCP port 80 to allow the certificate validation to pass.

#### Obtain TLS Certificate 

```shell
$ sudo apt-get update
$ sudo apt-get -y install certbot 
$ sudo certbot certonly --non-interactive --standalone --agree-tos --email [email address] --rsa-key-size 4096 --domain
[fully-qualified hostname, e.g. api.occupancyapp.com]
```

All files will be written to `/etc/letsencrypt/live/[hostname]`.

#### Close HTTP Port 

Now that the certificate was assigned, close TCP port 80 (HTTP) access to this host.


#### Create High-Quality Diffie-Hellman Parameter File

```
$ mkdir -p ~/git/Occupany-App-API/docker/reverse_proxy/crypto
$ cd ~/git/Occupancy-App-API/docker/reverse_proxy/crypto
$ openssl dhparam -out dhparam.pem 4096
```

The `openssl` command will take quite some time (5-15 minutes based on 
CPU speed from my experience). Turns out high-grade prime numbers that
are 4,096 bits in size take awhile to find. :)

#### Install Docker

Instructions [here](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04).

#### Install Docker Compose

Use [these instructions](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-20-04).


#### Automatic TLS Certificate Renewal

```
$ sudo bash
# cd ~
# vi crontab.root
```

Add the following file contents:

```
DOCKER_COMPOSE_YAML=/full/path/to/Occupancy-App-API/docker/docker-compose.yaml

# Example of job definition:
# .---------------- minute (0 - 59)
# |  .------------- hour (0 - 23)
# |  |  .---------- day of month (1 - 31)
# |  |  |  .------- month (1 - 12) OR jan,feb,mar,apr ...
# |  |  |  |  .---- day of week (0 - 6) (Sunday=0 or 7) OR sun,mon,tue,wed,thu,fri,sat
# |  |  |  |  |
# *  *  *  *  * user-name command to be executed
0 6  *  *  *  /usr/bin/certbot renew --pre-hook "/usr/local/bin/docker-compose -f $DOCKER_COMPOSE_YAML down" --post-hook "/usr/local/bin/docker-compose -f $DOCKER_COMPOSE_YAML up -d"
```

Obviously update to the proper path for your system, e.g., `/home/ubuntu/git/Occupancy-App-API/docker/docker-compose.yaml`.

Then run:

```
# crontab crontab.root
# crontab -l
# exit
$ 
```

The contents of the file should be shown for the `crontab -l` command.

#### Find nginx and Alpine OpenSSL Versions

* nginx Version
    - Go to the [Docker Hub page for nginx](https://hub.docker.com/_/nginx) and click on the `stable-alpine` tag
    - In the first 15-20 lines of the displayed Dockerfile, it'll say something like `ENV NGINX_VERSION 1.18.0`
    - That means your nginx version will be 1.18.0
* Alpine OpenSSL Version
    - In the same displayed Dockerfile, the very first line will be `FROM alpine:[version identifier]`
    - Example: as of 2020-12-27, it's Alpine 3.11
    - Go to [this Alpine package search page](https://pkgs.alpinelinux.org/packages)
    - In "Package Filter" section, enter `openssl` as the Package Name and click the first dropdown and select the proper version of
Alpine (e.g., 3.11)
    - Click the blue "Search" button
    - The entries in the "Version" column will tell you which version of OpenSSL will be used
    - Example: [Alpine 3.11 ships with OpenSSL version 1.1.1i](https://pkgs.alpinelinux.org/packages?name=openssl&branch=v3.11).

#### Create proper NGINX Config, Update As Necessary

* Go to the [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
* Enter the following values:
    - *Server*: nginx
    - *Mozilla Configuration*: Intermediate
    - *Environment*
        - *Server Version*: the version of nginx determined in previous section
        - *OpenSSL Version*: the OpenSSL version determined in previous section
    - *Miscellaneous*
        - *HTTP Strict Transport Security*: checked
        - *OCSP Stapling*: checked

Compare the generated configuration to `.../Occupancy-App-API/docker/reverse_proxy/config/nginx.conf`.

Update any fields that are incorrect for your installation 
(e.g., server_name and path to the certificate files).

Also update any recommended security settings that may have changed since this writing.

#### Open HTTPS Firewall port

Permit incoming HTTPS traffic (TCP port 443) to reach your host. 

#### Run containers

```
$ cd ~/git/Occupancy-App-API/docker
$ docker-compose up --build --detach
```

#### Make sure containers started cleanly

##### Check Running Containers

```
$ docker ps
```

You should see the three Occupancy backend containers running:

```
CONTAINER ID   IMAGE                 COMMAND                  CREATED              STATUS              PORTS                          NAMES
f0eb3694303f   nginx:stable-alpine   "/docker-entrypoint.…"   About a minute ago   Up About a minute   80/tcp, 0.0.0.0:443->443/tcp   reverse_proxy
27c8ccb23d30   docker_api_endpoint   "python occupancy_ap…"   About a minute ago   Up About a minute   80/tcp, 8000/tcp               docker_api_endpoint_1
31214a56b1a0   redis:6-alpine        "docker-entrypoint.s…"   About a minute ago   Up About a minute   6379/tcp                       docker_redis_1
```

##### Check Docker Logs

The following output shows a healthy startup of the system.

```
$ docker-compose logs
Attaching to reverse_proxy, docker_api_endpoint_1, docker_redis_1
api_endpoint_1         | 2020-12-27 21:02:19Z INFO     Listening for connections on port 8000
redis_1                | 1:C 27 Dec 2020 21:02:18.673 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
redis_1                | 1:C 27 Dec 2020 21:02:18.673 # Redis version=6.0.9, bits=64, commit=00000000, modified=0, pid=1, just started
redis_1                | 1:C 27 Dec 2020 21:02:18.673 # Configuration loaded
redis_1                | 1:M 27 Dec 2020 21:02:18.675 * Running mode=standalone, port=6379.
redis_1                | 1:M 27 Dec 2020 21:02:18.675 # Server initialized
redis_1                | 1:M 27 Dec 2020 21:02:18.675 # WARNING overcommit_memory is set to 0! Background save may fail under low memory condition. To fix this issue add 'vm.overcommit_memory = 1' to /etc/sysctl.conf and then reboot or run the command 'sysctl vm.overcommit_memory=1' for this to take effect.
redis_1                | 1:M 27 Dec 2020 21:02:18.675 * Ready to accept connections
reverse_proxy          | /docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to perform configuration
reverse_proxy          | /docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/
reverse_proxy          | /docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh
reverse_proxy          | 10-listen-on-ipv6-by-default.sh: Getting the checksum of /etc/nginx/conf.d/default.conf
reverse_proxy          | 10-listen-on-ipv6-by-default.sh: Enabled listen on IPv6 in /etc/nginx/conf.d/default.conf
reverse_proxy          | /docker-entrypoint.sh: Launching /docker-entrypoint.d/20-envsubst-on-templates.sh
reverse_proxy          | /docker-entrypoint.sh: Configuration complete; ready for start up
```

##### Test Locally

See if you can hit port 443 locally. 

*Note*: we have to put curl in an insecure mode as the hostname will not 
match the hostname in the TLS certificate presented by the server, which 
quite rightly curl should be concerned about.

```
$ curl --insecure -X PUT https://localhost/space/new/occupancy/current/0/max/50/name/testingonetwothree
```

Should get data returned for a JSON object describing a new space, similar to:

```json
{"space_id": "7fcccca5-5ee3-4c82-a0fc-4d1df69a882d", "space_name": "testingonetwothree", "occupancy": {"current": 0, "maximum": 50}, "created": "2020-12-27T21:10:28.602467Z", "last_updated": "2020-12-27T21:10:28.602467Z"}
```

##### Test Remotely

Go to a separate host that will have to reach across the network to talk to your new API endpoint, and run:

```
$ curl -X PUT https://[your hostname]/space/new/occupancy/current/0/max/50/name/testingonetwothree
```

Success will be JSON output similar to the previous section.

##### Test TLS Security Grade

Go to SSL Labs [SSL Server Test](https://www.ssllabs.com/ssltest/), enter 
the hostname of your endpoint, and click "Submit."

Should get an A+ grade. If you don't, figure out what needs to change in 
nginx configuration to get a better score.

#### Confirm Containers Restart Cleanly After Reboot

Reboot the host running the Docker containers, and re-run the "Remote Test"
section. Need to make sure that a

#### Set up recurring rebuild/restart job

```
$ cd ~
$ mkdir bin
$ cd bin
$ cp /path/to/Occupancy-App-API/docker/app/util/pull-upstream-images-and-rebuild-occupancy .
$ chmod u+x ./pull-upstream-images-and-rebuild-occupancy
```

Edit the new script to match the location of the Occupancy Git repository 
on your host.

Run the new script and make sure Occupancy restarts cleanly.

```
$ ~/bin/pull-upstream-images-and-rebuild-occupancy
No stopped containers
Pulling redis               ... done
Pulling api_endpoint        ... done
Pulling https_reverse_proxy ... done
redis uses an image, skipping
https_reverse_proxy uses an image, skipping
Building api_endpoint
Step 1/11 : FROM python:3.9-alpine
 ---> d4d4f50f871a
Step 2/11 : EXPOSE 8000
 ---> Running in 437ad7101111
Removing intermediate container 437ad7101111
 ---> c554194fd9b3
Step 3/11 : COPY requirements.txt /tmp
 ---> 44280fffbd5f
Step 4/11 : RUN pip install --no-cache-dir -r /tmp/requirements.txt
 ---> Running in 0ee99aba44ed
Collecting redis==3.5.3
  Downloading redis-3.5.3-py2.py3-none-any.whl (72 kB)
Collecting tornado==6.1
  Downloading tornado-6.1.tar.gz (497 kB)
Building wheels for collected packages: tornado
  Building wheel for tornado (setup.py): started
  Building wheel for tornado (setup.py): finished with status 'done'
  Created wheel for tornado: filename=tornado-6.1-cp39-cp39-linux_x86_64.whl size=414477 sha256=9370f789c61e614afffa0f3dfb8bb61c9c4456e0251f53a702221607d7ab0efb
  Stored in directory: /tmp/pip-ephem-wheel-cache-imd8w7lr/wheels/e6/6b/c3/dbb71bdabdc4681fb3cdf364f2c969f39ebc13c1a512cf6e43
Successfully built tornado
Installing collected packages: tornado, redis
Successfully installed redis-3.5.3 tornado-6.1
Removing intermediate container 0ee99aba44ed
 ---> fb23e7278556
Step 5/11 : ENV PYTHONUNBUFFERED=1
 ---> Running in f3e5b3176740
Removing intermediate container f3e5b3176740
 ---> ed06e6adee89
Step 6/11 : ENV PYTHONDONTWRITEBYTECODE=1
 ---> Running in fb7f6d7fe5ac
Removing intermediate container fb7f6d7fe5ac
 ---> 5996fbe9934d
Step 7/11 : RUN adduser --disabled-password apiuser
 ---> Running in 6ed73f4cfbbd
Removing intermediate container 6ed73f4cfbbd
 ---> 9eea1df87cbf
Step 8/11 : WORKDIR /home/apiuser/api_app
 ---> Running in b06fd64f8652
Removing intermediate container b06fd64f8652
 ---> dd26264488f2
Step 9/11 : USER apiuser
 ---> Running in c20ffd1da6ad
Removing intermediate container c20ffd1da6ad
 ---> 57c0315115e2
Step 10/11 : COPY src/ ./
 ---> 6b8271a28457
Step 11/11 : ENTRYPOINT [ "python", "occupancy_api_endpoint.py" ]
 ---> Running in dccc0b2e25a5
Removing intermediate container dccc0b2e25a5
 ---> 24991e1aadf1

Successfully built 24991e1aadf1
Successfully tagged docker_api_endpoint:latest
Recreating docker_redis_1 ... done
Recreating docker_api_endpoint_1 ... done
Recreating reverse_proxy         ... done

$ docker ps
$ docker ps
CONTAINER ID   IMAGE                 COMMAND                  CREATED              STATUS              PORTS                          NAMES
7aef6b2582f8   nginx:stable-alpine   "/docker-entrypoint.…"   About a minute ago   Up About a minute   80/tcp, 0.0.0.0:443->443/tcp   reverse_proxy
d16790fcb798   docker_api_endpoint   "python occupancy_ap…"   About a minute ago   Up About a minute   80/tcp, 8000/tcp               docker_api_endpoint_1
f01ad2e8c359   redis:6-alpine        "docker-entrypoint.s…"   About a minute ago   Up About a minute   6379/tcp                       docker_redis_1
```

Now create a nightly cron job to run this script.

```
$ cd ~
$ vi crontab.[your username]
```

Add the following contents:

```
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# Example of job definition:
# .---------------- minute (0 - 59)
# |  .------------- hour (0 - 23)
# |  |  .---------- day of month (1 - 31)
# |  |  |  .------- month (1 - 12) OR jan,feb,mar,apr ...
# |  |  |  |  .---- day of week (0 - 6) (Sunday=0 or 7) OR sun,mon,tue,wed,thu,fri,sat
# |  |  |  |  |
# *  *  *  *  * user-name command to be executed

# 0700 (host time) every day
0 7 * * * /home/[username]/bin/pull-upstream-images-and-rebuild-occupancy
```

Now set this crontab for the user:

```
$ crontab crontab.[username]
$ crontab -l
```

That should list the contents of the file you just added.

