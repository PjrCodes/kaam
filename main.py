#!/opt/homebrew/bin/python3

import argparse
from utils.wrappers.parser import Parser
from utils.wrappers.database import Database

VERSION = "0.0.2"

def main(args: argparse.Namespace):
    args.func(args)


if __name__ == "__main__":
    myparser = Parser(version=VERSION)
    Database.setup_databases()
    myparser.setup()
    args = myparser.get_args()
    main(args)
    Database.dispose()
