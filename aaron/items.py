import dateparser
import itemloaders.processors
import lxml.html
import lxml.html.clean
import scrapy
import scrapy.loader
import tzlocal
import w3lib.html
import w3lib.url


def process_timestamp(value, loader_context):
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


def process_html(value, loader_context):
    value = value or ""
    value = w3lib.html.remove_comments(value)
    value = lxml.html.clean.clean_html(value)
    response = loader_context["response"]

    parsed_html = lxml.html.fromstring(value, base_url=response.url)

    for el in parsed_html.xpath("//a"):
        el.attrib["href"] = response.urljoin(el.attrib["href"])

    for el in parsed_html.xpath("//img"):
        el.attrib["src"] = response.urljoin(el.attrib["src"])

    return lxml.html.tostring(parsed_html, encoding="unicode")


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
        # TODO: rewrite URLS
        input_processor=itemloaders.processors.MapCompose(
            process_html,
        )
    )
    updated = scrapy.Field(
        input_processor=itemloaders.processors.MapCompose(process_timestamp),
        serializer=lambda x: x.isoformat(),
    )
    published = scrapy.Field(
        input_processor=itemloaders.processors.MapCompose(process_timestamp),
        serializer=lambda x: x.isoformat(),
    )

    author_name = scrapy.Field()
    author_email = scrapy.Field()
    author_url = scrapy.Field(
        input_processor=itemloaders.processors.MapCompose(process_url)
    )


class ItemLoader(scrapy.loader.ItemLoader):
    default_item_class = Item
    default_output_processor = itemloaders.processors.TakeFirst()
    default_input_processor = itemloaders.processors.MapCompose(
        w3lib.html.remove_tags,
        w3lib.html.replace_entities,
        w3lib.html.strip_html5_whitespace,
    )
