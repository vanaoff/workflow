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
                        help='Alias for azkaban configuration (stored in ~/.azkabanrc)', type=str,
                        default='zactverec')
    parser.add_argument('-u', '--url', dest='url', help='Azkaban url.')
    parser.add_argument('-l', '--local', action='store_true', dest='local', help='Build zip instead of upload.')
    return parser


def yml_read(file):
    logger.info('Reading %s', file)
    with open(file, 'r') as definition:
        return yaml.load(definition)


def repo_revision(dir):
    try:
        repo = git.Repo(path=dir, search_parent_directories=True)
        sha = repo.head.object.hexsha[:8]
        return sha if not repo.is_dirty() else '%s.dirty' % sha
    except git.exc.InvalidGitRepositoryError as e:
        return 'unversioned'


def build_project(session, dir, name=None, global_props=None, description=None, upload=True):
    if not name:
        name = path.basename(dir.rstrip('/')).split(path.sep)[-1]

    logger.info("Building project %s.", name)

    project = Project(name, root=os.curdir, version=repo_revision(dir))

    definition = yml_read(path.join(dir, 'project.yml'))

    if not global_props:
        try:
            global_props_path = path.join(dir, os.pardir, 'global.yml')
            global_props = yml_read(global_props_path)
            logger.info('Loaded %s as global property dict.', global_props_path)
        except FileNotFoundError:
            global_props = dict()

    project.properties = global_props

    for prop, value in definition.get('properties', dict()).items():
        project.properties[prop] = value

    for job_name, job_definition in definition.get('jobs', dict()).items():
        project.add_job(job_name, Job(job_definition))

    for file in glob(path.join(dir, '**/*'), recursive=True):
        project.add_file(file, file.replace(dir, './'))

    _zip = '%s.zip' % project.versioned_name

    project.build(_zip, overwrite=True)

    if upload:
        existing = {project['projectName'] for project in session.get_projects()['projects']}
        if name not in existing:
            logger.info("Project %s not in %. Creating.", name, existing)
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


def build_many(session, root_dir, upload=False):
    try:
        global_props_path = yml_read(path.join(root_dir, 'global.yml'))
        global_props = yml_read(global_props_path)
        logger.info('Loaded %s as global property dict.')
    except FileNotFoundError:
        global_props = dict()

    for dir in glob(path.join(root_dir, '*/')):
        logger.info('Preparing project %s.', dir)
        build_project(session, dir, global_props=global_props, upload=upload)


def create_session(alias=None, url=None):
    if url:
        return Session(url=config.url)
    elif alias:
        return Session.from_alias(config.alias)


if __name__ == '__main__':
    config = get_parser().parse_args()
    session = create_session(config.alias, config.url)
    if session:
        if config.project:
            build_project(session, config.project, upload=not config.local)
        elif config.projects:
            build_many(session, config.projects, upload=not config.local)
