from django.db import migrations

def ensure_user_status(apps, schema_editor):
    """Ensure all users have a UserStatus record."""
    User = apps.get_model('auth', 'User')
    UserStatus = apps.get_model('chat', 'UserStatus')
    
    for user in User.objects.all():
        UserStatus.objects.get_or_create(
            user=user,
            defaults={
                'is_online': False,
                'ai_bot_enabled': False
            }
        )

class Migration(migrations.Migration):
    dependencies = [
        ('chat', '0002_userstatus_ai_bot_enabled'),
    ]

    operations = [
        migrations.RunPython(ensure_user_status),
    ] 