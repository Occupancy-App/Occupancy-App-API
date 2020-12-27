# OccupancyApp API Endpoint App

## Installation

### Ubuntu 20.04

#### Set up DNS record

Need a DNS A record to point to IP address where you're installing in order 
to get a certificate assigned for that host.

#### Open Firewall For Certificate Request

Open incoming connections to TCP port 80 to allow the certificate validation to pass.

#### LetsEncrypt

Using [these instructions](https://tecadmin.net/how-to-setup-lets-encrypt-on-ubuntu-20-04/).

```shell
$ sudo apt-get update
$ sudo apt-get -y install certbot 
$ sudo certbot certonly --non-interactive --standalone --agree-tos --email [email address] --rsa-key-size 4096 --domain
[fully-qualified hostname, e.g. api.occupancyapp.com]
```

Certificate and chain written to `/etc/letsencrypt/live/api.occupancyapp.com/fullchain.pem`

Key file written to `/etc/letsencrypt/live/api.occupancyapp.com/privkey.pem`

#### Close HTTP Port 

Now that the certificate was assigned, close TCP port 80 (HTTP) access to this host.


#### Create High-Quality Diffie-Helman Parameter File

```
$ mkdir -p ~/git/Occupany-App-API/docker/reverse_proxy/crypto
$ cd ~/git/Occupancy-App-API/docker/reverse_proxy/crypto
$ openssl dhparam -out dhparam.pem 4096
```

The `openssl` command will take awhile (5-10 minutes based on CPU speed from my experience).

#### Install Docker

Instructions [here](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04).

#### Install Docker Compose

Use [these instructions](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-20-04)


#### Automatic TLS Certificate Renewal

Do the cron stuff needed for daily renewal check and container rebuild.

#### Find nginx and Alpine OpenSSL Versions

We need to know versions.

#### Create proper NGINX Config, Update As Necessary

Do the auto config builder, check against existing.

#### Build containers

```
$ docker-compose build
```

#### Open HTTPS Firewall port

Do some firewall stuff.

#### Run containers

```
$ docker-compose up --detach
```

(Leave off the detach if you want to stay attached and watch logs)
