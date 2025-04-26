FROM alpine:latest

RUN apk add --no-cache mysql-client bash

COPY backup.sh /backup.sh
RUN chmod +x /backup.sh

ENTRYPOINT ["/backup.sh"]