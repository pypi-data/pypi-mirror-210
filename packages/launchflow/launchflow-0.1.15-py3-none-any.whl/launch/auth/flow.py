"""Utils for authenticating a user."""

import datetime
import logging
import socket
import wsgiref
import wsgiref.simple_server
from contextlib import closing
from urllib.parse import parse_qs, urlparse

import google.oauth2.credentials
import requests

from launch.auth import cache

_START_PORT = 3570
_END_PORT = 3579
_LOGGER = logging.getLogger(__name__)


def is_port_open(port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        try:
            sock.bind(('localhost', port))
            sock.listen(1)
        except socket.error:
            is_open = False
        else:
            is_open = True
    return is_open


def find_open_port():
    start = _START_PORT
    stop = _END_PORT

    for port in range(start, stop):
        if is_port_open(port):
            return port

    # No open ports found.
    return None


def web_server_flow(
        base_auth_endpoint: str) -> google.oauth2.credentials.Credentials:
    port = find_open_port()
    if port is None:
        raise ValueError(
            f'No valid port between {3569}-{3579} please ensure one of these '
            'ports is open for authentication.')
    wsg_app = _RedirectWSGIApp('Succesfully authenticated with launchflow.')
    wsgiref.simple_server.WSGIServer.allow_reuse_address = False
    local_server = wsgiref.simple_server.make_server(
        'localhost',
        find_open_port(),
        wsg_app,
        handler_class=_WSGIRequestHandler)
    response = requests.get(f'{base_auth_endpoint}/auth/url')
    if response.status_code != 200:
        raise ValueError('Failed to authenticate.')
    auth_url = response.json()['url']
    print('Authenticating with launchflow...')
    # TODO: some reason webbrowser.open wasn't working.
    print(f'Go to the following link in your brower:\n\n\t{auth_url}')
    local_server.handle_request()
    auth_response = wsg_app.last_request_uri
    parsed_url = urlparse(auth_response)
    parsed_query = parse_qs(parsed_url.query)
    code = parsed_query['code'][0]

    response = requests.get(f'{base_auth_endpoint}/auth/token?code={code}')
    if response.status_code != 200:
        raise ValueError(f'Failed to authenticate: {response.content}')

    auth_json = response.json()
    creds = google.oauth2.credentials.Credentials(
        token=auth_json['access_token'],
        refresh_token=auth_json['refresh_token'],
        id_token=auth_json['id_token'],
        scopes=auth_json['scope'],
        expiry=datetime.datetime.utcfromtimestamp(auth_json['expires_at']))
    print('Successfully authenticated.')
    local_server.server_close()
    cache.save_user_creds(creds)


class _WSGIRequestHandler(wsgiref.simple_server.WSGIRequestHandler):
    """Custom WSGIRequestHandler.
    Uses a named logger instead of printing to stderr.
    """

    def log_message(self, format, *args):
        # pylint: disable=redefined-builtin
        # (format is the argument name defined in the superclass.)
        _LOGGER.info(format, *args)


class _RedirectWSGIApp(object):
    """WSGI app to handle the authorization redirect.
    Stores the request URI and displays the given success message.
    """

    def __init__(self, success_message):
        """
        Args:
            success_message (str): The message to display in the web browser
                the authorization flow is complete.
        """
        self.last_request_uri = None
        self._success_message = success_message

    def __call__(self, environ, start_response):
        """WSGI Callable.
        Args:
            environ (Mapping[str, Any]): The WSGI environment.
            start_response (Callable[str, list]): The WSGI start_response
                callable.
        Returns:
            Iterable[bytes]: The response body.
        """
        start_response("200 OK",
                       [("Content-type", "text/plain; charset=utf-8")])
        self.last_request_uri = wsgiref.util.request_uri(environ)
        return [self._success_message.encode("utf-8")]
