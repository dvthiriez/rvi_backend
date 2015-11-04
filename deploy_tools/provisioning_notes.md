Provisioning a new site
======================

## Required packages:

* Python 2.7
* build-essential
* pip
* mysql
* libffi-development
* libssl-development
* python-mysql
* nginx
* Erlang
* Git
* vritualenv

eg, on Ubuntu:

    sudo apt-get update
    sudo apt-get install build-essential python-pip python-dev mysql-server python-mysqldb
    sudo apt-get install libffi-dev libssl-dev libmysqlclient-dev nginx erlang git
    sudo update-rc.d mysql defaults
    sudo pip install virtualenv

## Nginx Virtual Host config

* see nginx.template.conf
* replace SITENAME with, eg, staging.my-domain.com

## Upstart Job

* see gunicorn-upstart.template.conf
* replace SITENAME with, eg, staging.my-domain.com

## Folder structure:
Assume we have a user account at /home/username
