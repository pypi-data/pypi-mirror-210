import dataclasses
import json
import os
import requests
from typing import Optional

from launch import constants

_CONFIG_FILE = 'config.json'
_CONFIG_PATH = os.path.join(constants.CONFIG_DIR, _CONFIG_FILE)


@dataclasses.dataclass
class LaunchFlowConfig:
    default_account_id: Optional[str] = None

    def write(self):
        os.makedirs(constants.CONFIG_DIR, exist_ok=True)
        with open(_CONFIG_PATH, 'w') as f:
            json.dump(dataclasses.asdict(self), f)

    @classmethod
    def load(cls,
             server_address: str = '',
             id_token: str = '') -> 'LaunchFlowConfig':
        if os.path.exists(_CONFIG_PATH):
            with open(_CONFIG_PATH, 'r') as f:
                try:
                    json_config = json.load(f)
                    config = cls(**json_config)
                except Exception:
                    # If we fail to load it for whatever reason treat it as an
                    # unset config.
                    config = cls()
        else:
            config = cls()
        # if no account ID is set try to look it up to see if the user only has
        # access to one acount. If this is true use that account for all
        # actions.
        if config.default_account_id is None and server_address and id_token:
            response = requests.post(
                f'{server_address}/accounts/list',
                headers={'Authorization': f'Bearer {id_token}'})

            if response.status_code != 200:
                raise ValueError('failed to list accounts. Error code: '
                                 f'{response.status_code}')

            json_response = response.json()
            if len(json_response['accounts']) > 1:
                accounts = [(account['display_name'], account['id'])
                            for account in json_response['accounts']]
                raise ValueError(
                    'You have access to multiple accounts. Please run '
                    '`launch actions set-default-account $ACCOUNT_ID` to set '
                    f'the default account.\nAccounts\n------\n{accounts}')
            elif not json_response:
                raise ValueError(
                    'You do not have access to any accounts. Please signup '
                    'with `launch accounts signup`.')
            config.default_account_id = json_response['accounts'][0]['id']
            config.write()
        return config
