FROM archlinux:latest AS build_env

# System deps
RUN pacman -Sy --noconfirm python python-pip protobuf \
    && pacman -Scc --noconfirm

COPY . /hope-project/
WORKDIR /hope-project/

RUN pip install --no-cache-dir -r requirements.txt --break-system-packages

WORKDIR /hope-project/
ENV PYTHONPATH ${PYTHONPATH}:/hope-project/app/

CMD ["gunicorn", "--workers=8", "--bind=webapp:5000", "app.main:create_app()"]
