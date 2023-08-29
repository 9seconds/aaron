import heapq
import urllib.parse

import feeder
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
        self.items = []
        self.settings = scrapy.utils.project.get_project_settings()

    def export_item(self, item):
        heap_el = item["updated"], item["item_id"], item

        if len(self.items) < self.settings.getint("MAX_ITEMS"):
            heapq.heappush(self.items, heap_el)
        elif item["updated"] > self.items[0][0]:
            heapq.heapreplace(self.items, heap_el)

    def finish_exporting(self):
        if not self.items:
            return

        feed = feeder.render_feed(
            [item for _, _, item in sorted(self.items, reverse=True)]
        )
        self.file.write(feed.encode("utf-8"))
        self.file.write(b"\n")
