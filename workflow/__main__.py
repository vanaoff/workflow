from logging.config import dictConfig

import yaml
from pkg_resources import resource_stream

from workflow import logger, __version__
from workflow.builder import process_project
from workflow.config import Config

dictConfig(yaml.load(resource_stream(__name__, 'log.yml')))

if __name__ == '__main__':
    c = Config()
    logger.info('Azkaban Workflow Builder and Uploader version %s.' % __version__)
    process_project(c.session, c.name, c.definition, c.extra_properties, c.version, c.files)
