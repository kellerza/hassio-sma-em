ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN pip3 install --no-cache-dir asyncio-mqtt icecream attrs

RUN set -ex \
    && ping dl-cdn.alpinelinux.org -c 4 \
    && apk add --no-cache \
        git

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN git clone https://github.com/datenschuft/SMA-EM.git .

COPY config.ini run.py ./

# CMD ["tail", "-f", "/dev/null"]
CMD ["./run.py"]