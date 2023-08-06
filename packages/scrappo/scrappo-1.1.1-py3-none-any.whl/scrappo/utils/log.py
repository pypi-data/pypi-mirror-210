import sys
from datetime import datetime


def throw(message):
    print('[' + str(datetime.utcnow()) + ']>>!ERROR:\t' + message)
    sys.exit()


def show(message, to_exit=False, with_date=True, end='\n'):
    if with_date:
        print('[' + str(datetime.utcnow()) + ']', end='')
    print('\t>>!:' + message, end=end)

    if to_exit:
        sys.exit()
