FROM postgres
COPY *.sql /docker-entrypoint-initdb.d
ENV POSTGRES_PASSWORD 1
ENV POSTGRES_USER postgres
ENV POSTGRES_DB postgres
EXPOSE 5432
USER postgres
VOLUME  ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql"]
RUN  /etc/init.d/postgresql start
RUN pg_createcluster 13 main
