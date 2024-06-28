FROM python:3.11-slim AS build_env

# get master branch
COPY . /hope-project/
WORKDIR /hope-project/

RUN pip3 install --no-cache-dir -r requirements.txt

# setting unprivileged user to run server & gunicorn from
RUN groupadd runner && useradd -g runner runner

# testing stage
FROM build_env as testing_env

WORKDIR /hope-project/
RUN for test in app/tests/*.py; do python3 $test; done

# final container
FROM build_env AS deployment_env

WORKDIR /hope-project/
RUN for entity in ./*; do test "$entity" != "./app" && rm -r $entity; done

ENV PYTHONPATH ${PYTHONPATH}:/hope-project/app/
CMD su runner && \
    gunicorn --workers=8 --bind=webapp:5000 'app.main:create_app()'
