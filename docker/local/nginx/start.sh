#!/bin/sh
envsubst '$ADMIN_PATH' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf
echo "Replaced ADMIN_PATH with \${ADMIN_PATH}"
nginx -g 'daemon off;'