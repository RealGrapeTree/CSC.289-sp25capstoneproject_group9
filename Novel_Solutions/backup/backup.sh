#!/bin/sh

echo "Starting backup loop..."
while true
do
  DATE=$(date +%Y-%m-%d_%H-%M-%S)
  echo "Backing up database at $DATE..."
  mysqldump -h novel_solutions_db -uadmin -padmin novel_solutions_db > /backups/db_backup_$DATE.sql
  echo "Backup complete: db_backup_$DATE.sql"

  sleep 86400 # Sleep for 24 hours before the next backup
done
