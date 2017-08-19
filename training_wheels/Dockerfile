FROM python:2


RUN apt-get update
RUN apt-get install -y python-pip manpages manpages-dev freebsd-manpages funny-manpages gmt-manpages man2html manpages-posix manpages-posix-dev asr-manpages

RUN pip install colorama 

ENV USER uscga

ENV HOSTNAME cyberteam
ENV HOST cyberteam

RUN useradd -m uscga

COPY ./ /home/uscga
RUN chmod -R 750 /home/uscga
RUN chmod 755 /home/uscga/training_wheels

WORKDIR /home/uscga

CMD ["/home/uscga/training_wheels"]