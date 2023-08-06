from typing import Any, Dict

import requests
import typer


def list_deployments(
    project_id: str,
    launchflow_server_address: str,
    creds,
    running: bool,
) -> Dict[str, Any]:
    response = requests.post(
        f'{launchflow_server_address}/deployments/list',
        json={
            'project_id': project_id,
            'running': running
        },
        headers={'Authorization': f'Bearer {creds.id_token}'})
    if response.status_code != 200:
        typer.echo(f'Failed to list deployments: {response.content.decode()}')
        raise typer.Exit(1)
    return response.json()
