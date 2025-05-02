from django.contrib import admin
from .models import Message, UserStatus

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'content', 'timestamp', 'is_read', 'is_bot_response')
    list_filter = ('is_read', 'is_bot_response', 'timestamp')
    search_fields = ('content', 'sender__username', 'receiver__username')
    date_hierarchy = 'timestamp'

@admin.register(UserStatus)
class UserStatusAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_online', 'last_online')
    list_filter = ('is_online',)
