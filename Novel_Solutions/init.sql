
CREATE DATABASE IF NOT EXISTS novel_solutions_db;

CREATE USER IF NOT EXISTS 'admin'@'%' IDENTIFIED BY 'admin';
GRANT ALL PRIVILEGES ON novel_solutions_db.* TO 'admin'@'%';
FLUSH PRIVILEGES;
