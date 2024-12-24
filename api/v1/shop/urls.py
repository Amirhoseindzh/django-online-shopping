from django.urls import include, path
from rest_framework import routers
from .views import (
    ProductDetailView,
    CartViewSet,
    ProductCommentViewSet,
    PostReadOnlyViewSet,
)

router = routers.DefaultRouter()
router.register(r"cart", CartViewSet, basename="cart")
router.register(r"comments", ProductCommentViewSet, basename="product-comments")
router.register(r"posts", PostReadOnlyViewSet, basename="post")


urlpatterns = [
    path("", include(router.urls)),
    path("product/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
]
