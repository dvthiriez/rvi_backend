from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run, warn_only
from fabric.context_managers import shell_env
import random

GIT_USERNAME = ''
GIT_PASSWORD = ''
BACKEND_REPO_URL = 'https://%s:%s@github.com/dvthiriez/rvi_backend.git' % (GIT_USERNAME, GIT_PASSWORD)
CORE_REPO_URL = 'https://%s:%s@github.com/dvthiriez/rvi_core.git' % (GIT_USERNAME, GIT_PASSWORD)
MYSQL_PW = 'newpwd'


def deploy():
    backend_site_folder = '/home/%s/sites/%s' % (env.user, env.host)
    backend_source_folder = backend_site_folder + '/source'

    core_site_folder = '/home/%s/rvi_core' % (env.user,)

    _create_directory_structure_if_necessary(backend_site_folder)
    _get_latest_source(backend_source_folder, BACKEND_REPO_URL)
    _get_latest_source(core_site_folder, CORE_REPO_URL)
    _update_and_build_rvi_core(core_site_folder, env.host)
    _update_settings(backend_source_folder, env.host)
    _update_virtualenv(backend_source_folder)
    with shell_env(PYTHONPATH=backend_source_folder):
        _update_static_files(backend_source_folder)
        _update_database(backend_source_folder)
    _config_gunicorn_and_nginx(backend_source_folder, env.host)
    _launch_gunicorn_and_ngninx(env.host)
 

def _create_directory_structure_if_necessary(backend_site_folder):
    for subfolder in ('static', 'virtualenv', 'source'):
        run('mkdir -p %s/%s' % (backend_site_folder, subfolder))


def _get_latest_source(source_folder, repo_url):
    if exists(source_folder + '/.git'):
        run('cd %s && git fetch' % (source_folder,))
    else:
        run('git clone %s %s' % (repo_url, source_folder))
    # TODO code below is only applicable to rvi_backend, needs to also accomodate
    # rvi_core
    # current_commit = local("git log -n 1 --format=%H", capture=True)
    # run('cd %s && git reset --hard %s' % (source_folder, current_commit))


def _update_and_build_rvi_core(core_site_folder, site_name):
    run('cd %s && make clean && make' % (core_site_folder,))
    backend_config_file = core_site_folder + '/backend.config'
    sed(backend_config_file,
        '\{ node_address, "54.172.25.254:8807" \},',
        '\{ node_address, "%s:8807" \},' % (site_name,)
    )
    run('cd %s && ./scripts/setup_rvi_node.sh -n backend_node -c backend.config' % (core_site_folder,))


def _update_settings(backend_source_folder, site_name):
    settings_path = backend_source_folder + '/config/settings/base.py'
    sed(settings_path, "DEBUG = True", "DEBUG = False")
    sed(settings_path,
        'ALLOWED_HOSTS =.+$',
        'ALLOWED_HOSTS = ["%s"]' % (site_name,)
    )
    secret_key_file = backend_source_folder + '/config/settings/secrets.json'
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%&^*(-_=+)'
    key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
    sed(secret_key_file,
        '"DJANGO_SECRET_KEY": "y7pg3qz\)6fs4vk4=\)_*fn\(dagsx+t!wvl=p&d3ybm\(yc%\(\(&pg",',
        '"DJANGO_SECRET_KEY": "%s",' % (key,)
    )


def _update_virtualenv(backend_source_folder):
    virtualenv_folder = backend_source_folder + '/../virtualenv'
    if not exists(virtualenv_folder + '/bin/pip'):
        run('virtualenv --python=python2.7 %s' % (virtualenv_folder,))
    run('%s/bin/pip install -r %s/config/requirements/base.txt' % (
        virtualenv_folder, backend_source_folder
    ))


def _update_static_files(backend_source_folder):
    run('cd %s/web && ../../virtualenv/bin/python2.7 manage.py collectstatic --noinput' % (
        backend_source_folder,
    ))


def _update_database(backend_source_folder):
    run('mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -p%s -u root mysql' % (
        MYSQL_PW,
    ))

    mysql_command = 'mysql -p%s -u root -e' % (MYSQL_PW,)
    run(('%s "select user, host, password from mysql.user;'
         'update mysql.user set password = PASSWORD(\'%s\') where user = \'root\';'
         'flush privileges;"' % (mysql_command, MYSQL_PW)
     ))

    with warn_only():
        run('%s "drop user \'\'@\'localhost\';"' % (mysql_command,))
        run('%s "drop user \'\'@\'hostname\';"' % (mysql_command,))
        run('%s "drop database test;"' % (mysql_command,))
        run('%s "create database rvi character set utf8;"' % (mysql_command,))
        run('%s "create user \'rvi_user\'@\'localhost\' identified by \'rvi\';"' % (
            mysql_command,
        ))
        run('%s "grant all on rvi.* to \'rvi_user\'@\'localhost\';"' % (mysql_command,))
        run('%s "grant all on test_rvi.* to \'rvi_user\'@\'localhost\';"' % (mysql_command,))

    run('cd %s/web && ../../virtualenv/bin/python2.7 manage.py migrate --noinput' % (
        backend_source_folder,
    ))

def _config_gunicorn_and_nginx(backend_source_folder, site_name):
    run(('cd %s && \\'
         'sed "s/SITENAME/%s/g" \\'
         'deploy_tools/nginx.template.conf | sudo tee \\'
         '/etc/nginx/sites-available/%s')
         % (backend_source_folder, site_name, site_name)
     )
    run(('cd %s && \\'
         'sudo ln -s ../sites-available/%s \\'
         '/etc/nginx/sites-enabled/%s')
         % (backend_source_folder, site_name, site_name)
     )
    run(('cd %s && \\'
         'sed "s/SITENAME/%s/g" \\'
         'deploy_tools/gunicorn-upstart.template.conf | sudo tee \\'
         '/etc/init/gunicorn-%s.conf')
         % (backend_source_folder, site_name, site_name)
     )


def _launch_gunicorn_and_ngninx(site_name):
    run('sudo /etc/init.d/mysql start')
    run('sudo service nginx reload && sudo start gunicorn-%s' % (site_name,))
