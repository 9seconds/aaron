#!/usr/bin/env python3

import argparse
import pathlib
import shutil
import tempfile

import feeder.bin


def main():
    options = get_options()

    return run(options.spider, options.output_dir)


def run(names, output_dir):
    output_dir.mkdir(exist_ok=True)

    process = feeder.bin.get_crawler_process()
    all_names = set(process.spider_loader.list())
    names = set(names or ()) or all_names

    if absent := names - all_names:
        raise ValueError(f"Unknown spiders {', '.join(sorted(absent))}")

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
        shutil.copytree(tmpdir, output_dir, dirs_exist_ok=True)


def get_options():
    parser = argparse.ArgumentParser(description="Crawl all websites")

    parser.add_argument(
        "-s",
        "--spider",
        type=lambda value: {v.strip() for v in value.split(",")},
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
