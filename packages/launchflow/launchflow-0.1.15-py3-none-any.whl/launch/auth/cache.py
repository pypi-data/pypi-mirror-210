"""Cache for oauth credentials."""

import datetime
import json
import os

import google.oauth2.credentials
import requests
import typer

from launch import constants

_DEFAULT_FILE = 'launchflow_google_creds.json'
_CREDS_PATH = os.path.join(constants.CONFIG_DIR, _DEFAULT_FILE)


class CredsCache:

    def save(self, creds):
        os.makedirs(constants.CONFIG_DIR, exist_ok=True)
        credentials_json = {
            "access_token": creds.token,
            "refresh_token": creds.refresh_token,
            "id_token": creds.id_token,
            "scopes": creds.scopes,
            'expires_at': creds.expiry.timestamp()
        }
        with open(_CREDS_PATH, 'w') as f:
            json.dump(credentials_json, f)

    def load(self, auth_end_point: str):
        if not os.path.exists(_CREDS_PATH):
            typer.echo('No credentials found. Please run: `launch auth login`')
            raise typer.Exit(1)
        with open(_CREDS_PATH, 'r') as f:
            credentials_json = json.load(f)
            creds = google.oauth2.credentials.Credentials(
                token=credentials_json['access_token'],
                refresh_token=credentials_json['refresh_token'],
                id_token=credentials_json['id_token'],
                scopes=credentials_json['scopes'],
                expiry=datetime.datetime.utcfromtimestamp(
                    credentials_json['expires_at']))

        # Attempt to refresh the creds.
        # TODO: we should really only do this if the previous
        # credentials have expired.
        response = requests.get(
            f'{auth_end_point}/auth/refresh?refresh_token={creds.refresh_token}',  # noqa
            headers={'Authorization': f'Bearer {creds.token}'})
        if response.status_code != 200:
            typer.echo(
                'Failed to refresh creds. Please re-run: `launch auth`.')
            raise typer.Exit(1)
        json_creds = response.json()
        creds = google.oauth2.credentials.Credentials(
            token=json_creds['access_token'],
            refresh_token=json_creds['refresh_token'],
            id_token=json_creds['id_token'],
            scopes=json_creds['scopes'],
            expiry=datetime.datetime.utcfromtimestamp(
                json_creds['expires_at']))
        self.save(creds)
        return creds

    def logout(self):
        try:
            os.remove(_CREDS_PATH)
        except FileNotFoundError:
            pass


CREDS_CACHE = CredsCache()


def get_user_creds(endpoint: str):
    creds = CREDS_CACHE.load(endpoint)
    if creds is None:
        typer.echo('Failed to load creds. Please re-run: `launch auth`.')
        raise typer.Exit(1)
    return creds


def save_user_creds(creds):
    CREDS_CACHE.save(creds)


def logout():
    CREDS_CACHE.logout()
