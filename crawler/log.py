import logging
import logging.handlers
import os
import time
from  datetime import datetime

def log_service( logfilename,
            loglevel = logging.INFO,
            formatstring = "%(asctime)s -<%(lineno)d> %(levelname)s: \t%(message)s ",
            #debug = False,
            debug = True,
            splitby = 'time',
    ):

    _dir = "./"
    if not os.path.exists(_dir):
        os.mkdir(_dir)
    _format = logging.Formatter (formatstring)
    log = logging.getLogger(_dir + logfilename + "__")
    if splitby == 'time':
        fh = logging.handlers.TimedRotatingFileHandler(_dir + logfilename, 'W0')
    elif splitby == 'size':
        fh = logging.handlers.RotatingFileHandler(_dir + logfilename, maxBytes=1024 * 1024 * 10, backupCount=10)
    else:
        fh = logging.FileHandler(_dir + logfilename)
    fh.setFormatter(_format)
    fh.setLevel(loglevel)
    log.addHandler(fh)
    log.setLevel(loglevel)

    if debug:
        debughandler = logging.StreamHandler()
        debughandler.setLevel(logging.DEBUG)
        debughandler.setFormatter(_format)
        log.addHandler(debughandler)
        log.setLevel(logging.DEBUG)
    return log
   
 
def test():
    today = datetime.now().strftime("%Y%m%d")
    log = log_service('craw_log_%s.log' %today) 
    log.info("log info from test")  

if __name__ == "__main__":
    test()
