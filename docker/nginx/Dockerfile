FROM nginx:stable-alpine

RUN apk add --no-cache gettext

COPY ./docker/nginx/nginx.conf.template /etc/nginx/nginx.conf.template
COPY ./docker/nginx/start.sh /start.sh

# Fix line endings and make scripts executable
RUN sed -i 's/\r$//g' /start.sh \
    && chmod +x /start.sh

CMD ["/start.sh"]