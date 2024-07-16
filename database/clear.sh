# A bash script to clear the database

source .env
export PGPASSWORD=$DB_PASSWORD
psql --host $DB_IP -U $DB_USERNAME -p $DB_PORT $DB_NAME -f schema.sql