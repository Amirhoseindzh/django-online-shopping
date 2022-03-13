from django.shortcuts import render , redirect , get_object_or_404
from django.views.generic.edit import UpdateView 
from django.views.generic import DetailView , ListView 
from .models import *
from .forms import ProfileForm , PriceFilter , checkoutForm 
from django.http import  HttpResponse , HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required 
from django.contrib import messages
from django.urls import  reverse_lazy , reverse
from django.core.exceptions import ObjectDoesNotExist

from django.db.models import Count
from django.db.models import Q

from config import settings
from django.core.mail import send_mail, EmailMessage
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from . tokens import generateToken


def register(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        confirmpwd = request.POST['comfirmpwd']
        
        if User.objects.filter(email = email).exists():
            messages.error(request, 'This email has an account.')
            return redirect('login')

        if password != confirmpwd:
            messages.error(request, 'The password did not match! ')  
            return redirect('login')                  

        my_user = User.objects.create_user(username = email ,email = email, password = password)
        my_user.is_active = False
        my_user.save()
        messages.success(request, 'Your account has been successfully created. we have sent you an email You must comfirm in order to activate your account.')
        # send email when account has been created successfully
        subject = "Welcome to django-application donaldPro"
        message = "Welcome "+ my_user.email + "\n thank for chosing AbzarKade .\n To order login you need to comfirm your email account.\n thanks\n\n\n Amirhosein Dezhabdolahi"
        
        from_email = settings.EMAIL_HOST_USER
        to_list = [my_user.email]
        send_mail(subject, message, from_email, to_list, fail_silently=False)

        # send the the confirmation email
        current_site = get_current_site(request) 
        email_suject = "confirm your email"
        messageConfirm = render_to_string("emailConfimation.html", {
            'domain':current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(my_user.pk)),
            'token': generateToken.make_token(my_user)
        })       

        email = EmailMessage(
            email_suject,
            messageConfirm,
            settings.EMAIL_HOST_USER,
            [my_user.email]
        )

        email.fail_silently = False
        email.send()
        return redirect('login')
    return render(request, 'account-register.html')    




class Login(LoginView):
    template_name = 'account-login.html'

    def get_success_url(self):
        user=self.request.user

        if user.is_superuser and user.is_staff:
            return reverse('dashboard')
        else:
            return reverse('dashboard')



@login_required(login_url="login")
def logout_user(request):
    logout(request)
    messages.success(request,(_("شما از حساب خود خارج شدید!")))
    return redirect('login')


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        my_user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        my_user = None

    if my_user is not None and generateToken.check_token(my_user, token):
        my_user.is_active  = True        
        my_user.save()
        messages.success(request, "You are account is activated you can login by filling the form below.")
        return redirect("login")
    else:
        messages.success(request, 'Activation failed please try again')
        return redirect('register')



class Profile(LoginRequiredMixin , UpdateView):
    model = User
    template_name = 'account-profile.html'
    form_class = ProfileForm
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        return User.objects.get(pk=self.request.user.pk)


class KalaListView(ListView):
    model = Kala
    context_object_name = 'kala'
    template_name = 'index.html'
    paginate_by = 12

    def post(self ,request, *args, **kwargs):
        kala_id = request.POST.get('kala')
        if request.user.is_authenticated:
            if 'addCart' in request.POST:
                colorid = request.POST.get('Color')
                salerid = request.POST.get('Saller')
                sizeid = request.POST.get('Size')
                materialid  = request.POST.get('Material')
                UsersProducts = Cart.objects.filter(username = request.user, payed = 'F')
                Found = False
                for i in UsersProducts:
                    if i.saller == KalaInstance.objects.get(id = salerid) and \
                        i.size == ProductSize.objects.get(id = sizeid) and \
                        i.material == Materials.objects.get(id = materialid) and \
                        i.color == Color.objects.get(id = colorid):
                        i.count += 1
                        i.save()
                        Found = True
                        break

                if not Found:    
                    addCart = Cart.objects.create(username= request.user, product_id = kala_id,
                                                size = ProductSize.objects.get(id = sizeid),
                                                color= Color.objects.get(id= colorid),
                                                material = Materials.objects.get(id = materialid),
                                                saller= KalaInstance.objects.get(id = salerid))
                return redirect(request.META['HTTP_REFERER'])

            elif 'addWishlist' in request.POST:
                kala_id = request.POST['kala']
                kala_check = Kala.objects.get(id = kala_id)
                if kala_check:
                    product= WishList.objects.filter(user=request.user , product_id = kala_id )
                    if product :
                        product.delete()
                        return redirect(request.META['HTTP_REFERER'])
                    else:
                        w = WishList.objects.create(user = request.user , product_id = kala_id)
                        w.save()
                        return redirect(request.META['HTTP_REFERER'])
                else:
                    return redirect(request.META['HTTP_REFERER'])
            

            elif 'addCompare' in request.POST:
                kala_id = request.POST['kala']
                kala_check = Kala.objects.get(id = kala_id)
                if kala_check:
                    product= Compare.objects.filter(user=request.user , product_id = kala_id )
                    if product :
                        product.delete()
                        return redirect(request.META['HTTP_REFERER'])
                    else:
                        w = Compare.objects.create(user = request.user , product_id = kala_id)
                        w.save()
                        return redirect(request.META['HTTP_REFERER'])
                else:
                    return redirect(request.META['HTTP_REFERER'])

    def get_context_data(self, **kwargs):
        context = super(KalaListView, self).get_context_data(**kwargs)
        mostsalled = Cart.objects.annotate(num_kalas = Count('saller')).order_by('-num_kalas')
        instock = KalaInstance.objects.filter(~Q(instock = 0)).values() 
        context.update({
            'kala': Kala.objects.all(),
            'mostSalled' : mostsalled,
            'instock' : instock,
            'Brands': Brand.objects.all(),
            'posts' : Post.objects.all(),
        })
        return context





def KalaDetailView(request, kalaslug):
    k = get_object_or_404(Kala, slug = kalaslug)
    akala = Kala.objects.filter(category = k.category)
    comments = Comments.objects.filter(kala__id = k.id)

    inst = []
    i = KalaInstance.objects.filter(kala = k)
    for a in i:
        if a.instock != 0:
            inst.append(a)

    if request.user.is_authenticated:
            is_authenticated = True
    else:
            is_authenticated = False

    if request.method == 'POST':
        if request.user.is_authenticated:
                if 'addComment' in request.POST:
                    text = request.POST['text']
                    c = Comments.objects.create(writer = request.user, body = text, Kala = k)
                    c.save()

                elif 'addCart' in request.POST:
                
                    try:
                        colorid = request.POST.get('Color')
                        salerid = request.POST.get('Saller')
                        sizeid = request.POST.get('Size')
                        materialid  = request.POST.get('Material')
                        UsersProducts = Cart.objects.filter(username = request.user, payed = 'F')
                        Found = False
                        for i in UsersProducts:
                            if i.saller == KalaInstance.objects.get(id = salerid) and \
                                i.size == ProductSize.objects.get(id = sizeid) and \
                                i.material == Materials.objects.get(id = materialid) and \
                                i.color == Color.objects.get(id = colorid):
                                i.count += 1
                                i.save()
                                Found = True
                                break

                        if not Found:    
                            addCart = Cart.objects.create(username= request.user, product = k,
                                                        size = ProductSize.objects.get(id = sizeid),
                                                        color= Color.objects.get(id= colorid),
                                                        material = Materials.objects.get(id = materialid),
                                                        saller= KalaInstance.objects.get(id = salerid))
                    except ObjectDoesNotExist:
                        return HttpResponse('<br><center>مشخصات کالا  مورد نظر را انتخاب کنید و دوباره امتحان کنید </center>')
                
                elif 'addWishlist' in request.POST:
                    kala_id = request.POST['kala']
                    kala_check = Kala.objects.get(id = kala_id)
                    if kala_check:
                        product= WishList.objects.filter(user=request.user , product_id = kala_id )
                        if product :
                            product.delete()
                            return redirect(request.META['HTTP_REFERER'])
                        else:
                            w = WishList.objects.create(user = request.user , product_id = kala_id)
                            w.save()
                            return redirect(request.META['HTTP_REFERER'])
                    else:
                        return redirect(request.META['HTTP_REFERER'])
                

                elif 'addCompare' in request.POST:
                    kala_id = request.POST['kala']
                    kala_check = Kala.objects.get(id = kala_id)
                    if kala_check:
                        product= Compare.objects.filter(user=request.user , product_id = kala_id )
                        if product :
                            product.delete()
                            return redirect(request.META['HTTP_REFERER'])
                        else:
                            w = Compare.objects.create(user = request.user , product_id = kala_id)
                            w.save()
                            return redirect(request.META['HTTP_REFERER'])
                    else:
                        return redirect(request.META['HTTP_REFERER'])
            

    if inst:
        context = {
            'kala' : k,
            'Allkala' : akala,
            'comments' : comments,
            'inst' : inst,
            'is_authenticated' : is_authenticated,
            'finst': inst[0],
        }
    else:
        context = {
            'kala' : k,
            'Allkala' : akala,
            'comments' : comments,
            'is_authenticated' : is_authenticated,
        }
    return render(request, 'product.html', context)



def CategoryOrInstockSluger(catslug):
   
    kalasCat = get_object_or_404(KalaCategory, slug = catslug)
    kalas = kalasCat.Category.all()
    cate = kalasCat

    return kalas, cate



def JustInstock(kalas):
    lstKalas = []
    for i in kalas:
        if i.kalainst.filter(~Q(instock = 0)):
            lstKalas.append(i)
    return lstKalas



def MaxMinPrice(kalas, minPrice, maxPrice):
    lstKalas = []
    for i in kalas:
        if i.kalainst.filter(~Q(instock = 0)):
            if i.kalainst.filter(price__lte = maxPrice):
                if len(i.kalainst.filter(price__gt = minPrice)):
                    lstKalas.append(i)
    return lstKalas



class CategoryListView(ListView):
    model = Kala
    context_object_name = 'kalas'
    template_name = 'shop-grid.html'
    paginate_by = 12
    queryset = Kala.objects.all() 

    def post(self, request, *args, **kwargs):
        form = PriceFilter(request.POST)
        if form.is_valid():
            minPrice = form.cleaned_data['minPrice']
            maxPrice = form.cleaned_data['maxPrice']
            return HttpResponseRedirect(reverse('CategoryPriceFilter', kwargs={'catslug' : self.kwargs['catslug'],'minPrice' : minPrice, 'maxPrice' : maxPrice}))
        return HttpResponseRedirect(reverse('CategoryListViewInstock', kwargs={'catslug' : self.kwargs['catslug']}))
     
    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        catslug = self.kwargs['catslug']
        lst = CategoryOrInstockSluger(catslug)
        form = PriceFilter()
        color = Color.objects.all()
        mostsalled = Cart.objects.annotate(num_kalas = Count('saller')).order_by('-num_kalas')
        context.update({
            'kalas' : lst[0],
            'cate' : lst[1],
            'brands' : Brand.objects.all(),
            'mostsalled' : mostsalled,
            'form' : form,
            'colors' : color,
            'is_authenticated' : self.request.user.is_authenticated,
        })
        return context



class CategoryListViewInstock(CategoryListView):
    model = Kala
    context_object_name = 'kalas'
    template_name = 'shop-grid.html'
    paginate_by = 12

    def post(self, request, *args, **kwargs):
        form = PriceFilter(request.POST)
        if form.is_valid():
            minPrice = form.cleaned_data['minPrice']
            maxPrice = form.cleaned_data['maxPrice']
            return HttpResponseRedirect(reverse('CategoryPriceFilter', kwargs={'catslug' : self.kwargs['catslug'],'minPrice' : minPrice, 'maxPrice' : maxPrice}))
        return HttpResponseRedirect(reverse('CategoryListViewInstock', kwargs={'catslug' : self.kwargs['catslug']}))
        
    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        catslug = self.kwargs['catslug']
        lst = CategoryOrInstockSluger(catslug)
        form = PriceFilter()
        kalas = JustInstock(lst[0])
        mostsalled = Cart.objects.annotate(num_kalas = Count('saller')).order_by('-num_kalas')[:5]
        context.update({
            'kalas' : kalas,
            'cate' : lst[1],
            'brands' : Brand.objects.all(),
            'mostsalled' : mostsalled,
            'is_authenticated' : self.request.user.is_authenticated,
            'form' : form,
        }) 
        return context



class CategoryPriceFilterListView(ListView):
    model = Kala
    context_object_name = 'kalas'
    template_name = 'shop-grid.html'
    paginate_by = 12

    def post(self, request, *args, **kwargs):
        form = PriceFilter(request.POST)
        if form.is_valid():
            minPrice = form.cleaned_data['minPrice']
            maxPrice = form.cleaned_data['maxPrice']
            return HttpResponseRedirect(reverse('CategoryPriceFilter', kwargs={'catslug' : self.kwargs['catslug'],'minPrice' : minPrice, 'maxPrice' : maxPrice}))
        return HttpResponseRedirect(reverse('CategoryListViewInstock', kwargs={'catslug' : self.kwargs['catslug']}))
  
    def get_context_data(self, **kwargs):
        context = super(CategoryPriceFilterListView, self).get_context_data(**kwargs)
        minPrice = int(self.kwargs['minPrice'])
        maxPrice = int(self.kwargs['maxPrice'])
        lst = CategoryOrInstockSluger(self.kwargs['catslug'])
        kalas = MaxMinPrice(lst[0], minPrice, maxPrice)
        form = PriceFilter()
        mostsalled = Cart.objects.annotate(num_kalas = Count('saller')).order_by('-num_kalas')[:5]
        context.update({
            'kalas' : kalas,
            'cate' : lst[1],
            'brands' : Brand.objects.all(),
            'mostsalled' : mostsalled,
            'is_authenticated' : self.request.user.is_authenticated,
            'form' : form,
        })
        return context
    

class BrandListView(ListView):
    model = Kala
    context_object_name = 'kalas'
    template_name = 'shop-grid.html'
    paginate_by = 12

    def post(self, request, *args, **kwargs):
        form = PriceFilter(request.POST)
        if form.is_valid():
            minPrice = form.cleaned_data['minPrice']
            maxPrice = form.cleaned_data['maxPrice']
            return HttpResponseRedirect(reverse('BrandPriceFilter', kwargs={'brandslug' : self.kwargs['brandslug'],'minPrice' : minPrice, 'maxPrice' : maxPrice}))
         
    def get_context_data(self, **kwargs):
        context = super(BrandListView, self).get_context_data(**kwargs)
        maker = get_object_or_404(Brand, slug = self.kwargs["brandslug"])
        products = maker.brand.all()
        mostsalled = Cart.objects.annotate(num_kalas = Count('saller')).order_by('-num_kalas')[:5]
        context.update({
            'kalas' : products,
            'brand': maker,
            'mostsalled' : mostsalled,
            'brands' : Brand.objects.all(),
            'is_authenticated' : self.request.user.is_authenticated,
            'form' : PriceFilter(),
        })
        return context

class BrandListViewInstock(ListView):
    model = Kala
    context_object_name = 'kalas'
    template_name = 'shop-grid.html'
    paginate_by = 12

    def post(self, request, *args, **kwargs):
        form = PriceFilter(request.POST)
        if form.is_valid():
            minPrice = form.cleaned_data['minPrice']
            maxPrice = form.cleaned_data['maxPrice']
            return HttpResponseRedirect(reverse('BrandPriceFilter', kwargs={'brandslug' : self.kwargs['brandslug'],'minPrice' : minPrice, 'maxPrice' : maxPrice}))
        
    def get_context_data(self, **kwargs):
        context = super(BrandListViewInstock, self).get_context_data(**kwargs)
        maker = get_object_or_404(Brand, slug = self.kwargs["brandslug"])
        products = JustInstock(maker.manufactor.all())
        mostsalled = Cart.objects.annotate(num_kalas = Count('saller')).order_by('-num_kalas')[:5]
        context.update({
            'kalas' : products,
            'brand': maker,
            'mostsalled' : mostsalled,
            'brands' : Brand.objects.all(),
            'is_authenticated' : self.request.user.is_authenticated,
            'form' : PriceFilter(),
        })
        return context

class BrandPriceFilter(ListView):
    model = Kala
    context_object_name = 'kalas'
    template_name = 'shop-grid.html'
    paginate_by = 12

    def post(self, request, *args, **kwargs):
        form = PriceFilter(request.POST)
        if form.is_valid():
            minPrice = form.cleaned_data['minPrice']
            maxPrice = form.cleaned_data['maxPrice']
            return HttpResponseRedirect(reverse('BrandPriceFilter', kwargs={'brandslug' : self.kwargs['brandslug'],'minPrice' : minPrice, 'maxPrice' : maxPrice}))
     
    def get_context_data(self, **kwargs):
        context = super(BrandPriceFilter, self).get_context_data(**kwargs)
        maker = get_object_or_404(Brand, slug = self.kwargs["brandslug"])
        products = MaxMinPrice(maker.manufactor.all(), self.kwargs['minPrice'], self.kwargs['maxPrice'])
        mostsalled = Cart.objects.annotate(num_kalas = Count('saller')).order_by('-num_kalas')[:5]
        context.update({
            'kalas' : products,
            'brand': maker,
            'mostsalled' : mostsalled,
            'brands' : Brand.objects.all(),
            'is_authenticated' : self.request.user.is_authenticated,
            'form' : PriceFilter(),
        })
        return context


def BrandCategorySluger(catslug, manu):
   
    kalasCat = get_object_or_404(KalaCategory, slug = catslug)
    kalas = manu.brand.filter(category = kalasCat)
    cate = kalasCat

    return kalas, cate

class BrandCategory(ListView):
    model = Kala
    context_object_name = 'kalas'
    template_name = 'shop-grid.html'
    paginate_by = 12

    def post(self, request, *args, **kwargs):
        form = PriceFilter(request.POST)
        if form.is_valid():
            minPrice = form.cleaned_data['minPrice']
            maxPrice = form.cleaned_data['maxPrice']
            return HttpResponseRedirect(reverse('BrandCategoryPriceFilter', kwargs={'catslug' : self.kwargs['catslug'],'brandslug' : self.kwargs['brandslug'],'minPrice' : minPrice, 'maxPrice' : maxPrice}))
    
    def get_context_data(self, **kwargs):
        context = super(BrandCategory, self).get_context_data(**kwargs)
        brand = self.kwargs['brandslug']
        catslug = self.kwargs['catslug']
        manu = get_object_or_404(Brand, slug = brand)
        lst = BrandCategorySluger(catslug, manu)
        mostsalled = Cart.objects.annotate(num_kalas = Count('saller')).order_by('-num_kalas')[:5]
        context.update({
            'kalas' : lst[0],
            'cate' : lst[1],
            'mostsalled' : mostsalled,
            'brand': manu,
            'brands' : Brand.objects.all(),
            'is_authenticated' : self.request.user.is_authenticated,
            'form' : PriceFilter(),
        })
        return context

class BrandCategoryInstock(ListView):
    model = Kala
    context_object_name = 'kalas'
    template_name = 'shop-grid.html'
    paginate_by = 12

    def post(self, request, *args, **kwargs):
        form = PriceFilter(request.POST)
        if form.is_valid():
            minPrice = form.cleaned_data['minPrice']
            maxPrice = form.cleaned_data['maxPrice']
            return HttpResponseRedirect(reverse('BrandCategoryPriceFilter', kwargs={'catslug' : self.kwargs['catslug'],'brandslug' : self.kwargs['brandslug'],'minPrice' : minPrice, 'maxPrice' : maxPrice}))
    
    def get_context_data(self, **kwargs):
        context = super(BrandCategoryInstock, self).get_context_data(**kwargs)
        brand = self.kwargs['brandslug']
        catslug = self.kwargs['catslug']
        manu = get_object_or_404(Brand, slug = brand)
        lst = BrandCategorySluger(catslug, manu)
        kalas = JustInstock(lst[0])
        mostsalled = Cart.objects.annotate(num_kalas = Count('saller')).order_by('-num_kalas')
        context.update({
            'kalas' : kalas,
            'cate' : lst[1],
            'mostsalled' : mostsalled,
            'brand': manu,
            'brands' : Brand.objects.all(),
            'is_authenticated' : self.request.user.is_authenticated,
            'form' : PriceFilter(),
        })
        return context

class BrandCategoryPriceFilter(ListView):
    model = Kala
    context_object_name = 'kalas'
    template_name = 'shop-grid.html'
    paginate_by = 12

    def post(self, request, *args, **kwargs):
        form = PriceFilter(request.POST)
        if form.is_valid():
            minPrice = form.cleaned_data['minPrice']
            maxPrice = form.cleaned_data['maxPrice']
            return HttpResponseRedirect(reverse('BrandCategoryPriceFilter', kwargs={'catslug' : self.kwargs['catslug'], 'brandslug' : self.kwargs['brandslug'], 'minPrice' : minPrice, 'maxPrice' : maxPrice}))

    def get_context_data(self, **kwargs):
        context = super(BrandCategoryPriceFilter, self).get_context_data(**kwargs)
        brand = self.kwargs['brandslug']
        catslug = self.kwargs['catslug']
        maxPrice = self.kwargs['maxPrice']
        minPrice = self.kwargs['minPrice']
        manu = get_object_or_404(Brand, slug = brand)
        lst = BrandCategorySluger(catslug, manu)
        kalas = MaxMinPrice(lst[0], minPrice, maxPrice)
        mostsalled = Cart.objects.annotate(num_kalas = Count('saller')).order_by('-num_kalas')[:5]
        context.update({
            'kalas' : kalas,
            'cate' : lst[1],
            'mostsalled' : mostsalled,
            'brand': manu,
            'brands' : Brand.objects.all(),
            'is_authenticated' : self.request.user.is_authenticated,
            'form' : PriceFilter(),
        })
        return context

def is_authenticated(user):
    return not user.is_authenticated



@login_required(login_url="login" , )
def cart_(request):
    objs = Cart.objects.filter(username = request.user ,payed = 'F')
    tPrice = 0
    for i in objs:
        tPrice += i.total()
    final = 0
    for i in objs:
        final += i.total_price()
    CFinal = 0
    for i in objs:
        CFinal += i.finally_price()
    
    tax = final - tPrice  
    coupon = CFinal - final  
    sendCost = 5000 * len(objs)
    toPay = CFinal + tax + sendCost

    if objs:
        if request.method == 'POST':
            if 'update' in request.POST:
                slug = request.POST.get('product_slug')
                count = request.POST.get('quantity')
                product_obj = Kala.objects.get(slug = slug)
                for obj in objs:
                    if obj.product == product_obj:
                        obj.count = int(count)
                        obj.save()
                        break
            if 'delete' in request.POST:
                slug = request.POST.get('product_slug')
                count = request.POST.get('quantity')
                product_obj = Kala.objects.get(slug = slug)
                for obj in objs:
                    if obj.product == product_obj:
                        print('-----   Found : True   -----')
                        obj.delete()
                        break
                return redirect(request.META['HTTP_REFERER'])

            if 'applyCoupon' in request.POST:
                code = request.POST.get('couponCode')
                error = None
                try:
                    co = Coupon.objects.get(code = code)
                    if co.is_expired():
                        error = 'تاریخ استفاده از این کوپن به پایان رسیده است!'
                    elif not co.count > 0:
                        error = 'تعداد استفاده از این کوپن به پایان رسیده است!'
                    else:
                        for obj in objs:
                            obj.coupon = co
                            obj.save()
                        return HttpResponseRedirect(reverse('cart'))
                except Coupon.DoesNotExist:
                    error = 'کد کوپن نادرست می باشد!'
                
                if error != None:
                    context = {
                        'carts' : objs,
                        'is_authenticated' : True,
                        'error' : error,
                    }
                return render(request, 'cart.html', context)
            
        context = {
            'carts' : objs,
            'is_authenticated' : True,
            'totalPrice': tPrice,
            'finalPrice' : final,
            'tax' : tax,
            'coupon': coupon,
            'sendCost' : sendCost,
            'toPay': toPay,
        }
        return render(request, 'cart.html', context)
    else:
        return render(request, 'cart-empty.html')


def contact_us(request):
    context = {}
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        description = request.POST['description']
        call = ContactUs.objects.create(name = name, email = email, desc = description)
        call.save()
        context = {
            'sent' : True,
        }
    return render(request, 'contact-us.html', context)


@login_required(login_url="login")
def checkout(request):
    usr = User.objects.get(username= request.user)
    carts = Cart.objects.filter(username = request.user, payed = 'F')
    tPrice=0
    for i in carts:
        tPrice += i.total()
    final = 0
    for i in carts:
        final += i.total_price()
    CFinal = 0
    for i in carts:
        CFinal += i.finally_price()
    
    tax = final - tPrice  
    coupon = CFinal - final  
    sendCost = 5000 * len(carts)
    toPay = CFinal + tax + sendCost

    if request.method == 'POST':
        form = checkoutForm(request.POST)
        if form.is_valid():
            company = form.cleaned_data['company']
            address = form.cleaned_data['address']
            city = form.cleaned_data['city']
            postcode = form.cleaned_data['postcode']
            state = form.cleaned_data['state'] 
            description = form.cleaned_data['desc']  
            sell = Salled.objects.create(user= request.user, company= company,
                                        address = address, zip_code= postcode,
                                        state= States.objects.get(id = state),
                                        city= city, total_price= CFinal, send_price= sendCost, tax= tax,
                                        total= toPay, desc= description)
                
            for c in carts:
                sell.products.add(c)
                instance = c.saller
                instance.instock -= 1
                instance.save()
                c.payed = 'T'
                c.save()

            sell.save()
            return HttpResponseRedirect(reverse('cart'))
        
    else:
        
        form = checkoutForm(initial={'address' : usr.address, 'city' : usr.city, 'state' : usr.state, 'postcode' : usr.postcode})
    
    context = {
        'form' : form,
        'state' : States.objects.all(),
        'not_authenticated' : False,
        'carts' : carts,
        'totalPrice': tPrice,
        'finalPrice' : final,
        'tax' : tax,
        'coupon': coupon,
        'sendCost' : sendCost,
        'toPay': toPay,
        'is_authenticated' : True,
        'usr' : usr,
    }
    return render(request, 'checkout.html', context)



class PostListView(ListView):
    model = Post
    template_name = 'blog-classic.html'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        post = Post.objects.all()
        context.update({
            'posts' : post  
        })
        return context


class LatestPostsMixin(object):

    def get_context_data(self, **kwargs):
        context = super(LatestPostsMixin, self).get_context_data(**kwargs)
        try:
            context['latest_posts_list'] =  Post.objects.all()
        except:
            pass
        return context


class PostDetailView(LatestPostsMixin,DetailView):
    model = Post
    template_name = 'post.html'
    slug = 'slug'
    


class Address(LoginRequiredMixin,DetailView):
    model = User
    template_name = 'account-addresses.html'

    def get_object(self):
        return User.objects.get(pk=self.request.user.pk )



"""from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger

def search_post(request , search=None):
    if request.method =='POST':
        user_search = request.POST.get('search')
        
        if user_search:
            post_results1 = Post.objects.filter(body__icontains= user_search)
            post_results2 = Post.objects.filter(title__icontains= user_search)
            posts = post_results1 | post_results2

            if search:
                posts.filter(slug__in= search)
            
            paginator = Paginator(posts , 6)
            page = request.GET.get('page')

            try:
                posts = paginator.page(page)
            except PageNotAnInteger:
                posts = paginator.page(1)
            except EmptyPage:
                posts = paginator.page(paginator.num_pages)
            
            return render(request , 'blog-classic.html' , {'posts':posts , 'page':page })
    
    post_results = Post.objects.all()
    posts = post_results
    if search:
        posts.filter(slug__in= search)
        
    paginator = Paginator(posts , 6)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request , 'blog-classic.html' , {'posts':posts , 'page':page })
"""




from functools import reduce
import operator

class SearchKala(KalaListView):
    """
        Display a Product List  filtered by search query
    """
    paginate_by = 12
    template_name = 'shop-grid.html'
    context_object_name = 'kalas'
    
    def get_queryset(self):
        result = super(SearchKala, self).get_queryset()
        query = self.request.GET.get('search')
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(operator.and_,
                (Q(name__icontains = q) for q in query_list))
            )
        return result

    def get_context_data(self, **kwargs):
        context = super(SearchKala, self).get_context_data(**kwargs)
        mostsalled = Cart.objects.annotate(num_kalas = Count('saller')).order_by('-num_kalas')[:5]
        context.update({
            'is_authenticated' : self.request.user.is_authenticated,
            'mostsalled' : mostsalled,
            'color':Color.objects.all()
        })
        return context

    def reduce(func, items):
        result = items.pop()
        for item in items:
            result = func(result, item)
        return result       
    
    def and_(a, b):
        return a and b
   

@login_required(login_url='login')
def compare(request):
    compare = Compare.objects.filter( user = request.user)
    product = []

    for p in compare:
        product_detail = KalaInstance.objects.filter(kala__slug=p.product.slug)
 
        for a in product_detail:
            
            product.append(a) 
            

    if request.method == 'POST':

        if 'delete' in request.POST:
            slug = request.POST.get('product_slug')
            product_obj = Kala.objects.get(slug = slug)
            for obj in compare:
                if obj.product == product_obj:
                    print('-----   Found : True   -----')
                    obj.delete()
                    break
        return redirect(request.META['HTTP_REFERER'])


    context = {
        'compare':compare,
        'detail':product,

    }
    return render(request , 'compare.html' , context)


    


def error_404(request , *args ,**kwargs):
    return render(request ,'404.html')

def error_500(request , *args ,**kwargs):
    return render(request ,'500.html')

def about_us(request):
    return render(request ,'about-us.html')


from django.core.paginator import Paginator ,EmptyPage, PageNotAnInteger
@login_required(login_url="login")
def account_orders(request):
    cart = Cart.objects.filter(username = request.user, payed = 'T')
    page = request.GET.get('page', 1)
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
        'salled':reverse_list,
        'page_obj': carts,
    }
    return render(request ,'account-orders.html' , context)



def brands(request):
    context = {
        'brands' : Brand.objects.all(),
    }
    return render(request ,'brands.html' , context)


def faq(request):
    return render(request ,'faq.html')



@login_required(login_url="login")
def account_dashboard(request):
    cart = Cart.objects.filter(username = request.user, payed = 'T')
    salled = []
    for product in cart:
        salled.append(product)
    
    reverse_list = salled[::-1]
    lenSalled = len(reverse_list)//2
    context = {
        'salled':reverse_list,
        'lenSalled': lenSalled,
        
    }
    return render(request ,'account-dashboard.html' , context)



def terms_and_conditions(request):
    return render(request ,'terms-and-conditions.html')
    

@login_required(login_url="login")
def track_order(request):
        return render(request ,'track-order.html')



@login_required( login_url ='login')
def wishlist(request):
    wishlist = WishList.objects.filter( user = request.user)
    product = []

    for p in wishlist:
        product_detail = KalaInstance.objects.filter(kala__slug=p.product.slug)
 
        for a in product_detail:
            
            product.append(a) 
            

    if request.method == 'POST':

        if 'delete' in request.POST:
            slug = request.POST.get('product_slug')
            product_obj = Kala.objects.get(slug = slug)
            for obj in wishlist:
                if obj.product == product_obj:
                    print('-----   Found : True   -----')
                    obj.delete()
                    break
        return redirect(request.META['HTTP_REFERER'])


    context = {
        'wishlist':wishlist,
        'detail':product,

    }
    return render(request , 'wishlist.html' , context)








