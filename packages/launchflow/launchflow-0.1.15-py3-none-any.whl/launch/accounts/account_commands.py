import requests
import typer

from launch import constants
from launch.auth import cache
from launch.projects import project_helper
from launch.utils import print_response

app = typer.Typer()


@app.command()
def signup(launchflow_server_address: str = constants.
           LAUNCHFLOW_SERVER_ADDRESS_OPTION, ):
    creds = cache.get_user_creds(launchflow_server_address)
    response = requests.post(
        f'{launchflow_server_address}/account/signup',
        headers={'Authorization': f'Bearer {creds.id_token}'})
    if response.status_code != 200:
        print(f'Failed to signup: {response.content.decode()}')
        return

    print_response('Account', response)


EXPAND_HELP = (
    'Show all resources below accounts, includes projects and deployments.')


@app.command()
def list(launchflow_server_address: str = constants.
         LAUNCHFLOW_SERVER_ADDRESS_OPTION,
         expand: bool = typer.Option(False, '--expand', '-e',
                                     help=EXPAND_HELP),
         running: bool = constants.EXPAND_RUNNING_OPTION):
    creds = cache.get_user_creds(launchflow_server_address)
    response = requests.get(
        f'{launchflow_server_address}/account/list',
        headers={'Authorization': f'Bearer {creds.id_token}'})
    if response.status_code != 200:
        typer.echo(f'Failed to list accounts: {response.content.decode()}')
        raise typer.Exit(1)

    response_json = response.json()
    if expand:
        expanded_response = []
        accounts = response_json['accounts']
        for account in accounts:
            project = project_helper.list_projects(
                account_id=account['id'],
                launchflow_server_address=launchflow_server_address,
                expand=True,
                running=running,
                creds=creds)
            account['projects'] = project['projects']
            expanded_response.append(account)
        response_json = {'accounts': expanded_response}

    print_response('Accounts', response_json)
