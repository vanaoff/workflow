import yaml

from workflow import logger

DIRTY_POSTFIX = 'dirty'


def yml_read(file):
    logger.debug('Reading %s', file)
    with open(file, 'r') as definition:
        loaded = yaml.load(definition)
        return loaded if loaded is not None else dict()
