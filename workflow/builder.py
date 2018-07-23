import os

from azkaban import Job
from azkaban import Project
from azkaban.util import AzkabanError

from workflow import logger
from workflow.common import DIRTY_POSTFIX


def upload_project(session, name, zipfile, version, description):
    existing = {project['projectName'] for project in session.get_projects()['projects']}
    if name not in existing:
        logger.info("Project %s doesn't exist. Creating.", name)
        session.create_project(name, description=description)

    if version.endswith(DIRTY_POSTFIX):
        logger.warning('Uploading uncommitted version of workflow.')

    session.upload_project(name, zipfile)


def schedule_flow(session, name, flow, schedule):
    try:
        current = session.get_schedule(name, flow)
    except AzkabanError:
        current = None
    if current is None:
        logger.info('Scheduling %s@%s to %s', flow, name, schedule)
        session.schedule_cron_workflow(name, flow, schedule)
    elif current['cronExpression'] != schedule:
        logger.info('Rescheduling %s @ %s from %s to %s.', flow, name, current['cronExpression'], schedule)
        session.unschedule_workflow(name, flow)
        session.schedule_cron_workflow(name, flow, schedule)


def build_project(name, properties, extra_properties, jobs, files, version):
    logger.info("Building workflow %s, version: %s.", name, version)

    project = Project(name, root=os.curdir, version=version)
    project.properties = extra_properties
    project.properties.update(properties)

    for job_name, job_definition in jobs.items():
        logger.info('Adding job %s.', job_name)
        project.add_job(job_name, Job(job_definition))

    for file, target in files:
        logger.info('Adding file %s as %s', file, target)
        project.add_file(file, target)
    return project


def process_project(session, name, definition, extra_properties, version, files):
    properties = definition.get('properties', dict())
    jobs = definition.get('jobs', dict())
    description = definition.get('description', name)
    schedules = definition.get('schedule', dict())

    project = build_project(name, properties, extra_properties, jobs, files, version)

    zipfile = '%s.zip' % project.versioned_name
    project.build(zipfile, overwrite=True)

    if session is not None:
        upload_project(session, name, zipfile, version, description)
        for flow, schedule in schedules.items():
            schedule_flow(session, name, flow, schedule)
        os.remove(zipfile)
