import json
import os

import urwid
import websockets

from launch.auth import cache
from launch.deployments import urwid_color

test = '?[2m?[36m(ASDFASDF)?[0m'

PALETTE = [
    ('normal', '', ''),
    ('header', 'bold,light magenta', ''),
    ('bold', 'bold', ''),
    ('highlight', 'black', 'dark blue'),
]

urwid.set_encoding('UTF-8')

logs_list = urwid.SimpleFocusListWalker([])
logs_widget = urwid.AttrMap(urwid.ListBox(logs_list), 'body')

status_header = urwid.AttrMap(urwid.Text('Status'), 'bold', 'bold')
status_data = urwid.Text('N/A')


def is_running() -> bool:
    status_text, _ = status_data.get_text()
    return status_text not in ['SUCCEEDED', 'STOPPED', 'FAILED']


num_replicas_header = urwid.AttrMap(urwid.Text('Num Replicas'), 'bold', 'bold')
num_replicas_data = urwid.Text('N/A')

throughput_header = urwid.AttrMap(urwid.Text('Throughput'), 'bold', 'bold')
throughput_data = urwid.Text('N/A')

proc_latency_header = urwid.AttrMap(urwid.Text('Processor Latency'), 'bold',
                                    'bold')
proc_latency_data = urwid.Text('N/A')

deployment_info_widget = urwid.Columns([
    urwid.Pile([status_header, urwid.Divider('-'), status_data]),
    urwid.Pile([num_replicas_header,
                urwid.Divider('-'), num_replicas_data]),
    urwid.Pile([throughput_header,
                urwid.Divider('-'), throughput_data]),
    urwid.Pile([proc_latency_header,
                urwid.Divider('-'), proc_latency_data])
])

drain_button = urwid.Button('Drain Deployment')
stop_button = urwid.Button('Stop Deployment')
status_message_widget = urwid.Text('')


def get_main_frame(deployment_id: int):
    header_widget = urwid.Pile([
        urwid.AttrMap(
            urwid.Text(f'Deployment ID: {deployment_id}', align='center'),
            'header', 'bold'),
        urwid.Divider('-'),
        deployment_info_widget,
        urwid.Divider(),
        urwid.Divider(),
        urwid.AttrMap(urwid.Text('Logs', align='center'), 'header', 'bold'),
        urwid.Divider('-'),
    ])

    footer_widget = urwid.Pile([
        urwid.Divider(),
        urwid.AttrMap(
            urwid.Text('Deployment Operations', align='center'),
            'header',
            'bold',
        ),
        urwid.Divider('-'),
        urwid.Divider(),
        urwid.GridFlow([drain_button, stop_button],
                       cell_width=15,
                       h_sep=10,
                       v_sep=1,
                       align='center'),
        urwid.Divider(),
        status_message_widget,
    ])

    return urwid.Frame(header=header_widget,
                       body=logs_widget,
                       footer=footer_widget)


def update_deployment_info(data):
    try:
        json_data = json.loads(data)
        status_data.set_text(str(json_data['deployment_status']))
        status_message = json_data['status_message']
        if status_message is not None:
            status_message_widget.set_text(str(json_data['status_message']))
        else:
            status_message_widget.set_text('')
        metrics = json_data['latest_metrics']
        if 'num_replicas' in metrics:
            num_replicas_data.set_text(str(metrics['num_replicas']))
        if 'throughput' in metrics:
            throughput_data.set_text(str(metrics['throughput']))
        if 'processor_latency' in metrics:
            proc_latency_data.set_text(str(metrics['processor_latency']))
    except Exception:
        pass


async def get_deployment_info(file_descriptor, deployment_id, server_address):
    creds = cache.get_user_creds(server_address)
    ws_endpoint = server_address.replace('http://', 'ws://').replace(
        'https://', 'wss://')
    if ws_endpoint.endswith('/'):
        ws_endpoint = ws_endpoint[:-1]
    try:
        async for ws in websockets.connect(
                f'{ws_endpoint}/deployments/info?deployment_id={deployment_id}',  # noqa
                open_timeout=1,
                extra_headers={'Authorization': f'Bearer {creds.id_token}'}):
            while True:
                data = await ws.recv()
                os.write(file_descriptor, data.encode())
                if not is_running():
                    await ws.close()
                    return
    except Exception as e:
        status_message_widget.set_text(f'Get deployment info error: {str(e)}')


async def get_logs(deployment_id, server_address):
    creds = cache.get_user_creds(server_address)
    ws_endpoint = server_address.replace('http://', 'ws://').replace(
        'https://', 'wss://')
    if ws_endpoint.endswith('/'):
        ws_endpoint = ws_endpoint[:-1]
    try:
        async for ws in websockets.connect(
                f'{ws_endpoint}/deployments/tail_logs?deployment_id={deployment_id}',  # noqa
                extra_headers={'Authorization': f'Bearer {creds.id_token}'}):
            while True:
                try:
                    data = await ws.recv()
                except Exception as e:
                    status_message_widget.set_text(f'Get logs error: {str(e)}')
                    continue
                data = data.split('\n')
                data = [
                    urwid_color.translate_text_for_urwid(line) for line in data
                ]
                data = [d for d in data if d]
                if not data:
                    continue
                positions = len(logs_list.positions())
                if positions:
                    _, focus_pos = logs_list.get_focus()
                    if focus_pos == len(logs_list.positions()) - 1:
                        new_pos = focus_pos + len(data)
                    else:
                        new_pos = focus_pos
                else:
                    new_pos = len(data) - 1
                logs_widgets = [urwid.Text(line) for line in data]
                logs_list.extend(logs_widgets)
                logs_list.set_focus(new_pos)
                if not is_running():
                    await ws.close()
                    return
    except Exception as e:
        status_message_widget.set_text(f'Get logs error: {str(e)}')
