import os
from types import MappingProxyType

# RBAC CONFIGURATION
X_TENANT_ID = os.getenv('X_TENANT_ID', 'frinx')
X_FROM = os.getenv('X_FROM', 'fm-base-workers')
X_AUTH_USER_GROUP = os.getenv('X_AUTH_USER_GROUP', 'network-admin')

# SET SERVICES URL VARIABLES
UNICONFIG_URL_BASE = os.getenv('UNICONFIG_URL_BASE', 'http://uniconfig:8181/rests')
CONDUCTOR_URL_BASE = os.getenv('CONDUCTOR_URL_BASE', 'http://workflow-proxy:8088/proxy/api')
INVENTORY_URL_BASE = os.getenv('INVENTORY_URL_BASE', 'http://inventory:8000/graphql')
INFLUXDB_URL_BASE = os.getenv('INFLUXDB_URL_BASE', 'http://influxdb:8086')
RESOURCE_MANAGER_URL_BASE = os.getenv('RESOURCE_MANAGER_URL_BASE', 'http://resource-manager:8884/query')

# URL HEADERS
UNICONFIG_HEADERS = MappingProxyType({'Content-Type': 'application/json'})
CONDUCTOR_HEADERS = MappingProxyType(
    {
        'Content-Type': 'application/json',
        'x-tenant-id': X_TENANT_ID,
        'from': X_FROM,
        'x-auth-user-groups': X_AUTH_USER_GROUP
    }
)
ADDITIONAL_UNICONFIG_REQUEST_PARAMS = MappingProxyType(
    {
        'verify': False,
        'headers': UNICONFIG_HEADERS
    }
)

CREATE_TRANSACTION_URL = '/operations/uniconfig-manager:create-transaction'
COMMIT_TRANSACTION_URL = '/operations/uniconfig-manager:commit'
CLOSE_TRANSACTION_URL = '/operations/uniconfig-manager:close-transaction'
CREATE_SNAPSHOT_URL = '/operations/snapshot-manager:create-snapshot'
DELETE_SNAPSHOT_URL = '/operations/snapshot-manager:delete-snapshot'
REPLACE_CONFIG_WITH_SNAPSHOT_URL = '/operations/snapshot-manager:replace-config-with-snapshot'
REPLACE_CONFIG_WITH_OPERATIONAL_URL = '/operations/uniconfig-manager:replace-config-with-operational'
SYNC_FROM_NETWORK_URL = '/operations/uniconfig-manager:sync-from-network'
INSTALL_NODE_URL = '/operations/connection-manager:install-node'
UNINSTALL_NODE_URL = '/operations/connection-manager:uninstall-node'
CLI_EXECUTE_AND_READ_URL = '/operations/network-topology:network-topology/' \
                           'topology=cli/node={}/yang-ext:mount/cli-unit-generic:execute-and-read'
CLI_EXECUTE_URL = '/operations/network-topology:network-topology/' \
                  'topology=cli/node={}/yang-ext:mount/cli-unit-generic:execute'
