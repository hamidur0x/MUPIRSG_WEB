from django.contrib.auth import get_user_model
User = get_user_model()
u = User.objects.get(username="YOUR_BS_ID_OR_USERNAME")
u.is_staff = True
u.save()
exit()