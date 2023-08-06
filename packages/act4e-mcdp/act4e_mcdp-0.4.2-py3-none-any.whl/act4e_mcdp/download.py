import argparse
import os

from . import logger

__all__ = ["download_main"]


def download_main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", help="Where to put the data", default="downloaded")

    args = parser.parse_args()

    output = args.output

    from .autogen_packed_test_data import resources

    os.makedirs(output, exist_ok=True)

    for name, data in resources.items():
        fn = os.path.join(output, name)
        logger.info("Writing %r", fn)
        with open(fn, "w") as f:
            f.write(data)
