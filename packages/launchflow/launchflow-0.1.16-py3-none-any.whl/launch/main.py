import typer

from launch.accounts import account_commands
from launch.auth import auth_commands
from launch.config import config_commands
from launch.gen import gen_commands
from launch.deployments import deployment_commands
from launch.projects import project_commands

app = typer.Typer()
app.add_typer(auth_commands.app,
              name='auth',
              help='Commands for authenticating with LaunchFlow')
app.add_typer(account_commands.app,
              name='accounts',
              help='Account commands for managing accounts')
app.add_typer(config_commands.app,
              name='config',
              help='Commands for managing CLI configuration')
app.add_typer(gen_commands.app,
              name='gen',
              help='Commands for generating BuildFlow and LaunchFlow files.')
app.add_typer(deployment_commands.app,
              name='deployments',
              help='Commands for managing LaunchFlow deployments')
app.add_typer(project_commands.app,
              name='projects',
              help='Commands for managing LaunchFlow projects')


def main():
    app()


if __name__ == "__main__":
    main()
