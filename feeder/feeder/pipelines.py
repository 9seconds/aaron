import scrapy.exceptions


class FeederDefaultsPipeline:
    def process_item(self, item, spider):
        item.setdefault("published", item["updated"])
        item.setdefault("item_id", item["url"].rstrip("/"))

        if item["published"] > item["updated"]:
            raise scrapy.exceptions.DropItem(
                f"Published {item['published']} is later than "
                f"updated {item['updated']}"
            )

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
