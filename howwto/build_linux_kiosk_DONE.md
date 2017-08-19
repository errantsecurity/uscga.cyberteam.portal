How to Build "Linux Kiosk"
=============

> John Hammond | July 21st, 2017

This is miscellaneous challenge that lives just inside a [Docker] container. All it is is an [SSH] connection, which will only show the [man page] for the [`less`][less] command. The catch is just using [`less`][less] to run commands.

We create our own [Docker] container here with a [Dockerfile].

The Dockerfile
------------

The [Dockerfile] does everything to set up this challenge. It sets up the [SSH] connection, creates the flag file, and it adds the gimmick for the [`less`][less] [man page] loop.

```
FROM rastasheep/ubuntu-sshd

# Create the new user...
RUN adduser --disabled-password --gecos '' user
RUN echo "user:userpass" | chpasswd

# setup SSH and man
RUN apt-get -y update && apt-get install -y man

# create the flag
RUN echo 'USCGA{less_is_more!!!}' > /home/user/flag

# create the challenge
RUN echo "man less; exit" > /home/user/.bashrc
```

The container is built off of a [`rastasheep/ubuntu-sshd`][rastasheep/ubuntu-sshd] container, which is just a pre-built container that offers [SSH] that we can take advantage of.

[Docker] lets us run commands, so I do this to set up a new user, install [`man`][man], create the flag file, and ensure that only the [man page] for [`less`][less] is visible once a user connects to a [`bash`][bash] shell.

Docker Build
----------

In the same directory as our [Dockerfile], run the command to build a new [Docker] container. I use the `.` period to denote the current directory... that's why you have to be in the same directory as the [Dockerfile].

The `-t` argument you can think of as "tag", which will just be the name of the [Docker] container

```
 #!/bin/bash
docker build . -t johnhammond/linux_kiosk
```

Docker Run
----------

The run command here for [Docker] does not take much. You just need to map the port for [SSH], and tell it to run as a [daemon].

```
 #!/bin/bash

docker run -d -p 1888:22 johnhammond/linux_kiosk
```



[Docker]:
[SSH]: 
[man page]: 
[less]: 
[rastasheep/ubuntu-sshd]
[man]: 
[Dockerfile]: 
[daemon]: 