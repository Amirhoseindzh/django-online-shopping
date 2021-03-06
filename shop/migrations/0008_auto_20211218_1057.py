# Generated by Django 3.2.9 on 2021-12-18 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0007_auto_20211212_1659'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kala',
            name='pic0',
            field=models.ImageField(default='no-image.jpg', height_field='imageheight', upload_to='static/images/products/20211218-072701', width_field='imagewidth'),
        ),
        migrations.AlterField(
            model_name='kala',
            name='pic1',
            field=models.ImageField(blank=True, default='no-image.jpg', null=True, upload_to='static/images/products/20211218 - 072701'),
        ),
        migrations.AlterField(
            model_name='kala',
            name='pic2',
            field=models.ImageField(blank=True, default='no-image.jpg', null=True, upload_to='static/images/products/20211218 - 072701'),
        ),
        migrations.AlterField(
            model_name='kala',
            name='pic3',
            field=models.ImageField(blank=True, default='no-image.jpg', null=True, upload_to='static/images/products/20211218 - 072701'),
        ),
        migrations.AlterField(
            model_name='kala',
            name='pic4',
            field=models.ImageField(blank=True, default='no-image.jpg', null=True, upload_to='static/images/products/20211218 - 072701'),
        ),
        migrations.AlterField(
            model_name='post',
            name='pic',
            field=models.ImageField(blank=True, null=True, upload_to='static/images/posts/20211218-072701'),
        ),
    ]
