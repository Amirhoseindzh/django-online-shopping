from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage, send_mail
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView
from django.views.generic.base import ContextMixin
from django.views.generic.edit import UpdateView
from .forms import CommentForm
from .forms import CheckoutForm, PriceFilter, ProfileForm
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


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        my_user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        my_user = None

    if my_user is not None and generateToken.check_token(my_user, token):
        my_user.is_active = True
        my_user.save()
        messages.success(
            request,
            "You are account is activated you can login by filling the form below.",
        )
        return redirect("login")
    else:
        messages.success(request, "Activation failed please try again")
        return redirect("register")


class Profile(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "account-profile.html"
    form_class = ProfileForm
    success_url = reverse_lazy("profile")

    def get_object(self):
        return User.objects.get(pk=self.request.user.pk)


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
                seller_id = request.POST.get("Saller")
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
        mostsalled = Cart.objects.annotate(num_kalas=Count("seller")).order_by(
            "-num_kalas"
        )[:5]
        context.update(
            {
                "kalas": kalas,
                "cate": lst[1],
                "brands": Brand.objects.all(),
                "mostsalled": mostsalled,
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
        mostsalled = Cart.objects.annotate(num_kalas=Count("seller")).order_by(
            "-num_kalas"
        )[:5]
        context.update(
            {
                "kalas": kalas,
                "cate": lst[1],
                "brands": Brand.objects.all(),
                "mostsalled": mostsalled,
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
        products = maker.objects.all()
        mostsalled = Cart.objects.annotate(num_kalas=Count("seller")).order_by(
            "-num_kalas"
        )[:5]
        context.update(
            {
                "kalas": products,
                "brand": maker,
                "mostsalled": mostsalled,
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
        mostsalled = Cart.objects.annotate(num_kalas=Count("seller")).order_by(
            "-num_kalas"
        )[:5]
        context.update(
            {
                "kalas": products,
                "brand": maker,
                "mostsalled": mostsalled,
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
        mostsalled = Cart.objects.annotate(num_kalas=Count("seller")).order_by(
            "-num_kalas"
        )[:5]
        context.update(
            {
                "kalas": products,
                "brand": maker,
                "mostsalled": mostsalled,
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
        mostsalled = Cart.objects.annotate(num_kalas=Count("seller")).order_by(
            "-num_kalas"
        )[:5]
        context.update(
            {
                "kalas": lst[0],
                "cate": lst[1],
                "mostsalled": mostsalled,
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
        mostsalled = Cart.objects.annotate(num_kalas=Count("seller")).order_by(
            "-num_kalas"
        )
        context.update(
            {
                "kalas": kalas,
                "cate": lst[1],
                "mostsalled": mostsalled,
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
        mostsalled = Cart.objects.annotate(num_kalas=Count("seller")).order_by(
            "-num_kalas"
        )[:5]
        context.update(
            {
                "kalas": kalas,
                "cate": lst[1],
                "mostsalled": mostsalled,
                "brand": manu,
                "brands": Brand.objects.all(),
                "is_authenticated": self.request.user.is_authenticated,
                "form": PriceFilter(),
            }
        )
        return context


def is_authenticated(user):
    return not user.is_authenticated


@login_required(login_url="login")
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


@login_required(login_url="login")
def checkout(request):
    carts = Cart.objects.filter(username=request.user, payed="F")

    if not carts.exists():
        return redirect("cart-empty")

    # Calculate total prices and final amounts in a single loop
    tPrice, final, CFinal = 0, 0, 0
    for cart in carts:
        tPrice += cart.total()
        final += cart.total_price()
        CFinal += cart.finally_price()

    tax = final - tPrice
    coupon = CFinal - final
    sendCost = 5000 * len(carts)
    toPay = CFinal + tax + sendCost

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            company = form.cleaned_data["company"]
            address = form.cleaned_data["address"]
            city = form.cleaned_data["city"]
            postcode = form.cleaned_data["postcode"]
            state = form.cleaned_data["state"]
            description = form.cleaned_data["desc"]

            # Create the Sold record
            sell = Sold.objects.create(
                user=request.user,
                company=company,
                address=address,
                zip_code=postcode,
                state=get_object_or_404(States, id=state),
                city=city,
                total_price=CFinal,
                send_price=sendCost,
                tax=tax,
                total=toPay,
                desc=description,
            )

            # Update cart items and product stock
            for cart in carts:
                if cart.seller:
                    sell.products.add(cart)
                    instance = cart.seller
                    if instance.instock > 0:
                        instance.instock -= 1
                        instance.save()
                    else:
                        # Handle out-of-stock scenario
                        return render(
                            request,
                            "checkout.html",
                            {
                                "form": form,
                                "state": States.objects.all(),
                                "error": f"Product {cart.product} is out of stock.",
                                "carts": carts,
                                "totalPrice": tPrice,
                                "finalPrice": final,
                                "tax": tax,
                                "coupon": coupon,
                                "sendCost": sendCost,
                                "toPay": toPay,
                                "is_authenticated": True,
                                "usr": request.user,
                            },
                        )

            # Bulk update all cart items to mark them as "payed"
            carts.update(payed="T")
            sell.save()

            # Redirect to cart page after successful checkout
            return HttpResponseRedirect(reverse("cart"))
    else:
        form = CheckoutForm(
            initial={
                "address": getattr(request.user, "address", ""),
                "city": getattr(request.user, "city", ""),
                "state": getattr(request.user, "state", None),
                "postcode": getattr(request.user, "postcode", ""),
            }
        )

    context = {
        "form": form,
        "state": States.objects.all(),
        "carts": carts,
        "totalPrice": tPrice,
        "finalPrice": final,
        "tax": tax,
        "coupon": coupon,
        "sendCost": sendCost,
        "toPay": toPay,
        "is_authenticated": True,
        "usr": request.user,
    }

    return render(request, "checkout.html", context)


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
        mostsalled = Cart.objects.annotate(num_kalas=Count("seller")).order_by(
            "-num_kalas"
        )[:5]
        context.update(
            {
                "is_authenticated": self.request.user.is_authenticated,
                "mostsalled": mostsalled,
                "color": Color.objects.all(),
            }
        )
        return context

    # def reduce(func, items):
    #     result = items.pop()
    #     for item in items:
    #         result =  func(result, item)
    #     return result

    def and_(a, b):
        return a and b


@login_required(login_url="login")
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


@login_required(login_url="login")
def account_orders(request):
    cart = Cart.objects.filter(username=request.user, payed="T")
    page = request.GET.get("page", 1)
    paginator = Paginator(cart, 5)
    try:
        carts = paginator.page(page)
    except PageNotAnInteger:
        carts = paginator.page(1)
    except EmptyPage:
        carts = paginator.page(paginator.num_pages)

    salled = []
    for product in cart:
        salled.append(product)

    reverse_list = salled[::-1]
    context = {
        "salled": reverse_list,
        "page_obj": carts,
    }
    return render(request, "account-orders.html", context)


def brands(request):
    context = {
        "brands": Brand.objects.all(),
    }
    return render(request, "brands.html", context)


def faq(request):
    return render(request, "faq.html")


@login_required(login_url="login")
def account_dashboard(request):
    cart = Cart.objects.filter(username=request.user, payed="T")
    salled = []
    for product in cart:
        salled.append(product)

    reverse_list = salled[::-1]
    len_Sold = len(reverse_list) // 2
    context = {
        "salled": reverse_list,
        "lenSold": len_Sold,
    }
    return render(request, "account-dashboard.html", context)


def terms_and_conditions(request):
    return render(request, "terms-and-conditions.html")


@login_required(login_url="login")
def track_order(request):
    return render(request, "track-order.html")


@login_required(login_url="login")
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
