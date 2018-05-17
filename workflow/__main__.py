from workflow import logger, __version__
from workflow.builder import process_project
from workflow.config import Config

if __name__ == '__main__':
    c = Config()
    logger.info('Azkaban Workflow Builder and Uploader version %s.' % __version__)
    for project_dir in c.projects:
        process_project(project_dir, c.session, c.global_props, c.repo_revision)
