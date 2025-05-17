from django.db import migrations


def create_user_profiles(apps, schema_editor):
    User = apps.get_model("auth", "User")
    UserProfile = apps.get_model("myapp", "UserProfile")
    for user in User.objects.all():
        UserProfile.objects.get_or_create(user=user)


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "previous_migration"),
    ]

    operations = [
        migrations.RunPython(create_user_profiles),
    ]
