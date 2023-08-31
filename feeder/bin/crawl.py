#!/usr/bin/env python3

import argparse
import pathlib
import shutil
import tempfile

import feeder.bin


@feeder.bin.with_scrapy
def main():
    options = get_options()
    options.output_dir.mkdir(exist_ok=True)

    process = feeder.bin.get_crawler_process()

    names = options.spider
    if not names:
        names = set(process.spider_loader.list())

    with tempfile.TemporaryDirectory() as _tmpdir:
        tmpdir = pathlib.Path(_tmpdir)
        for name in names:
            crawler = feeder.bin.get_crawler(
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
        shutil.copytree(tmpdir, options.output_dir, dirs_exist_ok=True)


def get_options():
    parser = argparse.ArgumentParser(description="Crawl all websites")
    all_spiders = set(feeder.bin.list_spiders())

    def spiders_list_type(value):
        names = set(v.strip() for v in value.split(","))
        if unknown_names := names - all_spiders:
            raise argparse.ArgumentTypeError(
                f"Unknown spiders {', '.join(sorted(unknown_names))}"
            )

        return names

    parser.add_argument(
        "-s",
        "--spider",
        type=spiders_list_type,
        help="List of spiders to use (comma-separated-list)",
        default=None,
    )
    parser.add_argument(
        "output_dir",
        help="Output dir",
        type=lambda x: pathlib.Path(x).resolve(),
    )

    return parser.parse_args()


if __name__ == "__main__":
    main()
