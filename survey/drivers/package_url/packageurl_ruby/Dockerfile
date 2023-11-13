FROM ruby

WORKDIR /purl
COPY . .

RUN chmod a+x format.rb parse.rb && \
    ln -s /purl/format.rb /usr/local/bin/format && \
    ln -s /purl/parse.rb /usr/local/bin/parse
