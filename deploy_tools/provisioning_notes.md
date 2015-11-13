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

    # You may be prompted to set the mysql root password at this point. If so, use 'newpwd'
    # However, if you'd like to set it to something else, just update your local machine's 
    # fabfile.py if you plan on using Fabric for remote deployment

    sudo apt-get install libffi-dev libssl-dev libmysqlclient-dev nginx erlang git
    sudo update-rc.d mysql defaults
    sudo pip install virtualenv


## Usage and setup of automated deployment using Fabric:
Proceed with the steps above to set up all packages required on your server.

Then, to use the fabfile.py to perform a remote deployment, execute the following commands on your local machine,
replacing *staging.my-domain.com* with the server you're provisioning.
```
$ cd rvi_backend/deploy_tools
$ pip2 install fabric
$ fab deploy:host=ubuntu@staging.my-domain.com
```

**Note:** If access to your server is via private key, you'll have to add the key on your local maching. e.g.
```
$ eval `ssh-agent -s`
$ ssh-add ~/.ssh/ec2key.pem
$ fab deploy:host=ubuntu@staging.my-domain.com
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
