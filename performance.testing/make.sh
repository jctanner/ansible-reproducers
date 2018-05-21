if [[ ! -f sshkey ]]; then
    ssh-keygen -b 521 -t ecdsa -f sshkey -q -N ""
fi

cp -f sshkey.pub docker/node/authorized_keys

docker build -t ansiscale:1.0 docker/node/.
docker build -t ansible-el7:1.0 docker/controller.centos7/.
docker build -t ansible-f27:1.0 docker/controller.fedora27/.
