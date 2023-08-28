#!/usr/bin/env python3

import argparse
import os
import pathlib
import copy

import scrapy.crawler
import scrapy.utils.project


def main():
    options = get_options()
    options.output_dir.mkdir(exist_ok=True)

    os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "feeder.settings")

    settings = scrapy.utils.project.get_project_settings()
    process = scrapy.crawler.CrawlerProcess(settings)
    init_reactor = True

    for name in process.spider_loader.list():
        spider_cls = process.spider_loader.load(name)

        settings = copy.deepcopy(process.settings)
        settings.setdict(
            {
                "FEEDS": {
                    options.output_dir.joinpath(f"{name}.xml"): {
                        "format": "atom"
                    }
                }
            },
            priority="cmdline",
        )

        crawler = scrapy.crawler.Crawler(
            spider_cls, settings, init_reactor=init_reactor
        )
        init_reactor = False

        process.crawl(crawler)

    return process.start()


def get_options():
    parser = argparse.ArgumentParser(description="Crawl all websites")

    parser.add_argument(
        "output_dir",
        help="Output dir",
        type=lambda x: pathlib.Path(x).resolve(),
    )

    return parser.parse_args()


if __name__ == "__main__":
    main()
