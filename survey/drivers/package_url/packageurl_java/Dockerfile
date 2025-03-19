FROM maven:3-eclipse-temurin-8 AS repo

WORKDIR /purl/repo
COPY repo .

RUN --mount=type=cache,target=/root/.m2,sharing=locked \
    mvn package -Dmaven.test.skip

FROM gradle

ENTRYPOINT [ "java", "-classpath", "build/libs/*" ]

WORKDIR /purl
COPY . .
COPY --from=repo /purl/repo repo

RUN --mount=type=cache,target=/home/gradle/.gradle/caches,sharing=locked \
    gradle --build-cache --no-daemon build
