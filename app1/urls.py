
from django.urls import path
from .views import *

urlpatterns = [
    path('', LoginView, name='LoginView'),
    path('dashboard/', Dashboard, name='Dashboard'),
    path('View_Bills/<str:ids>', SK_View_Bills, name='SK_View_Bills'),
    path('SK_create_pdf/<str:dt>', SK_Create_Pdf, name='sk_create_pdf'),
    path('addproduct/', AddProduct, name='AddProduct'),
    path('productlist/', ProductListView, name='ProductListView'),
    path('deleteproduct/<int:id>', DeleteProduct, name='DeleteProduct'),
    path('editproduct/<int:id>', EditProduct, name='EditProduct'),
    path('addsales/', AddSaleView, name='AddSaleView'),
    path('saleslist/', SalesListView, name='SalesListView'),
    path('salesdelete/<int:id>', SalesDelete, name='SalesDelete'),
    path('logoutstore/', LogoutStore, name='LogoutStore'),
    path('profile/', profileview, name='profile'),

    # path('profileedit/<int:pk>',profileedit,name = 'profileedit'),

    # path('search/',search,name = 'search'),
    # ======================Admin=======================>
    path('adminregister/', Adminregister, name='Adminregister'),
    path('adminlogin/', Adminlogin, name='Adminlogin'),

    path('admin_SK_create_pdf/<str:dt>',
         admin_SK_Create_Pdf, name='admin_sk_create_pdf'),
    # Forget Password -----------
    path('forgotpass/', forgot_pass, name='forgotpass'),
    path('otpcheck/', otpcheck, name='otpcheck'),
    path('newpassword/', newpassword, name='newpassword'),
    path('upload_dataset/',upload_dataset,name='upload_dataset'),
    # Forget Password -----------
    path('admindashboard/', AdminDashboard, name='AdminDashboard'),
    path('storedelete/<int:id>', deletestore, name='deletestore'),
    path('storeview/<int:id>', viewstore, name='viewstore'),
    path('storeedit/<int:id>', editstore, name='editstore'),
    path('addstore/', addstore, name='addstore'),
    path('addstock/', addstock, name='addstock'),
    path('viewstock/', viewstock, name='viewstock'),
    path('editstock/<int:id>', editstock, name='editstock'),
    path('accept_data/<int:sk>/<int:id>/', accepteddata, name='accept_data'),
    path('denied_data/<int:sk>/<int:id>/', denieddata, name='denied_data'),
    path('salefilter/', SalefilterView, name='SalefilterView'),
    path('storesales/', GraphCall, name='storesales'),
    path('monthsale/', monthsaleview, name='monthsaleview'),
    path('adminlogout/', adminlogout, name='adminlogout'),
    path('totallist/', totallistview, name='totallistview'),
    path('todaylist/', todaylistview, name='todaylistview'),
    path('Confirm_Orders/', Confirm_Orders, name="confirm_order"),
    path('billdata/<str:dt>', billdata, name='billdata'),
    path('Order_Bills_data/', Order_Bills_data, name='Order_Bills_data'),
    # HTml To PDF -------------
    path('create_pdf/<str:dt>', Create_Pdf, name='create_pdf'),
    #path('salesprediction/',predict_graph,name = 'prediction'),
    path('createGraph/', createGraph, name="createGraph"),
]
