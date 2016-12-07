FROM mysql:5.7

ENV MYSQL_ROOT_PASSWORD=123456 \
    MYSQL_USER=vsenti \
    MYSQL_PASSWORD=123456 \
    MYSQL_DATABASE=vsenti_database

ADD vsenti_schema_latest.sql /docker-entrypoint-initdb.d

EXPOSE 3306
