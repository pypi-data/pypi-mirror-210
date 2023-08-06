#!/usr/bin/env python3
import argparse


def get_opts(prog_name="stmd"):
    parser = argparse.ArgumentParser(
        prog=prog_name,
        description="""stmd - scrape to markdown""",
        allow_abbrev=False,
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="""
        Scrape all href links from URL.
        """,
    )
    parser.add_argument(
        "-m",
        "--match",
        action="store",
        metavar="REGEX",
        help="""
        Only download links matching REGEX. Ignored when --all is not given.
        """,
    )
    parser.add_argument(
        "-o",
        "--output",
        action="store",
        metavar="DIR",
        help="""
        Output to DIR.
        """,
    )
    parser.add_argument(
        "url",
        metavar="URL",
        help="""
        URL to scrape.
        """,
    )
    args = parser.parse_args()
    return args
