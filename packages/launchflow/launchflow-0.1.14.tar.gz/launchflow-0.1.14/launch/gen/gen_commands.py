import requests
import typer

from launch import constants
from launch.gen import utils

# from launch.session_state import LaunchFlowSession

app = typer.Typer()


@app.command()
def inspect(
    buildflow_file_path: str,
    extension_server_address: str = constants.EXTENSION_SERVER_ADDRESS_OPTION,
):
    result = utils.inspect(buildflow_file_path)
    if extension_server_address:
        result = requests.post(extension_server_address,
                               json={
                                   'source': result.source,
                                   'sink': result.sink,
                               })
    else:
        print(result)


@app.command()
def schemas(buildflow_file_path: str):
    raise NotImplementedError


@app.command()
def tests(buildflow_file_path: str):
    raise NotImplementedError


if __name__ == "__main__":
    app()
