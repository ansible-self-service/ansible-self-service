import contextlib
import os
import sys
import traceback
from functools import wraps
from multiprocessing import Process, Queue


@contextlib.contextmanager
def set_env(**environ: str):
    """
    Temporarily set the process environment variables.

    >>> with set_env(PLUGINS_DIR=u'test/plugins'):
    ...   "PLUGINS_DIR" in os.environ
    True

    >>> "PLUGINS_DIR" in os.environ
    False

    :type environ: dict[str, unicode]
    :param environ: Environment variables to set
    """
    old_environ = dict(os.environ)
    os.environ.update(environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_environ)


def processify(func):
    """Decorator to run a function as a process.
    Be sure that every argument and the return value
    is *pickable*.
    The created process is joined, so the code does not
    run in parallel.
    """

    def process_func(queue, *args, **kwargs):
        try:
            ret = func(*args, **kwargs)
        except Exception:  # pylint: disable=broad-except
            ex_type, ex_value, trace_back = sys.exc_info()
            error = ex_type, ex_value, "".join(traceback.format_tb(trace_back))
            ret = None
        else:
            error = None

        queue.put((ret, error))

    # register original function with different name
    # in sys.modules so it is pickable
    process_func.__name__ = func.__name__ + "processify_func"
    setattr(sys.modules[__name__], process_func.__name__, process_func)

    @wraps(func)
    def wrapper(*args, **kwargs):
        queue = Queue()
        process = Process(
            target=process_func, args=(queue,) + tuple(args), kwargs=kwargs
        )
        process.start()
        ret, error = queue.get()
        process.join()

        if error:
            ex_type, ex_value, tb_str = error
            message = f"{ex_value.message} (in subprocess)\n{tb_str}"
            raise ex_type(message)

        return ret

    return wrapper
