from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from django.contrib.auth import get_user_model
from shop.models import (
    KalaCategory,
    Kala,
    KalaInstance,
    Cart,
    ProductComments,
    Rating,
    Post,
    Compare,
    PostComments,
    WishList,
)
from api.v1.accounts.serializers import UserSerializer

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = KalaCategory
        fields = ["id", "name"]


class ProductSerializer(ModelSerializer):
    category = CategorySerializer(read_only=True)  # Nested category details

    class Meta:
        model = Kala
        fields = "__all__"


class RelatedProductSerializer(ModelSerializer):
    category = CategorySerializer(read_only=True)  # Nested category details

    class Meta:
        model = Kala
        exclude = (
            "color",
            "size",
            "material",
            "mini_description",
            "description",
        )


class ProductInstanceSerializer(ModelSerializer):
    kala = ProductSerializer(read_only=True)
    seller = UserSerializer(read_only=True)

    class Meta:
        model = KalaInstance
        fields = [
            "kala",
            "seller",
            "price",
            "off",
            "instock",
        ]


class AddToCartSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False)

    class Meta:
        model = Cart
        fields = "__all__"


class CartSerializer(serializers.ModelSerializer):
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    finally_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Cart
        fields = [
            "id",
            "user",
            "product",
            "color",
            "size",
            "material",
            "seller",
            "count",
            "coupon",
            "paid",
            "total_price",
            "finally_price",
        ]
        read_only_fields = ["user", "total_price", "finally_price"]

    def validate_count(self, value):
        if value < 1:
            raise serializers.ValidationError("Count must be at least 1.")
        return value


class RatingSerializer(ModelSerializer):
    class Meta:
        model = Rating
        fields = "__all__"


class ProductCommentSerializer(ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)
    replies = serializers.SerializerMethodField()
    # rating = RatingSerializer()

    class Meta:
        model = ProductComments
        fields = [
            "id",
            "kala",
            "author",
            "author_username",
            "body",
            "rating",
            "created_at",
            "updated_at",
            "replies",
        ]
        read_only_fields = [
            "id",
            "author",
            "created_at",
            "updated_at",
            "status",
            "replies",
        ]

    def get_replies(self, obj):
        """Fetch replies for the comment."""
        replies = obj.replies.filter(is_active=True)
        return ProductCommentSerializer(replies, many=True).data


class PostSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"
