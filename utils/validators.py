import argparse 

def valid_id(idstr: str) -> int:
    try:
        intid = int(idstr)
        if intid < 0:
            raise ValueError()
        
        return int(idstr)

    except ValueError:
        msg = f"Invalid ID: {idstr}"
        raise argparse.ArgumentTypeError(msg) 