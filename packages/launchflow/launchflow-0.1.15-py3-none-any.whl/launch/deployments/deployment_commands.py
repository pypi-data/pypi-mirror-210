import asyncio
import logging
import os
import tempfile
import zipfile
from asyncio import run as aiorun
from typing import List, Optional

import typer

from launch import constants, utils
from launch.auth import cache
from launch.deployments import local_utils, deployments_helper, remote_utils

app = typer.Typer()

MODULE_HELP_TEXT = 'whether or not to run the python entry point as a module. e.g. python -m flow'  # noqa: E501
WORKING_DIR_HELP_TEXT = 'The working directory for your flow. Defaults to your current directory. This can be used if you need to include your working directory files with your executable.'  # noqa: E501
REQUIREMENTS_HELP_TEXT = 'The requirements.txt file containing requirements for your flow.'  # noqa: E501
STREAM_DEPLOYMENT_LOGS_HELP_TEXT = 'Whether or not to stream the deployment logs after submission.'  # noqa: E501
STREAM_TO_EXTENSION_HELP_TEXT = 'Whether or not to stream the deployment logs to the extension.'  # noqa: E501


@app.command()
def runtime():
    if local_utils.local_runtime_is_initialized():
        local_utils.shutdown_local_runtime_environment()

    local_utils.initialize_local_runtime_environment_and_block()


@app.command()
def submit(
    entrypoint: str = typer.Argument(
        ..., help='The python file or module for your BuildFlow node.'),
    local: bool = constants.LOCAL_OPTION,
    account_id: Optional[str] = constants.ACCOUNT_OPTION,
    project_id: Optional[str] = constants.PROJECT_OPTION,
    module: bool = typer.Option(False, '-m', help=MODULE_HELP_TEXT),
    working_dir: str = typer.Option('.', help=WORKING_DIR_HELP_TEXT),
    requirements_file: str = typer.Option('', help=REQUIREMENTS_HELP_TEXT),
    stream_deployment_logs: bool = typer.Option(
        default=False, help=STREAM_DEPLOYMENT_LOGS_HELP_TEXT),
    stream_to_extension: bool = typer.Option(
        default=False, help=STREAM_TO_EXTENSION_HELP_TEXT, hidden=True),
    extension_server_address: str = constants.EXTENSION_SERVER_ADDRESS_OPTION,
    launchflow_server_address: str = constants.
    LAUNCHFLOW_SERVER_ADDRESS_OPTION,
    bearer_token: str = constants.BEARER_TOKEN_OPTION,
):
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

    if not local:
        account_id = utils.get_account_id(account_id)
        if all([account_id is None, project_id is None]):
            typer.echo('You must specify an accountor project to run '
                       'this deployment remotely.')
            raise typer.Exit(1)

    if module:
        entrypoint = f'-m {entrypoint}'
    if working_dir:
        # Expand the full path so users can use relative paths.
        working_dir = os.path.abspath(working_dir)
    if requirements_file:
        requirements_file = os.path.abspath(requirements_file)

    # If we are running in local mode, we need to initialize the local runtime
    if local:
        if not local_utils.local_runtime_is_initialized():
            local_utils.initialize_local_runtime_environment()

        deployment_id = local_utils.submit_deployment_to_ray_cluster(
            entrypoint=f'python {entrypoint}',
            working_dir=working_dir,
            requirements_file=requirements_file)

    if not local:
        if not bearer_token:
            creds = cache.get_user_creds(launchflow_server_address)
            bearer_token = creds.id_token

        if working_dir or requirements_file:
            try:
                _, tf = tempfile.mkstemp(suffix='.zip')
                with zipfile.ZipFile(tf, mode='w') as zf:
                    if working_dir:
                        remote_utils.zipdir(working_dir, zf, requirements_file)
                    if requirements_file:
                        zf.write(requirements_file, 'requirements.txt')
                deployment_id = remote_utils.send_deploy_request(
                    server_address=launchflow_server_address,
                    zip_file=tf,
                    entry_point=entrypoint,
                    account_id=account_id,
                    project_id=project_id,
                    has_requirements=True,
                    bearer_token=bearer_token)
            finally:
                os.remove(tf)
        else:
            deployment_id = remote_utils.send_deploy_request(
                server_address=launchflow_server_address,
                zip_file=None,
                entry_point=entrypoint,
                account_id=account_id,
                project_id=project_id,
                has_requirements=False,
                bearer_token=bearer_token)

    async_tasks: List[asyncio.Task] = []
    loop = None
    if stream_deployment_logs:
        if loop is None:
            loop = asyncio.new_event_loop()
        if local:
            async_tasks.append(
                loop.create_task(
                    local_utils.stream_deployment_logs_async(deployment_id)))
        else:
            async_tasks.append(
                loop.create_task(
                    remote_utils.stream_deployment_logs(
                        deployment_id, launchflow_server_address, bearer_token,
                        extension_server_address)))

    if stream_to_extension:
        if extension_server_address is None:
            raise ValueError(
                'You must provide an extension server address to stream '
                'to the extension.')
        if loop is None:
            loop = asyncio.new_event_loop()
        if local:
            async_tasks.append(
                loop.create_task(
                    local_utils.stream_deployment_info_async(
                        deployment_id, extension_server_address)))
        else:
            async_tasks.append(
                loop.create_task(
                    remote_utils.stream_deployment_info(
                        deployment_id, launchflow_server_address, bearer_token,
                        extension_server_address)))

    if loop is not None:
        try:
            loop.run_until_complete(asyncio.wait(async_tasks))
        except KeyboardInterrupt:
            print('Interrupt received. Shutting down tasks...')
            for task in async_tasks:
                task.cancel()
        finally:
            loop.close()


@app.command(help='Stream info from a running deployment.')
def stream(
    deployment_id: str = typer.Argument(
        ..., help='The deployment id to stream info for.'),
    local: bool = constants.LOCAL_OPTION,
    extension_server_address: str = constants.EXTENSION_SERVER_ADDRESS_OPTION,
    launchflow_server_address: str = constants.
    LAUNCHFLOW_SERVER_ADDRESS_OPTION,
    bearer_token: str = constants.BEARER_TOKEN_OPTION,
):
    async_tasks: List[asyncio.Task] = []
    loop = asyncio.new_event_loop()
    if local:
        async_tasks.append(
            loop.create_task(
                local_utils.stream_deployment_logs_async(deployment_id)))
        async_tasks.append(
            loop.create_task(
                local_utils.stream_deployment_info_async(
                    deployment_id, extension_server_address)))
    else:
        async_tasks.append(
            loop.create_task(
                remote_utils.stream_deployment_logs(deployment_id,
                                                    launchflow_server_address,
                                                    bearer_token,
                                                    extension_server_address)))
        async_tasks.append(
            loop.create_task(
                remote_utils.stream_deployment_info(deployment_id,
                                                    launchflow_server_address,
                                                    bearer_token,
                                                    extension_server_address)))

    try:
        loop.run_until_complete(asyncio.wait(async_tasks))
    except KeyboardInterrupt:
        print('Interrupt received. Shutting down tasks...')
        for task in async_tasks:
            task.cancel()
    finally:
        loop.close()


@app.command(help='Ping info for a list of deployments.')
def ping(
    deployment_ids: List[str] = typer.Argument(
        ..., help='The deployment ids to fetch info for.'),
    local: bool = constants.LOCAL_OPTION,
    extension_server_address: str = constants.EXTENSION_SERVER_ADDRESS_OPTION,
    launchflow_server_address: str = constants.
    LAUNCHFLOW_SERVER_ADDRESS_OPTION,
    bearer_token: str = constants.BEARER_TOKEN_OPTION,
):
    if local:
        local_utils.ping_deployment_info(deployment_ids,
                                         extension_server_address)
    else:
        raise NotImplementedError(
            'Pinging remote deployments is not yet supported.')


@app.command(help='Stop a running deployment.')
def stop(
    deployment_id: str = typer.Argument(...,
                                        help='The deployment id to stop.'),
    local: bool = constants.LOCAL_OPTION,
    launchflow_server_address: str = constants.
    LAUNCHFLOW_SERVER_ADDRESS_OPTION,
    bearer_token: str = constants.BEARER_TOKEN_OPTION,
):
    if local:
        local_utils.stop_deployment(deployment_id)
    else:
        remote_utils.stop_deployment_cli(deployment_id,
                                         launchflow_server_address,
                                         bearer_token)


@app.command(help='Drain a running deployment.')
def drain(
    deployment_id: str = typer.Argument(...,
                                        help='The deployment id to drain.'),
    local: bool = constants.LOCAL_OPTION,
    launchflow_server_address: str = constants.
    LAUNCHFLOW_SERVER_ADDRESS_OPTION,
    bearer_token: str = constants.BEARER_TOKEN_OPTION,
):
    if local:
        local_utils.drain_deployment(deployment_id)
    else:
        remote_utils.drain_deployment_cli(deployment_id,
                                          launchflow_server_address,
                                          bearer_token)


@app.command(help='Attach to a deployment.')
def attach(
    deployment_id: str = typer.Argument(
        ..., help='The deployment id to attach to.'),
    local: bool = constants.LOCAL_OPTION,
    launchflow_server_address: str = constants.LAUNCHFLOW_SERVER_ADDRESS_OPTION
):
    if local:
        raise NotImplementedError(
            'Attaching to local deployments is not yet supported.')
    else:
        aiorun(
            remote_utils.run_console_ui(deployment_id,
                                        launchflow_server_address))


@app.command(help='List deployments for a project.')
def list(
    project_id: Optional[str] = typer.Option(
        ..., help='The project to list deployments for.'),
    running: bool = typer.Option(
        False,
        '--running',
        '-r',
        help='If --running is set only running deployments will be returned.'),
    launchflow_server_address: str = constants.
    LAUNCHFLOW_SERVER_ADDRESS_OPTION,
):
    creds = cache.get_user_creds(launchflow_server_address)
    response = deployments_helper.list_deployments(
        project_id=project_id,
        running=running,
        creds=creds,
        launchflow_server_address=launchflow_server_address)

    utils.print_response('Deployments', response)


@app.command(help='Get logs for a deployment.')
def get_logs(
    deployment_id: str = typer.Argument(
        ..., help='The deployment id to attach to.'),
    launchflow_server_address: str = constants.LAUNCHFLOW_SERVER_ADDRESS_OPTION
):
    remote_utils.get_logs(deployment_id, launchflow_server_address)


if __name__ == "__main__":
    app()
