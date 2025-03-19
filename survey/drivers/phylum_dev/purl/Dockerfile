FROM rust

WORKDIR /purl
COPY . .
RUN --mount=type=cache,target=/usr/local/cargo/registry,sharing=locked --mount=type=cache,id=phylum-dev/purl/purl/target,target=/purl/target  \
    cargo build --release --bins && \
    install -m 755 target/release/format /usr/local/bin/format && \
    install -m 755 target/release/parse /usr/local/bin/parse
