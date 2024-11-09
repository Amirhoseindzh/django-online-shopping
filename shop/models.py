from django.db import models
from django.utils import timezone
from django.template.defaultfilters import truncatechars
from django.utils.translation import gettext_lazy as _
from django.conf import settings 
from time import gmtime, strftime
import random

User = settings.AUTH_USER_MODEL

PRODUCT_IMAGE_ADDRESS = "static/images/products/{0}"
DEFAULt_IMAGE_ADDRESS = "no-image.jpg"


class States(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "States"

    def __str__(self):
        return f"{self.name}"


class KalaCategory(models.Model):
    slug = models.SlugField(allow_unicode=True)
    name = models.CharField(max_length=100)

    class meta:
        verbose_name_plural = "Product Category-s"

    def __str__(self):
        return f"{self.name}"


class Brand(models.Model):
    slug = models.SlugField(allow_unicode=True)
    name = models.CharField(max_length=50)
    logo = models.ImageField(
        upload_to="static/images/logos/",
        default=DEFAULt_IMAGE_ADDRESS,
        null=True,
        blank=True,
        width_field="image_width",
        height_field="image_height",
    )
    image_width = models.PositiveIntegerField(editable=False, default=50)
    image_height = models.PositiveIntegerField(editable=False, default=50)

    class Meta:
        verbose_name_plural = "Brand"

    def __str__(self):
        return self.name


class ProductSize(models.Model):
    size_no = models.CharField(max_length=20, help_text="Enter a product size")

    class Meta:
        verbose_name_plural = "Product Sizes"

    def __str__(self):
        return self.size_no


class Color(models.Model):
    name = models.CharField(max_length=20, help_text="Enter a Product Color")

    class Meta:
        verbose_name_plural = "Product Colors"

    def __str__(self):
        return self.name


class Materials(models.Model):
    name = models.CharField(max_length=20, help_text="Enter a Product Materials")

    class Meta:
        verbose_name_plural = "Product Materials"

    def __str__(self):
        return self.name


class Kala(models.Model):
    slug = models.SlugField(allow_unicode=True, null=True)
    name = models.CharField(max_length=150)
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Brand",
        related_name="brand",
    )
    size = models.ManyToManyField(ProductSize, help_text="Enter Size of the product")
    mini_description = models.CharField(max_length=200)
    color = models.ManyToManyField(Color, help_text="Select Color of the product")
    material = models.ManyToManyField(
        Materials, help_text="Select Material of the Product"
    )
    pic0 = models.ImageField(
        upload_to=PRODUCT_IMAGE_ADDRESS.format(strftime("%Y%m%d-%H%M%S", gmtime())),
        default=DEFAULt_IMAGE_ADDRESS,
        width_field="image_width",
        height_field="image_height",
    )
    pic1 = models.ImageField(
        upload_to=PRODUCT_IMAGE_ADDRESS.format(strftime("%Y%m%d - %H%M%S", gmtime())),
        default=DEFAULt_IMAGE_ADDRESS,
        null=True,
        blank=True,
    )
    pic2 = models.ImageField(
        upload_to=PRODUCT_IMAGE_ADDRESS.format(strftime("%Y%m%d - %H%M%S", gmtime())),
        default=DEFAULt_IMAGE_ADDRESS,
        null=True,
        blank=True,
    )
    pic3 = models.ImageField(
        upload_to=PRODUCT_IMAGE_ADDRESS.format(strftime("%Y%m%d - %H%M%S", gmtime())),
        default=DEFAULt_IMAGE_ADDRESS,
        null=True,
        blank=True,
    )
    pic4 = models.ImageField(
        upload_to=PRODUCT_IMAGE_ADDRESS.format(strftime("%Y%m%d - %H%M%S", gmtime())),
        default=DEFAULt_IMAGE_ADDRESS,
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        KalaCategory,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Category",
        related_name="Category",
        help_text="category",
    )
    description = models.TextField(max_length=255, blank=True, null=True)
    image_width = models.PositiveIntegerField(editable=False, default=401)
    image_height = models.PositiveIntegerField(editable=False, default=401)

    class Meta:
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name


class KalaInstance(models.Model):
    kala = models.ForeignKey(
        Kala, on_delete=models.CASCADE, related_name="kala_instance"
    )
    seller = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    price = models.BigIntegerField(verbose_name="Price")
    off = models.IntegerField(default=0)
    instock = models.IntegerField()

    class Meta:
        verbose_name_plural = "Product Instances"

    def __str__(self):
        return f"{self.pk} : {self.seller}"

    def new_price(self):
        if self.off == 0:
            return self.price
        else:
            return self.price - self.off


class WishList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Kala, on_delete=models.CASCADE, null=True)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Wishlist"

    def __str__(self):
        return f"{self.user} : {self.product}"


class Compare(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Kala, on_delete=models.CASCADE, null=True)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Compare"

    def __str__(self):
        return f"{self.user} : {self.product}"


class Post(models.Model):
    title = models.CharField(max_length=100, help_text="Enter title for Post")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255, unique=True, null=True)
    body = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True, null=True)
    pic = models.ImageField(
        upload_to="static/images/posts/{0}".format(strftime("%Y%m%d-%H%M%S", gmtime())),
        null=True,
        blank=True,
        default=DEFAULt_IMAGE_ADDRESS,
        width_field="image_width",
        height_field="image_height",
    )
    image_width = models.PositiveIntegerField(
        editable=False, default=401, null=True, blank=True
    )
    image_height = models.PositiveIntegerField(
        editable=False, default=401, null=True, blank=True
    )

    class Meta:
        verbose_name_plural = "Post"

    @property
    def short_description(self):
        return truncatechars(self.body, 250)

    def __str__(self):
        return self.title


class ProductComments(models.Model):
    class StatusChoice(models.TextChoices):
        OK = "T", "It's Ok"
        WAITING = "W", "Waiting"

    kala = models.ForeignKey(Kala, on_delete=models.SET_NULL, null=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    body = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=1, choices=StatusChoice.choices, default=StatusChoice.WAITING
    )

    class Meta:
        verbose_name_plural = "Product Comments"

    def __str__(self):
        if self.author and self.kala is not None:
            return f"Comment by {self.author.username} on {self.kala.name}"


class PostComments(models.Model):
    class StatusChoice(models.TextChoices):
        OK = "T", "It's Ok"
        WAITING = "W", "Waiting"

    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=1, choices=StatusChoice.choices, default=StatusChoice.WAITING
    )

    class Meta:
        verbose_name_plural = "Post Comments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"


class Coupon(models.Model):
    code = models.CharField(max_length=20)
    count = models.IntegerField()
    off = models.IntegerField(default=0, help_text="Off-price")
    expire = models.DateTimeField(verbose_name="Expire Date")

    class Meta:
        verbose_name_plural = "Coupons"

    def is_expired(self):
        if self.expire < timezone.now():
            return True
        else:
            return False

    def __str__(self):
        return f"Code : {self.code} - Count : {self.count}"


class Cart(models.Model):
    class SendChoice(models.TextChoices):
        IS_PAYED = "T", "Payed"
        IS_NOT_PAYED = "F", "Not Payed"

    username = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(
        Kala, verbose_name="Products", on_delete=models.CASCADE, null=True
    )
    color = models.ForeignKey(
        Color, on_delete=models.CASCADE, related_name="Color", null=True
    )
    size = models.ForeignKey(
        ProductSize, on_delete=models.CASCADE, related_name="ProductSize", null=True
    )
    material = models.ForeignKey(
        Materials, on_delete=models.CASCADE, related_name="Materials", null=True
    )
    seller = models.ForeignKey(
        KalaInstance, on_delete=models.CASCADE, related_name="Instance", null=True
    )
    count = models.IntegerField(default=1)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, null=True, blank=True)
    payed = models.CharField(
        max_length=1, choices=SendChoice.choices, default=SendChoice.IS_NOT_PAYED
    )

    class Meta:
        verbose_name_plural = "Carts"

    def total(self):
        if self.seller is not None:
            return self.seller.price * self.count
        else:
            return 0

    def _get_discount(self, discount):
        """Helper method to safely return discount or 0 if None."""
        return discount if discount is not None else 0

    def total_price(self):
        seller_discount = self._get_discount(self.seller.off) if self.seller else 0
        total_price = max(self.total() - seller_discount, 0)  # Prevent negative price
        return total_price

    def finally_price(self):
        total_price = self.total_price()
        coupon_discount = self._get_discount(self.coupon.off) if self.coupon else 0
        final_price = max(total_price - coupon_discount, 0)  # Prevent negative price
        return final_price

    def __str__(self):
        return f"Product : {self.product} - Seller : {self.seller} - User : {self.username}"


class Sold(models.Model):
    SEND_CHOICES = {
        ("T", "Package sent"),
        ("F", "Package Wait for send"),
        ("B", "Back to Store"),
    }
    FollowUpCode = models.CharField(
        default="{}{}".format(
            random.randint(10, 99), strftime("%Y%m%d%H%M%S", gmtime())
        ),
        max_length=20,
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Buyer", null=True
    )
    products = models.ManyToManyField(Cart, verbose_name="Products")
    company = models.CharField(max_length=200, blank=True, null=True)
    address = models.CharField(max_length=500)
    zip_code = models.CharField(max_length=10, verbose_name="Zip Code")
    state = models.ForeignKey(States, on_delete=models.CASCADE)
    city = models.CharField(max_length=50)
    total_price = models.BigIntegerField(help_text="Total Price With offers & Coupons")
    send_price = models.IntegerField()
    tax = models.IntegerField()
    total = models.BigIntegerField(
        help_text="Total Price With offers, Coupons, tax & send price."
    )
    desc = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now=True)
    sent = models.CharField(
        help_text="Is package sent?",
        default="F",
        verbose_name="Send Status",
        choices=SEND_CHOICES,
        max_length=1,
    )

    def followup(self):
        r = random.randint(10000, 99999)
        return "{}{}".format(r, self.pk)

    def __str__(self):
        if self.user is not None:
            return "{0} - {1}".format(self.user.username, self.date)

    class Meta:
        verbose_name_plural = "Sold"


class ContactUs(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    description = models.TextField()

    class Meta:
        verbose_name_plural = "Contact-us Table"

    def __str__(self):
        return f"{self.name}, {self.email}"
