import heapq

import lxml.etree
import scrapy.exporters
import scrapy.utils.project


def set_el(root, name, text=None, attrib=None):
    sub = lxml.etree.SubElement(root, name, attrib)
    if text:
        sub.text = text


def set_el_if(root, name, text=None, attrib=None):
    if text:
        set_el(root, name, text, attrib)


class FeederAtomExporter(scrapy.exporters.BaseItemExporter):
    def __init__(self, file, *args, **kwargs):
        kwargs["export_empty_fields"] = False

        super().__init__(*args, **kwargs)

        self.file = file
        self.document = lxml.etree.Element(
            "feed", nsmap={None: "http://www.w3.org/2005/Atom"}
        )
        self.header_set = False
        self.items = []
        self.settings = scrapy.utils.project.get_project_settings()

    def export_metadata(self, metadata):
        set_el(self.document, "title", metadata["title"])
        set_el(self.document, "id", metadata["id"])
        set_el(self.document, "link", None, {"href": metadata["id"]})
        set_el_if(self.document, "icon", metadata["favicon"])
        set_el_if(self.document, "logo", metadata["logo"])

        if metadata["author_name"] or metadata["author_email"]:
            author = lxml.etree.SubElement(self.document, "author")
            set_el_if(author, "name", metadata["author_name"])
            set_el_if(author, "email", metadata["author_email"])

    def export_item(self, item):
        if not self.header_set:
            self.export_metadata(item["metadata"])
            self.header_set = True

        self.add_item(item)

    def add_item(self, item):
        el = lxml.etree.Element("entry")

        set_el(el, "id", item["item_id"])
        set_el(el, "title", item["title"])
        set_el(el, "link", None, {"href": item["url"]})
        set_el(el, "content", item["content"], {"type": "html"})
        set_el(el, "updated", item["updated"].isoformat())
        set_el(el, "published", item["published"].isoformat())
        set_el_if(el, "summary", item["summary"])

        if (
            item.get("author_name")
            or item.get("author_email")
            or item.get("author_url")
        ):
            author = lxml.etree.SubElement(el, "author")
            set_el_if(author, "name", item.get("author_name"))
            set_el_if(author, "email", item.get("author_email"))
            set_el_if(author, "uri", item.get("author_url"))

        heap_el = (item["updated"], item["item_id"], el)

        if len(self.items) < self.settings.getint("MAX_ITEMS"):
            heapq.heappush(self.items, heap_el)
        elif item["updated"] > self.items[0][0]:
            heapq.heapreplace(self.items, heap_el)

    def finish_exporting(self):
        if not self.items:
            return

        items = sorted(self.items, reverse=True)
        set_el(self.document, "updated", items[0][0].isoformat())

        for _, _, v in items:
            self.document.append(v)

        self.file.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
        self.file.write(
            lxml.etree.tostring(
                self.document, encoding="utf-8", pretty_print=True
            )
        )
