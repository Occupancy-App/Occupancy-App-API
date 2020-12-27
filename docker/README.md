# OccupancyApp Endpoing

## Installation

### Ubuntu 20.04


#### LetsEncrypt

Using [these instructions](https://tecadmin.net/how-to-setup-lets-encrypt-on-ubuntu-20-04/).

```shell
$ sudo apt-get -y install certbot 
$ sudo certbot certonly --standalone --rsa-key-size 4096 -d api.occupancyapp.com
```

Certificate and chain written to `/etc/letsencrypt/live/api.occupancyapp.com/fullchain.pem`

Key file written to `/etc/letsencrypt/live/api.occupancyapp.com/privkey.pem`

#### Create 4096-bit dhparams file

```
$ openssl dhparam -out dhparam.pem 4096
```

## Install Docker

Instructions [here](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04).

## Install Docker Compose

Use [these instructions](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-20-04)

## Build containers

```
$ docker-compose build
```

### Run containers

```
$ docker-compose up --detach
```

(Leave off the detach if you want to stay attached and watch logs)
