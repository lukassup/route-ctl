NAME = route-ctl

.PHONY: default setup test install docker-build docker-test docker-clean

default: test23

setup:
	{ dnf install -y python-setuptools; } \
	    || { yum install -y python-setuptools; } \
	    || { zypper install -y python-setuptools; } \
	    || { apt-get update && apt-get install -y python-setuptools; } \
	    || { pacman -Syyu --noconfirm python-setuptools; }


test:
	/usr/bin/env python setup.py test

test2:
	/usr/bin/env python2 setup.py test

test3:
	/usr/bin/env python3 setup.py test

test23: test2 test3

install:
	/usr/bin/env python setup.py install

docker-build:
	docker build -t $(NAME)/py26 -f Dockerfile.py26 . ; \
	    docker build -t $(NAME)/py27 -f Dockerfile.py27 . ; \
	    docker build -t $(NAME)/py33 -f Dockerfile.py33 . ; \
	    docker build -t $(NAME)/py34 -f Dockerfile.py34 . ; \
	    docker build -t $(NAME)/py35 -f Dockerfile.py35 . ; \
	    docker build -t $(NAME)/py36 -f Dockerfile.py36 .

docker-test: docker-build
	docker run $(NAME)/py26 ; \
	    docker run $(NAME)/py27 ; \
	    docker run $(NAME)/py33 ; \
	    docker run $(NAME)/py34 ; \
	    docker run $(NAME)/py35 ; \
	    docker run $(NAME)/py36

docker-clean:
	docker rmi -f \
	    $(NAME)/py26 \
	    $(NAME)/py27 \
	    $(NAME)/py33 \
	    $(NAME)/py34 \
	    $(NAME)/py35 \
	    $(NAME)/py36
