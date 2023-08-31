import copy
import os
import functools

import scrapy.crawler
import scrapy.utils.project
import scrapy.utils.reactor
import scrapy.utils.log


def with_scrapy(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        init_scrapy()
        return func(*args, **kwargs)

    return decorator


@functools.lru_cache()
def init_scrapy():
    settings = get_scrapy_project_settings()

    scrapy.utils.log.configure_logging(settings)
    scrapy.utils.reactor.install_reactor(
        settings["TWISTED_REACTOR"],
        settings["ASYNCIO_EVENT_LOOP"],
    )


def get_scrapy_project_settings():
    os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "feeder.settings")
    settings = scrapy.utils.project.get_project_settings()

    return settings


@with_scrapy
def get_crawler_process():
    settings = scrapy.utils.project.get_project_settings()
    process = scrapy.crawler.CrawlerProcess(
        settings,
        install_root_handler=False
    )

    return process


@with_scrapy
def list_spiders():
    process = get_crawler_process()

    return sorted(process.spider_loader.list())


@with_scrapy
def get_crawler(name, process, settings=None):
    spider_cls = process.spider_loader.load(name)

    all_settings = copy.deepcopy(process.settings)
    all_settings.setdict(settings or {}, priority="cmdline")

    crawler = scrapy.crawler.Crawler(spider_cls, all_settings)

    return crawler
