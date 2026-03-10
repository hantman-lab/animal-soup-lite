"""
The module that defines logging functionality.
"""

import sys
import time
import logging
import datetime
from contextlib import contextmanager


# %%%%% Logging


logger = logging.getLogger("animal-soup-lite")
logger.setLevel(logging.WARNING)  # the app sets the level based on the config


def setup_log_file_handler(log_dir):
    """Setup the log handler to customize formatting, write to stdout, and write to a logfile."""
    # Get filename for log file for this session
    now_tag = time.strftime("%Y%m%d_%H%M")
    for i in range(99):
        filename = log_dir / f"detect_{now_tag}_{i:02d}.log"
        if not filename.exists():
            break
    # Create handlers and add to root logger
    formatter = logging.Formatter("[%(levelname)s %(asctime)s %(name)s] %(message)s")
    handler1 = logging.StreamHandler(sys.stderr)
    handler2 = logging.FileHandler(filename)
    handler1.setFormatter(formatter)
    handler2.setFormatter(formatter)
    root = logging.getLogger()
    root.addHandler(handler1)
    root.addHandler(handler2)
    # Clean up old logs
    purge_old_log_files(log_dir)


def purge_old_log_files(log_dir):
    with log_exception("purging logs"):
        num_days_to_keep_logs = 10
        remove = []
        now = datetime.datetime.now()
        for path in log_dir.iterdir():
            if path.name.startswith("detect_"):
                date_str = path.name.split("_")[1].replace("-", "")
                assert len(date_str) == 8
                date = datetime.datetime.strptime(date_str, "%Y%m%d")
                diff = now - date
                if diff.days > num_days_to_keep_logs:
                    remove.append(path)
        for path in remove:
            try:
                path.unlink()
            except Exception:
                pass


err_hashes = {}  # hash -> [short-message, count, next-time]


def _error_message_hash(message):
    return hash(message)


@contextmanager
def log_exception(kind):
    """Context manager to log any exceptions, but only log a one-liner
    for subsequent occurrences of the same error to avoid spamming by
    repeating errors in e.g. a draw function or event callback.
    """
    try:
        yield
    except Exception as err:
        # Store exc info for postmortem debugging
        exc_info = list(sys.exc_info())
        exc_info[2] = exc_info[2].tb_next  # type: ignore | skip *this* function
        sys.last_type, sys.last_value, sys.last_traceback = exc_info
        # Show traceback, or a one-line summary
        msg = str(err)
        msgh = _error_message_hash(msg)
        if msgh not in err_hashes:
            # Prepare a short variant of the message for later use
            short_msg = kind + ": " + msg.split("\n")[0].strip()
            short_msg = short_msg if len(short_msg) <= 70 else short_msg[:69] + "…"
            err_hashes[msgh] = [short_msg, 1, 0]
            # Provide the exception, so the default logger prints a stacktrace.
            # IDE's can get the exception from the root logger for PM debugging.
            logger.error(kind, exc_info=err)
        else:
            # We've seen this message before, return a one-liner instead.
            short_count_tm = err_hashes[msgh]
            short, count, tm = short_count_tm
            short_count_tm[1] = count = count + 1
            # Show the message now?
            show_message = False
            cur_time = time.perf_counter()
            if count <= 5:
                show_message = True
            else:
                if cur_time > tm:
                    show_message = True
            # Log the messages and schedule when to show it next.
            # Next message is after 1-3 seconds (3 when count reaches 300).
            if show_message:
                short_count_tm[2] = cur_time + min(max(count / 100, 1), 3)
                logger.error(f"{short} ({count})")
