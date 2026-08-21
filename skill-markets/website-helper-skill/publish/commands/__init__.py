"""publish.commands — Layer 4 helper modules (one module per typer command).

Split out of cli.py (v0.3.0) so the router file stays under the
vibe-coding-standards 350-line soft cap.

* :mod:`commands.config`  — ``publish config {init,dns,ssh}``
* :mod:`commands.cert`    — ``publish cert {status,renew}``
* :mod:`commands.list`    — ``publish list``
* (deploy / rollback stay in cli.py because they need Pipeline wiring)
"""
