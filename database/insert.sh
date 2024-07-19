# A bash script to insert the database using the queries in the insert.sql file

source .env
export PGPASSWORD=$DB_PASSWORD
psql --host $DB_IP -U $DB_USERNAME -p $DB_PORT $DB_NAME -f insert.sql