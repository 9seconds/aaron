#!/bin/sh

OUTPUT_DIR="$(readlink -m out)"

mkdir -p "$OUTPUT_DIR" || true

cd ./feeder

poetry run scrapy crawl -O "$OUTPUT_DIR/xkcd.xml:atom" xkcd
