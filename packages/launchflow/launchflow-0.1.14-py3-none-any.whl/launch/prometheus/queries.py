from typing import Any, Optional

import requests


def _run_query(query: str) -> Optional[Any]:
    # We're pretty wide with this catch cause we don't want our check-ins to
    # fail.
    try:
        response = requests.get('http://localhost:9090/api/v1/query',
                                params={
                                    'query': query
                                }).json()
        result = response.get('data').get('result')
        return result[0].get('value')[1]
    except Exception:
        return 'N/A'


def throughput(ray_job_id: str):
    return _run_query(
        f'rate(ray_num_events_processed{{JobId="{ray_job_id}"}}[1m])')


def num_replicas(ray_job_id: str):
    return _run_query(f'ray_num_replicas{{JobId="{ray_job_id}"}}')


def processor_latency(ray_job_id: str):
    return _run_query(
        f'avg_over_time(ray_process_time{{JobId="{ray_job_id}"}}[1m])')
