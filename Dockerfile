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


FROM python:3-slim AS app

ENV PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/app/bin
EXPOSE 80

RUN DEBIAN_FRONTEND=noninteractive apt update -qq \
  && apt install -y \
    cron \
    nginx \
    runit \
    zopfli \
  && mkdir /feeds /var/log/feeder \
  && apt autoremove --yes --purge \
  && apt clean \
  && rm -rf /var/lib/apt/lists/*

COPY ./docker/crontab /crontab
RUN crontab /crontab && rm /crontab

COPY ./docker/nginx.conf /etc/nginx/nginx.conf
COPY ./docker/collect /usr/local/bin/collect
COPY ./docker/entrypoint /usr/local/bin/entrypoint
COPY ./docker/runit /runit
COPY --from=build /app /app

CMD ["entrypoint"]
