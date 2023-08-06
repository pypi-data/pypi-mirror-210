import logging
import logging.config
import sys

from izihawa_utils.exceptions import BaseError
from izihawa_utils.file import mkdir_p

from .formatters import DefaultFormatter, DefaultHttpFormatter
from .handlers import QueueHandler


def configure_logging(config, make_path=True):
    if config.get('application', {}).get('debug', False) or 'logging' not in config:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    else:
        if make_path:
            mkdir_p(config['log_path'])
        logging.config.dictConfig(config['logging'])


def error_log(e, level=logging.ERROR, **fields):
    level = getattr(e, 'level', level)
    if isinstance(e, BaseError):
        e = e.as_internal_dict()
        e.update(fields)
    elif fields:
        e = {'error': repr(e), **fields}
    logging.getLogger('error').log(
        msg=str(e),
        level=level
    )


__all__ = [
    'DefaultFormatter', 'DefaultHttpFormatter',
    'QueueHandler', 'configure_logging', 'error_log',
]
