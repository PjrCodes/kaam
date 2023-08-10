import argparse
from utils.wrappers.parser import Parser
from utils.wrappers.database import Database


def main(args: argparse.Namespace):
    args.func(args)


if __name__ == "__main__":
    myparser = Parser(version="0.1.0")
    Database.setup_databases()
    myparser.setup()
    args = myparser.get_args()
    main(args)
    Database.dispose()
