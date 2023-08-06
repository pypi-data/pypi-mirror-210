import typer

from launch import constants
from launch.auth import flow as auth_flow
from launch.auth import cache

app = typer.Typer()


@app.command(help='Authenticate with launchflow.')
def login(server_address: str = constants.LAUNCHFLOW_SERVER_ADDRESS_OPTION):
    auth_flow.web_server_flow(server_address)


@app.command(help='Logout from launchflow.')
def logout():
    cache.logout()
