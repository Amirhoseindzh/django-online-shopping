# Generated by Django 3.2.9 on 2021-12-06 09:15

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import shop.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=15, unique=True)),
                ('first_name', models.CharField(blank=True, max_length=20, null=True)),
                ('last_name', models.CharField(blank=True, max_length=20, null=True)),
                ('age', models.IntegerField(blank=True, null=True)),
                ('password', models.CharField(max_length=255)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('FM', 'Unset')], default='FM', max_length=2)),
                ('address', models.CharField(blank=True, max_length=60, null=True)),
                ('phone', models.CharField(blank=True, max_length=15, validators=[shop.validators.PhoneValidator()])),
                ('email', models.EmailField(blank=True, max_length=30, null=True)),
                ('date_joind', models.DateField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=True)),
                ('is_superuser', models.BooleanField(default=False)),
                ('last_login', models.DateField(blank=True, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(allow_unicode=True, auto_created=True)),
                ('name', models.CharField(max_length=50)),
                ('logo', models.ImageField(blank=True, default='no-image.jpg', height_field='imageheight', null=True, upload_to='images/logos/', width_field='imagewidth')),
                ('imagewidth', models.PositiveIntegerField(default=50, editable=False)),
                ('imageheigth', models.PositiveIntegerField(default=50, editable=False)),
            ],
            options={
                'verbose_name_plural': 'Brand',
            },
        ),
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Enter a Product Color', max_length=20)),
            ],
            options={
                'verbose_name_plural': 'Product Colors',
            },
        ),
        migrations.CreateModel(
            name='ContactUs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('description', models.TextField()),
            ],
            options={
                'verbose_name_plural': 'Contact-us Table',
            },
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20)),
                ('count', models.IntegerField()),
                ('off', models.IntegerField(default=0, help_text='Off percent')),
                ('expire', models.DateTimeField(verbose_name='Expire Data')),
            ],
            options={
                'verbose_name_plural': 'Coupons',
            },
        ),
        migrations.CreateModel(
            name='Kala',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(allow_unicode=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
                ('mini_description', models.CharField(max_length=200)),
                ('pic0', models.ImageField(default='no-image.jpg', height_field='imageheight', upload_to='kalaImages/20211206-091541', width_field='imagewidth')),
                ('pic1', models.ImageField(blank=True, default='no-image.jpg', null=True, upload_to='KalaImages/20211206 - 091541')),
                ('pic2', models.ImageField(blank=True, default='no-image.jpg', null=True, upload_to='KalaImages/20211206 - 091541')),
                ('pic3', models.ImageField(blank=True, default='no-image.jpg', null=True, upload_to='KalaImages/20211206 - 091541')),
                ('pic4', models.ImageField(blank=True, default='no-image.jpg', null=True, upload_to='KalaImages/20211206 - 091541')),
                ('description', models.TextField(blank=True, max_length=255, null=True)),
                ('imagewidth', models.PositiveIntegerField(default=401, editable=False)),
                ('imageheigth', models.PositiveIntegerField(default=401, editable=False)),
                ('brand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='brand', to='shop.brand', verbose_name='Brand')),
            ],
            options={
                'verbose_name_plural': 'Product',
            },
        ),
        migrations.CreateModel(
            name='KalaCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(allow_unicode=True, auto_created=True)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Materials',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Enter a Product Materials', max_length=20)),
            ],
            options={
                'verbose_name_plural': 'Product Matrials',
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Enter title for Post', max_length=100)),
                ('body', models.TextField()),
                ('pic', models.ImageField(blank=True, null=True, upload_to='images/posts/20211206-091541')),
            ],
            options={
                'verbose_name_plural': 'Post',
            },
        ),
        migrations.CreateModel(
            name='ProductSize',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sizeno', models.CharField(help_text='Enter a product size', max_length=20)),
            ],
            options={
                'verbose_name_plural': 'Product Sizes',
            },
        ),
        migrations.CreateModel(
            name='States',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'State Table',
            },
        ),
        migrations.CreateModel(
            name='MyUsers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, max_length=15, validators=[shop.validators.PhoneValidator()])),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('address', models.CharField(blank=True, max_length=100, null=True)),
                ('postcode', models.CharField(blank=True, max_length=10, null=True)),
                ('khabarname', models.CharField(blank=True, choices=[('T', 'مشترک خبرنامه'), ('F', 'عدم اشتراک در خبرنامه')], default='F', max_length=5, null=True)),
                ('state', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.states')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='MyUsers', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Normal Users',
            },
        ),
        migrations.CreateModel(
            name='KalaInstance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.BigIntegerField(verbose_name='Price')),
                ('off', models.IntegerField(default=0)),
                ('instock', models.IntegerField()),
                ('kala', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='kalainstance', to='shop.kala')),
                ('saller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Product Instances',
            },
        ),
        migrations.AddField(
            model_name='kala',
            name='category',
            field=models.ForeignKey(help_text='category', null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.kalacategory', verbose_name='Category'),
        ),
        migrations.AddField(
            model_name='kala',
            name='color',
            field=models.ManyToManyField(help_text='Select Color of the product', to='shop.Color'),
        ),
        migrations.AddField(
            model_name='kala',
            name='material',
            field=models.ManyToManyField(help_text='Select Material of the Product', to='shop.Materials'),
        ),
        migrations.AddField(
            model_name='kala',
            name='size',
            field=models.ManyToManyField(help_text='Enter Size of the product', to='shop.ProductSize'),
        ),
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.CharField(max_length=500)),
                ('data', models.DateField(auto_now_add=True)),
                ('status', models.CharField(choices=[('T', "It's Ok"), ('W', 'Waiting')], default='W', max_length=1)),
                ('kala', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.kala')),
                ('writer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Comments',
            },
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField(default=1)),
                ('payed', models.CharField(choices=[('T', 'Payed'), ('F', 'Not Payed')], default='F', max_length=1)),
                ('color', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Color', to='shop.color')),
                ('coupon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.coupon')),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Materials', to='shop.materials')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.kala', verbose_name='Products')),
                ('saller', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Instanse', to='shop.kalainstance')),
                ('size', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ProductSize', to='shop.productsize')),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Carts',
            },
        ),
    ]
