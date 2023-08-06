import os
import tomllib
import tomli_w
from argparse import ArgumentParser
from urllib.parse import urljoin, urlencode

from bovine.crypto import generate_ed25519_private_key, private_key_to_did_key


def build_parser():
    parser = ArgumentParser("Add a user to your mechanical_bull configuration")

    parser.add_argument("name", help="Name of the entry")
    parser.add_argument("host", help="Hostname of your ActivityPub Actor Host")

    parser.add_argument(
        "--accept",
        action="store_true",
        default=False,
        help="Include to set automatically accepting follow requests to true",
    )

    return parser


def main():
    config_file = "config.toml"

    args = build_parser().parse_args()

    print(f"Adding new user to {config_file}")

    if os.path.exists(config_file):
        with open(config_file, "rb") as fp:
            config = tomllib.load(fp)
    else:
        config = {}

    user = args.name

    if user in config:
        print(f"ERROR: {user} already exists in {config_file}")
        exit(1)

    host = args.host
    private_key = generate_ed25519_private_key()
    did_key = private_key_to_did_key(private_key)

    print(f"Please add {did_key} to the access list of your ActivityPub actor")

    if "management" in config:
        manage_url = (
            urljoin(config["management"], "/manage/did_key_to_account")
            + "?"
            + urlencode({"name": "bull", "key": did_key})
        )
        print(f"or open {manage_url}")

    config[user] = {
        "private_key": private_key,
        "host": host,
        "handlers": {
            "mechanical_bull.actions.accept_follow_request": args.accept,
        },
    }

    with open(config_file, "wb") as fp:
        tomli_w.dump(config, fp)


if __name__ == "__main__":
    main()
