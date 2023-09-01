#!/usr/bin/env python3

import argparse
import datetime
import os
import pathlib
import re
import sys
import urllib.parse
import urllib.request

import humanize
import tzlocal

import aaron


def main():
    def add_base_url(subparser):
        subparser.add_argument(
            "-b",
            "--base-url",
            type=type_url,
            default=os.getenv("AARON_BASE_URL", ""),
            help="Base URL for the HTTP endpoint",
        )

    def add_password(subparser):
        subparser.add_argument(
            "-p",
            "--password",
            type=type_password,
            default=os.getenv("AARON_PASSWORD", ""),
            help="Access password",
        )

    def add_output_dir(subparser):
        subparser.add_argument(
            "-o",
            "--output-dir",
            type=type_dir,
            default=os.getenv("AARON_FEEDS_DIR", "/feeds"),
            help="Directory to store output files",
        )

    parser = argparse.ArgumentParser(
        description="Do various things with aaron",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subcommands = parser.add_subparsers(required=True)

    sub_generate = subcommands.add_parser(
        "generate", help="Generate output related to the container"
    )
    add_base_url(sub_generate)
    add_password(sub_generate)
    add_output_dir(sub_generate)
    sub_generate.add_argument(
        "template",
        choices={"opml", "nginx", "url"},
        help="Template to generate",
    )
    sub_generate.set_defaults(func=do_generate)

    sub_healthcheck = subcommands.add_parser(
        "healthcheck",
        help="Verify aaron health",
    )
    add_base_url(sub_healthcheck)
    add_password(sub_healthcheck)
    sub_healthcheck.set_defaults(func=do_healthcheck)

    last_updated = subcommands.add_parser(
        "last-updated", help="Show dates of last update"
    )
    add_output_dir(last_updated)
    last_updated.add_argument(
        "-i",
        "--iso",
        action="store_true",
        default=False,
        help="Show timestamps in ISO formats",
    )
    last_updated.set_defaults(func=do_last_updated)

    list_spiders = subcommands.add_parser(
        "list-spiders", help="List available spiders"
    )
    list_spiders.set_defaults(func=do_list_spiders)

    run = subcommands.add_parser("run", help="Run a spider")
    run.add_argument(
        "spider",
        nargs=argparse.ZERO_OR_MORE,
        default="",
        help="Spider names",
    )
    add_output_dir(run)
    run.set_defaults(func=do_run)

    options = parser.parse_args()
    options.func(options)


def type_url(value):
    value = (value or "").strip()

    if not value:
        raise argparse.ArgumentTypeError("Value is not defined")

    parsed = urllib.parse.urlparse(value)
    if not parsed.scheme:
        raise argparse.ArgumentTypeError(
            f"Scheme for URL {value} is not defined"
        )

    if not parsed.netloc:
        raise argparse.ArgumentTypeError(f"Netloc for URL {value}")

    return value


def type_password(value):
    return urllib.parse.quote(value or "")


def type_dir(value):
    return pathlib.Path(value).resolve()


def do_generate(options):
    match options.template:
        case "opml":
            return do_generate_opml(options)
        case "nginx":
            return do_generate_nginx(options)
        case "url":
            return do_generate_url(options)

    raise ValueError(f"Unknown template {options.template}")


def do_generate_opml(options):
    items = []

    process = aaron.get_crawler_process()
    for name in process.spider_loader.list_spiders():
        crawler = process.create_crawler(name)
        items.append(
            {
                "feed_url": urllib.parse.urljoin(
                    options.base_url, f"{options.password}/{name}.xml"
                ),
                "html_url": crawler.settings.get("FEED_ID"),
                "title": crawler.settings.get("FEED_TITLE"),
            }
        )

    print(aaron.render_opml(items))


def do_generate_nginx(options):
    print(aaron.render_nginx(re.escape(options.password), options.output_dir))


def do_generate_url(options):
    print(urllib.parse.urljoin(options.base_url, options.password + "/"))


def do_healthcheck(options):
    url = urllib.parse.urljoin("http://127.0.0.1:80", options.password + "/")

    request = urllib.request.Request(url)
    request.add_header("User-Agent", "aaron-healthcheck")

    try:
        with urllib.request.urlopen(request, timeout=1) as response:
            if not (200 <= response.code < 299):
                sys.exit(
                    f"Backend has responded with {response.code} status code"
                )
    except Exception as exc:
        sys.exit(f"Cannot access backend: {exc}")

    print("OK")


def do_last_updated(options):
    local_tz = tzlocal.get_localzone()
    now = datetime.datetime.now(local_tz)

    for path in sorted(options.output_dir.iterdir()):
        timestamp = datetime.datetime.fromtimestamp(
            path.stat().st_mtime,
            tz=local_tz,
        )

        if options.iso:
            to_show = timestamp.isoformat()
        else:
            to_show = f"{humanize.naturaldelta(now - timestamp)} ago"

        print(f"{path.name}: {to_show}")


def do_list_spiders(_):
    for name in aaron.list_spiders():
        print(name)


def do_run(options):
    return aaron.run_crawl(options.spider, options.output_dir)
