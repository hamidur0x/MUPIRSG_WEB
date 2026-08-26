#!/usr/bin/env bash

set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

python manage.py migrate

python manage.py create_default_superuser

python manage.py shell -c "
import os
from django.contrib.auth import get_user_model

User = get_user_model()
usernames = [u.strip() for u in os.environ.get('ADMIN_USERNAMES', '').split(',') if u.strip()]

for username in usernames:
    user = User.objects.filter(username=username).first()

    if user:
        user.is_staff = True
        user.is_superuser = True
        user.save(update_fields=['is_staff', 'is_superuser'])
        print(f'Admin enabled: {username}')
    else:
        print(f'User not found: {username}')
"