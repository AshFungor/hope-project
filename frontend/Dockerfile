FROM archlinux:latest AS builder

RUN pacman -Syu --noconfirm \
    && pacman -S --noconfirm nodejs npm coreutils \
    && pacman -Scc --noconfirm

WORKDIR /frontend

COPY package*.json ./
RUN npm install
