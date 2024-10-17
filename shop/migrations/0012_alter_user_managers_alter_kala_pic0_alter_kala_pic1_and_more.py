# Generated by Django 4.2 on 2024-10-17 13:33

import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0011_alter_postcomments_options_alter_user_managers_and_more'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objs', django.db.models.manager.Manager()),
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AlterField(
            model_name='kala',
            name='pic0',
            field=models.ImageField(default='no-image.jpg', height_field='image_height', upload_to='static/images/products/20241017-133331', width_field='image_width'),
        ),
        migrations.AlterField(
            model_name='kala',
            name='pic1',
            field=models.ImageField(blank=True, default='no-image.jpg', null=True, upload_to='static/images/products/20241017 - 133331'),
        ),
        migrations.AlterField(
            model_name='kala',
            name='pic2',
            field=models.ImageField(blank=True, default='no-image.jpg', null=True, upload_to='static/images/products/20241017 - 133331'),
        ),
        migrations.AlterField(
            model_name='kala',
            name='pic3',
            field=models.ImageField(blank=True, default='no-image.jpg', null=True, upload_to='static/images/products/20241017 - 133331'),
        ),
        migrations.AlterField(
            model_name='kala',
            name='pic4',
            field=models.ImageField(blank=True, default='no-image.jpg', null=True, upload_to='static/images/products/20241017 - 133331'),
        ),
        migrations.AlterField(
            model_name='post',
            name='pic',
            field=models.ImageField(blank=True, default='no-image.jpg', height_field='image_height', null=True, upload_to='static/images/posts/20241017-133331', width_field='image_width'),
        ),
        migrations.AlterField(
            model_name='sold',
            name='FollowUpCode',
            field=models.CharField(default='8020241017133331', max_length=20),
        ),
        migrations.AlterField(
            model_name='sold',
            name='sent',
            field=models.CharField(choices=[('T', 'Package sent'), ('B', 'Back to Store'), ('F', 'Package Wait for send')], default='F', help_text='Is package sent?', max_length=1, verbose_name='Send Status'),
        ),
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(default='no-image.jpg', height_field='image_height', upload_to='static/images/profile/20241017-133331', width_field='image_width'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='newsletter',
            field=models.CharField(blank=True, choices=[('T', 'مشترک خبرنامه'), ('F', 'عدم اشتراک در خبرنامه')], default='F', max_length=5),
        ),
    ]