import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    # Basic configuration for logging
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')

    # File handler - logs will also be saved to a file
    file_handler = RotatingFileHandler('app.log', maxBytes=1024 * 1024 * 100, backupCount=20)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)

    # Return the configured file handler
    return file_handler
