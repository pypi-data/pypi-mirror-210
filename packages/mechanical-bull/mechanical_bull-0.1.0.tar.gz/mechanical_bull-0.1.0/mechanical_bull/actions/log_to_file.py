import json

from bovine import BovineClient


async def handle(actor: BovineClient, data: dict, filename=None) -> None:
    with open(filename, "a") as fp:
        fp.write(json.dumps(data, indent=2))
        fp.write("\n")
