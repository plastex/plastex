### Dockerfile for fork of plasTeX project

ARG PYTHON_IMAGE_TAG

FROM python:${PYTHON_IMAGE_TAG} as base

ARG NODE_JS_MAJOR_VERSION

RUN DEBIAN_FRONTEND=noninteractive \
    apt-get --quiet=2 update \
    && apt-get --no-install-recommends --option="DPkg::Use-Pty=0" \
               --quiet=2 install curl dvipng gosu make tidy \
    && { curl -sL https://deb.nodesource.com/setup_${NODE_JS_MAJOR_VERSION}.x \
             | bash - ; } \
    && apt-get --no-install-recommends --option="DPkg::Use-Pty=0" \
               --quiet=2 install nodejs \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /var/cache/plastex/

ENV PYTHONDONTWRITEBYTECODE=1

RUN pip install --requirement /var/cache/plastex/requirements.txt \
    && npm install -g css-validator html-validator-cli sass 

FROM base as development

COPY docker/entry-point.sh /usr/local/src/docker/

ENTRYPOINT ["/bin/sh", "/usr/local/src/docker/entry-point.sh"]

FROM base as application

COPY . /usr/local/src/plastex

RUN make \
    -C /usr/local/src/plastex/plasTeX/Renderers/HTMLNotes/Style \
    install \
    && pip install /usr/local/src/plastex \
    && rm -r /usr/local/src/plastex

### End of file

# Local Variables:
# mode: sh
# End:
