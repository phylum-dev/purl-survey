FROM perl

RUN cpan App::cpanminus && cpanm -n JSON Try::Tiny

WORKDIR /purl
COPY . .
RUN chmod a+x format parse && ln -s /purl/format /purl/parse /usr/local/bin
