import urllib.parse

import aaron
import aaron.items


class Carnegie(aaron.Spider):
    name = "carnegie"
    allowed_domains = ["carnegieendowment.org"]
    start_urls = ["https://carnegieendowment.org/politika/?lang=ru"]

    custom_settings = {
        "FEED_ID": "https://carnegieendowment.org/politika?lang=ru",
        "FEED_TITLE": "Carnegie",
        "FEED_AUTHOR_NAME": "Carnegie",
        "FEED_FAVICON": "https://carnegieendowment.org/favicon/favicon-32x32.png",  # noqa
        "FEED_LOGO": "https://carnegieendowment.org/favicon/android-icon-192x192.png",  # noqa
        "COOKIES_ENABLED": False,
        "AUTOTHROTTLE_ENABLED": False,
        "DOWNLOAD_DELAY": 30,
        "RETRY_HTTP_CODES": [500, 502, 503, 504, 429, 403],
    }

    def parse(self, response):
        return self.parse_page(
            response,
            {
                "lang": "ru",
                "pageOn": 1,
            },
        )

    def parse_page(self, response, params):
        yield from response.follow_all(
            xpath="//a[@class='black-text']/@href", callback=self.parse_article
        )

        params = urllib.parse.urlencode(
            dict(
                params,
                pageOn=params["pageOn"] + 1,
            )
        )
        return response.follow(
            f"?{params}",
            callback=self.parse_page,
            cb_kwargs={
                "params": params,
            },
        )

    def parse_article(self, response):
        loader = aaron.items.ItemLoader(response=response)

        loader.add_value("url", response.url)
        main_section = loader.nested_xpath(
            "//div[contains(@class, 'zone-main')]", response=response
        )
        main_section.add_xpath("title", ".//h1")
        main_section.add_xpath("summary", ".//div[@class='summary']")
        main_section.add_xpath(
            "published", ".//div[contains(@class, 'pub-date')]"
        )
        main_section.add_xpath("author_name", ".//a[@class='author']")
        main_section.add_xpath("author_url", ".//a[@class='author']/@href")
        main_section.add_xpath("text", ".//div[@class='article-body']")

        return loader.load_item()
