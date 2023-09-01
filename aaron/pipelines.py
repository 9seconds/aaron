import textwrap

import scrapy.exceptions
import w3lib.html

import aaron.items


class Pipeline:
    def __init__(self):
        self.seen_ids = set()

    def process_item(self, item, spider):
        self.assign_defaults(item, spider.settings)
        self.validate_absent_fields(item)
        self.validate_consistency(item)
        self.attach_metadata(item, spider.settings)

        return item

    def assign_defaults(self, item, settings):
        item.setdefault("item_id", item["url"].rstrip("/"))

        if "published" in item:
            item.setdefault("updated", item["published"])

        if "updated" in item:
            item.setdefault("published", item["updated"])

        if "summary" not in item:
            summary = w3lib.html.remove_tags(item.get("text", ""))
            summary = w3lib.html.strip_html5_whitespace(summary)
            item["summary"] = textwrap.shorten(
                summary,
                width=settings.getint("SUMMARY_LENGTH", 140),
                break_long_words=False,
                break_on_hyphens=False,
                tabsize=4,
                fix_sentence_endings=True,
                placeholder=" …",
            )

    def validate_absent_fields(self, item):
        for key in "item_id", "url", "title", "text", "updated", "published":
            if key not in item:
                raise scrapy.exceptions.DropItem(f"Empty {key} field")

    def validate_consistency(self, item):
        if (pub := item["published"]) > (up := item["updated"]):
            raise scrapy.exceptions.DropItem(
                f"Published {pub} is later than updated {up}"
            )

        if (_id := item["item_id"]) in self.seen_ids:
            raise scrapy.exceptions.DropItem(
                f"Item with ID {_id} was seen before"
            )

        self.seen_ids.add(item["item_id"])

    def attach_metadata(self, item, settings):
        item["metadata"] = aaron.items.Metadata(
            item_id=settings["FEED_ID"],
            title=settings["FEED_TITLE"],
            author_name=settings["FEED_AUTHOR_NAME"],
            author_email=settings["FEED_AUTHOR_EMAIL"],
            favicon=settings.get("FEED_FAVICON"),
            logo=settings.get("FEED_LOGO"),
        )
