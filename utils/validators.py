import argparse 
from datetime import datetime
from dateutil import parser

def valid_id(idstr: str) -> int:
    try:
        intid = int(idstr)
        if intid < 0:
            raise ValueError()
        
        return int(idstr)

    except ValueError:
        msg = f"Invalid ID: {idstr}"
        raise argparse.ArgumentTypeError(msg) 
    
def valid_date(datestr: [str]) -> datetime:
    datestr = " ".join(list(datestr))
    try:
        return parser.parse(datestr)
    except (parser.ParserError):
        msg = f"Invalid date: {datestr}"
        print(msg)
