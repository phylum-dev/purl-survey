FROM gradle:8-jdk17

ENTRYPOINT [ "java", "-classpath", "build/libs/*" ]

WORKDIR /purl
COPY . .

RUN --mount=type=cache,target=/home/gradle/.gradle/caches \
    (cd /purl/repo && gradle --build-cache build) && \
    gradle --build-cache build && \
    gradle --stop
