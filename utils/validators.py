import argparse 
from datetime import datetime
from dateutil import parser

from utils.wrappers.database import Database

def valid_id(idstr: str) -> int:
    try:
        intid = int(idstr)
        if intid < 0:
            raise ValueError()
        db = Database()
        if int(idstr) in db.get_ids():
            return int(idstr)
        else:
            raise ValueError()
    except ValueError:
        msg = f"Invalid ID: {idstr}"
        raise argparse.ArgumentTypeError(msg) 


def valid_date(datestr: [str]) -> datetime:
    if datestr:
        datestr = " ".join(list(datestr))
        try:
            return parser.parse(datestr)
        except (parser.ParserError):
            msg = f"Invalid date: {datestr}"
            print(msg)
    else:
        return datestr
