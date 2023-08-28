#!/bin/sh

OUT="$(mktemp -d)"

generate_opml "${BASE_URL?Base URL is not defined}" > "$OUT/index.opml"
crawl "$OUT" >> "/var/log/crawl/crawl-$(date -u +%F).log"
zopfli --i1000 "$OUT/*"
rsync -a --delete "$OUT/" /feeds/

rm -rf "$OUT"
