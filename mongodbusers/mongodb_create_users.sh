#!/bin/bash

BASE_PATH=/home/ubuntu/install
cd $BASE_PATH/code/private-gpt-backend/mongodbusers

cp mongo_users_orig.js mongo_users.js
cp idp_orig.js idp.js
sed -i -e "s/PRIVADO_DBA_PSW/$PRIVADO_DBA_PSW/g" mongo_users.js
sed -i -e "s/CONFIG_USERS_PSW/$CONFIG_USERS_PSW/g" mongo_users.js

sed -i -e "s#OKTA_INTROSPECT_DOMAIN#$OKTA_INTROSPECT_DOMAIN#g" idp.js
sed -i -e "s/OKTA_CLIENT_ID/$OKTA_CLIENT_ID/g" idp.js

retries=5
retry_delay=3

echo "Mongo Connection trying...."

for ((i=1; i<=$retries; i++)); 
do
	output=$(mongosh --eval 'db.runCommand("ping").ok' $MONGO_HOST --quiet);
	if [ "$output" == "1" ]; then   
		echo "MongoDB health check successful";
		break;
	else
		echo "Health check failed, Mongo connection failed : ""$MONGO_HOST";
		if [ $i -lt $retries ]; then
			echo "Retrying in $retry_delay seconds...";
			sleep $retry_delay;
		else
			echo "Exceeded maximum retries with "$MONGO_HOST" . Exiting...";
			exit 1;
		fi;
	fi;
done

echo "$MONGO_HOST"
if [[ $MONGO_HOST == *".mongodb.net" ]]; then
    echo "No need to create users... Mongo Cloud"
else
	echo "Creating users....."
    mongosh --host $MONGO_HOST --username "$MONGO_INITDB_ROOT_USERNAME" --password "$MONGO_INITDB_ROOT_PASSWORD" < mongo_users.js
    mongosh --host $MONGO_HOST --username "$MONGO_INITDB_ROOT_USERNAME" --password "$MONGO_INITDB_ROOT_PASSWORD" < idp.js
fi
mongosh --host $MONGO_HOST --username "$MONGO_INITDB_ROOT_USERNAME" --password "$MONGO_INITDB_ROOT_PASSWORD" < idp.js
