import importlib
import os
import pathlib


MAX_ITEMS = 20
SUMMARY_LENGTH = 140
CLOSESPIDER_ITEMS_FACTOR = 2
CLOSESPIDER_TIMEOUT_NO_ITEM = 60
# --- scrapy own settings ---
BOT_NAME = "aaron"
SPIDER_MODULES = [
    "aaron.spiders",
]
NEWSPIDER_MODULE = "aaron.spiders"

DEFAULT_ITEM_CLASS = "aaron.items.Item"
DEPTH_PRIORITY = -0.5
DOWNLOAD_TIMEOUT = 30
LOG_LEVEL = "WARNING"

MEMUSAGE_WARNING_MB = 256
MEMUSAGE_LIMIT_MB = 4 * MEMUSAGE_WARNING_MB

TELNETCONSOLE_ENABLED = False

HTTPCACHE_ENABLED = False
HTTPCACHE_EXPIRATION_SECS = 60 * 60 * 24  # day
HTTPCACHE_GZIP = True
HTTPCACHE_POLICY = "scrapy.extensions.httpcache.RFC2616Policy"

cache_dir = os.getenv("AARON_CACHE_DIR")
if cache_dir:
    cache_dir = pathlib.Path(cache_dir).joinpath("http")
    cache_dir.mkdir(parents=True, exist_ok=True)

    HTTPCACHE_DIR = str(cache_dir)
    HTTPCACHE_ENABLED = True

RETRY_TIMES = 5
RETRY_PRIORITY_ADJUST = -5

ROBOTSTXT_OBEY = True
COOKIES_ENABLED = True

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.5

EXTENSIONS = {
    "aaron.extensions.CloseSpider": 100,
}

ITEM_PIPELINES = {
    "aaron.pipelines.Pipeline": 100,
}
# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

FEED_EXPORTERS = {
    "atom": "aaron.exporters.AtomExporter",
}

DOWNLOADER_MIDDLEWARES = {
    "scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware": None,
    "scrapy.contrib.downloadermiddleware.retry.RetryMiddleware": None,
    "scrapy_fake_useragent.middleware.RandomUserAgentMiddleware": 400,
    "scrapy_fake_useragent.middleware.RetryUserAgentMiddleware": 401,
}

FAKEUSERAGENT_PROVIDERS = [
    "scrapy_fake_useragent.providers.FakeUserAgentProvider",
    "scrapy_fake_useragent.providers.FakerProvider",
    "scrapy_fake_useragent.providers.FixedUserAgentProvider",
]
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/116.0"  # noqa


try:
    user_settings = importlib.import_module("aaron.user_settings")
except ImportError:
    pass
else:
    for name in dir(user_settings):
        if not name.startswith("__"):
            globals()[name] = getattr(user_settings, name)
