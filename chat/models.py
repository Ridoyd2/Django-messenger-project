from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    is_bot_response = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'{self.sender} to {self.receiver}: {self.content[:20]}...'

class UserStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_online = models.BooleanField(default=False)
    last_online = models.DateTimeField(default=timezone.now)
    ai_bot_enabled = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} - {"Online" if self.is_online else "Offline"}'
