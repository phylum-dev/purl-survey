FROM golang

WORKDIR /purl
COPY . .
RUN go build -o /usr/local/bin/format format/main.go && \
    go build -o /usr/local/bin/parse parse/main.go 
