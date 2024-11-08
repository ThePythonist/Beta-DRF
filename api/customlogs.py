import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
)


def make_log(level, message):
    """Log a message at a specified level."""
    if level == 'debug':
        logging.debug(message)
    elif level == 'info':
        logging.info(message)
    elif level == 'warning':
        logging.warning(message)
    elif level == 'error':
        logging.error(message)
    elif level == 'critical':
        logging.critical(message)
    else:
        raise ValueError("Invalid log level. Choose from: debug, info, warning, error, critical.")


def tictoc(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Start timing
        result = func(*args, **kwargs)  # Call the original function
        duration = time.time() - start_time  # Calculate duration
        make_log("info", f"Response time for {func.__name__}: {duration:.2f} seconds.")  # Log the duration
        return result  # Return the result of the original function

    return wrapper
