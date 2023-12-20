#!/bin/bash -xv

BASE_PATH=/home/ubuntu/install

cd $BASE_PATH/code/private-gpt-backend

poetry run python extract-secrets.py

set -a
[ -f $BASE_PATH/code/private-gpt-backend/.env ] && . $BASE_PATH/code/private-gpt-backend/.env
set +a

chmod +x $BASE_PATH/code/private-gpt-backend/scripts/copy_file.sh
bash $BASE_PATH/code/private-gpt-backend/scripts/copy_file.sh

poetry run python manage.py migrate


nohup poetry run uwsgi --emperor /etc/uwsgi/sites/private-gpt-backend.ini &

echo "adding symbolic link for log file"
ln -s /home/ubuntu/log/uwsgi /var/log/uwsgi

echo "starting server"
nohup poetry run python manage.py runserver 8002 &

echo "> Starting nginx"
service nginx start
sleep 10
echo "> Checking nginx status"
service nginx status | grep "nginx is running"
if [ "$?" != 0 ]
then
  echo "Failed to start nginx, restarting ..."
    service nginx start
fi

curl --fail --retry 20 --retry-delay 3 http://localhost:8001/api/u/meta

echo "enterprise chat gpt is up and running ... ... ..."
tail -f /dev/null
