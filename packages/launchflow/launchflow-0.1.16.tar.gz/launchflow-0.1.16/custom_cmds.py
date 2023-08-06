import io
import os
import sys
import subprocess
from setuptools.command.build import build
import shutil
import tarfile
from urllib.request import urlopen

CUSTOM_COMMANDS = [['echo', f'DO NOT SUBMIT: {os.path.dirname(__file__)}']]


def get_virtualenv_path():
    """Used to work out path to install compiled binaries to."""
    if hasattr(sys, 'real_prefix'):
        return sys.prefix

    if hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix:
        return sys.prefix

    if 'conda' in sys.prefix:
        return sys.prefix

    return None


def _install_prometheus_release(download_url: str, extracted_dir: str,
                                output_dir: str):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    tar_base_path = 'launch/prometheus'
    final_output_dir = os.path.join(dir_path, tar_base_path, output_dir)
    final_binary_path = os.path.join(final_output_dir, 'prometheus')
    final_yaml_path = os.path.join(final_output_dir, 'prometheus.yml')
    if (os.path.exists(final_binary_path) and os.path.exists(final_yaml_path)):
        # Already exist we can just return. This really only happens with
        # local development.
        return

    response = urlopen(download_url)
    tar_bytes = io.BytesIO(response.read())

    with tarfile.open(fileobj=tar_bytes) as f:
        f.extractall(final_output_dir)

    if not os.path.exists(final_binary_path):
        shutil.move(
            os.path.join(final_output_dir, extracted_dir, 'prometheus'),
            final_output_dir)
    if not os.path.exists(final_yaml_path):
        shutil.move(
            os.path.join(final_output_dir, extracted_dir, 'prometheus.yml'),
            final_output_dir)

    shutil.rmtree(os.path.join(final_output_dir, extracted_dir))


class InstallCustomDeps(build):

    def _install_prometheus(self):
        _install_prometheus_release(
            'https://github.com/prometheus/prometheus/releases/download/v2.43.0/prometheus-2.43.0.linux-amd64.tar.gz',  # noqa: E501
            'prometheus-2.43.0.linux-amd64',
            'linux',
        )
        _install_prometheus_release(
            'https://github.com/prometheus/prometheus/releases/download/v2.43.0/prometheus-2.43.0.darwin-amd64.tar.gz',  # noqa: E501
            'prometheus-2.43.0.darwin-amd64',
            'mac',
        )

    def _run_custom_commands(self, command_list):
        print('Running command: %s' % command_list)
        p = subprocess.Popen(command_list,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        # Can use communicate(input='y\n'.encode()) if the command run requires
        # some confirmation.
        stdout_data, _ = p.communicate()
        print('Command output: %s' % stdout_data)
        if p.returncode != 0:
            raise RuntimeError('Command %s failed: exit code: %s' %
                               (command_list, p.returncode))

    def run(self) -> None:
        self._install_prometheus()
        build.run(self)
