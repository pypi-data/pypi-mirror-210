import importlib
import os
import shlex
import subprocess
import time

import pytest

import aiobtclientrpc

PACKAGE_NAME = 'tests.' + os.path.basename(os.path.dirname(__file__))


def log(*args):
    print('CONFTEST:', ' '.join(str(arg) for arg in args))


def _get_server_modules():
    server_modules = []
    servers_path = os.path.join(os.path.dirname(__file__), 'servers')
    log(servers_path)

    for filepath in sorted(os.listdir(servers_path)):
        filename = os.path.basename(filepath)
        if not filename.startswith('_') and filename.endswith('.py'):
            module_name = filename[:-len('.py')]
            module = importlib.import_module(f'.{module_name}', package=f'{PACKAGE_NAME}.servers')
            server_modules.append(module)
    return server_modules


@pytest.fixture(
    params=_get_server_modules(),
    scope='session',
    ids=lambda module: module.name,
)
def _server_info(request, tmp_path_factory):
    module = request.param
    tmp_path = tmp_path_factory.mktemp('X')
    info = module.run(tmp_path)

    def server_info():
        return info

    try:
        run_server(info, tmp_path)
        yield server_info
    finally:
        kill_server(info['server_name'])


@pytest.fixture
async def api(_server_info):
    info = _server_info()

    client = aiobtclientrpc.client(info['client_name'], url=info['server_url'])
    api_module = importlib.import_module('.' + info['client_name'], package=f'{PACKAGE_NAME}.apis')
    api = api_module.API(client)
    await api.reset()
    yield api


_running_servers = {}

def run_server(info, tmp_path):
    log('Running server:', info['server_name'], info['server_url'])

    try:
        info['proc'] = subprocess.Popen(
            shlex.split(info['server_start_cmd']),
            shell=False,
        )
    except FileNotFoundError:
        pytest.skip(info['server_name'] + ' is not installed')

    _running_servers[info['server_name']] = info

    # Check if server_start_cmd failed, e.g. due to invalid arguments
    if info['proc'].poll() is None:
        log('Server is now running:', info['server_name'])
        # Wait for RPC interface to come up
        time.sleep(3)

    # Process should still be running (poll() returns None); otherwise report
    # stdout/stderr
    if info['proc'].poll() is not None:
        raise RuntimeError(f'Failed to run {info["server_start_cmd"]}')


def kill_server(name):
    log('Killing server:', name)

    info = _running_servers.get(name, {})
    if info.get('proc', None):
        server_stop_cmd = info.get('server_stop_cmd')
        if server_stop_cmd:
            subprocess.run(shlex.split(server_stop_cmd), shell=False)
        else:
            info['proc'].terminate()
        info['proc'].wait()
