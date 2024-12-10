FROM nginx:stable-alpine

RUN apk add --no-cache gettext

COPY ./docker/local/nginx/nginx.conf.template /etc/nginx/nginx.conf.template
COPY ./docker/local/nginx/start.sh /start.sh

RUN chmod +x /start.sh

ENTRYPOINT ["/start.sh"]
