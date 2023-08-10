import argparse
from utils.wrappers import Parser, Database


def main(args: argparse.Namespace):
    args.func(args)


if __name__ == "__main__":
    myparser = Parser(version="0.1.0")
    database = Database()
    myparser.setup()
    args = myparser.get_args()
    main(args)
    database.dispose()
