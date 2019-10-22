#   Copyright 2019 Jeremy Schulman, nwkautomaniac@gmail.com
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


import sys
import os
import logging

from pyats.topology import Testbed
from pyats.topology.credentials import Credentials
from genie.conf.base.device import Device

from idreamofgenie.basic import find_os_name

log = logging.getLogger(__name__)

# declare a module scoped global variable for our testbed instance.

_g_network_testbed = None


def ensure_environment():
    try:
        assert all(os.environ[env] for env in ['PYATS_USERNAME', 'PYATS_PASSWORD'])
    except KeyError as exc:
        sys.exit(f"ERROR: missing environment variable: {exc}")


def make_testbed(name=__package__):
    global _g_network_testbed
    _g_network_testbed = Testbed(name)

    _g_network_testbed.credentials = Credentials(dict(default=dict(
        username=os.environ['PYATS_USERNAME'],
        password=os.environ['PYATS_PASSWORD'])))

    log.info(f"Created Genie testbed: {name}")
    return _g_network_testbed


def disable_console_log(dev):
    dev.connectionmgr.log.setLevel(logging.ERROR)


def connect_device(hostname, os_name=None, ipaddr=None, log_stdout=False, refresh=False):
    """
    This function will create a Device instance and initiate the connection
    with log_stdout disabled by default.  If the device already exists and is
    connected then this function will return what already exists.

    Examples
    --------
        dev = connect_device('switch1', 'nxos', testbed)
        dev.parse('show version')

    Parameters
    ----------
    hostname : str
        The hostname of the device

    os_name : str
        Optional. The OS type of the device.  If not provided, will default to
        'ios', and a 'show version' command will be execute to find the correct
        version. If provided, must be one of the values listed on the docs
        website:

        https://pubhub.devnetcloud.com/media/pyats-getting-started/docs/quickstart/manageconnections.html#manage-connections

    ipaddr : str
        Optional.  The IP address for the hostname.  If given, this value will
        be used to open the connection.  If not given, then the `hostname`
        parameter must be in DNS.

    log_stdout : bool
        Optional, default=False.  Controls the initial connection setting to
        disable/enable stdout logging.

    Returns
    -------
    Device
        Connected device instance
    """

    # see if the device already exists and is connected.  If it is, then return
    # what we have, otherwise proceed to create a new device and connect.

    has_device = _g_network_testbed.devices.get(hostname)
    if has_device:
        if refresh:
            _g_network_testbed.remove_device(has_device)

        if has_device.is_connected():
            return has_device

        # have device, but not connected, start over
        _g_network_testbed.remove_device(has_device)

    def _make_device(_os):
        return Device(hostname,
                      os=_os,  # required

                      # genie uses the 'custom' field to select parsers by os_type

                      custom={'abstraction': {'order': ['os']}},

                      # connect only using SSH, prevent genie from making config
                      # changes to the device during the login process.

                      connections={'default': dict(host=(ipaddr or hostname),
                                                   arguments=dict(init_config_commands=[],
                                                                  init_exec_commands=[]),
                                                   protocol='ssh')})

    if os_name:
        dev = _make_device(_os=os_name)

    else:
        dev = _make_device(_os='ios')
        _g_network_testbed.add_device(dev)
        dev.connect(log_stdout=log_stdout)
        os_name = find_os_name(dev)
        if os_name != 'ios':
            _g_network_testbed.remove_device(dev)
            dev = _make_device(_os=os_name)

    _g_network_testbed.add_device(dev)
    dev.connect(log_stdout=log_stdout)

    return dev


ensure_environment()
make_testbed()
