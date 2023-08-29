#!/usr/bin/env python3

import argparse
import os
import re
import urllib.parse

import scrapy.crawler
import scrapy.utils.project

import feeder


def password_type(value):
    return urllib.parse.quote(value or "")


def generate_opml():
    parser = argparse.ArgumentParser(description="Generate OPML")
    parser.add_argument("url", help="Base URL")
    parser.add_argument("password", help="Password to use as a subdirectory", type=password_type, default="")
    options = parser.parse_args()

    os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "feeder.settings")

    settings = scrapy.utils.project.get_project_settings()
    settings.set("LOG_LEVEL", "ERROR")

    process = scrapy.crawler.CrawlerProcess(settings)

    items = []
    for name in process.spider_loader.list():
        crawler = process.create_crawler(name)
        items.append({
            "feed_url": urllib.parse.urljoin(options.url, f"{options.password}/{name}.xml"),
            "html_url": crawler.settings.get("FEED_ID"),
            "title": crawler.settings.get("FEED_TITLE")
        })

    print(feeder.render_opml(items))


def generate_nginx():
    parser = argparse.ArgumentParser(
        description="Render nginx configuration"
    )
    parser.add_argument(
        "password",
        help="Password to use as a subdirectory",
        type=password_type,
        default=""
    )
    options = parser.parse_args()

    print(feeder.render_nginx(re.escape(options.password)))
