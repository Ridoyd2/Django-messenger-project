from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.utils import timezone
from .models import UserStatus

@receiver(post_save, sender=User)
def create_user_status(sender, instance, created, **kwargs):
    if created:
        UserStatus.objects.create(user=instance)

@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    user_status, created = UserStatus.objects.get_or_create(user=user)
    user_status.is_online = True
    user_status.last_online = timezone.now()
    user_status.save()

@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    if user:
        user_status, created = UserStatus.objects.get_or_create(user=user)
        user_status.is_online = False
        user_status.last_online = timezone.now()
        user_status.save() 