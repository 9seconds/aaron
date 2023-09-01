import scrapy.signals
import scrapy.extensions.closespider


class CloseSpider(scrapy.extensions.closespider.CloseSpider):
    def __init__(self, crawler):
        super().__init__(crawler)

        if not self.close_on.get("itemcount"):
            crawler.signals.connect(
                self.item_scraped, signal=scrapy.signals.item_scraped
            )

        self.close_on["itemcount"] = crawler.settings.getint(
            "CLOSESPIDER_ITEMS_FACTOR"
        ) * crawler.settings.getint("MAX_ITEMS")