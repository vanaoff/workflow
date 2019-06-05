import os
from argparse import ArgumentParser
from glob import glob

import git
import yaml
from azkaban.remote import Session

from workflow.common import DIRTY_POSTFIX, yml_read


class Config:
    def __init__(self, args=None):
        self.parsed = self._parser.parse_args(args)
        self._definition = None
        self._extra_properties = None

    @property
    def _parser(self):
        parser = ArgumentParser(description='Workflow builder and uploader.')

        parser.add_argument('--definition', '-d', required=True, help='Project definition yaml file.')
        parser.add_argument('--extra-properties', '-e', help='Extra properties to be included in project.')
        parser.add_argument('--files-to-upload', '-f',
                            help='Path to directory containing the files which should be uploaded.')
        parser.add_argument('--version', '-v',
                            help="Manual specification of deployed workflow version.")

        azkaban = parser.add_mutually_exclusive_group(required=True)
        azkaban.add_argument('--azkaban-alias', '-a',
                             help='Alias for azkaban configuration (configured in ~/.azkabanrc)')
        azkaban.add_argument('--azkaban-url', '-u', help="Url of azkaban to connect.")
        azkaban.add_argument('--local', '-l ', action='store_true', help='Build zip instead of upload.')
        return parser

    @property
    def definition(self):
        if self._definition is None:
            with open(self.parsed.definition, 'r') as f:
                self._definition = yaml.load(f)
        return self._definition

    @property
    def extra_properties(self):
        if self._extra_properties is None:
            if self.parsed.extra_properties is None:
                self._extra_properties = dict()
            else:
                self._extra_properties = yml_read(self.parsed.extra_properties)
        return self._extra_properties

    @property
    def name(self):
        candidate = os.path.basename(self.parsed.definition.rstrip('/').split(os.path.sep)[-1])
        return self.definition.get('name') or candidate

    def get_session(self):
        if not self.parsed.local:
            if self.parsed.azkaban_url is not None:
                return Session(url=self.parsed.azkaban_url, verify=True)
            return Session.from_alias(self.parsed.azkaban_alias)

    @property
    def repo_revision(self):
        try:
            repo = git.Repo(path=self.parsed.definition, search_parent_directories=True)
            sha = repo.head.object.hexsha[:8]
            return sha if not repo.is_dirty() else '%s.%s' % (sha, DIRTY_POSTFIX)
        except git.exc.InvalidGitRepositoryError as e:
            pass

    @property
    def version(self):
        return self.parsed.version \
               or self.repo_revision \
               or 'unversioned'

    @property
    def files(self):
        if self.parsed.files_to_upload is not None:
            path = self.parsed.files_to_upload.strip().rstrip('/*')
            for file in glob(os.path.join(path, '**/*'), recursive=True):
                yield file, file.replace(path, '.')
