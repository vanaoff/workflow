import os
from argparse import ArgumentParser
from glob import glob

import git
from azkaban.remote import Session

from workflow import logger
from workflow.common import yml_read, DIRTY_POSTFIX


class Config:
    _GLOBAL_PROPERTIES_BASENAME = 'global.yml'

    def __init__(self, args=None):
        self.parsed = self._parser.parse_args(args)
        self._global_props_file = self.parsed.global_props_file \
                                  or os.path.join(self.root_dir, self._GLOBAL_PROPERTIES_BASENAME)
        if os.path.exists(self._global_props_file):
            self.global_props = yml_read(self._global_props_file)
        else:
            logger.info("Global property file %s doesn't exist.", self._global_props_file)
            self.global_props = dict()

    @property
    def _parser(self):
        parser = ArgumentParser(description='Workflow builder and uploader.')
        project = parser.add_mutually_exclusive_group(required=True)

        project.add_argument('--definition', help='Project definition in file.')
        project.add_argument('--project-dir', help='Project directory to be built. The folder is supposed to contain '
                                                   'project.yml. All files in directory are uploaded to Azkaban.')
        project.add_argument('--projects-root', help='Directory containing multiple projects to be built.')

        azkaban_settings = parser.add_mutually_exclusive_group(required=True)
        azkaban_settings.add_argument('--azkaban-alias',
                                      help='Alias for azkaban configuration (stored in ~/.azkabanrc)')
        azkaban_settings.add_argument('--azkaban-url', )
        azkaban_settings.add_argument('--local', action='store_true', help='Build zip instead of upload.')

        parser.add_argument('--global-props-file',
                            help="Yaml file defining properties shared by all workflows in scope.", default=None)
        return parser

    @property
    def many(self):
        return self.parsed.projects_root is not None

    @property
    def definition_only(self):
        return self.parsed.definition is not None

    @property
    def root_dir(self):
        if self.many:
            return self.parsed.projects_root
        else:
            return os.path.join(self.parsed.project_dir, os.path.pardir)

    @property
    def projects(self):
        if self.many:
            for project_dir in glob(os.path.join(self.parsed.projects_root, '*/')):
                yield project_dir
        else:
            yield self.parsed.project_dir

    @property
    def session(self):
        if self.parsed.azkaban_url is not None:
            return Session(url=self.parsed.azkaban_url, verify=True)
        if self.parsed.azkaban_alias is not None:
            return Session.from_alias(self.parsed.azkaban_alias)

    @property
    def repo_revision(self):
        try:
            repo = git.Repo(path=self.root_dir, search_parent_directories=True)
            sha = repo.head.object.hexsha[:8]
            return sha if not repo.is_dirty() else '%s.%s' % (sha, DIRTY_POSTFIX)
        except git.exc.InvalidGitRepositoryError as e:
            return 'unversioned'
