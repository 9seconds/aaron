import dateparser
import itemloaders.processors
import scrapy
import scrapy.loader
import tzlocal
import w3lib.html
import w3lib.url


def parse_timestamp(value):
    tstamp = dateparser.parse(value)
    if not tstamp.tzinfo:
        tstamp = tstamp.astimezone(tzlocal.get_localzone())

    return tstamp


class FeedEntry(scrapy.Item):
    metadata = scrapy.Field()

    item_id = scrapy.Field()
    url = scrapy.Field(
        input_processor=itemloaders.processors.MapCompose(
            w3lib.html.strip_html5_whitespace, w3lib.url.canonicalize_url
        )
    )

    title = scrapy.Field()
    summary = scrapy.Field()
    content = scrapy.Field(
        input_processor=itemloaders.processors.MapCompose(
            w3lib.html.strip_html5_whitespace
        )
    )
    updated = scrapy.Field(
        input_processor=itemloaders.processors.MapCompose(
            w3lib.html.remove_tags,
            w3lib.html.replace_entities,
            w3lib.html.strip_html5_whitespace,
            parse_timestamp,
        ),
        serializer=lambda x: x.isoformat(),
    )
    published = scrapy.Field(
        input_processor=itemloaders.processors.MapCompose(
            w3lib.html.remove_tags,
            w3lib.html.replace_entities,
            w3lib.html.strip_html5_whitespace,
            parse_timestamp,
        ),
        serializer=lambda x: x.isoformat(),
    )

    author_name = scrapy.Field()
    author_email = scrapy.Field()
    author_url = scrapy.Field()


class FeedEntryLoader(scrapy.loader.ItemLoader):
    default_item_class = FeedEntry
    default_output_processor = itemloaders.processors.TakeFirst()
    default_input_processor = itemloaders.processors.MapCompose(
        w3lib.html.remove_tags,
        w3lib.html.replace_entities,
        w3lib.html.strip_html5_whitespace,
    )
