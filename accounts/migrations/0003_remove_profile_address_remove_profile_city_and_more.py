# Generated by Django 4.2 on 2024-11-24 13:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0006_alter_productcomments_options_remove_cart_payed_and_more'),
        ('accounts', '0002_profile_state_profile_user_user_groups_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='address',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='city',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='postcode',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='state',
        ),
        migrations.AlterField(
            model_name='user',
            name='last_login',
            field=models.DateField(auto_now=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('postal_address', models.TextField(help_text='Your exact address', max_length=50)),
                ('full_name', models.CharField(help_text="Recipient's full name", max_length=100)),
                ('phone_number', models.CharField(max_length=15)),
                ('neighborhood', models.CharField(help_text='Street address, P.O. box, company name, etc.', max_length=1000)),
                ('city', models.CharField(max_length=100)),
                ('postal_code', models.PositiveIntegerField()),
                ('license_plate', models.PositiveIntegerField()),
                ('unit', models.CharField(help_text='Apartment or house unit', max_length=15)),
                ('is_default', models.BooleanField(default=False)),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.states')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-is_default', 'id'],
            },
        ),
    ]