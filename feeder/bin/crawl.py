#!/usr/bin/env python3

import argparse
import pathlib

import feeder.bin


def main():
    options = get_options()

    return feeder.bin.run_crawl(options.spider, options.output_dir)


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
