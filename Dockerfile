FROM python:3-slim AS runit

RUN apt update -qq \
  && apt install -y \
    gcc \
    make

ADD https://github.com/kosma/runit-docker/archive/refs/tags/1.2.tar.gz /runit/

WORKDIR /runit

RUN tar xf 1.2.tar.gz \
  && cd runit-docker-1.2 \
  && make runit-docker.so \
  && mv ./runit-docker.so /runit-docker.so

# -----------------------------------------------------------------------------

FROM python:3-slim AS build

RUN python3 -m pip install \
      --disable-pip-version-check \
      --no-cache-dir \
      --no-python-version-warning \
      --no-input \
      poetry \
    && poetry self add poetry-plugin-bundle

COPY . /project/

RUN poetry bundle venv \
      --without=dev \
      --no-interaction \
      --no-cache \
      -C /project \
    /app

# -----------------------------------------------------------------------------

FROM python:3-slim AS app

EXPOSE 80

ENV PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/app/bin
ENV LD_PRELOAD=/usr/lib/runit-docker/runit-docker.so

COPY --from=runit /runit-docker.so /usr/lib/runit-docker/runit-docker.so

RUN apt update -qq \
  && apt install -y \
    cron \
    nginx \
    runit \
    zopfli \
  && mkdir /feeds /var/log/feeder \
  && apt autoremove --yes --purge \
  && apt clean \
  && rm -rf /var/lib/apt/lists/* /etc/nginx/sites-enabled/*

COPY ./docker/crontab /crontab
RUN crontab /crontab && rm /crontab

COPY ./docker/collect /usr/local/bin/collect
COPY ./docker/entrypoint /usr/local/bin/entrypoint
COPY ./docker/runit /runit
COPY --from=build /app /app

CMD ["entrypoint"]
