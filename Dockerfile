FROM ubuntu:18.04

ENV PYTHONUNBUFFERED 1

ENV TERM xterm
ENV PIP_NO_CACHE_DIR false
ENV DEBIAN_FRONTEND noninteractive
ENV PIPENV_HIDE_EMOJIS 1

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

RUN mkdir -p /app 

ADD Pipfile /tmp/
ADD Pipfile.lock /tmp/
WORKDIR /tmp

RUN apt-get -qq update &&  \
    apt-get -y install python3-pip python3-dev libmysqlclient-dev libssl-dev

RUN pip3 install pipenv && pipenv install --deploy --ignore-pipfile --system

WORKDIR /app

ADD . /app
RUN find /app -name '*.pyc' -delete

RUN ./manage.py collectstatic --noinput

CMD ["daphne", "-b", "0.0.0.0", "-p", "5222", "src.asgi:application"]
