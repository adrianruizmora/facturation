CREATE DATABASE db_facturation DEFAULT CHARACTER SET utf8;
USE db_facturation;

CREATE USER 'selemmerili1'@'192.168.3.6' IDENTIFIED BY 'Selma2015@';
GRANT ALL PRIVILEGES ON db_facturation.* TO 'selemmerili1'@'192.168.3.6';


FLUSH PRIVILEGES;

SHOW DATABASES;
SHOW TABLES;
select user,host from mysql.user;
-- select host,user from mysql.user

