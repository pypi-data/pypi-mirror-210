import os
import subprocess
import sys
from collections import defaultdict
from functools import partial
import kthread
from kthread_sleep import sleep
from pywinpipe import ReadFromPipe
from varpickler import decode_var, encode_var
from time import perf_counter
from subprocess_alive import is_process_alive

pipresults = sys.modules[__name__]
pipresults.pipedict = defaultdict(list)
pipresults.running_pipes = defaultdict(list)
startupinfo = subprocess.STARTUPINFO()
creationflags = 0 | subprocess.CREATE_NO_WINDOW
startupinfo.wShowWindow = subprocess.SW_HIDE
invisibledict = {
    "startupinfo": startupinfo,
    "creationflags": creationflags,
}


class MultiProcPipe:
    def __init__(
        self,
        sub_process,
        write_thread,
        write_function,
        pyfile,
        bytesize,
        pipename,
        pickle_or_dill,
        deque_size,
        other_args,
        timeswritten,
        killfunction,
    ):
        """
        The MultiProcPipe class encapsulates the subprocess, its communication threads, and functions into a single entity,
        allowing for easier management and control of the subprocess and its associated resources.

        Attributes:

            sub_process: The subprocess object representing the running process.
            write_thread: The thread used for writing data to the subprocess.
            write_function: A function used to write data to the subprocess.
            pyfile: The path to the Python script file executed as the subprocess.
            bytesize: The size of the data chunks sent to the subprocess.
            pipename: The name of the named pipe used for inter-process communication.
            pickle_or_dill: The serialization method used for data.
            deque_size: The size of the deque used for storing data chunks.
            other_args: Additional arguments passed to the subprocess script.
            qty_written: A list that keeps track of the number of times data is written to the subprocess.
            kill_process: A function used to terminate the subprocess and associated threads.

        Methods:

            __init__(...): The initialization method of the class. It sets the initial values of the attributes based on the provided arguments.
            start_subprocess(...) -> MultiProcPipe: A static method that starts a subprocess and returns a MultiProcPipe object.
            read_from_windows_pipe(...): A function that reads data from the pipe associated with the subprocess and appends it to pipresults.pipedict[pipename].
            taskkill(...): A function that terminates a process using the taskkill command-line utility.
            kill_pro(...): A function that kills the subprocess and associated threads.
            send_to_process(...) -> bool: A function that sends data to the subprocess by encoding it and writing it to the subprocess's stdin. It returns a boolean indicating the success of the operation.


        """
        self.sub_process = sub_process
        self.write_thread = write_thread
        self.write_function = write_function
        self.pyfile = pyfile
        self.bytesize = bytesize
        self.pipename = pipename
        self.pickle_or_dill = pickle_or_dill
        self.deque_size = deque_size
        self.other_args = other_args
        self.qty_written = timeswritten
        self.kill_process = killfunction


def start_subprocess(
    pyfile: str,
    bytesize: int,
    pipename: str | None = None,
    pickle_or_dill: str = "dill",
    deque_size: int = 20,
    other_args: tuple = (),
    write_first_twice: bool = False,
    block_or_unblock: str = "block",
    pipe_timeout_ms: int = 2000,
    pipe_max_instances: int = 10,
) -> MultiProcPipe:
    """
    Start a subprocess with the provided parameters and return a MultiProcPipe object.

    Args:
        pyfile: The path to the Python script file to be executed as a subprocess.
        bytesize: The size of the data chunks to be sent to the subprocess.
        pipename: The name of the pipe for inter-process communication (optional).
        pickle_or_dill: The serialization method for the data (default: "dill").
        deque_size: The size of the deque for storing data chunks (default: 20).
        other_args: Additional arguments to be passed to the subprocess script (default: empty tuple).
        write_first_twice: Flag indicating whether the first data chunk should be written twice (default: False).
        block_or_unblock: block/unblock named pipe access (default: block)
        pipe_timeout_ms: named pipe timeout (default: 2000)
        pipe_max_instances: max named pipe instances (default: 10)


    Returns:
        A MultiProcPipe object representing the subprocess and associated communication threads/functions.

    """

    startp = os.path.normpath(pyfile) if "\\" in pyfile or "/" in pyfile else pyfile
    imagesize = int(bytesize)
    funa = str(perf_counter())
    pipeadd = []
    if pipename:
        pipeadd = ["--pipename", pipename]

    p = subprocess.Popen(
        [
            sys.executable,
            startp,
            "--objectsize",
            str(imagesize),
            *pipeadd,
            "--dequesize",
            str(deque_size),
            "--block_or_unblock",
            str(block_or_unblock),
            "--pipe_timeout_ms",
            str(pipe_timeout_ms),
            "--pipe_max_instances",
            str(pipe_max_instances),
            *other_args,
        ],
        stdin=subprocess.PIPE,
        start_new_session=True,
        bufsize=imagesize,
        **invisibledict,
    )

    if pipename:
        t = kthread.KThread(
            target=read_from_windows_pipe,
            args=(
                imagesize,
                pipename,
            ),
            name=funa,
        )
        t.start()

    else:
        t = None
    if write_first_twice:
        timeswritten = [0]
    else:
        timeswritten = [1]
    f = partial(
        send_to_process,
        pipename,
        timeswritten,
        bytesize,
        p,
        t,
        pickle_or_dill,
    )
    killfu = partial(kill_pro, p, t, pipename)
    return MultiProcPipe(
        p,
        t,
        f,
        pyfile,
        bytesize,
        pipename,
        pickle_or_dill,
        deque_size,
        other_args,
        timeswritten,
        killfu,
    )


def read_from_windows_pipe(bytesize, pipename):
    baba = ReadFromPipe(
        pipename=pipename,
    )
    here = baba.read_message(bytesize)
    while True:
        try:
            u = next(here)
            pipresults.pipedict[pipename].append(decode_var(u[0]))
            pipresults.running_pipes[pipename].append(baba)
        except Exception as fe:
            baba.close_pipe()
            sleep(0.1)
            if pipresults.pipedict[pipename]:
                break
            try:
                baba = ReadFromPipe(
                    pipename=pipename,
                )
                here = baba.read_message(bytesize)
            except Exception:
                pass
            continue
    try:
        baba.close_pipe()
    except Exception:
        pass


def taskkill(pid):
    _ = subprocess.run(
        f"taskkill.exe /F /PID {pid}",
        start_new_session=True,
        **invisibledict,
        shell=False,
    )


def kill_pro(p, runningthread, pipename):

    try:
        try:
            p.stdout.close()
        except Exception:
            pass

        try:
            p.stderr.close()
        except Exception:
            pass

        try:
            p.stdin.close()
        except Exception:
            pass

        try:
            p.wait(timeout=5)
        except Exception:
            pass
        try:
            p.terminate()
        except Exception:
            pass

        sleep(0.1)
        try:
            for pi in pipresults.running_pipes[pipename]:
                try:
                    pi.close_pipe()
                except Exception:
                    continue
        except Exception:
            pass
        try:
            if runningthread.is_alive():
                try:
                    runningthread.kill()
                except Exception:
                    pass
        except Exception:
            pass
    except Exception:
        pass
    try:
        while is_process_alive(p.pid):
            try:
                taskkill(p.pid)
                sleep(0.1)
            except Exception:
                pass


    except Exception:
        pass


def send_to_process(
    pipename, timeswritten, bytesize, p, runningthread, pickle_or_dill, obj
):
    try:
        numpybytes = encode_var(obj, pickle_or_dill)
        lennum = len(numpybytes)
        if lennum > bytesize:
            print("ERROR! More bytes than defined! Closing everything...")
            raise ValueError

        else:
            if lennum < bytesize:
                addtoby = (bytesize - lennum) * b" "
                numpybytes = numpybytes + addtoby

            if timeswritten[0] == 0:
                p.stdin.write(numpybytes)
                timeswritten[0] += 1
                sleep(1)
                p.stdin.write(numpybytes)
                timeswritten[0] += 1
            p.stdin.write(numpybytes)
            timeswritten[0] += 1
            return True
    except Exception as fa:
        kill_pro(p, runningthread, pipename)
    return False
