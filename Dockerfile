FROM python:3.13.0b1-alpine3.19 AS deplyment_env

EXPOSE 5000

RUN apk update
RUN apk add git py3-virtualenv

# get master branch
# RUN git clone https://gitverse.ru/ser1a/hope-project
COPY . /hope-project/
WORKDIR /hope-project/

# create venv (might be used if apk will be used further)
RUN virtualenv ./venv --copies
ENV PYTHON /hope-project/venv/bin/python
ENV PIP /hope-project/venv/bin/pip
ENV PYTHONPATH ${PYTHONPATH}:/hope-project/app/

RUN $PIP install --break-system-packages -r requirements.txt

# testing stage
RUN $PYTHON app/tests/env_test.py

# handle SSL certs

ENV FLASK /hope-project/venv/bin/flask
CMD $FLASK --app $APP run --host 0.0.0.0 --port 5000
