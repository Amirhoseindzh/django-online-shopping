from django.db import models
from django.contrib.auth.models import AbstractUser , BaseUserManager
from time import gmtime, strftime
from django.utils import timezone
from django.conf import Settings
from .validators import phone_validator
from django.utils.text import slugify
from django.template.defaultfilters import truncatechars
from unidecode import unidecode
from django.utils.translation import gettext_lazy as _
import random



class States(models.Model):
    id = models.AutoField(primary_key=True)
    name =models.CharField(max_length=50)
    
    class Meta:
        verbose_name_plural ='States'

    def __str__(self):
        return f'{self.name}'



"""class CustomUserManager(BaseUserManager):
    #Define a model manager for User model with no username field.

    def _create_user(self, email, password=None, **extra_fields):
        #Create and save a User with the given email and password.
        if not email:
            raise ValueError('The given email must be set')

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        #Create and save a SuperUser with the given email and password.
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)"""



class User(AbstractUser):
    
    class GenderChoice(models.TextChoices):
        MALE = "M" ,"Male"
        FEMAILE = "F" ,"Female"
        UNSET = "FM" ,"Unset"

    class NewsChoice(models.TextChoices):
        TRUE = 'T','مشترک خبرنامه'
        FALSE = 'F' , 'عدم اشتراک در خبرنامه'

    id = models.AutoField(primary_key=True)
    
    first_name = models.CharField(max_length=20 ,null=True ,blank=True)
    last_name = models.CharField(max_length=20 ,null=True ,blank=True)
    age = models.IntegerField(blank=True ,null=True)
    password = models.CharField(max_length=255)
    gender=models.CharField(max_length=2 ,choices=GenderChoice.choices ,default=GenderChoice.UNSET)
    address =models.CharField(max_length=60 ,null=True ,blank=True )
    phone=models.CharField(max_length=15 ,validators=[phone_validator] ,blank=True)
    email=models.EmailField(_('email address') ,unique=True ,  max_length=30 ,blank=True ,null=True)
    city=models.CharField(max_length=100, null=True , blank=True)
    state=models.ForeignKey(States, on_delete=models.CASCADE , null=True,blank=True)
    postcode=models.CharField(max_length=10 , null=True, blank=True)
    date_joind=models.DateField(blank=True ,null=True)
    description=models.TextField(blank=True ,null=True)
    is_active=models.BooleanField(default=True)
    is_staff=models.BooleanField(default=True)
    is_superuser=models.BooleanField(default=False)
    last_login=models.DateField(blank=True ,null=True)
    khabarname=models.CharField(
        max_length=5 ,
        choices=NewsChoice.choices , 
        default=NewsChoice.FALSE ,
        null=True, blank=True
    )
    avatar= models.ImageField(
        upload_to= 'static/images/profile/{0}'.format(strftime('%Y%m%d-%H%M%S',gmtime())) ,
        default='no-image.jpg' ,
        width_field='imagewidth' ,
        height_field='imageheight' ,
        )

    imagewidth = models.PositiveIntegerField(editable = False, default = 65)
    imageheight = models.PositiveIntegerField(editable = False, default = 65)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    #objects = CustomUserManager

    class Meta:
        verbose_name_plural = "User"
        

    def __str__(self):
        return self.email

   
    



class KalaCategory(models.Model):
    slug = models.SlugField(allow_unicode=True)
    name = models.CharField(max_length=100)

    class meta:
        verbose_name_plural ="Product Category-s"

    def __str__(self):
        return f"{self.name}"



class Brand(models.Model):
    slug = models.SlugField(allow_unicode= True)
    name = models.CharField(max_length=50)
    logo = models.ImageField(
        upload_to='static/images/logos/' ,
        default='no-image.jpg' ,
        null=True ,blank=True  ,
        width_field='imagewidth'  ,
        height_field='imageheight' ,
    )
    imagewidth = models.PositiveIntegerField(editable = False, default = 50)
    imageheight = models.PositiveIntegerField(editable = False, default = 50)

    class Meta: 
        verbose_name_plural= "Brand"

    def __str__(self):
        return self.name



class ProductSize(models.Model):
    sizeno = models.CharField(max_length=20 , help_text='Enter a product size')

    class Meta:
        verbose_name_plural = 'Product Sizes'

    def __str__(self):
        return self.sizeno




class Color(models.Model):
    name = models.CharField(max_length=20 , help_text="Enter a Product Color")

    class Meta: 
        verbose_name_plural ="Product Colors"

    def __str__(self):
        return self.name


class Materials(models.Model):
    name = models.CharField(max_length=20 , help_text="Enter a Product Materials")

    class Meta: 
        verbose_name_plural ="Product Matrials"

    def __str__(self):
        return self.name



class Kala(models.Model):
    slug=models.SlugField(allow_unicode=True)
    name=models.CharField(max_length=150)
    brand=models.ForeignKey(Brand ,on_delete=models.SET_NULL, null=True , blank=True , verbose_name='Brand' , related_name='brand') 
    size = models.ManyToManyField(ProductSize , help_text="Enter Size of the product")
    mini_description = models.CharField(max_length=200)
    color = models.ManyToManyField(Color , help_text="Select Color of the product")
    material = models.ManyToManyField(Materials , help_text="Select Material of the Product")
    pic0 = models.ImageField(
        upload_to= 'static/images/products/{0}'.format(strftime('%Y%m%d-%H%M%S',gmtime())) ,
        default='no-image.jpg' ,
        width_field='imagewidth' ,
        height_field='imageheight' ,
    )
    pic1 = models.ImageField(
        upload_to= 'static/images/products/{0}'.format(strftime("%Y%m%d - %H%M%S",gmtime())) ,
        default = 'no-image.jpg' ,
        null = True, blank = True ,
    )
    pic2 = models.ImageField(
        upload_to= 'static/images/products/{0}'.format(strftime("%Y%m%d - %H%M%S",gmtime())) ,
        default = 'no-image.jpg' ,
        null = True ,blank = True ,
    )
    pic3 = models.ImageField(
        upload_to= 'static/images/products/{0}'.format(strftime("%Y%m%d - %H%M%S",gmtime())) ,
        default = 'no-image.jpg' ,
        null = True, blank = True,
    )
    pic4 = models.ImageField(
        upload_to= 'static/images/products/{0}'.format(strftime("%Y%m%d - %H%M%S" ,gmtime())) ,
        default = 'no-image.jpg' ,
        null = True, blank = True ,
    )
    category=models.ForeignKey(
        KalaCategory ,
        on_delete=models.SET_NULL ,
        null=True ,
        verbose_name="Category" ,
        related_name= 'Category',
        help_text="category" ,
    )
    description=models.TextField(max_length=255 ,null=True, blank=True)
    imagewidth = models.PositiveIntegerField(editable = False, default = 401)
    imageheight = models.PositiveIntegerField(editable = False, default = 401)


    class Meta:
        verbose_name_plural = "Products"

    # Adding brand to admin prepopulated_fields dictionary only returns id ,
    # One way to do is adding save method 
    def save(self):
        if not self.id: # if this is a new item
            newslug = '{0} {1}'.format(self.brand, self.name)  
            self.slug = slugify(unidecode(newslug))
        super(Kala, self).save()

    def __str__(self):
        return self.name
    


class KalaInstance(models.Model):
    kala=models.ForeignKey(Kala ,on_delete=models.CASCADE , related_name='kalainstance')
    saller=models.ForeignKey(User , on_delete=models.CASCADE)
    price=models.BigIntegerField(verbose_name='Price')
    off = models.IntegerField(default=0)
    instock = models.IntegerField()

    class Meta:
        verbose_name_plural = "Product Instances"

    def __str__(self):
        return f"{self.id} : {self.saller}"

    def new_price(self):
        if self.off == 0: 
            return self.price
        else:
            return self.price - self.off



class WishList(models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    product = models.ForeignKey(Kala , on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Wishlist"

    def __str__(self):
        return f"{self.user} : {self.product}"



class Compare(models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    product = models.ForeignKey(Kala , on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Compare"

    def __str__(self):
        return f"{self.user} : {self.product}"



class Post(models.Model):
    title = models.CharField(max_length = 100 , help_text = "Enter title for Post")
    slug = models.SlugField(max_length=255, unique=True ,null=True)
    body = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True  , null=True)
    pic = models.ImageField(
        upload_to="static/images/posts/{0}".format(strftime("%Y%m%d-%H%M%S" , gmtime())) ,
        null=True , blank=True ,default='no-image.jpg' ,
        width_field='imagewidth' ,
        height_field='imageheight' ,
    )
    imagewidth = models.PositiveIntegerField(editable = False, default = 401 , null= True , blank=True)
    imageheight = models.PositiveIntegerField(editable = False, default = 401 , null=True , blank=True)

    class Meta:
        verbose_name_plural = "Post"

    @property
    def short_description(self): 
        return truncatechars(self.body ,250)

    def __str__(self):
        return self.title
    


class Comments(models.Model):

    class StatusChoice(models.TextChoices):
        OK ='T',"It's Ok"
        WAITING ='W',"Waiting"
    
    writer = models.ForeignKey(User , on_delete=models.SET_NULL , null=True )
    body = models.CharField(max_length=500)
    data = models.DateField(auto_now_add=True)
    kala = models.ForeignKey(Kala,on_delete=models.SET_NULL , null=True )
    status = models.CharField(max_length=1 , choices = StatusChoice.choices , default=StatusChoice.WAITING)

    class Meta:
        verbose_name_plural = "Comments"


class Coupon(models.Model):
    code = models.CharField(max_length=20)
    count = models.IntegerField()
    off = models.IntegerField(default=0 , help_text="Off-price")
    expire = models.DateTimeField(verbose_name='Expire Date')

    class Meta:
        verbose_name_plural="Coupons"

    
    def is_expired(self):
        if self.expire < timezone.now():
            return True
        else: 
            return False

    def __str__(self):
        return f"Code : {self.code} - Count : {self.count}"


class Cart(models.Model):

    class SendChoice(models.TextChoices):
        IS_PAYED='T','Payed'
        IS_NOT_PAYED = 'F','Not Payed'
    
    username = models.ForeignKey(User ,on_delete=models.CASCADE)
    product = models.ForeignKey(Kala ,verbose_name="Products" ,on_delete=models.CASCADE)
    color = models.ForeignKey(Color ,on_delete=models.CASCADE  ,related_name="Color")
    size = models.ForeignKey(ProductSize ,on_delete=models.CASCADE ,related_name="ProductSize")
    material = models.ForeignKey(Materials ,on_delete=models.CASCADE ,related_name="Materials")
    saller=models.ForeignKey(KalaInstance ,on_delete=models.CASCADE ,related_name="Instanse" ,null=True)
    count = models.IntegerField(default=1)
    coupon = models.ForeignKey(Coupon ,on_delete=models.CASCADE ,null=True ,blank=True)
    payed = models.CharField(max_length=1 ,choices=SendChoice.choices ,default=SendChoice.IS_NOT_PAYED)  

    class Meta:
        verbose_name_plural ="Carts"
    
    def total(self):
        return self.saller.price * self.count
    
    def total_price(self):
        if self.saller.off !=0:
            return self.total() - self.saller.off
        else:
            return self.total()

    def finally_price(self):
        if self.coupon:
            return self.total_price() - self.coupon.off 
        return self.total_price()

    def __str__(self):
        return f"Product : {self.product} - Saller : {self.saller} - User : {self.username} "



class Salled(models.Model):
    SEND_CHOICES = {
        ('T','Packege sent'),
        ('F','Packege Wait for send'),
        ('B','Back to Store'),
    }
    FollowUpCode = models.CharField(default= '{}{}'.format(random.randint(10,99),strftime('%Y%m%d%H%M%S',gmtime())), max_length = 20)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name = 'Buyer')
    products = models.ManyToManyField(Cart, verbose_name= 'Products')
    company = models.CharField(max_length= 200, null= True, blank = True)
    address = models.CharField(max_length= 500)
    zip_code = models.CharField(max_length= 10, verbose_name = 'Zip Code')
    state = models.ForeignKey(States, on_delete= models.CASCADE)
    city = models.CharField(max_length= 50)
    total_price = models.BigIntegerField(help_text = 'Total Price With offers & Coupons')
    send_price = models.IntegerField()
    tax = models.IntegerField()
    total = models.BigIntegerField(help_text = 'Total Price With offers, Coupons, tax & send price.')
    desc = models.TextField(null= True, blank= True)
    date = models.DateField(auto_now= True)
    sent = models.CharField(help_text= 'Is package sent?', default= 'F', verbose_name= 'Send Status', choices = SEND_CHOICES, max_length = 1)

    def followup(self):
        r = random.randint(10000,99999) 
        return '{}{}'.format(r, self.id)

    def __str__(self):
        return "{0} - {1}".format(self.user.username, self.date)

    class Meta:
        verbose_name_plural = "Salled"


        
class ContactUs(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    description = models.TextField()

    class Meta: 
        verbose_name_plural="Contact-us Table"

    def __str__(self):
        return f"{self.name}, {self.email}"


