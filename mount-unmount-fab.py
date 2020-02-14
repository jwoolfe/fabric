#!/usr/bin/env python

from fabric.api import *
from fabric.contrib import files

env.use_ssh_config = True
env.colorize_errors = True

def read_hosts():
    with open('nfsserver-hosts', 'r') as hostsfile:
        for host in hostsfile:
            yield host.strip()


def umount_dir():
    sudo('/bin/umount -fl /nfsmount')

def mount_dir():
    sudo ('/bin/mount -a')


@hosts(read_hosts())
@task
def unmount():
    umount_dir()

@hosts(read_hosts())
@task
def remount():
    mount_dir()
