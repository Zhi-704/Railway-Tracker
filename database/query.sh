# A bash script to query the database using the queries in the queries.sql file

source .env
export PGPASSWORD=$DB_PASSWORD
psql --host $DB_IP -U $DB_USERNAME -p $DB_PORT $DB_NAME -f query.sql