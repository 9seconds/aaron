#!/usr/bin/env python3

import argparse
import datetime
import os
import pathlib
import sys
import urllib.parse
import urllib.request

import humanize

import feeder.bin
import feeder.bin.generators


def main():
    if not os.getenv("BASE_URL"):
        sys.exit("Base URL is not defined")

    parser = argparse.ArgumentParser(
        description="Do various things with feeder"
    )

    subcommands = parser.add_subparsers(required=True)

    url = subcommands.add_parser("url", description="Get OPML url")
    url.set_defaults(func=do_url)

    health = subcommands.add_parser(
        "healthcheck", description="Run healthcheck"
    )
    health.set_defaults(func=do_healthcheck)

    health = subcommands.add_parser(
        "list-spiders", description="Get list of spiders"
    )
    health.set_defaults(func=do_list_spiders)

    last_updated = subcommands.add_parser(
        "last_updated", description="Date of last update"
    )
    last_updated.set_defaults(func=do_last_updated)

    options = parser.parse_args()
    options.func(options)


def do_url(_):
    print(urllib.parse.urljoin(os.getenv("BASE_URL"), get_password() + "/"))


def do_healthcheck(_):
    url = urllib.parse.urljoin("http://127.0.0.1:80", get_password() + "/")

    request = urllib.request.Request(url)
    request.add_header("User-Agent", "feeder-healthcheck")

    try:
        with urllib.request.urlopen(request, timeout=1) as response:
            if not (200 <= response.code < 299):
                sys.exit(
                    f"Backend has responded with {response.code} status code"
                )
    except Exception as exc:
        sys.exit(f"Cannot access backend: {exc}")

    print("OK")


def do_list_spiders(_):
    for name in feeder.bin.list_spiders():
        print(name)


def do_last_updated(_):
    feed_dir = pathlib.Path("out")
    now = datetime.datetime.now()

    for path in sorted(feed_dir.iterdir()):
        timestamp = datetime.datetime.fromtimestamp(path.stat().st_mtime)
        print(f"{path.name}: {humanize.naturaldelta(now - timestamp)} ago")


def get_password():
    return feeder.bin.generators.password_type(os.getenv("PASSWORD") or "")
