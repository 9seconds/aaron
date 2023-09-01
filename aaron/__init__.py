import copy
import os
import pathlib
import shutil
import tempfile

import jinja2
import scrapy.crawler
import scrapy.spiders
import scrapy.utils.log
import scrapy.utils.project
import scrapy.utils.reactor


os.environ["SCRAPY_SETTINGS_MODULE"] = "aaron.settings"


SCRAPY_SETTINGS = scrapy.utils.project.get_project_settings()

bytecode_cache = None
cache_dir = os.getenv("AARON_CACHE_DIR")
if cache_dir:
    cache_dir = pathlib.Path(cache_dir).joinpath("jinja2")
    cache_dir.mkdir(parents=True, exist_ok=True)

    bytecode_cache = jinja2.FileSystemBytecodeCache(str(cache_dir))

JINJA_ENV = jinja2.Environment(
    loader=jinja2.PackageLoader("aaron", "templates"),
    autoescape=jinja2.select_autoescape(
        enabled_extensions=("html", "html.j2", "xml", "xml.j2"),
    ),
    auto_reload=False,
    keep_trailing_newline=True,
    bytecode_cache=bytecode_cache,
)


def render_html(template_name, ctx):
    return render_template(f"{template_name}.html.j2", ctx)


def render_feed(items):
    return render_template("atom.xml.j2", {"items": items})


def render_opml(items):
    return render_template("opml.xml.j2", {"items": items})


def render_nginx(password, output_dir):
    return render_template(
        "nginx.conf.j2",
        {
            "password": password,
            "output_dir": str(output_dir),
        },
    )


def render_template(template_name, ctx):
    return JINJA_ENV.get_template(template_name).render(ctx)


def list_spiders():
    settings = scrapy.utils.project.get_project_settings()
    all_spiders = frozenset(get_crawler_process().spider_loader.list())
    wanted_spiders = frozenset(settings.get("SPIDERS")) or all_spiders

    return sorted(all_spiders & wanted_spiders)


def run_crawl(names, output_dir):
    def ignore_empty_files(src, names):
        root = pathlib.Path(src)
        return [
            name for name in names if not root.joinpath(name).stat().st_size
        ]

    output_dir = pathlib.Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    process = get_crawler_process()
    all_names = frozenset(list_spiders())
    names = frozenset(names or ()) or all_names

    if absent := names - all_names:
        raise ValueError(f"Unknown spiders {', '.join(sorted(absent))}")

    with tempfile.TemporaryDirectory() as _tmpdir:
        tmpdir = pathlib.Path(_tmpdir)
        for name in names:
            crawler = get_crawler(
                name,
                process,
                {
                    "FEEDS": {
                        tmpdir.joinpath(f"{name}.xml"): {
                            "format": "atom",
                        }
                    }
                },
            )
            process.crawl(crawler)

        process.start()
        shutil.copytree(
            tmpdir, output_dir, ignore=ignore_empty_files, dirs_exist_ok=True
        )


def get_crawler_process():
    return scrapy.crawler.CrawlerProcess(
        SCRAPY_SETTINGS, install_root_handler=False
    )


def get_crawler(name, process, settings=None):
    spider_cls = process.spider_loader.load(name)

    all_settings = copy.deepcopy(process.settings)
    all_settings.setdict(settings or {}, priority="cmdline")

    return scrapy.crawler.Crawler(spider_cls, all_settings)


scrapy.utils.log.configure_logging(SCRAPY_SETTINGS)
scrapy.utils.reactor.install_reactor(
    SCRAPY_SETTINGS["TWISTED_REACTOR"],
    SCRAPY_SETTINGS["ASYNCIO_EVENT_LOOP"],
)


class Spider(scrapy.spiders.Spider):
    template_name = None

    def render_template(self, ctx):
        template_name = self.template_name
        if not template_name:
            template_name = self.name

        return render_html(template_name, ctx)
