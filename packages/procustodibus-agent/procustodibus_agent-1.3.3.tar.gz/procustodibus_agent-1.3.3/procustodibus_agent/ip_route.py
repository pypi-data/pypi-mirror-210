# -*- coding: utf-8 -*-
"""Routing and addressing utilities."""

from json import loads
from platform import system
from re import fullmatch
from subprocess import PIPE, run  # noqa: S404


def run_ip_address_show(device):
    """Runs `ip address show` command for specified device.

    Arguments:
        device (str): Device name (eg 'wg0').

    Returns:
        dict: Parsed JSON from `ip --json address show` command.
    """
    args = ["ip", "--json", "address", "show", "dev", device]
    result = run(args, stdout=PIPE)  # noqa: S603 S607
    output = result.stdout.decode("utf-8")
    return loads(output)[0] if fullmatch(r"\[\{.*\}\]\s*", output) else {}


def run_ifconfig(device):
    """Runs `ifconfig` command for specified device.

    Arguments:
        device (str): Device name (eg 'wg0').

    Returns:
        list: Lines from `ifconfig -f inet:cidr,inet6:cidr` command.
    """
    args = ["ifconfig", "-f", "inet:cidr,inet6:cidr", device]
    result = run(args, stdout=PIPE)  # noqa: S603 S607
    output = result.stdout.decode("utf-8")
    return [x.strip() for x in output.split("\n")]


def annotate_wg_show_with_ip_address_show(interfaces):
    """Annotates parsed output of `wg show` with output of `ip address show`.

    Arguments:
        interfaces (dict): Dict parsed from `wg show` command.

    Returns:
        dict: Same dict with additional properties.
    """
    for name, properties in interfaces.items():
        _annotate_interface(name, properties)
    return interfaces


def _annotate_interface(name, properties):
    """Annotates specified dict with wg config for specified interface.

    Arguments:
        name (str): Interface name (eg 'wg0').
        properties (dict): Dict of interface properties.

    Returns:
        dict: Same dict with additional properties.
    """
    if system() == "Linux":
        _annotate_interface_with_ip_address_show(name, properties)
    else:
        _annotate_interface_with_ifconfig(name, properties)
    return properties


def _annotate_interface_with_ip_address_show(name, properties):
    """Annotates specified dict with wg config for specified interface.

    Arguments:
        name (str): Interface name (eg 'wg0').
        properties (dict): Dict of interface properties.

    Returns:
        dict: Same dict with additional properties.
    """
    info = run_ip_address_show(name)
    if info:
        properties["address"] = [_format_address_info(a) for a in info["addr_info"]]
    return properties


def _format_address_info(info):
    """Formats the addr_info object from `ip address show` as a CIDR.

    Arguments:
        info (dict): addr_info object.

    Returns:
        string: CIDR.
    """
    return "{}/{}".format(info["local"], info["prefixlen"])


def _annotate_interface_with_ifconfig(name, properties):
    """Annotates specified dict with wg config for specified interface.

    Arguments:
        name (str): Interface name (eg 'wg0').
        properties (dict): Dict of interface properties.

    Returns:
        dict: Same dict with additional properties.
    """
    addresses = [x.split(" ")[1] for x in run_ifconfig(name) if x.startswith("inet")]
    if addresses:
        properties["address"] = addresses
    return properties
