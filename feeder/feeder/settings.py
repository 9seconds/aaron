import os


BOT_NAME = "feeder"
SPIDER_MODULES = [
    "feeder.spiders",
]
NEWSPIDER_MODULE = "feeder.spiders"

MAX_ITEMS = 10

DEFAULT_ITEM_CLASS = "feeder.items.FeedEntry"
DEPTH_PRIORITY = -0.5
DOWNLOAD_TIMEOUT = 30
LOG_LEVEL = "INFO"

MEMUSAGE_WARNING_MB = 256
MEMUSAGE_LIMIT_MB = 4 * MEMUSAGE_WARNING_MB

TELNETCONSOLE_ENABLED = False

HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = (
    60 *  # minute
    60 *  # hour
    24    # day
)
HTTPCACHE_GZIP = True
HTTPCACHE_DIR = os.getenv("FEEDER_HTTPCACHE_DIR", "httpcache")
HTTPCACHE_POLICY = "scrapy.extensions.httpcache.RFC2616Policy"

RETRY_TIMES = 5
RETRY_PRIORITY_ADJUST = -5

ROBOTSTXT_OBEY = True
COOKIES_ENABLED = True

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.5

EXTENSIONS = {
    "scrapy.extensions.closespider.CloseSpider": 100,
}
CLOSESPIDER_ITEMCOUNT = 2 * MAX_ITEMS
CLOSESPIDER_TIMEOUT_NO_ITEM = 60

ITEM_PIPELINES = {
    "feeder.pipelines.FeederDefaultsPipeline": 100,
    "feeder.pipelines.FeederFilterPipeline": 101,
    "feeder.pipelines.FeederMetadataPipeline": 102,
}

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

FEED_EXPORTERS = {
    "atom": "feeder.exporters.FeederAtomExporter",
}
