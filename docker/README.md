# OccupancyApp Endpoing

## Installation

### Ubuntu 20.04


#### LetsEncrypt

Using [these instructions](https://tecadmin.net/how-to-setup-lets-encrypt-on-ubuntu-20-04/).

```shell
$ sudo apt-get -y install certbot 
$ sudo certbot certonly --standalone -d [FQDN, e.g. "api.occupancyapp.com")]
```

Certificate and chain written to `/etc/letsencrypt/live/[domain]/fullchain.pem`

Key file written to `/etc/letsencrypt/live/[domain]/privkey.pem`


## Install Docker

(Use digitalocean Ubuntu 20.04 instructions)

## Install Docker Compose

Use [these instructions](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-20-04)

## Build container

*NOTE*: MUST be run as a user able to run sudo *without a password*.

```shell
$ OCCUPANCY_CERT_DIR=[path to fullchain.pem and privkey.pem, e.g. "OCCUPANCY_CERT_DIR=/etc/letsencrypt/live/api.occupancyapp.com"] build-container
```
