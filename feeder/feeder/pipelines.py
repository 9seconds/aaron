import scrapy.exceptions
import dateparser


class FeederDefaultsPipeline:
    def process_item(self, item, spider):
        try:
            updated_date = dateparser.parse(item["updated"])
        except ValueError as exc:
            raise scrapy.exceptions.DropItem(
                "Incorrect updated field value"
            ) from exc

        try:
            published_date = dateparser.parse(item["published"])
        except (KeyError, ValueError):
            published_date = updated_date

        item["updated"] = updated_date
        item["published"] = published_date

        item.setdefault("item_id", item["url"].rstrip("/"))

        return item


class FeederFilterPipeline:
    def __init__(self):
        self.seen_ids = set()

    def process_item(self, item, spider):
        for key in ("item_id", "url", "title", "content", "updated"):
            if not item.get(key):
                raise scrapy.exceptions.DropItem(f"Empty {key} field")

        if item["item_id"] in self.seen_ids:
            raise scrapy.exceptions.DropItem(
                f"Duplicated item {item['item_id']}"
            )

        self.seen_ids.add(item["item_id"])

        return item


class FeederMetadataPipeline:
    def process_item(self, item, spider):
        item["metadata"] = {
            "id": spider.settings["FEED_ID"],
            "title": spider.settings["FEED_TITLE"],
            "author_name": spider.settings["FEED_AUTHOR_NAME"],
            "author_email": spider.settings["FEED_AUTHOR_EMAIL"],
            "favicon": spider.settings.get("FEED_FAVICON"),
            "logo": spider.settings.get("FEED_LOGO"),
        }
        return item
