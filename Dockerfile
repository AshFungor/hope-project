FROM python:3.11-slim AS build_env

COPY . /hope-project/
WORKDIR /hope-project/

RUN pip3 install --no-cache-dir -r requirements.txt

RUN groupadd runner && useradd -g runner runner

FROM build_env AS deployment_env

WORKDIR /hope-project/
RUN for entity in ./*; do test "$entity" != "./app" && rm -r $entity; done

ENV PYTHONPATH ${PYTHONPATH}:/hope-project/app/
CMD su runner && \
    gunicorn --workers=8 --bind=webapp:5000 'app.main:create_app()'
