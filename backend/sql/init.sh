#!/bin/bash
echo "Starting MySQL server..."

# 檢查資料庫是否已經初始化
if [ ! -d "/var/lib/mysql/$MYSQL_DATABASE" ]; then
    echo "Initializing database..."
    mysql -u root -p$MYSQL_ROOT_PASSWORD webapp_db < /docker-entrypoint-initdb.d/create_db.sql
    echo "Database initialized."
else
    echo "Database already initialized, skipping SQL script."
fi