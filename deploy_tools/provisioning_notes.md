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

```
ubuntu@server:$ sudo apt-get update
ubuntu@server:$ sudo apt-get install build-essential python-pip python-dev mysql-server python-mysqldb

    # You may be prompted to set the mysql root password at this point. If so, use 'newpwd'
    # However, if you'd like to set it to something else, just update your local machine's 
    # fabfile.py if you plan on using Fabric for remote deployment

ubuntu@server:$ sudo apt-get install libffi-dev libssl-dev libmysqlclient-dev nginx erlang git
ubuntu@server:$ sudo update-rc.d mysql defaults
ubuntu@server:$ sudo pip install virtualenv
```

## Usage and setup of automated deployment using Fabric:
If a new deployment, proceed with the steps above to set up all packages required on your server.

Then, use Fabric and the included fabfile.py to perform a remote deployment by executing the following 
commands on your local machine (replacing *staging.my-domain.com* with the server you're provisioning)
```
$ cd rvi_backend/deploy_tools
$ pip2 install fabric
$ fab deploy:host=ubuntu@staging.my-domain.com
```

**Note:** If access to your server is via private key, you'll have to first add the key to your local 
machine. e.g.
```
$ eval `ssh-agent -s`
$ ssh-add ~/.ssh/ec2key.pem
$ fab deploy:host=ubuntu@staging.my-domain.com
```


Next, connect to your instance over SSH once the Fabric is complete
and restart your Nginx and Gunicorn services.

```
ubuntu@server:$ sudo service nginx reload
ubuntu@server:$ sudo stop gunicorn-staging.my-domain.com
ubuntu@server:$ sudo start gunicorn-staging.my-domain.com
```


Lastly, if this is a new deployment, finish by creating a super user for your instance.
```
ubuntu@server:$ export PYTHONPATH=~/sites/*SITENAME*/source

    # In order to set the Python path for your current shell

ubuntu@server:$ cd ~/sites/*SITENAME*/source/web
ubuntu@server:$ ../../virtualenv/bin/python manage.py createsuperuser

    # Using Python from your instance's virtual environment
```


For additional details or a full walkthrough, refer to chapters 8 and 9 in Test-Driven Development with Python,
by Harry J.W. Percival available @ http://www.obeythetestinggoat.com



## Additional deployment info...

## Folder structure:

Assume we have a user account at /home/username


## Nginx Virtual Host config

* see nginx.template.conf
* replace SITENAME with, eg, staging.my-domain.com


## Upstart Job

* see gunicorn-upstart.template.conf
* replace SITENAME with, eg, staging.my-domain.com
