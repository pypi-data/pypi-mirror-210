import sys
from collections import deque
from typing import Any
import kthread
from pywinpipe import Write2Pipe
from varpickler import decode_var, encode_var
from hackyargparser import add_sysargv
from threading import Lock

lock = Lock()
stdincollection = sys.modules[__name__]
stdincollection.stdin_deque = deque([], 100)
stdincollection.pipe_writer = None
stdincollection.ran_out_of_input = False


@add_sysargv
def create_deque(dequesize: int = 0):
    try:
        lock.acquire()
        olddeque = stdincollection.stdin_deque.copy()
        stdincollection.stdin_deque = deque([], dequesize)
        for d in olddeque:
            stdincollection.stdin_deque.append(d)
    finally:
        try:
            lock.release()
        except Exception:
            pass


@add_sysargv
def read_stdin(objectsize: int = 0):
    while True:
        try:
            sysin = decode_var(sys.stdin.buffer.read(objectsize).rstrip())
        except Exception as fa:
            stdincollection.ran_out_of_input = True
            print(fa, end='\r')
            continue
        try:
            lock.acquire()
            stdincollection.stdin_deque.append(sysin)
        except Exception:
            stdincollection.stdin_deque.append(sysin)
        finally:
            try:
                lock.release()
            except Exception:
                pass


@add_sysargv
def write2pipe(
    obj: Any = None,
    objectsize: int = 0,
    pipename: str | None = None,
    block_or_unblock: str = "unblock",
    pipe_timeout_ms: int = 2000,
    pipe_max_instances: int = 10,
):
    if not stdincollection.pipe_writer:
        stdincollection.pipe_writer = Write2Pipe(
            pipename=pipename,
            nMaxInstances=pipe_max_instances,
            nOutBufferSize=objectsize,
            nInBufferSize=objectsize,
            timeout=pipe_timeout_ms,
            block_or_nonblock=block_or_unblock,
        )
    im2 = encode_var(obj, pickle_or_dill="dill", base="base64")
    stdincollection.pipe_writer.write_message(im2)


create_deque()
t = kthread.KThread(target=read_stdin)
t.start()
