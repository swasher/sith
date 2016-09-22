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
    pip install fabric
    pip install ansible
  SHELL

  config.vm.provision "shell", privileged: false, inline: <<-SHELL
    mkdir --parents /home/vagrant/log
    touch /home/vagrant/log/ansible.log
    cd sith/provision && fab development provision
  SHELL

end
