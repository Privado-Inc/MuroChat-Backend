echo "Starting Application......"
source $(poetry env info --path)/bin/activate
python manage.py makemigrations
python manage.py migrate
python manage.py runserver