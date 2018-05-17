import logging
from logging.config import dictConfig

import yaml
from pkg_resources import resource_stream

from workflow._version import get_versions

__version__ = get_versions()['version']
del get_versions

dictConfig(yaml.load(resource_stream(__name__, 'log.yml')))

logger = logging.getLogger(__name__)


