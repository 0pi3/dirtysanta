from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

    class Meta:
        verbose_name = ('user')
        verbose_name_plural = ('users')