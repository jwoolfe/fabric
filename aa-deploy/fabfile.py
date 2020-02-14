#!/usr/bin/env python

'''
Deploys rpm package to appropriate dist repository, 
then installs to master and 
nodes on the hpc cluster.

Requires:
python
fabric libraries

'''

import os
from fabric.context_managers import (
    cd,
    hide,
    show,
)

from fabric.api import (
    env,
    run,
    put,
    get,
    settings,
    sudo,
    task,
)

env.use_ssh_config = True
env.colorize_errors = True

env.master_server = 'master.organization.com'
env.dist_server = 'dist.organization.com'
env.dist_path = '/srv/dist/centos/5/x86_64/'


def package(path_to_rpm):
    return os.path.basename(path_to_rpm)


def version(path_to_rpm):
    if 'package_version' not in env:
        with settings(host_string=env.dist_server):
            package_version = run('rpm -qp --qf %{NAME} '
                                  + env.dist_path + 'RPMS/' + package(path_to_rpm))
        return package_version


def copy_to_host(path_to_rpm):
    put('/tmp/' + package(path_to_rpm), env.dist_path + 'RPMS/')


def create_repo():
    with cd(env.dist_path):
        sudo('/usr/bin/createrepo .')


def run_yum():
    sudo('yum clean all')
    with settings(warn_only=True):
        sudo('yum check-update')
        sudo('yum -y install ' + env.package_version)
        sudo('pssh -h /etc/pssh/dc-all yum clean all')
        sudo('pssh -h /etc/pssh/dc-all yum check-update')
        sudo('pssh --timeout=300 -h /etc/pssh/dc-all yum -y install ' + env.package_version)


def verify_version():
    sudo('pssh -i -h /etc/pssh/dc-all rpm -q ' + env.package_version)


@task(default=True)
def deploy_aa(path_to_rpm):
    """ Deploys rpm package to hpc cluster. Usage: fab -H <FROM_HOST> deploy_aa:<PATH_TO_RPM> """
    with settings(hide('stdout'), warn_only=True):
        with settings(host_string=env.host):
            get(path_to_rpm, '/tmp')
        with settings(host_string=env.dist_server):
            copy_to_host(path_to_rpm)
            create_repo()
            env.package_version = version(path_to_rpm)
        with settings(host_string=env.master_server):
            run_yum()
            with show('stdout'):
                verify_version()
