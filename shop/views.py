from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Q
from django.forms import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView
from django.views.generic.base import ContextMixin
from django.views.generic.edit import UpdateView
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
from .tokens import generateToken

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
        kala_id = request.POST.get("kala")
        if request.user.is_authenticated:
            if "addCart" in request.POST:
                color_id = request.POST.get("Color")
                seller_id = request.POST.get("Seller")
                size_id = request.POST.get("Size")
                material_id = request.POST.get("Material")
                users_products = Cart.objects.filter(username=request.user, payed="F")
                Found = False
                for i in users_products:
                    if (
                        i.seller == KalaInstance.objects.get(id=seller_id)
                        and i.size == ProductSize.objects.get(id=size_id)
                        and i.material == Materials.objects.get(id=material_id)
                        and i.color == Color.objects.get(id=color_id)
                    ):
                        i.count += 1
                        i.save()
                        Found = True
                        break

                if not Found:
                    add_cart = Cart.objects.create(
                        username=request.user,
                        product_id=kala_id,
                        size=ProductSize.objects.get(id=size_id),
                        color=Color.objects.get(id=color_id),
                        material=Materials.objects.get(id=material_id),
                        seller=KalaInstance.objects.get(id=seller_id),
                    )
                return redirect(request.META["HTTP_REFERER"])

            elif "addWishlist" in request.POST:
                kala_id = request.POST["kala"]
                kala_check = Kala.objects.get(id=kala_id)
                if kala_check:
                    product = WishList.objects.filter(
                        user=request.user, product_id=kala_id
                    )
                    if product:
                        product.delete()
                        return redirect(request.META["HTTP_REFERER"])
                    else:
                        w = WishList.objects.create(
                            user=request.user, product_id=kala_id
                        )
                        w.save()
                        return redirect(request.META["HTTP_REFERER"])
                else:
                    return redirect(request.META["HTTP_REFERER"])

            elif "addCompare" in request.POST:
                kala_id = request.POST["kala"]
                kala_check = Kala.objects.get(id=kala_id)
                if kala_check:
                    product = Compare.objects.filter(
                        user=request.user, product_id=kala_id
                    )
                    if product:
                        product.delete()
                        return redirect(request.META["HTTP_REFERER"])
                    else:
                        w = Compare.objects.create(
                            user=request.user, product_id=kala_id
                        )
                        w.save()
                        return redirect(request.META["HTTP_REFERER"])
                else:
                    return redirect(request.META["HTTP_REFERER"])

    def get_context_data(self, **kwargs):
        context = super(KalaListView, self).get_context_data(**kwargs)
        most_sold = Cart.objects.annotate(num_kalas=Count("seller")).order_by(
            "-num_kalas"
        )
        instock = KalaInstance.objects.filter(~Q(instock=0)).values()
        context.update(
            {
                "kala": Kala.objects.all(),
                "most_sold": most_sold,
                "instock": instock,
                "Brands": Brand.objects.all(),
                "posts": Post.objects.all(),
            }
        )
        return context


def kala_detail_view(request, kalaslug):
    k = get_object_or_404(Kala, slug=kalaslug)
    akala = Kala.objects.filter(category=k.category)
    comments = ProductComments.objects.filter(kala__id=k.pk)

    inst = []
    i = KalaInstance.objects.filter(kala=k)
    for a in i:
        if a.instock != 0:
            inst.append(a)

    if request.user.is_authenticated:
        is_authenticated = True
    else:
        is_authenticated = False

    if request.method == "POST" and is_authenticated:
        if "addComment" in request.POST:
            text = request.POST["text"]
            c = ProductComments.objects.create(writer=request.user, body=text, Kala=k)
            c.save()

        elif "addCart" in request.POST:
            try:
                color_id = request.POST.get("Color")
                seller_id = request.POST.get("Seller")
                size_id = request.POST.get("Size")
                material_id = request.POST.get("Material")
                users_products = Cart.objects.filter(username=request.user, payed="F")
                Found = False
                for i in users_products:
                    if (
                        i.seller == KalaInstance.objects.get(id=seller_id)
                        and i.size == ProductSize.objects.get(id=size_id)
                        and i.material == Materials.objects.get(id=material_id)
                        and i.color == Color.objects.get(id=color_id)
                    ):
                        i.count += 1
                        i.save()
                        Found = True
                        break

                if not Found:
                    addCart = Cart.objects.create(
                        username=request.user,
                        product=k,
                        size=ProductSize.objects.get(id=size_id),
                        color=Color.objects.get(id=color_id),
                        material=Materials.objects.get(id=material_id),
                        seller=KalaInstance.objects.get(id=seller_id),
                    )
            except ObjectDoesNotExist:
                return HttpResponse(
                    "<br><center>مشخصات کالا  مورد نظر را انتخاب کنید و دوباره امتحان کنید </center>"
                )

        elif "addWishlist" in request.POST:
            kala_id = request.POST["kala"]
            kala_check = Kala.objects.get(id=kala_id)
            if kala_check:
                product = WishList.objects.filter(user=request.user, product_id=kala_id)
                if product:
                    product.delete()
                    return redirect(request.META["HTTP_REFERER"])
                else:
                    w = WishList.objects.create(user=request.user, product_id=kala_id)
                    w.save()
                    return redirect(request.META["HTTP_REFERER"])
            else:
                return redirect(request.META["HTTP_REFERER"])

        elif "addCompare" in request.POST:
            kala_id = request.POST["kala"]
            kala_check = Kala.objects.get(id=kala_id)
            if kala_check:
                product = Compare.objects.filter(user=request.user, product_id=kala_id)
                if product:
                    product.delete()
                    return redirect(request.META["HTTP_REFERER"])
                else:
                    w = Compare.objects.create(user=request.user, product_id=kala_id)
                    w.save()
                    return redirect(request.META["HTTP_REFERER"])
            else:
                return redirect(request.META["HTTP_REFERER"])

    if inst:
        context = {
            "kala": k,
            "Allkala": akala,
            "comments": comments,
            "inst": inst,
            "is_authenticated": is_authenticated,
            "finst": inst[0],
        }
    else:
        context = {
            "kala": k,
            "Allkala": akala,
            "comments": comments,
            "is_authenticated": is_authenticated,
        }
    return render(request, "product.html", context)


def category_or_instock_slugger(category_slug):
    kala_category = get_object_or_404(KalaCategory, slug=category_slug)
    kalas = kala_category.__class__.objects.all()
    category = kala_category

    return kalas, category


def JustInstock(kalas):
    lstKalas = []
    for i in kalas:
        if i.kalainst.filter(~Q(instock=0)):
            lstKalas.append(i)
    return lstKalas


def MaxMinPrice(kalas, minPrice, maxPrice):
    lstKalas = []
    for i in kalas:
        if i.kalainst.filter(~Q(instock=0)):
            if i.kalainst.filter(price__lte=maxPrice):
                if len(i.kalainst.filter(price__gt=minPrice)):
                    lstKalas.append(i)
    return lstKalas


class CategoryListView(ListView):
    model = Kala
    context_object_name = "kalas"
    template_name = "shop-grid.html"
    paginate_by = 12
    queryset = Kala.objects.all()

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
        color = Color.objects.all()
        most_sold = Cart.objects.annotate(num_kalas=Count("seller")).order_by(
            "-num_kalas"
        )
        context.update(
            {
                "kalas": lst[0],
                "cate": lst[1],
                "brands": Brand.objects.all(),
                "most_sold": most_sold,
                "form": form,
                "colors": color,
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
        kalas = JustInstock(lst[0])
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
        kalas = MaxMinPrice(lst[0], minPrice, maxPrice)
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
        products = maker.__class__.objects.all()
        most_sold = Cart.objects.annotate(num_kalas=Count("seller")).order_by(
            "-num_kalas"
        )[:5]
        context.update(
            {
                "kalas": products,
                "brand": maker,
                "most_sold": most_sold,
                "brands": Brand.objects.all(),
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
        products = JustInstock(maker.objects.all())
        most_sold = Cart.objects.annotate(num_kalas=Count("seller")).order_by(
            "-num_kalas"
        )[:5]
        context.update(
            {
                "kalas": products,
                "brand": maker,
                "most_sold": most_sold,
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
        products = MaxMinPrice(
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
                "is_authenticated": self.request.user.is_authenticated,
                "form": PriceFilter(),
            }
        )
        return context


def BrandCategorySluger(catslug, manu):
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
        brand = self.kwargs["brandslug"]
        catslug = self.kwargs["catslug"]
        manu = get_object_or_404(Brand, slug=brand)
        lst = BrandCategorySluger(catslug, manu)
        most_sold = Cart.objects.annotate(num_kalas=Count("seller")).order_by(
            "-num_kalas"
        )[:5]
        context.update(
            {
                "kalas": lst[0],
                "cate": lst[1],
                "most_sold": most_sold,
                "brand": manu,
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
        brand = self.kwargs["brandslug"]
        catslug = self.kwargs["catslug"]
        manu = get_object_or_404(Brand, slug=brand)
        lst = BrandCategorySluger(catslug, manu)
        kalas = JustInstock(lst[0])
        most_sold = Cart.objects.annotate(num_kalas=Count("seller")).order_by(
            "-num_kalas"
        )
        context.update(
            {
                "kalas": kalas,
                "cate": lst[1],
                "most_sold": most_sold,
                "brand": manu,
                "brands": Brand.objects.all(),
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
        brand = self.kwargs["brandslug"]
        catslug = self.kwargs["catslug"]
        maxPrice = self.kwargs["maxPrice"]
        minPrice = self.kwargs["minPrice"]
        manu = get_object_or_404(Brand, slug=brand)
        lst = BrandCategorySluger(catslug, manu)
        kalas = MaxMinPrice(lst[0], minPrice, maxPrice)
        most_sold = Cart.objects.annotate(num_kalas=Count("seller")).order_by(
            "-num_kalas"
        )[:5]
        context.update(
            {
                "kalas": kalas,
                "cate": lst[1],
                "most_sold": most_sold,
                "brand": manu,
                "brands": Brand.objects.all(),
                "is_authenticated": self.request.user.is_authenticated,
                "form": PriceFilter(),
            }
        )
        return context


def is_authenticated(user):
    return not user.is_authenticated


@login_required
def cart_(request):
    objs = Cart.objects.filter(username=request.user, payed="F")

    if not objs.exists():
        return render(request, "cart-empty.html")

    # Calculate prices in a single loop
    tPrice, final, CFinal = 0, 0, 0
    for obj in objs:
        tPrice += obj.total()
        final += obj.total_price()
        CFinal += obj.finally_price()

    tax = final - tPrice
    coupon = CFinal - final
    sendCost = 5000 * len(objs)
    toPay = CFinal + tax + sendCost

    if request.method == "POST":
        # Update cart item count
        if "update" in request.POST:
            slug = request.POST.get("product_slug")
            count = request.POST.get("quantity")
            product_obj = get_object_or_404(Kala, slug=slug)
            try:
                cart_item = objs.get(product=product_obj)
                cart_item.count = int(count)
                cart_item.save()
            except Cart.DoesNotExist:
                pass

        # Delete cart item
        if "delete" in request.POST:
            slug = request.POST.get("product_slug")
            product_obj = get_object_or_404(Kala, slug=slug)
            try:
                cart_item = objs.get(product=product_obj)
                cart_item.delete()
            except Cart.DoesNotExist:
                pass
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
                    objs.update(coupon=co)
                    return HttpResponseRedirect(reverse("cart"))
            except Coupon.DoesNotExist:
                error = "کد کوپن نادرست می باشد!"

            # Render the cart with error message if coupon application fails
            if error:
                context = {
                    "carts": objs,
                    "is_authenticated": True,
                    "error": error,
                }
                return render(request, "cart.html", context)

    # Context to pass to template
    context = {
        "carts": objs,
        "is_authenticated": True,
        "totalPrice": tPrice,
        "finalPrice": final,
        "tax": tax,
        "coupon": coupon,
        "sendCost": sendCost,
        "toPay": toPay,
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
    from .utils import CartCalculator, CheckoutProcessor
    
    carts = Cart.objects.filter(username=request.user, payed="F")

    if not carts.exists():
        return redirect("cart-empty")

    # Initialize CartCalculator and calculate totals
    calculator = CartCalculator(carts)
    totals = calculator.calculate_totals()

    # Fetch profile for form pre-filling if available
    profile = getattr(request.user, "profile", None)
    initial_data = {
        "address": profile.address if profile else "",
        "city": profile.city if profile else "",
        "state": profile.state.id if profile and profile.state else None,
        "postcode": profile.postcode if profile else "",
    }

    if request.method == "POST":
        form = CheckoutForm(request.POST, user=request.user, profile=profile)
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
        form = CheckoutForm(initial=initial_data, profile=profile)

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


class Address(LoginRequiredMixin, DetailView):
    model = User
    template_name = "account-addresses.html"

    def get_object(self):
        return User.objects.get(pk=self.request.user.pk)


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
            }
        )
        return context


@login_required
def compare(request):
    compare = Compare.objects.filter(user=request.user)
    product = []

    for p in compare:
        if p.product:
            product_detail = KalaInstance.objects.filter(kala__slug=p.product.slug)

        for a in product_detail:
            product.append(a)

    if request.method == "POST":
        if "delete" in request.POST:
            slug = request.POST.get("product_slug")
            product_obj = Kala.objects.get(slug=slug)
            for obj in compare:
                if obj.product == product_obj:
                    print("-----   Found : True   -----")
                    obj.delete()
                    break
        return redirect(request.META["HTTP_REFERER"])

    context = {
        "compare": compare,
        "detail": product,
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
    sold_orders = Sold.objects.filter(user=request.user).prefetch_related('products')
    cart_items = Cart.objects.select_related('product').filter(user=request.user, payed='T')

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
    cart = Cart.objects.filter(username=request.user, payed="T")
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
    product = []

    for p in wishlist:
        if p.product:
            product_detail = KalaInstance.objects.filter(kala__slug=p.product.slug)

        for a in product_detail:
            product.append(a)

    if request.method == "POST":
        if "delete" in request.POST:
            slug = request.POST.get("product_slug")
            product_obj = Kala.objects.get(slug=slug)
            for obj in wishlist:
                if obj.product == product_obj:
                    print("-----   Found : True   -----")
                    obj.delete()
                    break
        return redirect(request.META["HTTP_REFERER"])

    context = {
        "wishlist": wishlist,
        "detail": product,
    }
    return render(request, "wishlist.html", context)
