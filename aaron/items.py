import dateparser
import itemloaders.processors
import scrapy
import scrapy.loader
import tzlocal
import w3lib.html
import w3lib.url


def parse_timestamp(value, loader_context):
    value = value or ""
    value = w3lib.html.remove_tags(value)
    value = w3lib.html.replace_entities(value)
    value = w3lib.html.strip_html5_whitespace(value)

    dateparser_config = loader_context.get("dateparser_config") or {}

    tstamp = dateparser.parse(value, **dateparser_config)
    if not tstamp.tzinfo:
        return tstamp.astimezone(tzlocal.get_localzone())

    return tstamp


def process_url(value, loader_context):
    value = value or ""
    value = w3lib.html.strip_html5_whitespace(value)
    value = loader_context["response"].urljoin(value)

    return w3lib.url.canonicalize_url(value)


class Metadata(scrapy.Item):
    item_id = scrapy.Field()
    title = scrapy.Field()
    author_name = scrapy.Field()
    author_email = scrapy.Field()
    favicon = scrapy.Field()
    logo = scrapy.Field()


class Item(scrapy.Item):
    metadata = scrapy.Field()

    item_id = scrapy.Field()
    url = scrapy.Field(
        input_processor=itemloaders.processors.MapCompose(process_url)
    )

    title = scrapy.Field()
    summary = scrapy.Field()
    text = scrapy.Field(
        input_processor=itemloaders.processors.MapCompose(
            w3lib.html.remove_comments, w3lib.html.strip_html5_whitespace
        )
    )
    updated = scrapy.Field(
        input_processor=itemloaders.processors.MapCompose(parse_timestamp),
        serializer=lambda x: x.isoformat(),
    )
    published = scrapy.Field(
        input_processor=itemloaders.processors.MapCompose(parse_timestamp),
        serializer=lambda x: x.isoformat(),
    )

    author_name = scrapy.Field()
    author_email = scrapy.Field()
    author_url = scrapy.Field()


class ItemLoader(scrapy.loader.ItemLoader):
    default_item_class = Item
    default_output_processor = itemloaders.processors.TakeFirst()
    default_input_processor = itemloaders.processors.MapCompose(
        w3lib.html.remove_tags,
        w3lib.html.replace_entities,
        w3lib.html.strip_html5_whitespace,
    )
