from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.forms import ValidationError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView
from django.views.generic.base import ContextMixin
from django.views.decorators.csrf import csrf_exempt
import json
from .decorators import check_wishlist_compare_cart
from .utils import CartCalculator, CheckoutProcessor
from .forms import CommentForm
from .forms import CheckoutForm, PriceFilter
from .models import (
    Brand,
    Cart,
    Color,
    Compare,
    ContactUs,
    Coupon,
    Kala,
    KalaCategory,
    KalaInstance,
    Materials,
    Post,
    PostComments,
    ProductComments,
    ProductSize,
    Sold,
    States,
    WishList,
)
from accounts.models import Address

User = get_user_model()


@login_required(login_url="account_login")
def logout_user(request):
    logout(request)
    messages.success(request, (_("شما از حساب خود خارج شدید!")))
    return redirect("account_login")


class KalaListView(ListView):
    model = Kala
    context_object_name = "kala"
    template_name = "index.html"
    paginate_by = 12

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("account_login")  # Redirect to login if not authenticated

        kala_id = request.POST.get("kala")
        action = request.POST.get("action")  # Generalize action handling

        try:
            if action == "addCart":
                self.add_to_cart(request, kala_id)
            elif action == "addWishlist":
                self.toggle_wishlist(request, kala_id)
            elif action == "addCompare":
                self.toggle_compare(request, kala_id)
            else:
                messages.error(request, "Invalid action.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            
        return redirect(request.META.get("HTTP_REFERER", "/"))

    def add_to_cart(self, request, kala_id):
        kala = get_object_or_404(Kala, id=kala_id)
        color = Color.objects.get(id=request.POST.get("Color"))
        seller = KalaInstance.objects.get(id=request.POST.get("Seller"))
        size = ProductSize.objects.get(id=request.POST.get("Size"))
        material = Materials.objects.get(id=request.POST.get("Material"))

        # Check if item already exists in cart
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product_id=kala,
            color=color,
            size=size,
            material=material,
            seller=seller,
            paid="F",
        )

        if not created:
            cart_item.count += 1
            cart_item.save()

    def toggle_wishlist(self, request, kala_id):
        kala = get_object_or_404(Kala, id=kala_id)
        wishlist_item, created = WishList.objects.get_or_create(
            user=request.user, product_id=kala
        )
        if not created:
            wishlist_item.delete()

    def toggle_compare(self, request, kala_id):
        kala = get_object_or_404(Kala, id=kala_id)
        compare_item, created = Compare.objects.get_or_create(
            user=request.user, product_id=kala
        )
        if not created:
            compare_item.delete()
    
    def get_most_sold(self):
        return Cart.objects.annotate(num_kalas=Count("seller")).order_by("-num_kalas")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "most_sold": self.get_most_sold(),
                "instock": KalaInstance.objects.exclude(instock=0),
                "Brands": Brand.objects.all(),
                "posts": Post.objects.all(),
            }
        )
        return context



@login_required
def add_or_remove(request, model, kala_id, message):
    try:
        product = model.objects.filter(user=request.user, product_id=kala_id)
        if product:
            product.delete()
        else:
            model.objects.create(user=request.user, product_id=kala_id)
        return redirect(request.META.get("HTTP_REFERER"))
    except Kala.DoesNotExist:
        return HttpResponse(message)


@check_wishlist_compare_cart
def kala_detail_view(request, kalaslug):
    k = get_object_or_404(Kala, slug=kalaslug)
    all_kala = Kala.objects.filter(category=k.category)
    comments = ProductComments.objects.filter(kala=k)

    # Filter in-stock instances and set default instance for pre-selected values
    instance = KalaInstance.objects.filter(kala=k, instock__gt=0)
    first_inst = instance.first() if instance else None

    if request.method == "POST":
        if "addComment" in request.POST:
            text = request.POST.get("text", "")
            ProductComments.objects.create(writer=request.user, body=text, Kala=k)

        elif "addWishlist" in request.POST:
            kala_id = request.POST.get("kala")
            return add_or_remove(request, WishList, kala_id, "کالا مورد نظر موجود نیست")

        elif "addCompare" in request.POST:
            kala_id = request.POST.get("kala")
            return add_or_remove(request, Compare, kala_id, "کالا مورد نظر موجود نیست")

    context = {
        "kala": k,
        "Allkala": all_kala,
        "comments": comments,
        "inst": instance,
        "is_authenticated": request.user.is_authenticated,
        "finst": first_inst,
        "in_wishlist": request.in_wishlist,
        "in_compare": request.in_compare,
        "in_cart": request.in_cart,
    }
    return render(request, "product.html", context)


@csrf_exempt
@login_required
def update_cart_status(request):
    if request.method == "POST":
        try:
            # Parse the request data
            data = json.loads(request.body)
            slug = data.get("slug")
            add_to_cart = data.get("addToCart")
            quantity = int(data.get("quantity", 1))
            color_id = data.get("color")
            size_id = data.get("size")
            material_id = data.get("material")
            seller_id = data.get("seller")

            # Ensure the product exists
            product = Kala.objects.filter(slug=slug).first()
            if not product:
                return JsonResponse({"success": False, "error": "محصول یافت نشد."})

            # Fetch the related instances
            color = Color.objects.filter(id=color_id).first()
            size = ProductSize.objects.filter(id=size_id).first()
            material = Materials.objects.filter(id=material_id).first()
            seller = KalaInstance.objects.filter(id=seller_id).first()

            # Validate that all attributes are selected
            if not all([color, size, material, seller]):
                return JsonResponse(
                    {"success": False, "error": "لطفاً تمام مشخصات کالا را انتخاب کنید."}
                )

            # Handle adding or removing the item
            cart_item, created = Cart.objects.get_or_create(
                user=request.user,
                product=product,
                color=color,
                size=size,
                material=material,
                seller=seller,
                defaults={"count": quantity, "paid": "F"},
            )

            if add_to_cart:
                if not created:
                    # If the item already exists, increment the count
                    cart_item.count += quantity
                    cart_item.save()
            else:
                # Remove the item from the cart
                cart_item.delete()

            return JsonResponse(
                {"success": True, "message": "عملیات با موفقیت انجام شد."}
            )
        except Exception as e:
            # Log error and send a response
            print(f"Error updating cart: {e}")
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "روش درخواست نامعتبر است."})


def category_or_instock_slugger(category_slug):
    kala_category = get_object_or_404(KalaCategory, slug=category_slug)
    kalas = kala_category.Category.all()
    category = kala_category

    return kalas, category


def just_in_stock(kalas):
    kalas_list = []
    for i in kalas:
        if i.kala_instance.filter(~Q(instock=0)):
            kalas_list.append(i)
    return kalas_list


def max_min_price(kalas, minPrice, maxPrice):
    kalas_list = []
    for i in kalas:
        if i.kala_instance.filter(~Q(instock=0)):
            if i.kala_instance.filter(price__lte=maxPrice):
                if len(i.kala_instance.filter(price__gt=minPrice)):
                    kalas_list.append(i)
    return kalas_list


class CategoryListView(ListView):
    model = Kala
    context_object_name = "kalas"
    template_name = "shop-grid.html"
    paginate_by = 12

    def get_queryset(self):
        # Retrieve queryset based on category slug or other filters
        category_slug = self.kwargs.get("catslug")
        queryset, _ = category_or_instock_slugger(category_slug)

        # Apply price filtering if provided in GET parameters
        min_price = self.request.GET.get("minPrice")
        max_price = self.request.GET.get("maxPrice")
        if min_price and max_price:
            queryset = queryset.filter(price__gte=min_price, price__lte=max_price)

        return queryset

    def get_most_sold_items(self):
        return Cart.objects.annotate(num_kalas=Count("seller")).order_by("-num_kalas")

    def post(self, request, *args, **kwargs):
        form = PriceFilter(request.POST)
        if form.is_valid():
            min_price = form.cleaned_data["minPrice"]
            max_price = form.cleaned_data["maxPrice"]
            url = reverse(
                "CategoryPriceFilter",
                kwargs={
                    "catslug": self.kwargs["catslug"],
                    "minPrice": min_price,
                    "maxPrice": max_price,
                },
            )
            return HttpResponseRedirect(url)
        return HttpResponseRedirect(
            reverse(
                "CategoryListViewInstock", kwargs={"catslug": self.kwargs["catslug"]}
            )
        )
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "cate": category_or_instock_slugger(self.kwargs.get("catslug"))[1],
                "brands": Brand.objects.all(),
                "most_sold": self.get_most_sold_items(),
                "form": PriceFilter(),
                "colors": Color.objects.all(),
                "categories": KalaCategory.objects.all(),
                "is_authenticated": self.request.user.is_authenticated,
            }
        )
        return context


class CategoryListViewInstock(CategoryListView):
    model = Kala
    context_object_name = "kalas"
    template_name = "shop-grid.html"
    paginate_by = 12

    def post(self, request, *args, **kwargs):
        form = PriceFilter(request.POST)
        if form.is_valid():
            minPrice = form.cleaned_data["minPrice"]
            maxPrice = form.cleaned_data["maxPrice"]
            return HttpResponseRedirect(
                reverse(
                    "CategoryPriceFilter",
                    kwargs={
                        "catslug": self.kwargs["catslug"],
                        "minPrice": minPrice,
                        "maxPrice": maxPrice,
                    },
                )
            )
        return HttpResponseRedirect(
            reverse(
                "CategoryListViewInstock", kwargs={"catslug": self.kwargs["catslug"]}
            )
        )

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        catslug = self.kwargs["catslug"]
        lst = category_or_instock_slugger(catslug)
        form = PriceFilter()
        kalas = just_in_stock(lst[0])
        most_sold = Cart.objects.annotate(num_kalas=Count("seller")).order_by(
            "-num_kalas"
        )[:5]
        context.update(
            {
                "kalas": kalas,
                "cate": lst[1],
                "brands": Brand.objects.all(),
                "most_sold": most_sold,
                "categories": KalaCategory.objects.all(),
                "is_authenticated": self.request.user.is_authenticated,
                "form": form,
            }
        )
        return context


class CategoryPriceFilterListView(ListView):
    model = Kala
    context_object_name = "kalas"
    template_name = "shop-grid.html"
    paginate_by = 12

    def post(self, request, *args, **kwargs):
        form = PriceFilter(request.POST)
        if form.is_valid():
            minPrice = form.cleaned_data["minPrice"]
            maxPrice = form.cleaned_data["maxPrice"]
            return HttpResponseRedirect(
                reverse(
                    "CategoryPriceFilter",
                    kwargs={
                        "catslug": self.kwargs["catslug"],
                        "minPrice": minPrice,
                        "maxPrice": maxPrice,
                    },
                )
            )
        return HttpResponseRedirect(
            reverse(
                "CategoryListViewInstock", kwargs={"catslug": self.kwargs["catslug"]}
            )
        )

    def get_context_data(self, **kwargs):
        context = super(CategoryPriceFilterListView, self).get_context_data(**kwargs)
        minPrice = int(self.kwargs["minPrice"])
        maxPrice = int(self.kwargs["maxPrice"])
        lst = category_or_instock_slugger(self.kwargs["catslug"])
        kalas = max_min_price(lst[0], minPrice, maxPrice)
        form = PriceFilter()
        most_sold = Cart.objects.annotate(num_kalas=Count("seller")).order_by(
            "-num_kalas"
        )[:5]
        context.update(
            {
                "kalas": kalas,
                "cate": lst[1],
                "brands": Brand.objects.all(),
                "most_sold": most_sold,
                "is_authenticated": self.request.user.is_authenticated,
                "form": form,
            }
        )
        return context


class BrandListView(ListView):
    model = Kala
    context_object_name = "kalas"
    template_name = "shop-grid.html"
    paginate_by = 12

    def post(self, request, *args, **kwargs):
        form = PriceFilter(request.POST)
        if form.is_valid():
            minPrice = form.cleaned_data["minPrice"]
            maxPrice = form.cleaned_data["maxPrice"]
            return HttpResponseRedirect(
                reverse(
                    "BrandPriceFilter",
                    kwargs={
                        "brandslug": self.kwargs["brandslug"],
                        "minPrice": minPrice,
                        "maxPrice": maxPrice,
                    },
                )
            )

    def get_context_data(self, **kwargs):
        context = super(BrandListView, self).get_context_data(**kwargs)
        maker = get_object_or_404(Brand, slug=self.kwargs["brandslug"])
        products = maker.brand.all()
        most_sold = Cart.objects.annotate(num_kalas=Count("seller")).order_by(
            "-num_kalas"
        )[:5]
        
        context.update(
            {
                "kalas": products,
                "brand": maker,
                "most_sold": most_sold,
                "categories": KalaCategory.objects.all(),
                "brands": Brand.objects.all(),
                "colors": Color.objects.all(),
                "is_authenticated": self.request.user.is_authenticated,
                "form": PriceFilter(),
            }
        )
        return context


class BrandListViewInstock(ListView):
    model = Kala
    context_object_name = "kalas"
    template_name = "shop-grid.html"
    paginate_by = 12

    def post(self, request, *args, **kwargs):
        form = PriceFilter(request.POST)
        if form.is_valid():
            min_price = form.cleaned_data["minPrice"]
            max_price = form.cleaned_data["maxPrice"]
            return HttpResponseRedirect(
                reverse(
                    "BrandPriceFilter",
                    kwargs={
                        "brandslug": self.kwargs["brandslug"],
                        "minPrice": min_price,
                        "maxPrice": max_price,
                    },
                )
            )

    def get_context_data(self, **kwargs):
        context = super(BrandListViewInstock, self).get_context_data(**kwargs)
        maker = get_object_or_404(Brand, slug=self.kwargs["brandslug"])
        products = just_in_stock(maker.objects.all())
        most_sold = Cart.objects.annotate(num_kalas=Count("seller")).order_by(
            "-num_kalas"
        )[:5]
        context.update(
            {
                "kalas": products,
                "brand": maker,
                "most_sold": most_sold,
                "categories": KalaCategory.objects.all(),
                "brands": Brand.objects.all(),
                "is_authenticated": self.request.user.is_authenticated,
                "form": PriceFilter(),
            }
        )
        return context


class BrandPriceFilter(ListView):
    model = Kala
    context_object_name = "kalas"
    template_name = "shop-grid.html"
    paginate_by = 12

    def post(self, request, *args, **kwargs):
        form = PriceFilter(request.POST)
        if form.is_valid():
            minPrice = form.cleaned_data["minPrice"]
            maxPrice = form.cleaned_data["maxPrice"]
            return HttpResponseRedirect(
                reverse(
                    "BrandPriceFilter",
                    kwargs={
                        "brandslug": self.kwargs["brandslug"],
                        "minPrice": minPrice,
                        "maxPrice": maxPrice,
                    },
                )
            )

    def get_context_data(self, **kwargs):
        context = super(BrandPriceFilter, self).get_context_data(**kwargs)
        maker = get_object_or_404(Brand, slug=self.kwargs["brandslug"])
        products = max_min_price(
            maker.objects.all(), self.kwargs["minPrice"], self.kwargs["maxPrice"]
        )
        most_sold = Cart.objects.annotate(num_kalas=Count("seller")).order_by(
            "-num_kalas"
        )[:5]
        context.update(
            {
                "kalas": products,
                "brand": maker,
                "most_sold": most_sold,
                "brands": Brand.objects.all(),
                "categories": KalaCategory.objects.all(),
                "is_authenticated": self.request.user.is_authenticated,
                "form": PriceFilter(),
            }
        )
        return context


def brand_category_slugger(catslug, manu):
    kalasCat = get_object_or_404(KalaCategory, slug=catslug)
    kalas = manu.brand.filter(category=kalasCat)
    cate = kalasCat

    return kalas, cate


class BrandCategory(ListView):
    model = Kala
    context_object_name = "kalas"
    template_name = "shop-grid.html"
    paginate_by = 12

    def post(self, request, *args, **kwargs):
        form = PriceFilter(request.POST)
        if form.is_valid():
            minPrice = form.cleaned_data["minPrice"]
            maxPrice = form.cleaned_data["maxPrice"]
            return HttpResponseRedirect(
                reverse(
                    "BrandCategoryPriceFilter",
                    kwargs={
                        "catslug": self.kwargs["catslug"],
                        "brandslug": self.kwargs["brandslug"],
                        "minPrice": minPrice,
                        "maxPrice": maxPrice,
                    },
                )
            )

    def get_context_data(self, **kwargs):
        context = super(BrandCategory, self).get_context_data(**kwargs)
        brand_slug = self.kwargs["brandslug"]
        catslug = self.kwargs["catslug"]
        brand = get_object_or_404(Brand, slug=brand_slug)
        lst = brand_category_slugger(catslug, brand)
        most_sold = Cart.objects.annotate(num_kalas=Count("seller")).order_by(
            "-num_kalas"
        )[:5]
        context.update(
            {
                "kalas": lst[0],
                "cate": lst[1],
                "most_sold": most_sold,
                "brand": brand,
                "categories": KalaCategory.objects.all(),
                "brands": Brand.objects.all(),
                "is_authenticated": self.request.user.is_authenticated,
                "form": PriceFilter(),
            }
        )
        return context


class BrandCategoryInstock(ListView):
    model = Kala
    context_object_name = "kalas"
    template_name = "shop-grid.html"
    paginate_by = 12

    def post(self, request, *args, **kwargs):
        form = PriceFilter(request.POST)
        if form.is_valid():
            minPrice = form.cleaned_data["minPrice"]
            maxPrice = form.cleaned_data["maxPrice"]
            return HttpResponseRedirect(
                reverse(
                    "BrandCategoryPriceFilter",
                    kwargs={
                        "catslug": self.kwargs["catslug"],
                        "brandslug": self.kwargs["brandslug"],
                        "minPrice": minPrice,
                        "maxPrice": maxPrice,
                    },
                )
            )

    def get_context_data(self, **kwargs):
        context = super(BrandCategoryInstock, self).get_context_data(**kwargs)
        brand_slug = self.kwargs["brandslug"]
        catslug = self.kwargs["catslug"]
        brand = get_object_or_404(Brand, slug=brand_slug)
        lst = brand_category_slugger(catslug, brand)
        kalas = just_in_stock(lst[0])
        most_sold = Cart.objects.annotate(num_kalas=Count("seller")).order_by(
            "-num_kalas"
        )
        context.update(
            {
                "kalas": kalas,
                "cate": lst[1],
                "most_sold": most_sold,
                "brand": brand,
                "brands": Brand.objects.all(),
                "categories": KalaCategory.objects.all(),
                "is_authenticated": self.request.user.is_authenticated,
                "form": PriceFilter(),
            }
        )
        return context


class BrandCategoryPriceFilter(ListView):
    model = Kala
    context_object_name = "kalas"
    template_name = "shop-grid.html"
    paginate_by = 12

    def post(self, request, *args, **kwargs):
        form = PriceFilter(request.POST)
        if form.is_valid():
            minPrice = form.cleaned_data["minPrice"]
            maxPrice = form.cleaned_data["maxPrice"]
            return HttpResponseRedirect(
                reverse(
                    "BrandCategoryPriceFilter",
                    kwargs={
                        "catslug": self.kwargs["catslug"],
                        "brandslug": self.kwargs["brandslug"],
                        "minPrice": minPrice,
                        "maxPrice": maxPrice,
                    },
                )
            )

    def get_context_data(self, **kwargs):
        context = super(BrandCategoryPriceFilter, self).get_context_data(**kwargs)
        brand_slug = self.kwargs["brandslug"]
        catslug = self.kwargs["catslug"]
        maxPrice = self.kwargs["maxPrice"]
        minPrice = self.kwargs["minPrice"]
        brand = get_object_or_404(Brand, slug=brand_slug)
        lst = brand_category_slugger(catslug, brand)
        kalas = max_min_price(lst[0], minPrice, maxPrice)
        most_sold = Cart.objects.annotate(num_kalas=Count("seller")).order_by(
            "-num_kalas"
        )[:5]
        context.update(
            {
                "kalas": kalas,
                "cate": lst[1],
                "most_sold": most_sold,
                "brand": brand,
                "brands": Brand.objects.all(),
                "categories": KalaCategory.objects.all(),
                "is_authenticated": self.request.user.is_authenticated,
                "form": PriceFilter(),
            }
        )
        return context


@login_required
def cart_(request):
    carts = Cart.objects.filter(user=request.user, paid="F")
    cart_id = request.POST.get("cart_id")

    if not carts.exists():
        return render(request, "cart-empty.html")

    # Initialize CartCalculator and calculate totals
    calculator = CartCalculator(carts)
    totals = calculator.calculate_totals()

    if request.method == "POST":
        if "update" in request.POST:
            # Update cart item quantity
            quantity = request.POST.get("quantity")
            cart_item = get_object_or_404(
                Cart, id=cart_id, user=request.user, paid="F"
            )
            if int(quantity) > cart_item.seller.instock:
                return HttpResponse(
                    {
                        "success": False,
                        "error": "تعداد انتخابی از موجودی انبار بیشتر است.",
                    }
                )
            cart_item.count = int(quantity)
            cart_item.save()
            return redirect(request.META.get("HTTP_REFERER", reverse("cart")))

        # Delete cart item
        if "Delete" in request.POST:
            cart_item = get_object_or_404(Cart, id=cart_id)
            cart_item.delete()
            return redirect(request.META.get("HTTP_REFERER", reverse("cart")))

        # Apply coupon
        if "applyCoupon" in request.POST:
            code = request.POST.get("couponCode")
            error = None
            try:
                co = Coupon.objects.get(code=code)
                if co.is_expired():
                    error = "تاریخ استفاده از این کوپن به پایان رسیده است!"
                elif co.count <= 0:
                    error = "تعداد استفاده از این کوپن به پایان رسیده است!"
                else:
                    carts.update(coupon=co)
                    return HttpResponseRedirect(reverse("cart"))
            except Coupon.DoesNotExist:
                error = "کد کوپن نادرست می باشد!"

            # Render the cart with error message if coupon application fails
            if error:
                context = {
                    "carts": carts,
                    "error": error,
                }
                return render(request, "cart.html", context)

    # Context to pass to template
    context = {
        "carts": carts,
        "totalPrice": totals["tPrice"],
        "finalPrice": totals["final"],
        "tax": totals["tax"],
        "coupon": totals["coupon"],
        "sendCost": totals["sendCost"],
        "toPay": totals["toPay"],
    }
    return render(request, "cart.html", context)


def contact_us(request):
    context = {}
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        description = request.POST["description"]
        call = ContactUs.objects.create(name=name, email=email, desc=description)
        call.save()
        context = {
            "sent": True,
        }
    return render(request, "contact-us.html", context)


@login_required
def checkout(request):
    carts = Cart.objects.filter(user=request.user, paid="F")
    # Fetch profile for form pre-filling if available
    address = Address.objects.filter(user=request.user, is_default=True)

    if not carts.exists():
        return redirect("cart-empty")

    # Initialize CartCalculator and calculate totals
    calculator = CartCalculator(carts)
    totals = calculator.calculate_totals()

    initial_data = [
        {
            "postal_address": data.postal_address,
            "full_name": data.full_name,
            "phone_number": data.phone_number,
            "neighborhood": data.neighborhood,
            "city": data.city,
            "state": data.state,
            "postal_code": data.postal_code,
            "license_plate": data.license_plate,
            "unit": data.unit
        }
        for data in address
    ]

    if request.method == "POST":
        form = CheckoutForm(request.POST, user=request.user, address=address)
        if form.is_valid():
            # Initialize and process checkout with CheckoutProcessor
            processor = CheckoutProcessor(
                user=request.user,
                form_data=form.cleaned_data,
                carts=carts,
                totals=totals,
            )
            try:
                processor.process()
                return HttpResponseRedirect(reverse("orders"))
            except ValidationError as e:
                # Handle out-of-stock error and re-render with error
                context = _get_context(form, totals, carts, error=str(e))
                return render(request, "checkout.html", context)
    else:
        form = CheckoutForm(initial=initial_data[0], address=address)

    context = _get_context(form, totals, carts)
    return render(request, "checkout.html", context)


def _get_context(form, totals, carts, error=None):
    """Helper function to build the context dictionary for rendering the template."""
    return {
        "form": form,
        "state": States.objects.all(),
        "carts": carts,
        "totalPrice": totals["tPrice"],
        "finalPrice": totals["final"],
        "tax": totals["tax"],
        "coupon": totals["coupon"],
        "sendCost": totals["sendCost"],
        "toPay": totals["toPay"],
        "is_authenticated": True,
        "usr": form.user if form else None,
        "error": error,
    }


class PostListView(ListView):
    model = Post
    template_name = "blog-classic.html"
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        post = Post.objects.all()
        context.update({"posts": post})
        return context


class LatestPostsMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super(LatestPostsMixin, self).get_context_data(**kwargs)
        try:
            context["latest_posts_list"] = Post.objects.all()
        except:
            pass
        return context


class PostDetailView(LatestPostsMixin, DetailView):
    model = Post
    template_name = "post.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"  # The URL parameter for the slug

    def get_context_data(self, **kwargs):
        # Get the original context data from the parent class
        context = super().get_context_data(**kwargs)
        # Filter comments to show only those with status 'OK'
        context["comments"] = self.object.comments.filter(
            status=PostComments.StatusChoice.OK
        )
        # Add the comment form to the context
        context["form"] = CommentForm()
        return context


@login_required
def create_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            # Extract cleaned data from the form
            content = form.cleaned_data["content"]

            # Create the comment
            comment = PostComments.objects.create(
                post=post,
                author=request.user,
                text=content,
                status=PostComments.StatusChoice.WAITING,
            )
            # Add a success message
            messages.success(request, "نظر شما ارسال شد و در صف تایید میباشد.")
            return redirect("PostDetailView", slug=post.slug)
        else:
            # Add an error message if the form is invalid
            messages.error(request, "Please correct the errors below.")

    else:
        form = CommentForm()  # An empty form for GET requests

    # Pass the form and post to the context for rendering in the template
    return render(request, "post.html", {"post": post, "form": form})


import operator
from functools import reduce


class SearchKala(KalaListView):
    """
    Display a Product List  filtered by search query
    """

    paginate_by = 12
    template_name = "shop-grid.html"
    context_object_name = "kalas"

    def get_queryset(self):
        result = super(SearchKala, self).get_queryset()
        query = self.request.GET.get("search")
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(operator.and_, (Q(name__icontains=q) for q in query_list))
            )
        return result

    def get_context_data(self, **kwargs):
        context = super(SearchKala, self).get_context_data(**kwargs)
        most_sold = Cart.objects.annotate(num_kalas=Count("seller")).order_by(
            "-num_kalas"
        )[:5]
        context.update(
            {
                "is_authenticated": self.request.user.is_authenticated,
                "most_sold": most_sold,
                "color": Color.objects.all(),
                "categories": KalaCategory.objects.all(),
            }
        )
        return context


@login_required
def compare(request):
    # Fetch user-specific compare objects
    compare = Compare.objects.filter(user=request.user).select_related('product')
    
    # Fetch product details for the compared products in one query
    product_ids = [p.product.id for p in compare if p.product]
    product_details = KalaInstance.objects.filter(kala_id__in=product_ids)
    product_detail_map = {detail.kala_id: detail for detail in product_details}

    compare_data = [
        {
            "compare": entry,
            "details": product_detail_map.get(entry.product.id),  # Fetch detail for each product
            "size": ", ".join(str(size) for size in entry.product.size.all()),         # Add size
            "material": ", ".join(material.name for material in entry.product.material.all()),  # Add materials
            "color": ", ".join(color.name for color in entry.product.color.all()),      # Add color
        }
        for entry in compare
    ]
    
    if request.method == "POST":
        if "delete" in request.POST:
            slug = request.POST.get("product_slug")
            product_obj = get_object_or_404(Kala, slug=slug)
            # Delete the compare entry for the user and product
            Compare.objects.filter(user=request.user, product=product_obj).delete()
        
        return redirect(request.META.get("HTTP_REFERER", "/compare"))

    context = {
        "compare": compare_data
    }
    return render(request, "compare.html", context)


def error_404(request, *args, **kwargs):
    return render(request, "404.html")


def error_500(request, *args, **kwargs):
    return render(request, "500.html")


def about_us(request):
    return render(request, "about-us.html")


from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


def get_cart_items(cart_queryset):
    """Extracts cart item details."""
    return [
        {
            "product": item.product.name,
            "seller": item.seller if item.product else "Unknown Seller",
            "count": item.count,
        }
        for item in cart_queryset
    ]


def get_sold_data(sold_queryset):
    """Extracts sold order details, including human-readable status."""
    return [
        {
            "id": order.id,
            "grand_total": order.grand_total,
            "send_status": order.get_send_status_display(),
            "created_at": order.created_at,
            "zip_code": order.zip_code,
            "state": order.state.name,
            "city": order.city,
            "follow_up_code": order.follow_up_code,
        }
        for order in sold_queryset
    ]


@login_required
def account_orders(request):
    # Fetch sold orders and prefetch related cart products
    sold_orders = Sold.objects.filter(user=request.user).prefetch_related("products")
    cart_items = Cart.objects.select_related("product").filter(
        user=request.user, paid="T"
    )

    # Prepare cart and sold data
    cart_data = get_cart_items(cart_items)
    sold_data = get_sold_data(sold_orders)

    # Combine sold orders with their corresponding cart items
    combined_data = []
    for sold, cart in zip(sold_data, cart_data):
        combined_data.append({**sold, **cart})

    # Pagination for combined data
    page = request.GET.get("page", 1)
    paginator = Paginator(combined_data, 5)
    try:
        orders_page = paginator.page(page)
    except PageNotAnInteger:
        orders_page = paginator.page(1)
    except EmptyPage:
        orders_page = paginator.page(paginator.num_pages)

    # Render context
    context = {
        "orders_data": orders_page,
        "page_obj": orders_page,  # for pagination controls in the template
    }
    return render(request, "account-orders.html", context)


def brands(request):
    context = {
        "brands": Brand.objects.all(),
    }
    return render(request, "brands.html", context)


def faq(request):
    return render(request, "faq.html")


@login_required
def account_dashboard(request):
    cart = Cart.objects.filter(user=request.user, paid="T")
    sold = []
    for product in cart:
        sold.append(product)

    reverse_list = sold[::-1]
    len_Sold = len(reverse_list) // 2
    context = {
        "sold": reverse_list,
        "lenSold": len_Sold,
    }
    return render(request, "account-dashboard.html", context)


def terms_and_conditions(request):
    return render(request, "terms-and-conditions.html")


@login_required
def track_order(request):
    return render(request, "track-order.html")


@login_required
def wishlist(request):
    wishlist = WishList.objects.filter(user=request.user)
    products = list()
    for p in wishlist:
        if p.product:
            product_detail = KalaInstance.objects.filter(kala__slug=p.product.slug)
            for product in product_detail:
                products.append(product)

    if request.method == "POST":
        slug = request.POST.get("product_slug")
        product_obj = get_object_or_404(Kala, slug=slug)

        if "addToCart" in request.POST:
            pass

        if "delete" in request.POST:
            for obj in wishlist:
                if obj.product == product_obj:
                    obj.delete()
                    break
        return redirect(request.META["HTTP_REFERER"])

    context = {
        "wishlist": wishlist,
        "detail": products,
    }
    return render(request, "wishlist.html", context)
