from workflow import logger, __version__
from workflow.builder import process_project
from workflow.config import Config

if __name__ == '__main__':
    c = Config()
    logger.info('Azkaban Workflow Builder and Uploader version %s.' % __version__)
    if c.definition_only:
        process_project(c.session, c.global_props, c.version, project_file=c.parsed.project_file)
    else:
        for project_dir in c.projects:
            process_project(c.session, c.global_props, c.version, project_dir=project_dir)
