"""publish.actions — Layer 2: action functions returning :class:`Step`.

Each module owns ONE responsibility:

* ``dns``   – DNS provider wrappers
* ``nginx`` – nginx config deploy (delegates to ``publish.nginx.deploy``)
* ``ssl``   – SSL cert request/renew (delegates to ``publish.certs.cert_manager``)

Actions must NEVER print directly — they return :class:`Step` instances and let
the caller (Layer 4 / CLI) decide how to surface output. This makes them
trivially testable and sub-agent-friendly.
"""

from publish.actions.dns import action_dns_create_record
from publish.actions.nginx import action_nginx_deploy
from publish.actions.ssl import action_ssl_request_cert

__all__ = [
    "action_dns_create_record",
    "action_nginx_deploy",
    "action_ssl_request_cert",
]
