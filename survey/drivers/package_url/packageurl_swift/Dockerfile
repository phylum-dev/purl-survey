FROM swift

ENTRYPOINT [ "swift", "run", "--skip-build" ]

WORKDIR /purl
COPY . .

RUN swift build
