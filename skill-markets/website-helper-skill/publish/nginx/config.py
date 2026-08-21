"""Nginx server block config generator."""

NGINX_TEMPLATE = """server {{
    listen 80;
    listen [::]:80;

    server_name {server_name};

    root {webroot};
    index index.html index.htm;

    location / {{
        try_files $uri $uri/ =404;
    }}

    # Logs
    access_log /var/log/nginx/{server_name}-access.log;
    error_log /var/log/nginx/{server_name}-error.log;
}}
"""

NGINX_SSL_TEMPLATE = """server {{
    listen 80;
    listen [::]:80;
    server_name {server_name};
    return 301 https://$host$request_uri;
}}

server {{
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name {server_name};

    ssl_certificate /etc/letsencrypt/live/{server_name}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{server_name}/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    root {webroot};
    index index.html index.htm;

    location / {{
        try_files $uri $uri/ =404;
    }}

    access_log /var/log/nginx/{server_name}-access.log;
    error_log /var/log/nginx/{server_name}-error.log;
}}
"""

# VR-009: Reverse-proxy templates (2026-08-20)
# - proxy_pass to caller-supplied upstream (e.g. http://127.0.0.1:8088)
# - WebSocket upgrade headers preserved
# - client_max_body_size 100M (large uploads / artifacts / etc.)
NGINX_PROXY_TEMPLATE = """server {{
    listen 80;
    listen [::]:80;
    server_name {server_name};

    client_max_body_size 100M;
    proxy_read_timeout 300s;
    proxy_send_timeout 300s;

    location / {{
        proxy_pass {upstream};
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade           $http_upgrade;
        proxy_set_header Connection        "upgrade";
    }}

    access_log /var/log/nginx/{server_name}-access.log;
    error_log /var/log/nginx/{server_name}-error.log;
}}
"""

NGINX_PROXY_SSL_TEMPLATE = """server {{
    listen 80;
    listen [::]:80;
    server_name {server_name};
    return 301 https://$host$request_uri;
}}

server {{
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name {server_name};

    ssl_certificate     /etc/letsencrypt/live/{server_name}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{server_name}/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    client_max_body_size 100M;
    proxy_read_timeout 300s;
    proxy_send_timeout 300s;

    location / {{
        proxy_pass {upstream};
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade           $http_upgrade;
        proxy_set_header Connection        "upgrade";
    }}

    access_log /var/log/nginx/{server_name}-access.log;
    error_log /var/log/nginx/{server_name}-error.log;
}}
"""


def generate_server_block(subdomain: str, webroot: str, with_ssl: bool = False) -> str:
    """Generate Nginx server block configuration (static webroot)."""
    template = NGINX_SSL_TEMPLATE if with_ssl else NGINX_TEMPLATE
    return template.format(server_name=subdomain, webroot=webroot)


def generate_proxy_server_block(
    subdomain: str, upstream: str, with_ssl: bool = False
) -> str:
    """VR-009: Generate reverse-proxy Nginx server block.

    Args:
        subdomain: server_name, e.g. "zentaopms.example.com"
        upstream:  full URL, e.g. "http://127.0.0.1:8088" or "http://app:3000"
        with_ssl:  emit :80 → :443 redirect + SSL server block
    """
    template = NGINX_PROXY_SSL_TEMPLATE if with_ssl else NGINX_PROXY_TEMPLATE
    return template.format(server_name=subdomain, upstream=upstream)


def validate_nginx_config(ssh_client) -> tuple[bool, str]:
    """Run 'nginx -t' on the remote host. Returns (ok, output)."""
    exit_code, stdout, stderr = ssh_client.exec_command("nginx -t")
    output = stdout + stderr
    return exit_code == 0, output
