import dataclasses
import json
import os
from typing import Optional

from launch import constants

_SESSION_STATE_FILE = os.path.join(constants.CONFIG_DIR, 'session_state.json')


@dataclasses.dataclass
class LastDeploymentInfo:
    deployment_id: Optional[str]
    deployment_create_http_status: int


@dataclasses.dataclass
class LaunchFlowSession:
    source: str = ''
    sink: str = ''
    last_deployment_info: Optional[LastDeploymentInfo] = None

    def write(self):
        os.makedirs(constants.CONFIG_DIR, exist_ok=True)
        with open(_SESSION_STATE_FILE, 'w') as f:
            json.dump(dataclasses.asdict(self), f)

    @classmethod
    def load(cls) -> 'LaunchFlowSession':
        if os.path.exists(_SESSION_STATE_FILE):
            with open(_SESSION_STATE_FILE, 'r') as f:
                try:
                    json_state = json.load(f)
                    session_state = cls(**json_state)
                except Exception:
                    # If we fail to load it for whatever reason treat it as an
                    # unset config.
                    session_state = cls()
        else:
            session_state = cls()
        return session_state
