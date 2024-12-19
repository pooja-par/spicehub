from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    """
    Extend user model to store additional information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
