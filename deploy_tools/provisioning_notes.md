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
    # fabfile.py if you plan on using it for remote deployments

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


## Usage and setup:

To use the fabfile.py to perform a remote deployment, execute the following commands on your local machine
```
$ cd rvi_backend/deploy_tools
$ pip2 install fabric
$ fab deploy:host=ubuntu@staging.my-domain.com
```

Then connect to the remote server and update the Ngninx config
```
  ubuntu@server:$ cd ~/sites/staging.my-domain.com/source
```
```
  ubuntu@server:$ sed "s/SITENAME/staging.my-domain.com/g" \
  		   deploy_tools/nginx.template.conf | sudo tee \
		   /etc/nginx/sites-available/staging.my-domain.com
```
```
  ubuntu@server:$ sudo ln -s ../sites-available/staging.my-domain.com \
  		  /etc/nginx/sites-enabled/staging.my-domain.com
```

... and the Upstart job

 ```
  ubuntu@server: sed "s/SITENAME/staging.my-domain.com/g" \
  		 deploy_tools/gunicorn-upstart.template.conf | sudo tee \
		 /etc/init/gunicorn-staging.my-domain.com.conf
```

After setting up the Nginx and Upstart scripts, restart their respective services
```
ubuntu@server:$ sudo service nginx reload
ubuntu@server:$ sudo start gunicorn-staging.my-domain.com
```

For additional details or a full walkthrough, refer to chapters 8 and 9 in Test-Driven Development with Python,
by Harry J.W. Percival available @ http://www.obeythetestinggoat.com
