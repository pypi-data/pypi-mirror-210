import os

import typer

DEFAULT_LAUNCHFLOW_SERVER = 'https://apis.launchflow.com'
DEFAULT_EXTENSION_SERVER = 'http://localhost:3571'

ADD_READER_HELP_TEXT = 'Adds a reader to a{}'
REMOVE_READER_HELP_TEXT = 'Removes a reader from a{}'
ADD_WRITER_HELP_TEXT = 'Adds a writer to a{}'
REMOVE_WRITER_HELP_TEXT = 'Removes a writer from a{}'
GET_HELP_TEXT = 'Prints details about a{}'
CREATE_HELP_TEXT = 'Create a{}'
NAME_HELP_TEXT = 'The name of the {}'
PERMISSION_HELP_TEST = 'The permission to perform operations on. Should be of the format: (user|serviceAccount|domain):(email|domain)'  # noqa: E501

BEARER_TOKEN_OPTION = typer.Option(default=None, hidden=True)

LAUNCHFLOW_SERVER_ADDRESS_OPTION = typer.Option(
    default=DEFAULT_LAUNCHFLOW_SERVER, hidden=True)
EXTENSION_SERVER_ADDRESS_OPTION = typer.Option(
    default=DEFAULT_EXTENSION_SERVER, hidden=True)
LOCAL_OPTION = typer.Option(
    default=False,
    help='Whether or not to run this operation on a local deployment.')
PERMISSION_ARG = typer.Argument(...,
                                help=PERMISSION_HELP_TEST,
                                show_default=False)

_ACCOUNT_HELP = (
    'The name of the account to apply the operation on. If this is unset we '
    'will use the default account set in the config. Should be of the format:'
    '`account_XXXXX`')
ACCOUNT_OPTION = typer.Option(default=None, help=_ACCOUNT_HELP)

_PROJECT_HELP = (
    'The name of the project to apply the operation on. If this is unset we '
    'will use the default project set in the config. Should be of the format:'
    '`project_XXXXX`')
PROJECT_OPTION = typer.Option(default=None, help=_PROJECT_HELP)

CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.config', 'launchflow')
EXPAND_RUNNING_OPTION = typer.Option(
    False,
    '--running',
    '-r',
    help=('Only to include running deployments in expansion. '
          'NOTE: this only applies if you pass the --expand or -e flag'))
