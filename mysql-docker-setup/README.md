install docker
build the custom image from the mysql-setup-docker folder: docker build -t echobyte-sql .
run the docker container: docker run -d --name echobyte-db -p 1433:1433 -v mssql-data:/var/opt/mssql echobyte-sql


docker exec echobyte-db /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P 'YourStrong!Passw0rd' -C -i /setup/setup.sql

