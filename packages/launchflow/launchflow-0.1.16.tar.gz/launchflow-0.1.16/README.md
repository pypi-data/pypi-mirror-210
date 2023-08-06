# Launchflow CLI

LaunchFlow CLI.

This CLI allows you to use our VS code extension with [BuildFlow](https://www.buildflow.dev) to easily
test your flows locally.

Coming soon this CLI will also allow you to deploy your BuildFlow deployments to
LaunchFlow and manage your remote deployments.

## Help

```
$ launch --help

 Usage: launch [OPTIONS] FLOW

 Launch your BuildFlow node.

╭─ Arguments ─────────────────────────────────────────────────────────────────────────────╮
│ *    flow      TEXT  The python file or module for your flow node. [default: None]      │
│                      [required]                                                         │
╰─────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ───────────────────────────────────────────────────────────────────────────────╮
│                       -m                      whether or not to run the python entry    │
│                                               point as a module. e.g. python -m flow    │
│ --working-dir                           TEXT  The working directory for your flow.      │
│                                               Defaults to your current directory. This  │
│                                               can be used if you need to include your   │
│                                               working directory files with your         │
│                                               executable.                               │
│ --requirements-file                     TEXT  The requirements.txt file containing      │
│                                               requirements for your flow.               │
│ --name                                  TEXT  The name of this flow when deploying to   │
│                                               launchflow.                               │
│ --local                   --no-local          Whether or not to run in local mode.      │
│                                               [default: no-local]                       │
│ --install-completion                          Install completion for the current shell. │
│ --show-completion                             Show completion for the current shell, to │
│                                               copy it or customize the installation.    │
│ --help                                        Show this message and exit.               │
╰─────────────────────────────────────────────────────────────────────────────────────────╯
```

## Example usage

### Local Runs

Launch file:

```
launch --local flow.py
```

Launch module:

```
launch --local -m flow.main
```

Launch including working directory:

```
launch --local --working-dir=./ -m flow.main
```

Launch including working directory and extra requirements:

```
launch --local --working-dir=./ --requirements-file=./requirements.txt -m flow.main
```

### Remote Runs

Coming soon!
