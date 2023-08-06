import aiohttp
import asyncio
import json
import socket
import subprocess
import sys
from sys import platform
from typing import List, Optional
import atexit
import requests
from pkg_resources import resource_filename

from launch.prometheus import queries

RAY_CLUSTER_ADDRESS = 'http://127.0.0.1:8265'


def _port_is_open(port: str, host: str = 'http://localhost', timeout=1):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
    except Exception:
        return False
    else:
        sock.close()
        return True


def local_runtime_is_initialized():
    for port in ['8265', '9090']:
        if not _port_is_open(port):
            return False
    return True


def _get_prometheus_dir():
    try:
        # This is the directory pyinstaller uses
        return sys._MEIPASS
    except Exception:
        return resource_filename('launch', 'prometheus')


def initialize_local_runtime_environment_and_block():
    # TODO: should include other distributions.
    if platform == "linux" or platform == "linux2":
        executable = 'linux/prometheus'
    elif platform == "darwin":
        executable = 'mac/prometheus'
    else:
        raise ValueError(
            f'launch CLI is not supported for platform: {platform}')

    prom_process = subprocess.Popen(
        f'./{executable} --config.file=/tmp/ray/session_latest/metrics/prometheus/prometheus.yml',  # noqa
        cwd=f'{_get_prometheus_dir()}/.',
        shell=True)
    ray_process = subprocess.Popen('ray start --head --block', shell=True)

    atexit.register(prom_process.terminate)
    atexit.register(ray_process.terminate)
    ray_process.wait()
    print('Environment shutdown.')


def initialize_local_runtime_environment():
    subprocess.run('ray start --head', shell=True)
    # TODO: should include other distributions.
    if platform == "linux" or platform == "linux2":
        executable = 'linux/prometheus'
    elif platform == "darwin":
        executable = 'mac/prometheus'
    else:
        raise ValueError(
            f'launch CLI is not supported for platform: {platform}')
    # TODO: Add better process management for prometheus and ray.
    _ = subprocess.Popen(
        f'./{executable} --config.file=/tmp/ray/session_latest/metrics/prometheus/prometheus.yml',  # noqa
        cwd=f'{_get_prometheus_dir()}/.',
        shell=True)


def shutdown_local_runtime_environment():
    subprocess.run('ray stop', shell=True)
    subprocess.run('fuser -k 9090/tcp', shell=True)


async def stream_deployment_logs_async(
        deployment_id: str, cluster_address: str = RAY_CLUSTER_ADDRESS):
    async with aiohttp.ClientSession() as session:
        ws = await session.ws_connect(
            f"{cluster_address}/api/jobs/{deployment_id}/logs/tail")

        while True:
            msg = await ws.receive()

            if msg.type == aiohttp.WSMsgType.TEXT:
                print(msg.data, end="")
            elif msg.type == aiohttp.WSMsgType.CLOSED:
                break
            elif msg.type == aiohttp.WSMsgType.ERROR:
                pass


def stream_deployment_logs(deployment_id: str,
                           cluster_address: str = RAY_CLUSTER_ADDRESS):
    loop = asyncio.new_event_loop()
    loop.run_until_complete(
        stream_deployment_logs_async(deployment_id, cluster_address))
    loop.close()


def get_deployment_info(deployment_id: str):
    resp = requests.get(f"http://127.0.0.1:8265/api/jobs/{deployment_id}")
    ray_info = json.loads(resp.text)
    deployment_info = {
        'id': ray_info['submission_id'],
        'runtime': 'LOCAL',
        'deployment_status': ray_info['status'],
        'latest_metrics': {
            'throughput': '0',
            'processor_latency': '0',
            'num_replicas': '0',
        }
    }
    if ray_info['status'] in ['RUNNING', 'PENDING']:
        deployment_info['latest_metrics'] = {
            'throughput': queries.throughput(ray_info['job_id']),
            'processor_latency': queries.processor_latency(ray_info['job_id']),
            'num_replicas': queries.num_replicas(ray_info['job_id']),
        }
    return deployment_info


def ping_deployment_info(
    deployment_ids: List[str],
    extension_server_address: Optional[str] = None,
    cluster_address: str = RAY_CLUSTER_ADDRESS,
):
    print(
        f'pinging deployment status for {len(deployment_ids)} deployments...')
    for deployment_id in deployment_ids:
        deployment_info = get_deployment_info(deployment_id)
        print(deployment_info)
        if extension_server_address is not None:
            requests.post(extension_server_address, json=deployment_info)


async def stream_deployment_info_async(
    deployment_id: str,
    extension_server_address: Optional[str] = None,
    cluster_address: str = RAY_CLUSTER_ADDRESS,
):
    print('streaming deployment status...')
    while True:
        deployment_info = get_deployment_info(deployment_id)
        if extension_server_address is not None:
            requests.post(extension_server_address, json=deployment_info)
        if deployment_info['deployment_status'] in [
                'FAILED', 'STOPPED', 'SUCCEEDED'
        ]:
            break
        await asyncio.sleep(3)


def stream_deployment_info(
    deployment_id: str,
    extension_server_address: Optional[str] = None,
    cluster_address: str = RAY_CLUSTER_ADDRESS,
):
    loop = asyncio.new_event_loop()
    loop.run_until_complete(
        stream_deployment_info_async(deployment_id, extension_server_address,
                                     cluster_address))
    loop.close()
