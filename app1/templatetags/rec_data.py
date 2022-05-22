from django import template

from app1.models import StockDetails, ProductDetails

register = template.Library()

@register.filter(name='qty_check')
def qty_check(product):
    pro = StockDetails.objects.get(productName=product.productname)
    # print(pro.quantity, product.productquantity)
    if int(product.productquantity) <= int(pro.quantity):
        return True
    return False

@register.filter(name='qty_data')
def qty_data(product):
    pro = StockDetails.objects.get(productName=product.productname)
    # print(pro.quantity, product.productquantity)
    data = int(pro.quantity)
    return data
