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
  -h, --help            show this help message and exit
  -p PROJECT, --project PROJECT
                        Project to be uploaded.
  -d PROJECTS, --projects PROJECTS
                        Projects directory to be uploaded.
  -a ALIAS, --alias ALIAS
                        Alias for azkaban configuration (stored in
                        ~/.azkabanrc)
  -u URL, --url URL     Azkaban url.
  -l, --local           Build zip instead of upload.
```