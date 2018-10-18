# Workflow #

[AzkabanCLI](https://github.com/mtth/azkaban) wrapper for easier workflow definition.

### Installation ###

`pip install git+https://git@github.com/vanaoff/workflow.git@master`

### Usage ###

Workflow definition example could be found in [`./example`](https://github.com/vanaoff/workflow/tree/master/example).
Workflow could be built and uploaded by executing 
```bash
python -m workflow --definition project.yml --extra-properties extra.yml --files-to-upload files-i-need --azkaban-url https://user:P455w0rd@azkaban.domain.io:443
```
or equivalently
```bash
python -m workflow -d project.yml -e extra.yml -f directory-with-needed-files -u https://user:P455w0rd@azkaban.domain.io:443
```

It's convenient to create `~/.azkabanrc` file in your home directory with following structure:
```ini
[alias.one]
url = https://user:P455w0rd@azkaban.domain.io:443

[alias.two]
url = https://different-user:P455w0rd@azkaban.domain.io:443
```

Once it's available, it's possible to reference azkaban connection url with `--alias`, resp. `-a`, argument, so 
previous example will become
```bash
python -m workflow -d project.yml -e extra.yml -f files-i-need -a one 
``` 

For local build use `--local/-l` switch.

All options could be printed with `python -m workflow -h`.
