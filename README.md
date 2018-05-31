# Workflow #

[AzkabanCLI](https://github.com/mtth/azkaban) wrapper for easier workflow definition.

### Installation ###

`pip install git+https://git@github.com/vanaoff/workflow.git@master`

### Usage ###

Workflow definition structure: see `./example_projects/`

Workflow package relies there exists `~/.azkabanrc` file with connection definitions
```ini
[azkaban]
default.alias = one

[alias.one]
url = https://user:P455w0rd@azkaban.domain.io:443
``` 

Module could be run with `python -m workflow` with following parameters:

```
usage: __main__.py [-h]
                   (--definition DEFINITION | --project-dir PROJECT_DIR | --projects-root PROJECTS_ROOT)
                   (--azkaban-alias AZKABAN_ALIAS | --azkaban-url AZKABAN_URL | --local)
                   [--global-props-file GLOBAL_PROPS_FILE]

Workflow builder and uploader.

optional arguments:
  -h, --help            show this help message and exit
  --definition DEFINITION
                        Project definition in file.
  --project-dir PROJECT_DIR
                        Project directory to be built. The folder is supposed
                        to contain project.yml. All files in directory are
                        uploaded to Azkaban.
  --projects-root PROJECTS_ROOT
                        Directory containing multiple projects to be built.
  --azkaban-alias AZKABAN_ALIAS
                        Alias for azkaban configuration (stored in
                        ~/.azkabanrc)
  --azkaban-url AZKABAN_URL
  --local               Build zip instead of upload.
  --global-props-file GLOBAL_PROPS_FILE
                        Yaml file defining properties shared by all workflows
                        in scope.
```