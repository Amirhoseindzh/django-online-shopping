from django.db import transaction
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from .models import Sold, States


class CheckoutProcessor:
    """Handles the checkout process, including Sold record creation and stock updates."""

    def __init__(self, user, form_data, carts, totals):
        self.user = user
        self.form_data = form_data
        self.carts = carts
        self.totals = totals

    def process(self):
        """Process checkout and create necessary records."""
        with transaction.atomic():  # Ensure atomicity
            state = get_object_or_404(States, id=self.form_data["state"])
            sell = Sold.objects.create(
                user=self.user,
                address=self.form_data["postal_address"],
                zip_code=self.form_data["postal_code"],
                state=state,
                city=self.form_data["city"],
                total_price=self.totals["CFinal"],
                shipping_fee=self.totals["sendCost"],
                tax=self.totals["tax"],
                grand_total=self.totals["toPay"],
                description=self.form_data["desc"],
            )

            # Add cart items to sold record and update stock
            for cart in self.carts:
                if cart.seller:
                    if cart.seller.instock > 0:
                        cart.seller.instock -= 1
                        cart.seller.save()
                        sell.products.add(cart)
                    else:
                        raise ValidationError(
                            f"Product {cart.product} is out of stock."
                        )

            # Mark all cart items as "payed"
            self.carts.update(paid="T")
            sell.save()

        return sell


class CartCalculator:
    """A strategy class to calculate totals and prices for carts."""

    def __init__(self, carts):
        self.carts = carts

    def calculate_totals(self):
        """Calculate tPrice, final, CFinal, tax, coupon, and sendCost."""
        tPrice, final, CFinal = 0, 0, 0
        for cart in self.carts:
            tPrice += cart.total()
            final += cart.total_price()
            CFinal += cart.finally_price()

        tax = final - tPrice
        coupon = CFinal - final
        sendCost = 5000 * len(self.carts)
        toPay = CFinal + (-tax) + sendCost

        return {
            "tPrice": tPrice,
            "final": final,
            "CFinal": CFinal,
            "tax": tax,
            "coupon": coupon,
            "sendCost": sendCost,
            "toPay": toPay,
        }
