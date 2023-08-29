#!/usr/bin/env python3

import argparse
import os
import urllib.parse

import scrapy.crawler
import scrapy.utils.project

import feeder


def main():
    options = get_options()

    os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "feeder.settings")

    settings = scrapy.utils.project.get_project_settings()
    settings.set("LOG_LEVEL", "ERROR")

    process = scrapy.crawler.CrawlerProcess(settings)

    items = []
    for name in process.spider_loader.list():
        crawler = process.create_crawler(name)
        items.append({
            "feed_url": urllib.parse.urljoin(options.url, f"{name}.xml"),
            "html_url": crawler.settings.get("FEED_ID"),
            "title": crawler.settings.get("FEED_TITLE")
        })

    print(feeder.render_opml(items))


def get_options():
    parser = argparse.ArgumentParser(description="Generate OPML")

    parser.add_argument("url", help="Base URL")

    return parser.parse_args()


if __name__ == "__main__":
    main()
