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
"""
This file contains a collection of functions used to gather basic information
that could be commonly used by many different scripts.
"""
import re
from first import first

# unicon is part of genie framework
from unicon.core.errors import SubCommandFailure


__all__ = [
    'find_os_name',
    'find_cdp_neighbor',
    'find_ipaddr_by_arp',
    'find_macaddr_by_arp',
    'find_macaddr_via_iface',
    'find_portchan_members',
    'ping'
]


def ping(device, target):
    try:
        device.ping(target)
        return True
    except SubCommandFailure:
        return False


def find_macaddr_by_arp(dev, ipaddr):
    """ '10.9.2.171  00:13:37  0050.abcd.de17  Vlan18' """
    cli_text = dev.execute(f'show ip arp {ipaddr} | inc {ipaddr}')
    if not cli_text or 'Invalid' in cli_text:
        return None

    found_ipaddr, timestamp, macaddr, ifname = re.split(r'\s+', cli_text)
    return {
        'macaddr': macaddr,
        'interface': ifname
    }


def find_ipaddr_by_arp(dev, macaddr):
    """ '10.9.2.171  00:13:37  0050.abcd.de17  Vlan18' """
    cli_text = dev.execute(f'show ip arp | inc {macaddr}')
    if not cli_text or 'Invalid' in cli_text:
        return None

    ipaddr, timestamp, macaddr, ifname = re.split(r'\s+', cli_text)
    return {
        'ipaddr': ipaddr,
        'interface': ifname
    }


def find_macaddr_via_iface(dev, macaddr):
    """ '* 17       0050.abcd.de17    dynamic   0          F    F  Po1' """
    cli_text = dev.execute(f'show mac address-table | inc {macaddr}')
    if not cli_text:
        return None

    # the last item is the interface name
    return cli_text.split()[-1]


def find_portchan_members(dev, ifname):
    """ '1     Po1(SU)     Eth      LACP      Eth2/1(P)    Eth2/2(P)' """
    cli_text = dev.execute(f'show port-channel summary interface {ifname} | inc {ifname}')
    if not cli_text:
        return None

    members = re.split(r'\s+', cli_text)[4:]
    return [member.split('(')[0] for member in members]


def find_os_name(dev=None, content=None):
    if not content:
        content = dev.execute('show version')

    # look for specific Cisco OS names.  If one is not found, it means that the
    # CDP neighbor is not a recognized device, and return None.  If it is
    # recognized then the re will return a list, for which we need to extract
    # the actual found NOS name; thus using the first() function twice.

    os_name = first(re.findall('(IOSXE)|(NX-OS)|(IOS)', content, re.M))
    if not os_name:
        return None

    os_name = first(os_name)

    # convert OS name from show output to os name required by genie, if the OS
    # is not found, then return None

    return {'IOSXE': 'iosxe', 'NX-OS': 'nxos', 'IOS': 'ios'}[os_name]


def find_cdp_neighbor(dev, ifname):
    if dev.os == 'nxos':
        cli_text = dev.execute(f'show cdp neighbor interface {ifname} detail')
        if not cli_text or 'Invalid' in cli_text:
            return None

    else:
        cli_text = dev.execute(f'show cdp neighbors {ifname} detail')
        if "Total cdp entries displayed : 0" in cli_text:
            return None

    device = first(re.findall('Device ID:(.*)$', cli_text, re.M))
    if device and '.' in device:
        device = first(device.split('.'))

    platform = first(re.findall('Platform: (.*),', cli_text, re.M))
    os_name = find_os_name(content=cli_text)

    return {
        'device': device,
        'platform': platform,
        'os_name': os_name
    }
