import json
import logging

import scrapy
import w3lib.html

import feeder
import feeder.items


class PitchforkRssSpider(scrapy.Spider):
    allowed_domains = ["pitchfork.com"]

    def parse(self, response):
        for url in response.xpath("/rss/channel/item/link/text()").extract():
            yield response.follow(url, callback=self.parse_item)

    def parse_item(self, response):
        json_data = response.xpath(
            "//script[@type='application/ld+json']/text()"
        ).extract_first()
        if not json_data:
            self.log(
                f"Cannot get JSON data for {response.url}",
                level=logging.WARNING
            )
            return

        try:
            data = json.loads(json_data)
        except Exception as exc:
            self.log(
                f"Cannot extract JSON data for {response.url}: {exc}",
                level=logging.WARNING
            )
            return

        score = response.xpath(
            "//div[contains(@class,'ScoreCircle')]"
        ).extract_first()
        score = w3lib.html.remove_tags(score).strip()

        try:
            float(score)
        except Exception as exc:
            self.log(
                f"Cannot find out a correct score valuefor {score}",
                level=logging.WARNING
            )
            return


        loader = feeder.items.FeedEntryLoader()
        loader.add_value("title", f"({score}) {data['itemReviewed']['name']}")
        loader.add_value("updated", data["dateModified"])
        loader.add_value("published", data["datePublished"])
        loader.add_value("summary", data["description"])
        loader.add_value("url", response.url)
        loader.add_value("author_name", data["author"][0]["name"])
        loader.add_value("author_url", data["author"][0]["sameAs"])
        loader.add_value("content", feeder.render_template(
            "pitchfork",
            title=data["itemReviewed"]["name"],
            score=score,
            author={
                "name": data["author"][0]["name"],
                "url": data["author"][0]["sameAs"]
            },
            img={
                "url": data["image"]["url"],
                "title": data["headline"]
            },
            paragraphs=data["reviewBody"].split("\n")
        ))

        return loader.load_item()


class BestNewMusicSpider(PitchforkRssSpider):
    name = "pitchfork_best_new_music"
    start_urls = ["https://pitchfork.com/rss/reviews/best/albums/"]

    custom_settings = {
        "FEED_ID": "https://pitchfork.com/reviews/best/albums/",
        "FEED_TITLE": "Pitchfork: Best new albums",
        "FEED_AUTHOR_NAME": "Pitchfork",
        "FEED_FAVICON": "https://cdn.pitchfork.com/assets/misc/favicon-32.png",
        "FEED_LOGO": "https://cdn.pitchfork.com/assets/misc/favicon-152-v2.png"
    }


class ReviewsSpider(PitchforkRssSpider):
    name = "pitchfork_reviews"
    start_urls = ["https://pitchfork.com/feed/feed-album-reviews/rss"]

    custom_settings = {
        "FEED_ID": "https://pitchfork.com/reviews/albums/",
        "FEED_TITLE": "Pitchfork: All reviews",
        "FEED_AUTHOR_NAME": "Pitchfork",
        "FEED_FAVICON": "https://cdn.pitchfork.com/assets/misc/favicon-32.png",
        "FEED_LOGO": "https://cdn.pitchfork.com/assets/misc/favicon-152-v2.png"
    }
