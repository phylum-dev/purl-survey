FROM elixir

RUN mix local.hex --force

ENTRYPOINT [ "mix", "run", "--no-compile", "--no-deps-check", "-e", "Driver.run", "--" ]

WORKDIR /purl
COPY . .
RUN --mount=type=cache,target=/purl/deps \
    mix deps.get --only prod && mix compile
