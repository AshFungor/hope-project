FROM alpine:3.19.1 AS deplyment_env

EXPOSE 5000

RUN apk update
RUN apk add python3 py3-pip git

# get master branch
RUN git clone https://gitverse.ru/ser1a/hope-project
WORKDIR /hope-project

# create venv (might be used if apk will be used further)
RUN python3 -m venv ./venv
ENV PYTHON /hope-project/venv/bin/python
ENV PIP /hope-project/venv/bin/pip

RUN $PIP install -r requirements.txt

# add testing stage (?)

# handle SSL certs

ENV FLASK /hope-project/venv/bin/flask
ENV APP /hope-project/app
CMD $FLASK --app $APP run --host 0.0.0.0 --port 5000