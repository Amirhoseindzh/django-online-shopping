from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    IsAuthenticatedOrReadOnly,
)
from .serializers import (
    ProductInstanceSerializer,
    RelatedProductSerializer,
    CartSerializer,
    ProductCommentSerializer,
    PostSerializer,
)
from shop.models import (
    Kala as Product,
    KalaInstance,
    Cart,
    ProductComments,
    Post,
)


User = get_user_model()


class ProductDetailView(APIView):
    """view to product detail in website.

    Returns:
        API: return product details and related products in GET,
        send selected product items to cart in POST.
    """

    permission_classes = [AllowAny]

    def get(self, request, pk):
        """
        Fetch product details and a simplified list serializer for all products.
        """
        try:
            product = get_object_or_404(Product, id=pk)
            instance = get_object_or_404(KalaInstance, id=pk)
            related_products = Product.objects.filter(
                category=product.category
            ).exclude(id=product.id)

            product_instance_serializer = ProductInstanceSerializer(instance)
            related_products_serializer = RelatedProductSerializer(
                related_products, many=True
            )

            return Response(
                {
                    "product_detail": product_instance_serializer.data,
                    "related_products": related_products_serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
            )


class CartViewSet(ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Ensure users only access their own cart items and prefetch related objects
        return Cart.objects.filter(user=self.request.user).select_related(
            "product", "color", "size", "material", "seller", "coupon"
        )

    def perform_create(self, serializer):
        # Automatically associate the cart with the authenticated user
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"], url_path="checkout")
    def checkout(self, request):
        """
        Custom action to handle cart checkout.
        - Checks if all items are valid for payment.
        """
        user_cart = self.get_queryset().filter(paid="F")  # Only unpaid items
        if not user_cart.exists():
            return Response({"detail": "No items in the cart to checkout."}, status=400)

        total_price = sum(item.finally_price() for item in user_cart)

        # Mark all items as paid after successful payment
        user_cart.update(paid="T")
        return Response({"detail": "Checkout successful", "total_price": total_price})

    @action(detail=False, methods=["put"], url_path="bulk-update")
    def bulk_update(self, request):
        """
        Update multiple cart items' counts or apply coupons in one request.
        """
        updates = request.data.get("updates", [])
        if not updates:
            return Response(
                {"detail": "No updates provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        errors = []
        for item in updates:
            cart_id = item.get("id")
            count = item.get("count")
            coupon_id = item.get("coupon")

            try:
                cart = self.get_queryset().get(id=cart_id)
                if count:
                    if count < 1:
                        raise ValueError("Count must be at least 1.")
                    cart.count = count
                if coupon_id:
                    cart.coupon_id = coupon_id
                cart.save()
            except Cart.DoesNotExist:
                errors.append(f"Cart item with id {cart_id} does not exist.")
            except ValueError as e:
                errors.append(str(e))

        if errors:
            return Response(
                {"detail": "Some updates failed.", "errors": errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"detail": "Bulk update successful."}, status=status.HTTP_200_OK
        )


class ProductCommentViewSet(ModelViewSet):
    queryset = ProductComments.objects.filter(is_active=True).select_related(
        "author", "kala"
    )
    serializer_class = ProductCommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Automatically assign the logged-in user as the author
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        # Soft delete the comment
        instance.is_active = False
        instance.save()


class PostReadOnlyViewSet(ReadOnlyModelViewSet):
    queryset = Post.objects.all().order_by("-published_date")
    serializer_class = PostSerializer
    filter_backends = (
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    )
    search_fields = ["title", "author__username", "body"]
    ordering_fields = ["title", "published_date"]
    ordering = ["-published_date"]
