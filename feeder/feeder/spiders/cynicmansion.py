import lxml.etree
import scrapy
import w3lib.html

import feeder.items


class CynicmansionSpider(scrapy.Spider):
    name = "cynicmansion"
    allowed_domains = ["cynicmansion.ru"]
    start_urls = ["https://cynicmansion.ru"]

    custom_settings = {
        "FEED_ID": "https://cynicmansion.ru/",
        "FEED_TITLE": "Cynicmansion",
        "FEED_AUTHOR_NAME": "killallhumans",
        "FEED_FAVICON": "https://cynicmansion.ru/media/images/favicon.ico",
        "AUTOTHROTTLE_ENABLED": False,
    }

    def parse(self, response):
        page = response.xpath(
            "//div[@class='paginator_wrap']//a[1]/text()"
        ).get()
        page = int(page)

        return response.follow(
            f"/?page={page}", callback=self.parse_page, cb_kwargs={"page": page}
        )

    def parse_page(self, response, page):
        yield from (
            self.parse_item(el, response)
            for el in response.xpath(
                "//div[@class='comics_wrap'][position()>1]"
            )
        )

        if page > 1:
            yield response.follow(
                f"/?page={page - 1}",
                callback=self.parse_page,
                cb_kwargs={"page": page - 1},
            )

    def parse_item(self, root, response):
        loader = feeder.items.FeedEntryLoader(selector=root)

        loader.add_xpath("title", ".//p[@class='comics_name']")
        loader.add_value(
            "updated",
            w3lib.html.remove_tags_with_content(
                root.xpath(".//td[@class='comics_date']").get(),
                which_ones=("b",),
            ),
        )

        url = root.xpath(".//table[1]//a[1]/@href").extract_first()
        if url:
            loader.add_value("url", response.urljoin(url))

        body = lxml.etree.Element("div")
        for img in root.xpath(".//div[@class='comics_image']/img"):
            div_element = lxml.etree.SubElement(body, "div")
            lxml.etree.SubElement(
                div_element,
                "img",
                {"src": response.urljoin(img.xpath("@src").extract_first())},
            )

        loader.add_value("content", lxml.etree.tostring(body).decode())

        return loader.load_item()
