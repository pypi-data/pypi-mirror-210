import os
import signal
import subprocess
from sys import platform
from dataclasses import dataclass
import json
from pkg_resources import resource_filename
from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

from launch.prometheus import queries

RAY_CLUSTER_ADDRESS = 'http://127.0.0.1:8265'


@dataclass
class DeploymentInfo:
    deployment_id: str
    status: str
    metrics: Dict[str, str]


app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.on_event("startup")
def startup():
    prom_dir = resource_filename('launch', 'prometheus')
    if platform == "linux" or platform == "linux2":
        executable = 'linux/prometheus'
    elif platform == "darwin":
        executable = 'mac/prometheus'
    else:
        raise ValueError(
            f'launch CLI is not supported for platform: {platform}')
    subprocess.Popen(
        f'./{executable} --config.file=/tmp/ray/session_latest/metrics/prometheus/prometheus.yml',  # noqa
        cwd=f'{prom_dir}/.',
        shell=True)


@app.get('/')
async def get_deployment(deployment_id: str):
    resp = requests.get(f"http://127.0.0.1:8265/api/jobs/{deployment_id}")
    ray_info = json.loads(resp.text)
    deployment_info = {
        'id': ray_info['submission_id'],
        'runtime': 'REMOTE',
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


@app.get('/drain')
async def drain_deployment(deployment_id: str):
    deployment_info = await get_deployment(deployment_id)
    pid = deployment_info['driver_info']['pid']
    os.kill(int(pid), signal.SIGTERM)
    return True
