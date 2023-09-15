#!/opt/homebrew/bin/python3

import argparse
from utils.wrappers.parser import Parser
from utils.wrappers.database import Database
from utils import constants
import sys

def main(args: argparse.Namespace):
    if (args.meta == True):
        print(f"Config Location: {constants.DB_PATH}")
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    myparser = Parser(version=constants.VERSION)
    Database.setup_databases()
    myparser.setup()
    args = myparser.get_args()
    main(args)
    Database.dispose()
