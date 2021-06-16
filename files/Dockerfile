# syntax=docker/dockerfile:1
FROM debian:latest
RUN apt-get update
RUN apt-get install -y pdns-server pdns-backend-sqlite3 sqlite3

ADD pdns.conf /pdns/pdns.conf

# prepare the pdns sqlite3 database
RUN sqlite3 /pdns/pdns.sqlite3 </usr/share/pdns-backend-sqlite3/schema/schema.sqlite3.sql
RUN chown -R pdns: /pdns

CMD ["pdns_server", "--config-dir=/pdns"]
