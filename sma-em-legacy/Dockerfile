ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN pip3 install --no-cache-dir paho-mqtt~=1.5.0 requests~=2.24.0 icecream

RUN set -ex \
    && ping dl-cdn.alpinelinux.org -c 4 \
    && apk add --no-cache \
        git

# VOLUME /data
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN git clone https://github.com/datenschuft/SMA-EM.git .

COPY config.ini run.py ./

# CMD ["tail", "-f", "/dev/null"]
CMD ["./run.py"]