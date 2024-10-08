# Generated by Django 5.0.7 on 2024-07-25 00:02

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0005_account_user"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="account",
            name="email",
        ),
        migrations.RemoveField(
            model_name="account",
            name="first_name",
        ),
        migrations.RemoveField(
            model_name="account",
            name="groups",
        ),
        migrations.RemoveField(
            model_name="account",
            name="is_superuser",
        ),
        migrations.RemoveField(
            model_name="account",
            name="last_login",
        ),
        migrations.RemoveField(
            model_name="account",
            name="last_name",
        ),
        migrations.RemoveField(
            model_name="account",
            name="password",
        ),
        migrations.RemoveField(
            model_name="account",
            name="user_permissions",
        ),
    ]
