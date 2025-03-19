FROM mcr.microsoft.com/dotnet/sdk:7.0

WORKDIR /purl
COPY . .

RUN --mount=type=cache,target=/root/.nuget,sharing=locked \
    --mount=type=cache,target=/purl/core/obj \
    --mount=type=cache,target=/purl/format/obj \
    --mount=type=cache,target=/purl/parse/obj \
    --mount=type=cache,target=/purl/repo/obj \
        dotnet publish -c Release -p DisableGitVersionTask=true -p EnableSourceControlManagerQueries=false -p EnableSourceLink=false && \
        ln -s /purl/format/bin/Release/net7.0/publish/format /purl/parse/bin/Release/net7.0/publish/parse /usr/local/bin
