ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN pip3 install --no-cache-dir \
    mqtt-entity==0.0.4 \
    attrs==24.3.0 \
    pyyaml==6.0.2 \
    icecream

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY . ./
COPY rootfs /
