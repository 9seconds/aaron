#!/usr/bin/env python3

import argparse
import os
import pathlib
import urllib.parse

import lxml.etree
import scrapy.crawler
import scrapy.utils.project


def main():
    options = get_options()

    os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "feeder.settings")

    settings = scrapy.utils.project.get_project_settings()
    settings.set("LOG_LEVEL", "ERROR")

    process = scrapy.crawler.CrawlerProcess(settings)

    root = lxml.etree.Element("opml", {"version": "2.0"})

    head = lxml.etree.SubElement(root, "head")
    lxml.etree.SubElement(head, "title").text = "Feeder feeds"
    lxml.etree.SubElement(head, "docs").text = "http://opml.org/spec2.opml"

    body = lxml.etree.SubElement(root, "body")

    for name in sorted(process.spider_loader.list()):
        crawler = process.create_crawler(name)
        outline = lxml.etree.SubElement(body, "outline", {
            "type": "rss",
            "xmlUrl": urllib.parse.urljoin(options.url, f"{name}.xml"),
            "htmlUrl": crawler.settings.get("FEED_ID"),
            "text": crawler.settings.get("FEED_TITLE")
        })

    print('<?xml version="1.0" encoding="utf-8" ?>')
    print(lxml.etree.tostring(root, pretty_print=True).decode())


def get_options():
    parser = argparse.ArgumentParser(description="Generate OPML")

    parser.add_argument(
        "url",
        help="Base URL")

    return parser.parse_args()


if __name__ == "__main__":
    main()
