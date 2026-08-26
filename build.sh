#!/usr/bin/env bash

set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

python manage.py migrate

python manage.py create_default_superuser

python manage.py shell -c "import os; from django.contrib.auth import get_user_model; User=get_user_model(); u=User.objects.filter(username=os.environ.get('ADMIN_USERNAME')).first(); u and (setattr(u,'is_staff',True), setattr(u,'is_superuser',True), u.save(), print('Admin user promoted successfully'))"