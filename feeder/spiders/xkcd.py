import scrapy.spiders
import scrapy.linkextractors

import feeder
import feeder.items


class XkcdSpider(scrapy.spiders.CrawlSpider):
    name = "xkcd"
    allowed_domains = ["xkcd.com"]
    start_urls = ["https://xkcd.com"]

    custom_settings = {
        "FEED_ID": "https://xkcd.com",
        "FEED_TITLE": "XKCD",
        "FEED_AUTHOR_NAME": "Randall Munroe",
        "FEED_AUTHOR_EMAIL": "contact@xkcd.com",
        "FEED_FAVICON": "https://xkcd.com/s/919f27.ico",
        "FEED_LOGO": "https://xkcd.com/s/0b7742.png",
        "AUTOTHROTTLE_ENABLED": False,
    }

    rules = [
        scrapy.spiders.Rule(
            scrapy.linkextractors.LinkExtractor(
                restrict_xpaths=(
                    "//ul[@class = 'comicNav'][1]//a[@rel = 'prev']"
                )
            ),
            callback="parse_item",
            follow=True,
        )
    ]

    def parse_item(self, response):
        loader = feeder.items.FeedEntryLoader(response=response)

        comic = response.xpath("//div[@id='comic']/img[1]")

        img_url = response.urljoin(comic.xpath("@src").extract_first())
        if not img_url:
            return

        loader.add_value("url", response.url)
        loader.add_xpath("title", "//div[@id='ctitle']")
        loader.add_xpath("summary", "//div[@id='comic']/img[1]/@title")

        loader.add_value(
            "content",
            feeder.render_template(
                self,
                url=img_url,
                title=comic.xpath("@title").extract_first() or "",
            ),
        )

        return response.follow(
            img_url,
            self.parse_img_date,
            cb_kwargs={"loader": loader},
        )

    def parse_img_date(self, response, loader):
        loader.add_value("updated", response.headers["Last-Modified"].decode())

        return loader.load_item()
