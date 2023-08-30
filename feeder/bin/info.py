#!/usr/bin/env python3

import argparse
import datetime
import sys
import os
import urllib.request
import urllib.parse

import humanize
import scrapy.crawler
import scrapy.utils.project

import feeder.bin.generators


def main():
    os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "feeder.settings")

    parser = argparse.ArgumentParser(
        description="Get info about running instance"
    )

    subcommands = parser.add_subparsers(required=True)

    url = subcommands.add_parser("url", description="Get OPML url")
    url.set_defaults(func=do_url)

    health = subcommands.add_parser("health", description="Run healthcheck")
    health.set_defaults(func=do_healthcheck)

    health = subcommands.add_parser(
        "spiders", description="Get list of spiders"
    )
    health.set_defaults(func=do_spiders)

    last_updated = subcommands.add_parser(
        "last_updated", description="Date of last update"
    )
    last_updated.set_defaults(func=do_last_updated)

    options = parser.parse_args()
    options.func(options)


def do_url(_):
    base_url = os.getenv("BASE_URL")
    if not base_url:
        sys.exit("Base URL is not defined")

    password = feeder.bin.generators.password_type(os.getenv("PASSWORD") or "")

    print(urllib.parse.urljoin(base_url, password + "/"))


def do_healthcheck(_):
    password = feeder.bin.generators.password_type(os.getenv("PASSWORD") or "")
    url = urllib.parse.urljoin("http://127.0.0.1:80", password + "/")

    request = urllib.request.Request(url)
    request.add_header("User-Agent", "feeder-healthcheck")

    with urllib.request.urlopen(request, timeout=1) as response:
        if not (200 <= response.code < 299):
            sys.exit(f"Backend has responded with {response.code} status code")

    print("OK")


def do_spiders(_):
    settings = scrapy.utils.project.get_project_settings()
    settings.set("LOG_LEVEL", "ERROR")

    process = scrapy.crawler.CrawlerProcess(settings)
    process = scrapy.crawler.CrawlerProcess(settings)

    for name in sorted(process.spider_loader.list()):
        print(name)


def do_last_updated(_):
    try:
        stat = os.stat("/feeds/index.opml")
    except Exception as exc:
        sys.exit(f"Unknown timestamp ({exc})")

    timestamp = datetime.datetime.fromtimestamp(stat.st_mtime)
    now = datetime.datetime.now()

    print(f"{humanize.naturaldelta(now - timestamp)} ago")
