# --- coding: utf-8 ---

from fabric.api import local, hosts, env, run
from fabric.operations import prompt

env.use_ssh_config = True
env.project_path = '/home/swasher/sith'


def staging():
    env.hosts = ['staging']

def production():
    env.hosts = ['production']

def development():
    env.hosts = ['development']

def provision():
    """
    Setup all on provision/staging/deployment via Ansible. Development must run inside Vagrant box.

    Usage:
    fab [development|staging|production] provision
    """
    additional_params = '--skip-tags=vagrant_skip' if env.hosts[0] == 'development' else ''

    # Want more verbose output? Uncomment it.
    additional_params += ' -vvv'

    local('ansible-playbook -i inventories/all --limit {target} {additional_params} provision.yml'.
          format(target=env.hosts[0], additional_params=additional_params))


def recreate_db():
    """
    Make staging server is mirror of production (source code and db)

    Usage:
    fab recreate_db
    """
    local('ansible-playbook -i inventories/all --limit development recreate_db.yml')