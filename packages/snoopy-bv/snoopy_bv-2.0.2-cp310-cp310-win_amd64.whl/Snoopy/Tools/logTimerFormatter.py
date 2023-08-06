import logging
import time


class LogTimerFormatter( logging.Formatter ):
    """Logging Formatter which include a timer


    START in message start the timer (indicated by "s" in displayed message)
    STOP in message display the time since last "START"
    both START and STOP can be in present in a same message

    """
    def __init__(self, datefmt="%Y-%m-%d %H:%M:%S"):
        logging.Formatter.__init__(self)
        self.datefmt = datefmt
        self.tstart = time.time()

    def format(self, r) :
        ct = self.converter(r.created)

        message = r.getMessage()
        t = ""
        s = "-"
        if "STOP" in message :
            elapsed = time.time() - self.tstart
            message = message.replace("STOP" , "")
            t = f"{elapsed:.2f}s"

        if "START" in message :
            message = message.replace("START" , "")
            self.tstart = time.time()
            s = "s"

        if r.levelno == logging.DEBUG:
            s = f"{r.filename:} - {r.levelname:7s} {s:} {t:5s} - {message:}  "
        elif r.levelno > logging.CRITICAL:
            s = message
        else :
            s = f"{r.levelname:7s} {s:} {t:5s} - {message:}  "

        return s



if __name__ == "__main__" :
    #Create logger for Snoopy
    logger = logging.getLogger(__name__)
    if len(logger.handlers) == 0 :  # Avoid re-adding handlers (When script is re-run with spyder for instance)
        c_handler = logging.StreamHandler()
        c_handler.setFormatter( LogTimerFormatter() )
        logger.addHandler(c_handler)

    logger.setLevel(logging.DEBUG)
    logger.debug("test START")
    time.sleep(2)
    logger.warning("test1 START STOP")
    time.sleep(1)
    logger.warning("test2 STOP")
