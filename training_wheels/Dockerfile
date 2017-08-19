FROM python:2


RUN apt-get update
RUN apt-get install -y python-pip manpages manpages-dev freebsd-manpages man-db

RUN pip install colorama 

ENV USER uscga

ENV HOSTNAME cyberteam
ENV HOST cyberteam

RUN useradd -m uscga
USER uscga

COPY ./ /home/uscga

RUN chmod -R 755 /home/uscga
RUN chmod 755 /home/uscga/training_wheels
RUN chown uscga:uscga /home/uscga/*

WORKDIR /home/uscga

CMD ["/home/uscga/training_wheels"]