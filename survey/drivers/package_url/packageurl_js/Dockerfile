FROM node

WORKDIR /purl
RUN ln -s /purl/format.mjs /usr/local/bin/format && ln -s /purl/parse.mjs /usr/local/bin/parse

COPY . .
RUN npm install --omit dev && chmod a+x format.mjs parse.mjs
