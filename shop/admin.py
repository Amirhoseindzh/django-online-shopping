from django.contrib import admin
from django.utils.safestring import mark_safe
from django.contrib.auth import get_user_model
from .models import (
    Brand,
    Cart,
    Color,
    Kala,
    KalaCategory,
    KalaInstance,
    Materials,
    ProductSize,
    Post,
    States,
    Sold,
    WishList,
    Coupon,
    ContactUs,
    Compare,
    ProductComments,
    PostComments,
)

User = get_user_model()

IMAGE_PROPERTIES = '<img src="{url}" width="{width}" height={height} />'


@admin.register(KalaCategory)
class KalaCategoryAdmin(admin.ModelAdmin):
    list_display = [
        "name",
    ]
    prepopulated_fields = {
        "slug": ("name",),
    }
    search_fields = ["name"]
    fields = ["name", "slug"]


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name", "logo_image"]
    readonly_fields = ["logo_image"]
    search_fields = [
        "name",
    ]
    fields = ["name", "slug", "logo", "logo_image"]
    prepopulated_fields = {
        "slug": ("name",),
    }

    def logo_image(self, obj):
        return mark_safe(
            IMAGE_PROPERTIES.format(
                url=obj.logo.url,
                width=80,
                height=80,
            )
        )


@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = [
        "size_no",
    ]


@admin.register(States)
class StatesAdmin(admin.ModelAdmin):
    list_display = ["name", "id"]
    search_fields = [
        "name",
    ]
    order_by = ["A"]


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = [
        "name",
    ]
    search_fields = ["name"]
    order_by = ["A"]


@admin.register(Materials)
class MaterialsAdmin(admin.ModelAdmin):
    list_display = [
        "name",
    ]
    search_fields = ["name"]
    order_by = ["A"]


class KalaInstanceInline(admin.TabularInline):
    model = KalaInstance

    # this method show no extra empty fields from Inline fields
    def get_extra(self, request, obj=None, **kwargs):
        extra = 0
        return extra


@admin.register(Kala)
class KalaAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "category",
        "slug",
        "brand",
        "mini_description",
    ]
    list_editable = [
        "brand",
    ]
    list_filter = [
        "name",
        "category",
        "brand",
        "size",
        "color",
        "material",
    ]
    list_display_links = ("name",)
    sortable_by = [
        "name",
        "category",
    ]
    search_fields = ["name", "category", "brand", "color", "material", "size"]
    prepopulated_fields = {
        "slug": (
            "brand",
            "name",
        )
    }
    fieldsets = (
        (
            "General Info",
            {
                "fields": (
                    "name",
                    "slug",
                    "brand",
                    "category",
                )
            },
        ),
        (
            "Product Info",
            {
                "fields": (
                    "color",
                    "material",
                    "size",
                    "mini_description",
                )
            },
        ),
        (
            "pictures",
            {
                "fields": (
                    "pic0",
                    "pic1",
                    "pic2",
                    "pic3",
                    "pic4",
                )
            },
        ),
        (None, {"fields": ("description",)}),
    )
    inlines = [KalaInstanceInline]


@admin.register(KalaInstance)
class KaLaInstanceAdmin(admin.ModelAdmin):
    list_display = [
        "kala",
        "seller",
        "price",
        "off",
        "instock",
    ]
    list_filter = [
        "kala",
        "seller",
        "price",
        "off",
    ]
    list_display_links = [
        "kala",
        "seller",
    ]
    sortable_by = [
        "kala",
        "seller",
        "price",
        "off",
    ]
    search_fields = [
        "kala",
        "seller",
    ]
    list_editable = ["off", "instock"]


@admin.register(WishList)
class WishListAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "user",
        "create_at",
    ]
    fields = [
        "product",
        "user",
        "create_at",
    ]
    readonly_fields = [
        "create_at",
    ]


@admin.register(Compare)
class CompareAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "user",
        "create_at",
    ]
    fields = [
        "product",
        "user",
        "create_at",
    ]
    readonly_fields = [
        "create_at",
    ]


@admin.register(Sold)
class SoldAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "grand_total",
        "created_at",
        "send_status",
    ]
    search_fields = ["products", "user"]
    list_filter = [
        "user",
        "grand_total",
        "created_at",
        "send_status",
    ]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "short_description", "published_date", "post_image"]
    list_filter = ["published_date"]
    search_fields = [
        "title",
        "short_description",
    ]
    fields = ["title", "slug", "author", "body", "pic", "post_image", "published_date"]
    prepopulated_fields = {
        "slug": ("title",),
    }
    readonly_fields = ["post_image", "published_date"]

    def post_image(self, obj):
        try:
            return mark_safe(
                IMAGE_PROPERTIES.format(
                    url=obj.pic.url,
                    width=200,
                    height=200,
                )
            )
        except ValueError:
            print("go back")


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "off",
        "count",
        "expire",
    ]
    list_filter = [
        "count",
        "off",
        "expire",
    ]
    search_fields = [
        "code",
    ]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "product",
        "count",
        "seller",
        "coupon",
        "paid",
    ]
    list_filter = [
        "product",
        "seller",
        "paid",
    ]
    search_fields = [
        "username",
        "seller",
        "product",
    ]


@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "email",
    ]
    search_fields = [
        "name",
        "email",
    ]
    sortable_by = [
        "name",
        "email",
    ]
    order_by = ["name"]


@admin.register(ProductComments)
class ProductCommentAdmin(admin.ModelAdmin):
    list_display = [
        "author",
        "body",
        "created_at",
        "kala",
        "status",
    ]
    search_fields = [
        "author",
        "kala",
        "body",
    ]


@admin.register(PostComments)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = [
        "author",
        "body",
        "post",
        "status",
        "created_at",
    ]
    search_fields = [
        "author",
        "kala",
        "body",
    ]
