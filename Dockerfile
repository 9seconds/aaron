FROM python:3-slim AS build

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
  && apt-get install -y \
        --no-install-recommends \
      gcc \
      libc6-dev \
      make \
  && python3 -m pip install \
        --disable-pip-version-check \
        --no-cache-dir \
        --no-python-version-warning \
        --no-input \
      poetry \
  && poetry self add poetry-plugin-bundle

ADD https://github.com/kosma/runit-docker/archive/refs/tags/1.2.tar.gz /runit/
WORKDIR /runit/

RUN tar xf 1.2.tar.gz \
  && cd runit-docker-1.2 \
  && make runit-docker.so \
  && mv ./runit-docker.so /runit-docker.so

COPY . /project/
WORKDIR /project/

RUN poetry bundle venv \
        --without=dev \
        --no-interaction \
        --no-cache \
      /app

# -----------------------------------------------------------------------------

FROM python:3-slim AS app

HEALTHCHECK \
  --start-period=1m \
  CMD info health

ENV PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/app/bin
ENV PASSWORD ""

EXPOSE 80

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y \
      --no-install-recommends \
    cron \
    nginx \
    runit \
    zopfli \
  && mkdir /feeds /var/log/feeder \
  && apt-get autoremove --yes --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY ./docker/crontab /crontab
RUN crontab /crontab && rm /crontab

ENV LD_PRELOAD=/usr/lib/runit-docker/runit-docker.so

COPY ./docker/collect /usr/local/bin/collect
COPY ./docker/entrypoint /usr/local/bin/entrypoint
COPY ./docker/runit /runit

COPY --from=build /app /app
COPY --from=build /runit-docker.so /usr/lib/runit-docker/runit-docker.so

CMD ["entrypoint"]
