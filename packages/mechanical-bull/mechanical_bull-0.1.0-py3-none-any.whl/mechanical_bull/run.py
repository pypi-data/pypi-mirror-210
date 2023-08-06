import tomllib
import asyncio
import logging

from .event_loop import loop
from .handlers import load_handlers


async def mechanical_bull(config_file):
    with open(config_file, "rb") as fp:
        config = tomllib.load(fp)

    if "logfile" in config:
        logging.basicConfig(level=logging.INFO, filename=config["logfile"])

    async with asyncio.TaskGroup() as taskgroup:
        for client_name, value in config.items():
            if isinstance(value, dict):
                handlers = load_handlers(value["handlers"])
                taskgroup.create_task(loop(client_name, value, handlers))


def main():
    asyncio.run(mechanical_bull("config.toml"))


if __name__ == "__main__":
    main()
