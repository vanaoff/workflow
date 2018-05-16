import logging
import os
from argparse import ArgumentParser
from glob import glob
from logging.config import dictConfig
from os import path

import git
import yaml
from azkaban import Job
from azkaban import Project
# noinspection PyUnresolvedReferences
from azkaban.remote import Session
from azkaban.util import AzkabanError
from pkg_resources import resource_filename

import workflow

dictConfig(yaml.load(open(file=resource_filename(__name__, 'log.yml'))))

logger = logging.getLogger(__name__)

logger.info('Azkaban Workflow Builder and Uploader version %s.' % workflow.__version__)


def get_parser():
    parser = ArgumentParser(description='Workflow builder and uploader.')
    parser.add_argument('-p', '--project', dest='project',
                        help='Project to be uploaded.', type=str)
    parser.add_argument('-d', '--projects', dest='projects',
                        help='Projects directory to be uploaded.', type=str)
    parser.add_argument('-a', '--alias', dest='alias',
                        help='Alias for azkaban configuration (stored in ~/.azkabanrc)', type=str)
    parser.add_argument('-u', '--url', dest='url', help='Azkaban url.')
    parser.add_argument('-l', '--local', action='store_true', dest='local', help='Build zip instead of upload.')
    return parser


def yml_read(file):
    logger.debug('Reading %s', file)
    with open(file, 'r') as definition:
        loaded = yaml.load(definition)
        return loaded if loaded is not None else dict()


def read_global_props(root_dir):
    global_props_path = path.join(root_dir, 'global.yml')
    try:
        global_props = yml_read(global_props_path)
        logger.info('Loaded global property dict %s.', global_props_path)
    except FileNotFoundError:
        logger.info("Global property file %s doesn't exist.", global_props_path)
        global_props = dict()
    return global_props


def repo_revision(dir):
    try:
        repo = git.Repo(path=dir, search_parent_directories=True)
        sha = repo.head.object.hexsha[:8]
        return sha if not repo.is_dirty() else '%s.dirty' % sha
    except git.exc.InvalidGitRepositoryError as e:
        return 'unversioned'


def build_project(dir, session=None, name=None, global_props=None, description=None, upload=False):
    if name is None:
        name = path.basename(dir.rstrip('/')).split(path.sep)[-1]

    logger.info("Building project %s.", name)

    project = Project(name, root=os.curdir, version=repo_revision(dir))

    definition = yml_read(path.join(dir, 'project.yml'))

    if global_props is None:
        global_props = read_global_props(path.join(dir, os.pardir))

    project.properties = global_props

    properties = definition.get('properties')

    if type(properties) == dict:
        for prop, value in properties.items():
            project.properties[prop] = value

    jobs = definition.get('jobs')
    if type(jobs) == dict:
        for job_name, job_definition in jobs.items():
            project.add_job(job_name, Job(job_definition))

    for file in glob(path.join(dir, '**/*'), recursive=True):
        project.add_file(file, file.replace(dir, './'))

    _zip = '%s.zip' % project.versioned_name

    project.build(_zip, overwrite=True)

    if upload:
        existing = {project['projectName'] for project in session.get_projects()['projects']}
        if name not in existing:
            logger.info("Project %s doesn't exist. Creating.", name)
            session.create_project(name, description=description if description else name)

        if project.versioned_name.endswith('dirty') or \
                project.versioned_name.endswith('unversioned'):
            logger.warning('Uploading uncommitted version of workflow.')

        session.upload_project(name, _zip)
        os.remove(_zip)

        for flow, schedule in definition.get('schedule', dict()).items():
            try:
                current = session.get_schedule(name, flow)
            except AzkabanError:
                current = None
            if not current:
                logger.info('Unscheduling %s@%s.', flow, name)
                session.schedule_cron_workflow(name, flow, schedule)
            elif current['cronExpression'] != schedule:
                logger.info('Rescheduling %s @ %s to %s.', flow, name, schedule)
                session.unschedule_workflow(name, flow)
                session.schedule_cron_workflow(name, flow, schedule)
    return project


def build_many(root_dir, session, upload=False):
    logger.info('Building all projects in %s', root_dir)
    global_props = read_global_props(root_dir)
    for dir in glob(path.join(root_dir, '*/')):
        build_project(dir, session, global_props=global_props, upload=upload)


def create_session(alias=None, url=None):
    if url:
        return Session(url=config.url, verify=False)
    elif alias:
        return Session.from_alias(config.alias)
    raise ValueError("Neither url or alias for azkaban configuration provided.")


if __name__ == '__main__':
    config = get_parser().parse_args()
    session = None if config.local else create_session(config.alias, config.url)

    if config.project:
        build_project(config.project, session, upload=not config.local)
    elif config.projects:
        build_many(config.projects, session, upload=not config.local)
