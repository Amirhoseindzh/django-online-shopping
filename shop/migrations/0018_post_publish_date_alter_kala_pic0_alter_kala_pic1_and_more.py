# Generated by Django 4.0 on 2022-01-22 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0017_alter_kala_pic0_alter_kala_pic1_alter_kala_pic2_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='publish_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='kala',
            name='pic0',
            field=models.ImageField(default='no-image.jpg', height_field='imageheight', upload_to='static/images/products/20220122-163446', width_field='imagewidth'),
        ),
        migrations.AlterField(
            model_name='kala',
            name='pic1',
            field=models.ImageField(blank=True, default='no-image.jpg', null=True, upload_to='static/images/products/20220122 - 163446'),
        ),
        migrations.AlterField(
            model_name='kala',
            name='pic2',
            field=models.ImageField(blank=True, default='no-image.jpg', null=True, upload_to='static/images/products/20220122 - 163446'),
        ),
        migrations.AlterField(
            model_name='kala',
            name='pic3',
            field=models.ImageField(blank=True, default='no-image.jpg', null=True, upload_to='static/images/products/20220122 - 163446'),
        ),
        migrations.AlterField(
            model_name='kala',
            name='pic4',
            field=models.ImageField(blank=True, default='no-image.jpg', null=True, upload_to='static/images/products/20220122 - 163446'),
        ),
        migrations.AlterField(
            model_name='post',
            name='pic',
            field=models.ImageField(blank=True, default='no-image.jpg', height_field='imageheight', null=True, upload_to='static/images/posts/20220122-163446', width_field='imagewidth'),
        ),
        migrations.AlterField(
            model_name='salled',
            name='FollowUpCode',
            field=models.CharField(default='1420220122163446', max_length=20),
        ),
        migrations.AlterField(
            model_name='salled',
            name='sent',
            field=models.CharField(choices=[('T', 'Packege sent'), ('B', 'Back to Store'), ('F', 'Packege Wait for send')], default='F', help_text='Is package sent?', max_length=1, verbose_name='Send Status'),
        ),
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(default='no-image.jpg', height_field='imageheight', upload_to='static/images/profile/20220122-163446', width_field='imagewidth'),
        ),
    ]
