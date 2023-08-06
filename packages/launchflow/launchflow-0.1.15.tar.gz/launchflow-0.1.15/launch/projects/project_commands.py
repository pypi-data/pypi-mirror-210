from typing import Optional

import requests
import typer

from launch import constants
from launch.utils import get_account_id, print_response
from launch.auth import cache
from launch.projects import project_helper

app = typer.Typer()

EXPAND_HELP = ('Show all resources below projects (deployments)')


@app.command(help='List projects for an account')
def list(
    account_id: Optional[str] = constants.ACCOUNT_OPTION,
    expand: bool = typer.Option(False, '--expand', '-e', help=EXPAND_HELP),
    running: bool = constants.EXPAND_RUNNING_OPTION,
    launchflow_server_address: str = constants.LAUNCHFLOW_SERVER_ADDRESS_OPTION
):
    creds = cache.get_user_creds(launchflow_server_address)
    account_id = get_account_id(account_id)
    response = project_helper.list_projects(
        account_id=account_id,
        launchflow_server_address=launchflow_server_address,
        creds=creds,
        running=running,
        expand=expand)

    print_response('Projects', response)


@app.command(help='Create a project in an account')
def create(
    display_name: str = typer.Option(..., help='Display name of the project'),
    account_id: Optional[str] = constants.ACCOUNT_OPTION,
    launchflow_server_address: str = constants.LAUNCHFLOW_SERVER_ADDRESS_OPTION
):
    creds = cache.get_user_creds(launchflow_server_address)
    account_id = get_account_id(account_id)
    response = requests.post(
        f'{launchflow_server_address}/projects/create',
        json={
            'account_id': account_id,
            'display_name': display_name
        },
        headers={'Authorization': f'Bearer {creds.id_token}'})
    if response.status_code != 200:
        print(f'Failed to create project: {response.content.decode()}')
        return

    print_response('Project', response)


if __name__ == "__main__":
    app()
