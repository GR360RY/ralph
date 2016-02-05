# -*- mode: ruby -*-

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.hostname = "ralph-dev"
  config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.vm.network "forwarded_port", guest: 19360, host: 1936  # for Sublime Text Anaconda plugin
  config.vm.provider :virtualbox do |vb|
    vb.linked_clone = true if Vagrant::VERSION =~ /^1.8/
    vb.name = "ralph_ng"
    vb.memory = 2048
    vb.cpus = 2
  end

  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "ansible/playbook.yml"
  end
end
