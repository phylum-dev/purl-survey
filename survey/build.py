"""Build all drivers."""

from concurrent.futures import ThreadPoolExecutor
import sys
import traceback

from tqdm import tqdm

if __name__ == "__main__":
    from . import drivers

    with tqdm() as pbar:

        def done(future):
            exception = future.exception()
            if exception is not None:
                traceback.print_exception(exception)
                sys.exit(1)
            pbar.update()

        with ThreadPoolExecutor() as executor:
            for driver in drivers():
                pbar.total = (pbar.total or 0) + 1
                pbar.update(0)

                future = executor.submit(lambda d: d.build(), driver)
                future.add_done_callback(done)

            executor.shutdown()
