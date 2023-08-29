import heapq

import feeder
import scrapy.exporters
import scrapy.utils.project


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
