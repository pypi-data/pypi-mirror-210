import asyncio
import json
import os
import subprocess
import sys
from typing import Optional

import httpx
import requests
import typer
import urwid
import websockets

from launch.auth import cache
from launch.deployments import console_ui
from launch.session_state import LastDeploymentInfo, LaunchFlowSession

RAY_CLUSTER_ADDRESS = 'http://127.0.0.1:8265'


def zipdir(path, ziph, requirements_path: str):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            full_file_path = os.path.join(root, file)
            if full_file_path == requirements_path:
                # No need to add requirements file we will do this below.
                continue
            ziph.write(
                full_file_path,
                os.path.relpath(full_file_path, os.path.join(path, '.')))


def _get_ray_version():
    output = subprocess.check_output('pip show ray | grep Version', shell=True)
    str_output = output.decode()
    return str_output.split(' ')[1].strip()


def send_deploy_request(
    server_address: str,
    zip_file: Optional[str],
    entry_point: str,
    account_id: Optional[int],
    project_id: Optional[int],
    has_requirements: bool,
    bearer_token: str,
) -> str:
    version = sys.version_info
    python_version = f'{version.major}.{version.minor}'

    if zip_file is not None:
        files = {
            'zip_file': ('working_dir.zip', open(zip_file,
                                                 'rb'), 'application/zip')
        }
    else:
        files = None
    data = {
        'account_id': account_id,
        'project_id': project_id,
        'entry_point': entry_point,
        'python_version': python_version,
        'ray_version': _get_ray_version()
    }
    if has_requirements:
        data['requirements_file_relative_path'] = './requirements.txt'
    client = httpx.Client(http2=True)
    response = client.post(
        f'{server_address}/deployments/create',
        headers={'Authorization': f'Bearer {bearer_token}'},
        files=files,
        data=data,
        timeout=60,
    )
    state = LaunchFlowSession.load()
    if response.status_code != 200:
        json_content = json.loads(response.content.decode())
        state.last_deployment_info = LastDeploymentInfo(
            deployment_id=None,
            deployment_create_http_status=response.status_code)
        state.write()
        typer.echo(f'Remote run failed: {json_content["detail"]}.')
        raise typer.Exit(1)
    output = response.json()
    deployment_id = output['id']
    print('Remote run launched succesfully. To track progress run:')
    print()
    print('    To attach to deployment run: ')
    print(f'        launch deployments attach {deployment_id}')
    print('    To drain deployment run:')
    print(f'        launch deployments drain {deployment_id}')
    print('    To stop deployment run:')
    print(f'        launch deployments stop {deployment_id}')
    state.last_deployment_info = LastDeploymentInfo(
        deployment_id=output['id'],
        deployment_create_http_status=response.status_code)
    state.write()
    return output['id']


async def stream_deployment_info(
    deployment_id: str,
    launchflow_server_address: str,
    bearer_token: Optional[str],
    extension_server_address: str,
):
    if bearer_token is None:
        creds = cache.get_user_creds(launchflow_server_address)
        bearer_token = creds.id_token

    ws_endpoint = launchflow_server_address.replace('http://',
                                                    'ws://').replace(
                                                        'https://', 'wss://')
    if ws_endpoint.endswith('/'):
        ws_endpoint = ws_endpoint[:-1]
    try:
        async for ws in websockets.connect(
                f'{ws_endpoint}/deployments/info?deployment_id={deployment_id}',  # noqa
                open_timeout=1,
                extra_headers={'Authorization': f'Bearer {bearer_token}'}):
            while True:
                data = await ws.recv()
                deployment_info = json.loads(data)
                deployment_info['runtime'] = 'REMOTE'
                requests.post(extension_server_address, json=deployment_info)
    except Exception as e:
        typer.echo(str(e))
        raise typer.Exit(1)


async def stream_deployment_logs(
    deployment_id: str,
    launchflow_server_address: str,
    bearer_token: Optional[str],
    extension_server_address: str,
):
    if bearer_token is None:
        creds = cache.get_user_creds(launchflow_server_address)
        bearer_token = creds.id_token

    ws_endpoint = launchflow_server_address.replace('http://',
                                                    'ws://').replace(
                                                        'https://', 'wss://')
    if ws_endpoint.endswith('/'):
        ws_endpoint = ws_endpoint[:-1]
    try:
        async for ws in websockets.connect(
                f'{ws_endpoint}/deployments/tail_logs?deployment_id={deployment_id}',  # noqa
                open_timeout=1,
                extra_headers={'Authorization': f'Bearer {bearer_token}'}):
            while True:
                data = await ws.recv()
                print(data)
                # requests.post(extension_server_address, json=data)
    except Exception as e:
        typer.echo(str(e))
        raise typer.Exit(1)


def _stop_deployment(deployment_id: str,
                     server_address: str,
                     bearer_token: Optional[str] = None):
    if not bearer_token:
        creds = cache.get_user_creds(server_address)
        bearer_token = creds.id_token
    response = requests.post(
        f'{server_address}/deployments/stop',
        headers={'Authorization': f'Bearer {bearer_token}'},
        json={'deployment_id': deployment_id})
    return response


def stop_deployment_cli(deployment_id: str,
                        server_address: str,
                        bearer_token: Optional[str] = None):
    response = _stop_deployment(deployment_id, server_address, bearer_token)
    if response.status_code != 200:
        print(f'Failed to stop deployment error: {response.content.decode()}')
        return
    print('Deployment is now stopping.')


def stop_deployment_urwid(deployment_id: str, server_address: str, button):
    response = _stop_deployment(deployment_id, server_address)
    if response.status_code != 200:
        try:
            json_error = response.json()
            console_ui.status_message_widget.set_text(json_error['detail'])
        except json.JSONDecodeError:
            console_ui.status_message_widget.set_text(
                f'Stop failed: {response.content}')


def _drain_deployment(deployment_id: str,
                      server_address: str,
                      bearer_token: Optional[str] = None):
    if not bearer_token:
        creds = cache.get_user_creds(server_address)
        bearer_token = creds.id_token
    response = requests.post(
        f'{server_address}/deployments/drain',
        headers={'Authorization': f'Bearer {bearer_token}'},
        json={'deployment_id': deployment_id})
    return response


def drain_deployment_cli(deployment_id: str,
                         server_address: str,
                         bearer_token: Optional[str] = None):
    response = _drain_deployment(deployment_id, server_address, bearer_token)
    if response.status_code != 200:
        print(f'Failed to drain deployment error: {response.content.decode()}')
        return
    print('Deployment is now draining.')


def drain_deployment_urwid(deployment_id: str, server_address: str, button):
    response = _drain_deployment(deployment_id, server_address)
    if response.status_code != 200:
        try:
            json_error = response.json()
            console_ui.status_message_widget.set_text(json_error['detail'])
        except json.JSONDecodeError:
            console_ui.status_message_widget.set_text(
                f'Drain failed: {response.content}')


async def run_console_ui(deployment_id: int, server_address: str):
    aloop = asyncio.get_event_loop()
    import nest_asyncio
    nest_asyncio.apply(aloop)
    ev_loop = urwid.AsyncioEventLoop(loop=aloop)
    loop = urwid.MainLoop(console_ui.get_main_frame(deployment_id),
                          palette=console_ui.PALETTE,
                          event_loop=ev_loop)

    update_deployment_fd = loop.watch_pipe(console_ui.update_deployment_info)
    aloop.create_task(
        console_ui.get_deployment_info(update_deployment_fd, deployment_id,
                                       server_address))
    aloop.create_task(console_ui.get_logs(deployment_id, server_address))

    urwid.connect_signal(obj=console_ui.drain_button,
                         name='click',
                         callback=drain_deployment_urwid,
                         user_args=[deployment_id, server_address])
    urwid.connect_signal(obj=console_ui.stop_button,
                         name='click',
                         callback=stop_deployment_urwid,
                         user_args=[deployment_id, server_address])

    loop.run()


def get_logs(deployment_id: str, server_address: str):
    creds = cache.get_user_creds(server_address)
    response = requests.post(
        f'{server_address}/deployments/get_logs',
        headers={'Authorization': f'Bearer {creds.id_token}'},
        json={'deployment_id': deployment_id})
    if response.status_code != 200:
        typer.echo(f'Failed to get logs: {response.content.decode()}')
        raise typer.Exit(1)
    log_lines = response.json()
    print('\n'.join(log_lines))
