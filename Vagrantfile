# -*- mode: ruby -*-
# vi: set ft=ruby :

internal_ip = "172.28.128.10"
project_name = "sith"

Vagrant.configure(2) do |config|

  config.vm.box = "ubuntu/wily64"
  config.vm.network "private_network", ip: internal_ip
  config.vm.hostname = "sith"

  config.vm.provider :virtualbox do |v|
    v.memory = 1024
    v.gui = false
  end

  # for supress "stdin: is not a tty error"
  config.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"

  config.vm.synced_folder ".", "/home/vagrant/" + project_name, id: "vagrant-root",
    owner: "vagrant",
    group: "vagrant",
    mount_options: ["dmode=775,fmode=664"]

  config.vm.provision "shell", inline: <<-SHELL
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -q
    apt-get autoremove -y
    apt-get install python-dev libyaml-dev -y -q
    curl -s https://bootstrap.pypa.io/get-pip.py | sudo python -
  SHELL
    #pip install fabric
    #pip install ansible


  config.vm.provision "shell", privileged: false, inline: <<-SHELL
    mkdir --parents /home/vagrant/log
    touch /home/vagrant/log/ansible.log
  SHELL

  # Run Ansible from the Vagrant VM
  config.vm.provision :ansible_local do |ansible|
    ansible.playbook       = "provision.yml"
    ansible.verbose        = true
    ansible.install        = true
    ansible.install_mode   = 'pip'
    ansible.limit          = 'development'
    ansible.provisioning_path = "/home/vagrant/sith/provision"
    ansible.inventory_path = "/home/vagrant/sith/provision/inventories"
  end

end
