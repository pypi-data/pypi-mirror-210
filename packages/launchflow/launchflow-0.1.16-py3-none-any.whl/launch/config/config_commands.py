import typer

from launch import constants
from launch.config.config import LaunchFlowConfig

app = typer.Typer()


@app.command()
def set_default_account(
    account_id: str = typer.Argument(...,
                                     help='The account ID to set as default'),
    server_address: str = constants.LAUNCHFLOW_SERVER_ADDRESS_OPTION,
):
    config = LaunchFlowConfig.load(server_address)
    config.default_account_id = account_id
    config.write()


@app.command()
def get():
    config = LaunchFlowConfig.load()
    print('Launchflow Config')
    print('-----------------')
    print(f'    default account ID: {config.default_account_id}')
