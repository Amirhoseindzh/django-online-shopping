# Generated by Django 4.0 on 2022-01-02 13:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0008_auto_20211218_1057'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='city',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='khabarname',
            field=models.CharField(blank=True, choices=[('T', 'مشترک خبرنامه'), ('F', 'عدم اشتراک در خبرنامه')], default='F', max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='postcode',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='state',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.states'),
        ),
        migrations.AlterField(
            model_name='kala',
            name='pic0',
            field=models.ImageField(default='no-image.jpg', height_field='imageheight', upload_to='static/images/products/20220102-133238', width_field='imagewidth'),
        ),
        migrations.AlterField(
            model_name='kala',
            name='pic1',
            field=models.ImageField(blank=True, default='no-image.jpg', null=True, upload_to='static/images/products/20220102 - 133238'),
        ),
        migrations.AlterField(
            model_name='kala',
            name='pic2',
            field=models.ImageField(blank=True, default='no-image.jpg', null=True, upload_to='static/images/products/20220102 - 133238'),
        ),
        migrations.AlterField(
            model_name='kala',
            name='pic3',
            field=models.ImageField(blank=True, default='no-image.jpg', null=True, upload_to='static/images/products/20220102 - 133238'),
        ),
        migrations.AlterField(
            model_name='kala',
            name='pic4',
            field=models.ImageField(blank=True, default='no-image.jpg', null=True, upload_to='static/images/products/20220102 - 133238'),
        ),
        migrations.AlterField(
            model_name='post',
            name='pic',
            field=models.ImageField(blank=True, null=True, upload_to='static/images/posts/20220102-133238'),
        ),
        migrations.DeleteModel(
            name='MyUsers',
        ),
    ]
