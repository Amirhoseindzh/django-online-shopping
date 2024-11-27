from django.db import models
from django.utils import timezone
from django.template.defaultfilters import truncatechars
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.conf import settings
from decimal import Decimal
from time import gmtime, strftime
import random
import os
from uuid import uuid4

User = settings.AUTH_USER_MODEL

PRODUCT_IMAGE_ADDRESS = "static/images/products/{0}"
DEFAULt_IMAGE_ADDRESS = "no-image.jpg"


def kala_directory_path(instance, filename):
    # Extract the file extension
    ext = filename.split('.')[-1]
    # Use the product's ID if available, otherwise generate a unique identifier
    kala_id = instance.kala.id if instance.kala and instance.kala.id else uuid4().hex[:8]
    # Generate a unique filename using a UUID and timestamp
    unique_filename = f"user_{kala_id}_{strftime('%Y%m%d-%H%M%S', gmtime())}_{uuid4().hex[:8]}.{ext}"
    # Construct the path, grouping by product ID for organization if available
    return os.path.join('static', 'images', 'products', f"product_{kala_id}", unique_filename)


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
        upload_to=kala_directory_path,
        default=DEFAULt_IMAGE_ADDRESS,
        width_field="image_width",
        height_field="image_height",
    )
    pic1 = models.ImageField(
        upload_to=kala_directory_path,
        default=DEFAULt_IMAGE_ADDRESS,
        null=True,
        blank=True,
    )
    pic2 = models.ImageField(
        upload_to=kala_directory_path,
        default=DEFAULt_IMAGE_ADDRESS,
        null=True,
        blank=True,
    )
    pic3 = models.ImageField(
        upload_to=kala_directory_path,
        default=DEFAULt_IMAGE_ADDRESS,
        null=True,
        blank=True,
    )
    pic4 = models.ImageField(
        upload_to=kala_directory_path,
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


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Kala, on_delete=models.CASCADE, related_name="ratings")
    score = models.PositiveSmallIntegerField(validators=[
        MinLengthValidator(1), MaxLengthValidator(5)
    ])
    review = models.TextField(blank=True, null=True)  # Optional review
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")  # Ensure one rating per user per product
        ordering = ["-created_at"]  # Show the latest reviews first

    def __str__(self):
        return f"{self.user} rated {self.product.name} ({self.score or 'No Rating'})"

    @property
    def has_rating(self):
        return self.score is not None

class ProductComments(models.Model):
    class StatusChoice(models.TextChoices):
        APPROVED = "A", "Approved"
        PENDING = "P", "Pending"
        REJECTED = "R", "Rejected"

    kala = models.ForeignKey(
        "Kala", on_delete=models.SET_NULL, null=True, related_name="comments"
    )
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="comments"
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    body = models.TextField(max_length=1000, null=True, help_text="Write your comment here.")
    rating = models.OneToOneField(
        Rating, on_delete=models.SET_NULL, null=True, blank=True, related_name="comment"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    status = models.CharField(
        max_length=1, choices=StatusChoice.choices, default=StatusChoice.PENDING
    )

    class Meta:
        verbose_name = "Product Comment"
        verbose_name_plural = "Product Comments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.author.username if self.author else 'Unknown'} on {self.kala.name if self.kala else 'Unknown'}"

    @property
    def is_reply(self):
        return self.parent is not None


class PostComments(models.Model):
    class StatusChoice(models.TextChoices):
        APPROVED = "A", "Approved"
        PENDING = "P", "Pending"
        REJECTED = "R", "Rejected"

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    body = models.TextField(max_length=1000, null=True, help_text="Write your comment here.")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    status = models.CharField(
        max_length=1, choices=StatusChoice.choices, default=StatusChoice.PENDING
    )

    class Meta:
        verbose_name_plural = "Post Comments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author.username} commented on {self.post.title}"
    
    @property
    def is_reply(self):
        return self.parent is not None


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
        IS_PAID = "T", "Paid"
        IS_NOT_PAID = "F", "Not Paid"

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(
        Kala,
        verbose_name="Products",
        related_name="Cart_Product",
        on_delete=models.CASCADE,
        null=True,
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
    paid = models.CharField(
        max_length=1, choices=SendChoice.choices, default=SendChoice.IS_NOT_PAID
    )

    class Meta:
        verbose_name_plural = "Carts"

    def total(self):
        """
        Calculates the total price for the product (price * count).
        """
        if self.seller and self.seller.price is not None:
            return self.seller.price * self.count
        else:
            return 0

    def _get_discount(self, discount):
        """Helper method to safely return discount or 0 if None."""
        return Decimal(discount) if discount is not None else Decimal(0)

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
        return f"Product : {self.product} - Seller : {self.seller} - User : {self.user}"


class Sold(models.Model):
    class SendChoice(models.TextChoices):
        SENT = "T", "Package Sent"
        WAITING = "F", "Package Wait for send"
        BACK = "B", "Back to Store"

    follow_up_code = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Buyer", null=True
    )
    products = models.ManyToManyField(
        Cart, verbose_name="Products", related_name="Sold_Product"
    )
    company = models.CharField(max_length=200, blank=True, null=True)
    address = models.CharField(max_length=500)
    zip_code = models.CharField(max_length=10, verbose_name="Zip Code")
    state = models.ForeignKey(States, on_delete=models.CASCADE)
    city = models.CharField(max_length=50)
    total_price = models.BigIntegerField(
        help_text="Total price after discounts and coupons."
    )
    shipping_fee = models.IntegerField(help_text="Shipping fee applied.")
    tax = models.IntegerField(help_text="Tax applied to the total price.")
    grand_total = models.BigIntegerField(
        help_text="Total Price With discounts, coupons, tax & shipping fee."
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateField(auto_now=True)
    send_status = models.CharField(
        help_text="Current shipping status of the order",
        default=SendChoice.WAITING,
        verbose_name="Send Status",
        choices=SendChoice.choices,
        max_length=1,
    )

    def save(self, *args, **kwargs):
        if not self.follow_up_code:
            self.follow_up_code = self.generate_followup_code()
        super().save(*args, **kwargs)

    def generate_followup_code(self):
        """Generates a unique follow-up code for each order."""
        return f"{random.randint(10, 99)}{timezone.now().strftime('%Y%m%d-%H%M%S')}"

    def __str__(self):
        buyer = self.user.username if self.user else "Unknown Buyer"
        return f"Order by {buyer} on {self.created_at}"

    def get_shipping_status_display(self):
        """Returns a human-readable shipping status.
        uses Django's built-in functionality to retrieve
        the human-readable label for a field defined with 'choices'.
        """
        return self.get_send_status_display()

    class Meta:
        verbose_name_plural = "Sold Orders"


class ContactUs(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    description = models.TextField()

    class Meta:
        verbose_name_plural = "Contact-us Table"

    def __str__(self):
        return f"{self.name}, {self.email}"
