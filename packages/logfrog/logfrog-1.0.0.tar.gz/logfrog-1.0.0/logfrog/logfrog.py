import datetime
from threading import Thread 
from queue import Queue 
import traceback 


class LogFrog:
    def __init__(self, filename= "logs.txt"):   
        self.filename = filename
        self.log_queue = Queue()
        self.thread = Thread(target=self._background_logger, daemon = True)
        self.thread.start()

    #background logger for async logging
    def _background_logger(self):
        while(True):
            item = self.log_queue.get(block=True)
            if(item is None):
                self.index = -1 
                break
            
            log_level, message, timestamp = item
            with open(self.filename, 'a+') as log_file:
                print(f"{timestamp} '{log_level}' '{message}'\n")
                log_file.write(f"{timestamp} '{log_level}' '{message}'\n")


    def stop(self):
        self.log_queue.put(None)
        
    def write_log(self, message, log_level ="INFO"):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("pushing to queue")
        self.log_queue.put((log_level, message, timestamp))

    def info(self, message):
        self.write_log("INFO", message)

    def debug(self, message):
        self.write_log("DEBUG", message)

    def warning(self, message):
        self.write_log("WARNING", message)

    def error(self, message):
        self.write_log("ERROR", message)

    def critical(self, message):
        self.write_log("CRITICAL", message)

    def log_function(self, func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            self.write_log("FUNCTION LOG", f"{func.__name__} {args} {kwargs} returned {result}")
            return result
        return wrapper

    def log_stack(self):
        stack = traceback.extract_stack()[:-1]  # remove the last entry
        stack_trace = "".join(traceback.format_list(stack))
        self.info(stack_trace)
