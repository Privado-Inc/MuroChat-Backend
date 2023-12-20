#!/bin/bash -xv

ERROR=false

BASE_PATH=/home/ubuntu/install
cd $BASE_PATH/code/private-gpt-backend

set -a
[ -f $BASE_PATH/code/private-gpt-backend/.env ] && . $BASE_PATH/code/private-gpt-backend/.env
set +a


touch /var/log/uwsgi/private-gpt-backend-cron.log

if [ -n "$MONGO_HOST" ] ; then
  sed -i -e "s/MONGO_HOST/$MONGO_HOST/g" $BASE_PATH/code/private-gpt-backend/migrations/chats/chats_config.ini
  sed -i -e "s/MONGO_HOST/$MONGO_HOST/g" $BASE_PATH/code/private-gpt-backend/migrations/idp/idp_config.ini

  sed -i -e "s/CONFIG_USERS_PSW/$CONFIG_USERS_PSW/g" $BASE_PATH/code/private-gpt-backend/migrations/chats/chats_config.ini
  sed -i -e "s/CONFIG_USERS_PSW/$CONFIG_USERS_PSW/g" $BASE_PATH/code/private-gpt-backend/migrations/idp/idp_config.ini
else
  echo "MONGO_HOST is not defined"
  exit 1
fi

echo "Creating default users..."
bash $BASE_PATH/code/private-gpt-backend/mongodbusers/mongodb_create_users.sh


MONGODB_MIGRATIONS_CONFIG=$BASE_PATH/code/private-gpt-backend/migrations/chats/chats_config.ini poetry run mongodb-migrate
MONGODB_MIGRATIONS_CONFIG=$BASE_PATH/code/private-gpt-backend/migrations/idp/idp_config.ini poetry run mongodb-migrate

poetryPath=$(poetry env info -p) #TODO
echo "poetryPath"
echo $poetryPath
sed -i -e "s#POETY_ENV#$poetryPath#g" $BASE_PATH/code/private-gpt-backend/config/uwsgi/private-gpt-backend.ini

UWSGI_CONF=$BASE_PATH/code/private-gpt-backend/config/uwsgi/private-gpt-backend.ini
if [[ -f "$UWSGI_CONF" ]]; then
   cp -rf $UWSGI_CONF /etc/uwsgi/sites/
fi

NGINX_FILE=$BASE_PATH/code/private-gpt-backend/config/nginx/private-gpt-backend.conf
  if [[ -f "$NGINX_FILE" ]]; then
      sed -i -e "s/_SERVER_NAME_/$SERVER_NAME/g" $NGINX_FILE

      cp -rf $NGINX_FILE /etc/nginx/sites-enabled/
      cp -rf $NGINX_FILE /etc/nginx/sites-available/
  else
      ERROR=true
  fi

# sed -i '2i\# CORS Settings\' $BASE_PATH/code/private-gpt-backend/private-gpt/settings/prod.py
# sed -i '3i\CORS_ALLOW_ALL_ORIGINS = False\' $BASE_PATH/code/private-gpt-backend/private-gpt/settings/prod.py
# sed -i '4i\CORS_ALLOWED_ORIGINS = ( "https://chat.privado.ai",  "https://chat.privado.ai",)\' $BASE_PATH/code/private-gpt-backend/private-gpt/settings/prod.py

if [ "$ERROR" = true ]; then
    exit 1
fi
