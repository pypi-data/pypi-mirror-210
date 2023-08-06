import json
from typing import Literal

import requests

from frinx.common.frinx_rest import INSTALL_NODE_URL
from frinx.common.frinx_rest import UNICONFIG_HEADERS
from frinx.common.frinx_rest import UNICONFIG_URL_BASE
from frinx.common.frinx_rest import UNINSTALL_NODE_URL
from frinx.common.type_aliases import DictAny
from frinx.common.util import normalize_base_url


def install_node(
    node_id: str,
    connection_type: Literal['netconf', 'cli'],
    install_params: DictAny,
    uniconfig_url_base: str | None = None
) -> requests.Response:
    """
    Install node to Uniconfig.
    https://docs.frinx.io/frinx-uniconfig/user-guide/network-management-protocols/uniconfig-installing/
    Args:
        node_id: Unique identifier, which will be assigned to a node after installation.
        connection_type: Connection type. Accepted values are "netconf" and "cli" values.
        install_params: Installation parameters. For more info check the Uniconfig install documentation.
        uniconfig_url_base: Override default Uniconfig url.

    Returns:
        Http response.
    """
    base_url = UNICONFIG_URL_BASE
    if uniconfig_url_base is not None:
        base_url = uniconfig_url_base

    url = normalize_base_url(base_url) + INSTALL_NODE_URL
    data: DictAny = {
        'input': {
            'node-id': node_id,
            connection_type: {
                **install_params
            }
        }
    }

    response = requests.post(url, data=json.dumps(data), headers=UNICONFIG_HEADERS)
    response.raise_for_status()
    return response


def uninstall_node(
    node_id: str,
    connection_type: Literal['netconf', 'cli'],
    uniconfig_url_base: str | None = None
) -> requests.Response:
    """
    Uninstall node from Uniconfig.
    https://docs.frinx.io/frinx-uniconfig/user-guide/network-management-protocols/uniconfig-installing/#example-request
    Args:
        node_id: Unique identifier of a node to be uninstalled.
        connection_type: Connection type. Accepted values are "netconf" and "cli" values.
        uniconfig_url_base: Override default Uniconfig url.

    Returns:
        Http response.
    """
    base_url = UNICONFIG_URL_BASE
    if uniconfig_url_base is not None:
        base_url = uniconfig_url_base

    url = normalize_base_url(base_url) + UNINSTALL_NODE_URL
    data = {
        'input': {
            'node-id': node_id,
            'connection-type': connection_type
        }
    }

    response = requests.post(url, data=json.dumps(data), headers=UNICONFIG_HEADERS)
    response.raise_for_status()
    return response
