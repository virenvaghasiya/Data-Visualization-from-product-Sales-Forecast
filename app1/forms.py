from django import forms
from .models import StoreDetails,ProductDetails,SalesDetails,FilterDate,StockDetails,profilemodel

#=============Admin=========>
from .models import adminregi
#<===========================

class StoreDetailsForm(forms.ModelForm):
    class Meta:
        model = StoreDetails
        fields = '__all__'

class StockDetailsForm(forms.ModelForm):
    class Meta:
        model = StockDetails
        fields = '__all__'


class ProductDetailsForm(forms.ModelForm):
    class Meta:
        model = ProductDetails
        fields = '__all__'

class SalesDetailsForm(forms.ModelForm):
    class Meta:
        model = SalesDetails
        fields = '__all__'

class FilterDateForm(forms.ModelForm):
    class Meta:
        model = FilterDate
        fields = '__all__'

class profileform(forms.ModelForm):
    class Meta:
        model = profilemodel
        fields = '__all__'
#=============Admin=========>

class adminregform(forms.ModelForm):
    class Meta:
        model = adminregi
        fields = '__all__'