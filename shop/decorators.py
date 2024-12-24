from functools import wraps
from .models import WishList, Compare, Cart


def check_wishlist_compare_cart(view_func):
    """this function decorator checks if products exist in 
        wishlist or compare or cart when user is logged in.

    Args:
        view_func (`kala_detail_view`): show all about product in view and render 
        it to template.

    Returns:
        _type_: bool.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        product_id = kwargs.get("kala_id")
        in_wishlist = in_compare = in_cart = False
        
        if request.user.is_authenticated:
            in_wishlist = WishList.objects.filter(user=request.user, product_id=product_id).exists()
            in_compare = Compare.objects.filter(user=request.user, product_id=product_id).exists()
            in_cart = Cart.objects.filter(user=request.user, product_id=product_id, paid="F").exists()
        
        request.in_wishlist = in_wishlist
        request.in_compare = in_compare
        request.in_cart = in_cart
        return view_func(request, *args, **kwargs)
    return wrapper
