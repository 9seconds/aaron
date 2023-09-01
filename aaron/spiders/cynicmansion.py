import w3lib.html

import aaron
import aaron.items


class Cynicmansion(aaron.Spider):
    name = "cynicmansion"
    allowed_domains = ["cynicmansion.ru"]
    start_urls = ["https://cynicmansion.ru"]

    custom_settings = {
        "FEED_ID": "https://cynicmansion.ru/",
        "FEED_TITLE": "Cynicmansion",
        "FEED_AUTHOR_NAME": "killallhumans",
        "FEED_FAVICON": "https://cynicmansion.ru/media/images/favicon.ico",
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
        for el in response.xpath("//div[@class='comics_wrap'][position()>1]"):
            yield self.parse_item(el, response)

        if page > 1:
            yield response.follow(
                f"/?page={page - 1}",
                callback=self.parse_page,
                cb_kwargs={"page": page - 1},
            )

    def parse_item(self, root, response):
        loader = aaron.items.ItemLoader(response=response, selector=root)
        loader.context["dateparser_config"] = {
            "languages": ["ru"],
            "settings": {
                "TIMEZONE": "Europe/Moscow",
            },
        }

        loader.add_xpath("url", ".//table[1]//a[1]/@href")
        loader.add_xpath("title", ".//p[@class='comics_name']")
        loader.add_value(
            "updated",
            w3lib.html.remove_tags_with_content(
                root.xpath(".//td[@class='comics_date']").get(),
                which_ones=("b",),
            ),
        )

        images = [
            response.urljoin(img)
            for img in root.xpath(
                ".//div[@class='comics_image']/img/@src"
            ).extract()
        ]
        if not images:
            return

        loader.add_value(
            "text",
            self.render_template(
                {
                    "images": images,
                    "title": loader.get_output_value("title"),
                }
            ),
        )

        return loader.load_item()
