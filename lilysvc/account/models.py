from django.db import models
from django.contrib.auth.models import User

class LilyProfile(models.Model):
    user = models.OneToOneField(User)
    display_name = models.CharField(max_length=12, null=True)
    lily_password = models.CharField(max_length=12, null=True)
    last_session = models.CharField(max_length=50, null=True)

