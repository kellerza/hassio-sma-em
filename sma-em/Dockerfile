ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . ./
COPY rootfs /
