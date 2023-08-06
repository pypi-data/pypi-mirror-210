from __future__ import annotations

import argparse
import pathlib
from typing import Sequence
import logging.handlers
import importlib_metadata

import yaml

from news_crawlers import scrape
from news_crawlers import scheduler
from news_crawlers import configuration

__version__ = importlib_metadata.version("news_crawlers")

logger = logging.getLogger("main")


def read_configuration(config_path: pathlib.Path | None = None) -> dict:
    # read configuration
    found_config_path = configuration.find_config(config_path)

    with open(found_config_path, encoding="utf8") as file:
        config_dict = yaml.safe_load(file)

    logger.debug(f"Found configuration in {found_config_path.resolve()}")

    return config_dict


def run_crawlers(config_path: pathlib.Path | None, spiders_to_run: list[str], cache_folder: pathlib.Path) -> None:
    logger.debug(f"Running crawlers with input parameters: {locals()}")
    scrape_configuration = configuration.NewsCrawlersConfig(**read_configuration(config_path))

    if spiders_to_run is None:
        spiders_to_run = list(scrape_configuration.spiders.keys())

    try:
        crawled_data = scrape.scrape(spiders_to_run, scrape_configuration.spiders, cache_folder)
        logger.debug("Scraping done.")

        # get difference with cached data
        logger.debug("Checking for difference with items that were obtained previously...")
        diff = scrape.check_diff(cache_folder, crawled_data)

        if diff:
            logger.debug(f"Found new items: {diff}")

            # send notifications to users (only if difference with cached data is found)
            logger.debug("Sending notifications")
            scrape.notify(diff, scrape_configuration.spiders)
            logger.debug("Notifications sent succesfully.")
        else:
            logger.debug("No new items were found.")

    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Exception occurred when running crawlers.", exc_info=exc)
    else:
        logger.debug("Crawlers were run successfully.")


def setup_logger(log_path: pathlib.Path, log_rotation_days: int) -> None:
    log_handler = logging.handlers.TimedRotatingFileHandler(log_path, when="d", interval=log_rotation_days)
    log_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s %(message)s"))
    logger.addHandler(log_handler)


def main(argv: Sequence[str] | None = None) -> int:

    parser = argparse.ArgumentParser(
        prog="News Crawlers",
        description="Runs web crawlers which will check for updates and alert users if there are any news.",
    )

    parser.add_argument("-v", "--version", action="version", version=importlib_metadata.version("news_crawlers"))
    parser.add_argument("-l", "--log", required=False, type=pathlib.Path)
    parser.add_argument("--log_rotation_days", default=7, required=False, type=int)
    subparsers = parser.add_subparsers(dest="command", required=False)
    scrape_parser = subparsers.add_parser("scrape")
    scrape_parser.add_argument("-s", "--spider", required=False, action="append")
    scrape_parser.add_argument("-c", "--config", type=pathlib.Path, required=False)
    scrape_parser.add_argument("--cache", required=False, type=pathlib.Path, default=scrape.DEFAULT_CACHE_PATH)

    scrape_subparsers = scrape_parser.add_subparsers(dest="scrape_command")
    schedule_parser = scrape_subparsers.add_parser("schedule")
    schedule_parser.add_argument("--every", required=False, default=1, type=int)
    schedule_parser.add_argument("--units", required=False, default="minutes")

    args = parser.parse_args(argv)

    if args.log:
        setup_logger(args.log, args.log_rotation_days)

    logger.info("Application started.")

    logger.info(f"Running application with args: {vars(args)}")

    scrape_configuration = configuration.NewsCrawlersConfig(**read_configuration(args.config))

    if args.scrape_command == "schedule":
        sch_config = configuration.ScheduleConfig(every=args.every, units=args.units)
        logger.debug(f"Scheduled crawling on every {args.every} {args.units}")
    elif scrape_configuration.schedule is not None:
        sch_config = scrape_configuration.schedule
        logger.debug(f"Scheduled crawling on every {sch_config.every} {sch_config.units}")
    else:
        logger.debug("Running crawlers without schedule.")
        run_crawlers(args.config, args.spider, args.cache)
        return 0

    scheduler.schedule_func(lambda: run_crawlers(args.config, args.spider, args.cache), sch_config)

    return 0


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)-8s %(message)s",
    )
    raise SystemExit(main())
