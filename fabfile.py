from fabric.api import *

import paramiko
import logging

FORMAT="%(name)s %(funcName)s:%(lineno)d %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)

env.use_ssh_config = True
#env.hosts = ['central-ws']

TEMP_DIR = '/tmp/central_install_dir'
TAR_FILE = '/tmp/central_tarball.tar.gz'
WSGI_FILE = '/var/www/html/yr-central/yr-central.wsgi'
GITHUB_REPO = 'git@github.com:youthradio/intranet.git'

def local_deploy():
    # create a new source distribution as tarball
    local('python setup.py sdist --formats=gztar', capture=False)

    # figure out the release name and version
    dist = local('python setup.py --fullname', capture=True).strip()
    # upload the source tarball to the temporary folder on the server
    put('dist/%s.tar.gz' % dist, TAR_FILE)
    # create a place where we can unzip the tarball, then enter
    # that directory and unzip it
    run('rm -Rf %s' % TEMP_DIR)
    run('mkdir %s' % TEMP_DIR)
    with cd(TEMP_DIR):
        run('tar xzf %s' % TAR_FILE)

    with cd(TEMP_DIR + '/' + dist):
        # now setup the package with our virtual environment's
        # python interpreter
        run('sudo python setup.py install')

    # now that all is set up, delete the folder again
    run('sudo rm -Rf %s %s' % (TEMP_DIR, TAR_FILE))
    # and finally touch the .wsgi file so that mod_wsgi triggers
    # a reload of the application
    run('sudo touch %s' % WSGI_FILE)

def git_deploy():
    # create a place where we can unzip the tarball, then enter
    # that directory and unzip it
    run('rm -Rf %s' % TEMP_DIR)
    run('mkdir %s' % TEMP_DIR)
    with cd(TEMP_DIR):
        run('git clone %s' % GITHUB_REPO)

    with cd(TEMP_DIR + '/intranet/intranet'):
        run('sudo python setup.py install')

    # now that all is set up, delete the folder again
    run('sudo rm -Rf %s %s' % (TEMP_DIR))
    # and finally touch the .wsgi file so that mod_wsgi triggers
    # a reload of the application
    run('sudo touch %s' % WSGI_FILE)

def cleanup():
    dist = local('python setup.py --name', capture=True).strip()

    local('rm -Rf dist')
    local('rm -Rf %s.egg-info' % dist)