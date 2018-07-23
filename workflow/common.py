import yaml

DIRTY_POSTFIX = 'dirty'


def yml_read(file):
    with open(file, 'r') as definition:
        loaded = yaml.load(definition)
        return loaded if loaded is not None else dict()
