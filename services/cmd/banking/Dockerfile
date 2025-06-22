ARG TAG=base-devel

FROM archlinux:${TAG}

RUN pacman -Syu --noconfirm     \
    --disable-download-timeout  \
    go git sqlite               \
    pacman-contrib base-devel   \
    && paccache -r -k 0

ENV CGO_ENABLED=0
ENV GO111MODULE=on
ENV GOPATH=/go
ENV PATH=$PATH:/go/bin

WORKDIR /workspace/app
COPY . .

RUN go build -o banking ./cmd/banking
