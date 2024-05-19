FROM python:3.11-slim AS build_env

# get master branch
COPY . /hope-project/
WORKDIR /hope-project/

ENV PYTHONPATH ${PYTHONPATH}:/hope-project/app/
ENV APP /hope-project/app/main
RUN pip3 install --no-cache-dir -r requirements.txt

# testing stage
FROM build_env as testing_env

WORKDIR /hope-project/
RUN for test in app/tests/*.py; do python3 $test; done

# final container
FROM build_env AS deployment_env

WORKDIR /hope-project/
RUN for entity in ./*; do test "$entity" != "./app" && rm -r $entity; done

CMD flask --app $APP run --host 0.0.0.0 --port 5000
