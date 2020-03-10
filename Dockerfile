### Dockerfile for fork of plasTeX project

FROM node:13-buster-slim AS css-generation-stage

RUN which npm

WORKDIR /usr/local/plastex

COPY plasTeX/Renderers/HTMLNotes/Style/install-prerequisites.sh .

RUN /bin/sh install-prerequisites.sh

COPY plasTeX/Renderers/HTMLNotes/Style .

RUN /bin/sh generate-css.sh

### End of file
