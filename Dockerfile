FROM alpine:3.19.1 AS deplyment_env

EXPOSE 5000

RUN apk update
RUN apk add python3 py3-pip git

# get master branch
# RUN git clone https://gitverse.ru/ser1a/hope-project
COPY . /hope-project/
WORKDIR /hope-project/

# create venv (might be used if apk will be used further)
# RUN /usr/bin/python3 -m venv ./venv --symlinks
# ENV PYTHON /hope-project/venv/bin/python
# ENV PIP /hope-project/venv/bin/pip
ENV PYTHON /usr/bin/python3
ENV PIP /usr/bin/pip3
ENV PYTHONPATH ${PYTHONPATH}:/hope-project/app/

RUN $PIP install --break-system-packages -r requirements.txt

# testing stage
RUN $PYTHON app/tests/env_test.py

# handle SSL certs

# ENV FLASK /hope-project/venv/bin/flask
ENV APP /hope-project/app/main
# CMD $FLASK --app $APP run --host 0.0.0.0 --port 5000
CMD flask --app $APP run --host 0.0.0.0 --port 5000