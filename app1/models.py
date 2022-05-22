from django.db import models

class StoreDetails(models.Model):
    StoreName = models.CharField(max_length = 50,blank = True)
    PersonName = models.CharField(max_length = 50,blank = True)
    Contact = models.IntegerField(blank = True)
    email = models.EmailField(blank = True, default="", max_length=150)
    password = models.CharField(max_length = 50)
    add1 = models.TextField(default="")

    def __str__(self):
        return self.StoreName


class StockDetails(models.Model):
    # admin_nm = models.ForeignKey('adminregi',on_delete=models.CASCADE, null=True)
    productName = models.CharField(max_length = 150,blank = True)
    #PersonName = models.CharField(max_length = 50,blank = True)
    quantity = models.IntegerField()
    price = models.IntegerField()

    def __str__(self):
        return self.productName

    #email = models.EmailField(blank = True, unique = True)
    #password = models.CharField(max_length = 50)


class SK_Bills(models.Model):
    store_person = models.ForeignKey('StoreDetails',on_delete=models.CASCADE, null=True)
    Bill_No = models.CharField(max_length = 200,default="")
    pd_nm = models.CharField(max_length = 200,default="")
    pd_price = models.FloatField(default=0.0)
    pd_qty = models.IntegerField(default=0)
    pd_tot = models.FloatField(default=0.0)
    date_data = models.DateField(auto_now=False,blank=True,null=True)
    
    def __str__(self):
        return self.Bill_No


class ProductDetails(models.Model):
    store_person = models.ForeignKey('StoreDetails',on_delete=models.CASCADE, null=True)
    productname = models.CharField(max_length = 50,default="")
    productquantity = models.IntegerField()
    date = models.DateField(auto_now=False,blank=True,null=True)
    status = models.BooleanField(default=False)
    isDeny = models.BooleanField(default=False)
    Bills_id = models.CharField(max_length = 200,default="",null=True,blank=True)

    def __str__(self):
        return self.productname

class SalesDetails(models.Model):
    productname = models.CharField(max_length = 50)
    qty = models.IntegerField()
    date = models.CharField(max_length = 50,blank = True)
    totalprice = models.CharField(max_length = 50, blank = True)

class FilterDate(models.Model):
    filterdataDate = models.CharField(max_length = 50,blank = True)

class profilemodel(models.Model):
    firstname= models.CharField(max_length=100)
    email = models.EmailField(max_length=100,default='')
    mobileno = models.PositiveIntegerField(default='')
    address = models.TextField(max_length=1000,default='')
    store = models.CharField(max_length=100)
#=====================ADMIN=============>
class adminregi(models.Model):
    admin_nm = models.CharField(max_length = 50,unique = True)
    email = models.EmailField(blank = True ,default='',max_length=100,unique=True)
    password1 = models.CharField(max_length = 50)
    password2 = models.CharField(max_length = 50)
    def __unicode__(self):
        return self.admin_nm


class SaleFilter(models.Model):
    ProductName = models.CharField(max_length = 50,blank = True)