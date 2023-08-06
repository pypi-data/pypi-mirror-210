import inspect
from fluent import asyncsender
import os
import msgpack
from io import BytesIO
import sys
import traceback


fluentd_host = os.environ.get("fluent_host", "")
fluentd_port = int(os.environ.get("fluent_port", 0))
component_name = os.environ.get("component_name", "")


def overflow_handler(pendings):
    unpacker = msgpack.Unpacker(BytesIO(pendings))
    for unpacked in unpacker:
        print(unpacked)

def log_emmiter(msg, typ="INFO"):
    try:
        #eval file name to log to from typ
        log_sender = asyncsender.FluentSender(component_name, host=fluentd_host, port=fluentd_port, buffer_overflow_handler=overflow_handler)
        log_sender.emit(typ, {"message": f"{msg}"})
        log_sender.close()
    except:
        e = sys.exc_info()
        traceback_output = "".join(traceback.format_exception(e[0], e[1], e[2]))
        print("Error occured in caching logger", str(traceback_output))

def logger(fn, typ="INFO"):
    from functools import wraps
    from datetime import datetime, timezone

    @wraps(fn)
    def inner(*args, **kwargs):
        run_time = datetime.now()
        line_num = inspect.currentframe().f_back.f_lineno
        fname = fn.__name__
        filename = fn.__module__
        arg = inspect.currentframe()
        all_locals = arg.f_back.f_locals
        logging_str = f" ~##~ LINE {line_num} FUNCTION {fname} FILE {filename} ALL_LOCALS ~##~ {all_locals}"
        # print(logging_str)
        log_emmiter(logging_str)
        return fn(*args, **kwargs)

    return inner
