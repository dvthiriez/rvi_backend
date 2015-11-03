from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run
import random


BACKEND_REPO_URL = 'https://github.com/dvthiriez/rvi_backend.git'
CORE_REPO_URL = 'https://github.com/dvthiriez/rvi_core.git'

def deploy():
    backend_site_folder = '/home/%s/sites/%s' % (env.user, env.host)
    backend_source_folder = backend_site_folder + '/source'

    core_site_folder = '/home/%s/rvi_core' % (env.user,)

    _create_directory_structure_if_necessary(backend_site_folder)
    _get_latest_source(backend_source_folder, BACKEND_REPO_URL)
    _get_latest_source(core_site_folder, CORE_REPO_URL)
    _update_settings(backend_source_folder, env.host)
    _update_virtualenv(backend_source_folder)
    _update_static_files(backend_source_folder)
    _update_database(backend_source_folder)
 

def _create_directory_structure_if_necessary(backend_site_folder):
    for subfolder in ('database', 'static', 'virtualenv', 'source'):
        run('mkdir -p %s/%s' % (backend_site_folder, subfolder))


def _get_latest_source(source_folder, repo_url):
    if exists(source_folder + '/.git'):
        run('cd %s && git fetch' % (source_folder,))
    else:
        run('git clone %s %s' % (repo_url, source_folder))
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run('cd %s && git reset --hard %s' % (source_folder, current_commit))


def _update_settings(backend_source_folder, site_name):
    settings_path = backend_source_folder + '/config/settings/base.py'
    sed(settings_path, "DEBUG = True", "DEBUG = False")
    sed(settings_path,
        'ALLOWED_HOSTS =.+$',
        'ALLOWED_HOSTS = ["%s"]' % (site_name,)
    )
    secret_key_file = backend_source_folder + '/config/settings/secret_key.py'
    if not exists(secret_key_file):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%&^*(-_=+)'
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file, "SECRET_KEY = '%s'" % (key,))
    append(settings_path, '\nfrom .secret_key import SECRET_KEY')


def _update_virtualenv(backend_source_folder):
    virtualenv_folder = backend_source_folder + '/../../virtualenv'
    if not exists(virtualenv_folder + '/bin/pip'):
        run('virtualenv --python=python2.7 %s' % (virtualenv_folder,))
    run('%s/bin/pip install -r %s/config/requirements/production.txt' % (
        virtualenv_folder, backend_source_folder
    ))


def _update_static_files(backend_source_folder):
    run('cd %s/web && ../../virtualenv/bin/python2.7 manage.py collectstatic --noinput' % (
        backend_source_folder,
    ))


def _update_database(backend_source_folder):
    run('cd %s/web && ../../virtualenv/bin/python2.7 manage.py migrate --noinput' % (
        backend_source_folder,
    ))
