from django.urls import path
from .views import (
    KalaListView,
    CategoryListView,
    CategoryListViewInstock,
    CategoryPriceFilterListView,
    BrandListView,
    BrandListViewInstock,
    BrandPriceFilter,
    BrandCategory,
    BrandCategoryInstock,
    BrandCategoryPriceFilter,
    SearchKala,
    Address,
    Profile,
    PostListView,
    PostDetailView,
    kala_detail_view,
    wishlist,
    compare,
    about_us,
    account_dashboard,
    activate,
    logout_user,
    account_orders,
    brands,
    cart_,
    checkout,
    contact_us,
    faq,
    create_comment,
    terms_and_conditions,
    track_order,
    error_404,
    error_500,
)


from django.contrib.auth.views import (
    # ...
    PasswordChangeView,
    PasswordChangeDoneView,
)
from django.urls import reverse_lazy


urlpatterns = [
    path("", KalaListView.as_view(), name="index"),
    path("kala/<slug:kalaslug>/", kala_detail_view, name="KalaDetailView"),
    path(
        "category/<slug:catslug>/", CategoryListView.as_view(), name="CategoryListView"
    ),
    path(
        "category/<slug:catslug>/instock/",
        CategoryListViewInstock.as_view(),
        name="CategoryInstock",
    ),
    path(
        "category/<slug:catslug>/instock/<int:minPrice>/<int:maxPrice>/",
        CategoryPriceFilterListView.as_view(),
        name="CategoryPriceFilter",
    ),
    path("brands/<slug:brandslug>/", BrandListView.as_view(), name="BrandListView"),
    path(
        "brands/<slug:brandslug>/instock/",
        BrandListViewInstock.as_view(),
        name="BrandListViewInstock",
    ),
    path(
        "brands/<slug:brandslug>/instock/<int:minPrice>/<int:maxPrice>/",
        BrandPriceFilter.as_view(),
        name="BrandPriceFilter",
    ),
    path(
        "category/<slug:catslug>/<slug:brandslug>/",
        BrandCategory.as_view(),
        name="BrandCategory",
    ),
    path(
        "category/<slug:catslug>/<slug:brandslug>/instock/",
        BrandCategoryInstock.as_view(),
        name="BrandCategoryInstock",
    ),
    path(
        "category/<slug:catslug>/<slug:brandslug>/instock/<int:minPrice>/<int:maxPrice>/",
        BrandCategoryPriceFilter.as_view(),
        name="BrandCategoryPriceFilter",
    ),
    path("wishlist/", wishlist, name="wishlist"),
    path("compare/", compare, name="compare"),
    path("search/", SearchKala.as_view(), name="search_kala"),
    path("about_us/", about_us, name="about-us"),
    path("address/", Address.as_view(), name="addresses"),
    path("dashboard/", account_dashboard, name="dashboard"),
    path("activate/<uidb64>/<token>", activate, name="activate"),
    path("profile/", Profile.as_view(), name="profile"),
    path("logout/", logout_user, name="logout"),
    path("orders/", account_orders, name="orders"),
    path("brands/", brands, name="brands"),
    path("cart/", cart_, name="cart"),
    # path('cart/cart-empty/',cart_empty , name = "cart-empty" ),
    path("checkout/", checkout, name="checkout"),
    path("contact-us/", contact_us, name="contact-us"),
    path("faq/", faq, name="faq"),
    path("blog/", PostListView.as_view(), name="blog"),
    path("blog/post/<slug:slug>/", PostDetailView.as_view(), name="PostDetailView"),
    path("blog/post/<int:post_id>/comment/", create_comment, name="create_comment"),
    # path('blog/search/', search_post, name='search_post'),
    path("terms_and_conditions/", terms_and_conditions, name="terms_and_conditions"),
    path("track_order/", track_order, name="track_order"),
    path(
        "password_change/",
        PasswordChangeView.as_view(
            template_name="account-password.html",
            success_url=reverse_lazy("password_change_done"),
        ),
        name="change-password",
    ),
    path(
        "password_change/done/",
        PasswordChangeDoneView.as_view(template_name="password_change_done.html"),
        name="password_change_done",
    ),
]


handler404 = error_404
handler500 = error_500
