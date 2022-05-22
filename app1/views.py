from json import dumps
from datetime import datetime, timezone
from django.shortcuts import render, redirect, get_object_or_404
from .models import StoreDetails, ProductDetails, SalesDetails, FilterDate, StockDetails, profilemodel, SK_Bills
from .forms import ProductDetailsForm, SalesDetailsForm, FilterDateForm, StoreDetailsForm, StockDetailsForm, profileform
from django.http import HttpResponse, HttpResponseRedirect
from datetime import date
import datetime
import pytz
import time
from django.contrib import messages
from django.db.models import Q
import math
# email ---------
import smtplib
import email.message
from smtplib import SMTP

import random

from django.conf import settings

# Html To Pdf -------------------

from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa

from django.http import HttpResponse
from django.views.generic import View

import pdfkit

# Html To Pdf -------------------

from sklearn.linear_model import LinearRegression

# ===============ADMIN=================>
from .models import adminregi, SaleFilter, SK_Bills
from .forms import adminregform
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# <====================================
from plotly.offline import plot
#pip install django==3.0
#pip install xhtml2pdf
#pip install pdfkit
from plotly.graph_objs import Scatter

def createGraph(request):
    bills = SK_Bills.objects.all()
    bills_store = list(set([b.store_person for b in bills]))
    bills_products = list(set([b.pd_nm for b in bills]))
    if request.POST:
        s=request.POST["store"]
        p=request.POST["product"]
        bills_requested = SK_Bills.objects.filter(store_person=StoreDetails.objects.get(
            StoreName=s), pd_nm=p).order_by('-date_data')

        bill_store_date_reuested, bills_store_quantity_requested = [], []
        [[bill_store_date_reuested.append(b.date_data.year), bills_store_quantity_requested.append(
            b.pd_qty)] for b in bills_requested]

        s1, s2 = pd.Series(bill_store_date_reuested), pd.Series(
            bills_store_quantity_requested)
        df = pd.DataFrame({'a': s1, 'b': s2})

        df = df.groupby(df['a'])['b'].agg(['sum'])
        bill_store_date_reuested, bills_store_quantity_requested = list(
            df.index), list(df["sum"])

        if (len(bills_store_quantity_requested) == 0):
            no_date = True
        else:
            no_date = False

        plot_div, data = None, None
        if not no_date:
            data = [[bill_store_date_reuested[i], bills_store_quantity_requested[i]]
                    for i in range(len(bills_store_quantity_requested))]
            model = LinearRegression()
            model.fit(np.array(bill_store_date_reuested).reshape(
                -1, 1), np.array(bills_store_quantity_requested).reshape(-1, 1))
            year = np.array(int(request.POST["year"])).reshape(-1, 1)

            predicted = model.predict(
                np.array(year).reshape(-1, 1))
            if predicted[0][0]<0:
                predicted[0][0]=0
            data.append([year[0][0], round(int(predicted[0][0]))])

            bill_store_date_reuested.append(year[0][0])
            bills_store_quantity_requested.append(int(predicted[0][0]))

            plot_div = plot([Scatter(x=bill_store_date_reuested, y=bills_store_quantity_requested,
                                     mode='lines', name='test',
                                     opacity=0.8, marker_color='green')],
                            output_type='div')
            print(bill_store_date_reuested[1])
        return render(request, 'admin/newGraph.html', {'year':year ,'s':s,'p':p,'no_data': no_date, 'store': bills_store, 'product': bills_products, 'plot_div': plot_div, 'data': data})
    return render(request, 'admin/newGraph.html', {'store': bills_store, 'product': bills_products})

def LoginView(request):
    if request.method == 'POST':
        try:
            obj = StoreDetails.objects.get(email=request.POST['email'])
            if obj.password == request.POST['password']:
                request.session['username'] = obj.email

                return HttpResponseRedirect('/dashboard/')

            else:
                # return HttpResponse("Incorrect Password")
                messages.warning(request, message="Invalid  Password!")
                return render(request, 'store/login.html')

        except:
            # return HttpResponse("Invalid username")
            messages.warning(request, message="Invalid Email!")
            return render(request, 'store/login.html')

    return render(request, 'store/login.html')


class ProductViewData():
    def __init__(self, name, date, status):
        self.name = name
        self.date = date
        self.status = status

def getStatusInStr(isStatus, isDeny):
    if isStatus == True:
        return "Accepted"
    else:
        if isDeny == True:
            return "Denied"
        return "Pending"

def Dashboard(request):
    if request.session.has_key('username'):
        username = request.session['username']
        store = StoreDetails.objects.get(email=username)

        pdBill = SK_Bills.objects.filter(store_person=store)
        Bcount = 0
        bset = set()
        for i in pdBill:
            bset.add(str(i.Bill_No))

        print(bset)
        bset = list(bset)
        # bset.sort()
        print(bset)

        model = ProductDetails.objects.filter(store_person=store).count()
        today_stock = ProductDetails.objects.filter(
            store_person=store, date=date.today())
        qty = 0
        today_date = date.today
        print(today_date)

        acceptedData = ProductDetails.objects.filter(store_person=store)
        acceptedData = map(lambda product: ProductViewData(getattr(product, 'productname'), getattr(product, 'date'), getStatusInStr(getattr(product, 'status'), getattr(product, 'isDeny'))), acceptedData)

        for i in today_stock:
            qty += i.productquantity
        return render(request, 'store/dashboard.html', {'acceptedData' : acceptedData, 'bset': bset, 'Bcount': len(bset), 'data': model, 'total': qty, 'date': today_date, 'username': username})
    else:
        return redirect('LoginView')


def SK_View_Bills(request, ids):
    pdBill = SK_Bills.objects.filter(Bill_No=ids)
    tot = 0.0
    date = ""
    sperson = ''
    for i in pdBill:
        date = i.date_data
        sperson = i.store_person
        tot += float(i.pd_tot)
    return render(request, 'store/SK_Order_Bill.html', {'billNo': ids, 'sperson': sperson, 'ddate': date, 'tot': tot, 'BillDes': pdBill})


# def SK_render_to_pdf(template_src, context_dict={}):
#     template = get_template(template_src)
#     html = template.render(context_dict)
#     result = BytesIO()
#     pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
#     if not pdf.err:
#         return HttpResponse(result.getvalue(), content_type='application/pdf')
#     return None


def SK_Create_Pdf(request, dt):
    if request.session.has_key('username'):
        username = request.session['username']
        store = StoreDetails.objects.get(email=username)

        pdBill = SK_Bills.objects.filter(Bill_No=dt)
        tot = 0.0
        date = ""
        sperson = ''
        for i in pdBill:
            date = i.date_data
            sperson = i.store_person
            tot += float(i.pd_tot)

        Order_Data = {}

        obj_data = SK_Bills.objects.filter(Bill_No=dt)

        prod_price = 0
        prod_qty = 0
        qty = 0
        new = {}
        grand_tot = 0
        for i in obj_data:
            recd_data = {}

            print("=============")
            # recd_data['prod_nm'] = data
            recd_data["prod_price"] = i.pd_tot
            grand_tot += i.pd_tot
            recd_data["prod_qty"] = i.pd_qty
            recd_data['real_price'] = i.pd_price
            new[str(i.pd_nm)] = recd_data
            print(new)

        Order_Data[store] = new
        print(Order_Data)
        print("======================")

        data = {'data': Order_Data, 'grand_tot': grand_tot}

        pdf = render_to_pdf('admin/Create_Pdf.html', data)
        return HttpResponse(pdf, content_type='application/pdf')
    else:
        return redirect('LoginView')


def GraphCall(request):
    model = StoreDetails.objects.all()
    sk_nm = []
    for i in model:
        sk_nm.append(str(i.StoreName))
    tots = []
    for i in sk_nm:
        std = StoreDetails.objects.get(StoreName=i)
        sk = SK_Bills.objects.filter(store_person=std)
        vals = 0
        for j in sk:
            vals += float(j.pd_qty)
        tots.append(vals)
    print(sk_nm)
    print(tots)
    data = {}

    for i in range(len(sk_nm)):
        data[tots[i]] = sk_nm[i]
    print(data)
    # data = dumps(data)
    return render(request, 'admin/grap.html', {'data': data, 'sks': sk_nm, 'tots': tots})


def Confirm_SK_Orders(request):
    if request.session.has_key('username'):
        username = request.session['username']
        SD = StoreDetails.objects.get(email=username)
        print("======================")
        print(SD)
        Order_Data = {}

        obj_data = ProductDetails.objects.filter(status=True, store_person=SD)

        prod_price = 0
        prod_qty = 0
        qty = 0
        new = {}
        grand_tot = 0
        for i in obj_data:
            recd_data = {}
            print(i)
            qty += 1
            print(qty)

            prod_qty += int(i.productquantity)
            print(prod_qty)

            data = StockDetails.objects.get(productName=i.productname)
            print(data, i.productquantity)
            print(data.price)
            rec = float(data.price * i.productquantity)
            print(rec)
            prod_price += rec
            print(prod_price)

            print("=============")
            # recd_data['prod_nm'] = data
            recd_data["prod_price"] = prod_price
            grand_tot += prod_price
            recd_data["prod_qty"] = prod_qty
            recd_data['real_price'] = data.price
            new[str(data.productName)] = recd_data
            print(new)
        Order_Data[SD] = new
        print(Order_Data)
        print("======================")

        return render(request, 'store/SK_Order_Bill.html', {'data': Order_Data, 'grand_tot': grand_tot})
    else:
        return redirect('LoginView')


def AddProduct(request):
    if request.session.has_key('username'):
        username = request.session['username']
        store = StoreDetails.objects.get(email=username)
        prods = StockDetails.objects.all()
        if request.POST:
            pro_data = request.POST['productname']
            pro_qty = request.POST['productquantity']
            prod_date = request.POST['data']

            obj = ProductDetails()
            obj.store_person = store

            pro_nm = StockDetails.objects.get(id=int(pro_data))

            obj.productname = pro_nm.productName
            obj.productquantity = pro_qty
            obj.date = prod_date
            obj.save()

        # form = ProductDetailsForm(request.POST)
        # if form.is_valid():
        #     form.save()
            return redirect('/productlist/')
        return render(request, 'store/addproduct.html', {'username': username, 'prods': prods})
    else:
        return redirect('LoginView')


def DeleteProduct(request, id):
    if request.session.has_key('username'):
        username = request.session['username']
        obj = ProductDetails.objects.get(id=id)
        obj.delete()
        return redirect('/productlist/', {'username': username})
    else:
        return redirect('LoginView')


def EditProduct(request, id):
    if request.session.has_key('username'):
        username = request.session['username']
        model = ProductDetails.objects.get(id=id)
        # form = ProductDetailsForm(request.POST, instance=model)
        if request.POST:
            model.productname=request.POST['productname']
            model.productquantity=request.POST['productquantity']
            model.save()
            return redirect('/productlist/')
        return render(request, 'store/editproduct.html', {'data': model, 'username': username})
    else:
        return redirect('LoginView')


def ProductListView(request):
    if request.session.has_key('username'):
        username = request.session['username']
        store = StoreDetails.objects.get(email=username)
        model = ProductDetails.objects.filter(store_person=store)
        return render(request, 'store/productlist.html', {'data': model, 'username': username})
    else:
        return redirect('LoginView')


def AddSaleView(request):
    if request.session.has_key('username'):
        username = request.session['username']
        model = ProductDetails.objects.all()

        form = SalesDetailsForm(request.POST)
        if form.is_valid():
            form.save()
            obj = request.POST['qty']  # Quantity
            filter_model = ProductDetails.objects.filter(
                productname=request.POST['productname'])
            price = ''
            for data in filter_model:
                price = data.productprice  # Price
            sales_model = SalesDetails.objects.all()
            idlist = []
            for value in sales_model:
                idlist.append(value.id)
            print('-----------')
            idlist.reverse()
            print(idlist)
            sales_id = idlist[0]
            filter_sales = SalesDetails.objects.get(id=sales_id)
            filter_sales.totalprice = int(price) * int(obj)
            filter_sales.save()
            return redirect('/saleslist/')
        return render(request, 'store/sales.html', {'data': model, 'username': username})
    else:
        return redirect('LoginView')


def profileview(request):
    if request.session.has_key('username'):
        username = request.session['username']
        obj = StoreDetails.objects.get(email=username)
        # a = profileform(instance=obj)

        if request.POST:
            obj.StoreName = request.POST['StoreName']
            obj.email = request.POST['email']
            request.session['username'] = request.POST['email']
            obj.PersonName = request.POST['PersonName']
            obj.Contact = request.POST['Contact']
            obj.add1 = request.POST['add1']
            obj.save()
            return redirect('Dashboard')

        b = {
            'shop': obj
        }

    return render(request, 'store/profile.html', b)


def SalesListView(request):
    if request.session.has_key('username'):
        username = request.session['username']
        model = SalesDetails.objects.all()
        return render(request, 'store/saleslist.html', {'data': model, 'username': username})
    else:
        return redirect('LoginView')


def SalesDelete(request, id):
    if request.session.has_key('username'):

        obj = SalesDetails.objects.get(id=id)
        obj.delete()
        return redirect('/saleslist/')
    else:
        return redirect('LoginView')


def LogoutStore(request):
    if request.session.has_key('username'):
        del request.session['username']
        return redirect('LoginView')
    else:
        return redirect('LoginView')

# ===============ADMIN=======================>


def Adminregister(request):
    # form = adminregform(request.POST)
    if request.POST:
        obj1 = adminregi()
        obj1.admin_nm = request.POST.get('username')
        obj1.email = request.POST.get('email')
        obj1.password1 = request.POST.get('password1')
        obj1.password2 = request.POST.get('password2')
        if obj1.password1 == obj1.password2:
            obj1.save()
            return redirect('Adminlogin')
        else:
            messages.warning(request, message="Password not same !")
            return redirect('Adminregister')
    return render(request, 'admin/adminregister.html')


def Adminlogin(request):
    if request.method == "POST":
        try:
            obj = adminregi.objects.get(email=request.POST['email'])
            if obj.password1 == request.POST['password1']:
                request.session['auser'] = obj.email
                return HttpResponseRedirect('/admindashboard/')
            else:
                # error = "The Password Is Incorrect"
                messages.warning(request, message="Invalid  Password!")

                return render(request, 'admin/adminlogin.html')
        except:
            # error = "The Username Can't be found"
            messages.warning(request, message="Invalid Email!")

            return render(request, 'admin/adminlogin.html')
    return render(request, 'admin/adminlogin.html')


def admin_SK_Create_Pdf(request, dt):
    if request.session.has_key('auser'):

        pdBill = SK_Bills.objects.filter(Bill_No=dt)
        objs = set()
        for i in pdBill:
            objs.add(i.store_person.email)

        username = list(objs)
        username = username[0]
        store = StoreDetails.objects.get(email=username)

        tot = 0.0
        date = ""
        sperson = ''
        for i in pdBill:
            date = i.date_data
            sperson = i.store_person
            tot += float(i.pd_tot)

        Order_Data = {}

        obj_data = SK_Bills.objects.filter(Bill_No=dt)

        prod_price = 0
        prod_qty = 0
        qty = 0
        new = {}
        grand_tot = 0
        for i in obj_data:
            recd_data = {}

            print("=============")
            # recd_data['prod_nm'] = data
            recd_data["prod_price"] = i.pd_tot
            grand_tot += i.pd_tot
            recd_data["prod_qty"] = i.pd_qty
            recd_data['real_price'] = i.pd_price
            new[str(i.pd_nm)] = recd_data
            print(new)

        Order_Data[store] = new
        print(Order_Data)
        print("======================")

        data = {'data': Order_Data, 'grand_tot': grand_tot}

        pdf = render_to_pdf('admin/Create_Pdf.html', data)
        return HttpResponse(pdf, content_type='application/pdf')
    else:
        return redirect('Adminlogin')


# def predict_graph():
    stores = StoreDetails.objects.all()
    sales_data = [ProductDetails.objects.filter(
        store_person=s).order_by("date") for s in stores]

    # sales_data = ProductDetails.objects.all().order_by("date")
    # sales_data_date, sales_data_quantity = [], []

    sale_dates, sale_quentity = [], []
    for i in range(len(sales_data)):
        date, quantity = [], []
        for x in sales_data[i]:
            date.append(x.date.year)
            quantity.append(x.productquantity)
        else:
            sale_dates.append(date)
            sale_quentity.append(quantity)

    sale_date_new, sale_quentity_new = [], []
    for i in range(len(sale_dates)):
        sale_date_new.append(list(set(sale_dates[i])))
        s1, s2 = pd.Series(sale_dates[i]), pd.Series(sale_quentity[i])
        df = pd.DataFrame({"a": s1, "b": s2})
        df = df.groupby(df['a'])['b'].agg(['sum'])
        sale_quentity_new.append((list(df["sum"])))

    linear_model = LinearRegression()
    legend = []
    for x in stores:
        legend.append(x.StoreName)
        legend.append(x.StoreName + " "+"Prediction")

    for i in range(len(sale_date_new)):
        linear_model.fit(np.array(
            sale_date_new[i]).reshape(-1, 1), np.array(sale_quentity_new[i]).reshape(-1, 1))
        predicted = linear_model.predict(
            np.array(sale_date_new[i][-1] + 1).reshape(-1, 1))

        plt.plot(sale_date_new[i], sale_quentity_new[i])
        plt.xlabel('Years')
        plt.ylabel('Quantity')

        plt.plot([sale_date_new[i][-1], sale_date_new[i][-1] + 1],
                 [sale_quentity_new[i][-1], predicted])
        plt.legend(legend, loc="best")
    else:
        plt.plot()
        paths = str(settings.BASE_DIR+"/app1/static/GRAPHS" +
                    "/prediction_graph.png")
    # nw_path = "GRAPHS/prediction_graph.png"
        plt.savefig(paths)


def Order_Bills_data(request):
    data = SK_Bills.objects.all()
    val = set()
    for i in data:
        val.add(str(i.store_person.StoreName))
    # print(val)
    val = list(val)
    # print(val)
    val.sort()
    # print(val)

    data_set = {}
    temp_data = {}
    for i in val:
        sp = StoreDetails.objects.get(StoreName=i)
        sb = SK_Bills.objects.filter(store_person=sp)
        data_list = set()
        for j in sb:
            data_list.add(str(j.Bill_No))
        data_list = list(data_list)
        data_list.sort()
        temp_data[i] = data_list

    data_set['data'] = temp_data

    return render(request, 'admin/Orders_Bill_Data.html', {'data': data_set})


def AdminDashboard(request):
    if request.session.has_key('auser'):
        auser = request.session['auser']

        model = StoreDetails.objects.all()
        # predict_graph()

        # print(today.month)
        data = {}
        try:
            q = request.GET.get('search')
        except:
            q = None
        if q:
            product = StoreDetails.objects.filter(
                Q(StoreName__icontains=q) | Q(PersonName__icontains=q))
            # dealer = Dealer.objects.filter(Q(name__icontains=q) | Q(address__icontains=q))
            data = {
                'data': model,
                'StoreDetails': product,
                'auser': auser
                # 'des': dealer
            }
        else:
            data = {'data': model}
        return render(request, 'admin/dashboard.html', data)
    else:
        return redirect('Adminlogin')

    # return render(request,'admin/dashboard.html',datao


def forgot_pass(request):
    if request.POST:
        email1 = request.POST['email']
        try:
            valid = adminregi.objects.get(email=email1)
            # if int(valid.phone) == int(number1):
            #     print(email1)

            request.session['email'] = email1

            numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
            num = ""
            for i in range(4):
                num += str(random.choice(numbers))

            num = int(num)
            print(num)

            # ============== Email ==============

            sender_email = "mailtesting681@gmail.com"
            sender_pass = "mailtest123@"
            receiver_email = email1

            server = smtplib.SMTP('smtp.gmail.com', 587)

            your_message = "This Is Your OTP Number = "+str(num)

            print(your_message)

            msg = email.message.Message()
            msg['Subject'] = "Your OTP From The Site"
            msg['From'] = sender_email
            msg['To'] = receiver_email
            password = sender_pass
            msg.add_header('Content-Type', 'text/html')
            msg.set_payload(your_message)

            server.starttls()
            server.login(msg['From'], password)
            server.sendmail(msg['From'], msg['To'], msg.as_string())

            # ============== End Email ===========

            request.session['otp'] = num

            return render(request, 'admin/OTP.html', {'otp': num})

            # else:
            #     return HttpResponse("<h2><a href=''>Mobile Number Is Not Registered</a></h2>")
        except:
            return HttpResponse("<h2><a href=''>Email Is Not Registered</a></h2>")

    return render(request, 'admin/Forgot_Pass.html')


def otpcheck(request):
    if request.session.has_key('otp'):
        if request.POST:
            otp = request.POST['otp']
            if int(request.session['otp']) == int(otp):
                del request.session['otp']
                return redirect('newpassword')
            else:
                return HttpResponse("<h2><a href=""> You Have Entered Wrong OTP </a></h2>")
        else:
            return redirect('forgotpass')
    return redirect('Adminlogin')


def newpassword(request):
    if request.session.has_key('email'):
        if request.POST:
            pass_1 = request.POST['pass1']
            pass_2 = request.POST['pass2']

            if pass_1 == pass_2:
                valid = adminregi.objects.get(email=request.session['email'])
                valid.password1 = pass_2
                valid.password2 = pass_2
                valid.save()
                del request.session['email']
                return redirect('Adminlogin')
            else:
                return HttpResponse("<h2><a href=''>Passwords Are Not Same ...</a></h2>")
        return render(request, 'admin/New_Pass.html')
    return redirect('Adminlogin')


def deletestore(request, id):
    if request.session.has_key('auser'):
        model = StoreDetails.objects.get(id=id)
        model.delete()
        return HttpResponseRedirect('/admindashboard/')
    else:
        return redirect('Adminlogin')


def viewstore(request, id):

    if request.session.has_key('auser'):
        model = StoreDetails.objects.get(id=id)
        prods = ProductDetails.objects.filter(store_person=model, status=False, isDeny=False)
        return render(request, 'admin/storedetails.html', {'data': model, 'prod': prods})
    else:
        return redirect('Adminlogin')


def editstore(request, id):
    if request.session.has_key('auser'):
        email = request.session['auser']
        obj1 = StoreDetails.objects.get(id=id)
        # a = profileform(instance=obj)
        # obj1 = StoreDetails.objects.all()
        if request.POST:
            obj1.StoreName = request.POST['StoreName']
            obj1.email = request.POST['email']
            request.session['auser'] = request.POST['email']
            obj1.PersonName = request.POST['PersonName']
            obj1.Contact = request.POST['Contact']
            obj1.add1 = request.POST['add1']
            obj1.save()
            return redirect('AdminDashboard')

        return render(request, 'admin/editstore.html', {'shop': obj1})
    else:
        return redirect('Adminlogin')

def addstore(request):
    if request.session.has_key('auser'):
        form = StoreDetailsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/admindashboard/')
        return render(request, 'admin/addstore.html')
    else:
        return redirect('Adminlogin')

def upload_dataset(request):    
    msg = ''
    if request.POST:
        f = request.FILES.get('file').read()
        print(f)
        f=str(f).split('\\n')
        for i in f[1:len(f)-1]:
            i=i.split(',')
            q = StockDetails.objects.filter(productName=i[0])
            try:
                if not q :
                    e = StockDetails()
                    e.productName = i[0]
                    e.quantity = i[1]
                    e.price = i[2].replace("\\r","")
                    e.save()
                    msg = "Product Saved Properly"
                    print(msg)
                else:
                    msg = "Product Already Exists"
                    print(msg)
            except:
                return HttpResponse('enter proper data')
    return render(request, 'admin/upload_dataset.html', {'msg': msg})

def addstock(request):
    #if request.session.has_key('auser'):
        # a = request.session['auser']
        # print(a)
        # admin_data = adminregi.objects.get(email=request.session['auser'])
        # print(admin_data)
        # admin_data = adminregi.objects.get(email = request.session['auser'])
    if request.POST:
        StoreName = request.POST['StoreName']
        quantity = request.POST['quantity']
        Pr = request.POST['Price']

        obj = StockDetails()
        #obj.email = admin_data
        #print(obj.email)
        obj.productName = StoreName
        obj.quantity = quantity
        obj.price = Pr
        obj.save()

        return redirect('/admindashboard/')
    return render(request, 'admin/addstock.html')
    # else:
    #     return redirect('Adminlogin')


def viewstock(request):
    if request.session.has_key('auser'):
        model = StockDetails.objects.all()
        return render(request, 'admin/stockdetails.html', {'data': model})
    else:
        return redirect('Adminlogin')


def editstock(request, id):
    if request.session.has_key('auser'):
        email = request.session['auser']
        obj1 = StockDetails.objects.get(id=id)
        # a = profileform(instance=obj)
        # obj1 = StoreDetails.objects.all()
        if request.POST:
            obj1.productName = request.POST['productName']
            obj1.quantity = request.POST['quantity']
            obj1.price = request.POST['price']
            obj1.save()
            return redirect('viewstock')

        return render(request, 'admin/editstock.html', {'prod': obj1})
    else:
        return redirect('Adminlogin')


def accepteddata(request, sk, id):
    print("=============================================")
    print(f"shope = {sk} -----  prod{id}")
    p_qty = 0
    p_nm = ""
    obj = ProductDetails.objects.get(id=id)
    obj.status = True
    p_nm = obj.productname
    p_qty = obj.productquantity
    obj.save()

    print(obj)
    product_obj = StockDetails.objects.get(productName=p_nm)
    print(product_obj)
    product_obj.quantity -= p_qty
    product_obj.save()
    print("=============================================")
    return redirect('viewstore', sk)


def denieddata(request, sk, id):
    print("=============================================")
    print(f"shope = {sk} -----  prod{id}")
    p_qty = 0
    p_nm = ""
    obj = ProductDetails.objects.get(id=id)
    obj.isDeny = True
    obj.status = False
    p_nm = obj.productname
    p_qty = obj.productquantity
    obj.save()

    print(obj)
    product_obj = StockDetails.objects.get(productName=p_nm)
    print(product_obj)
    product_obj.quantity -= p_qty
    product_obj.save()
    print("=============================================")
    return redirect('viewstore', sk)

def Confirm_Orders(request):
    obj = ProductDetails.objects.filter(status=True)

    data_set = set()
    for i in obj:
        nm = str(i.store_person)
        print(nm)
        data_set.add(nm)
    # print(data_set)
    data_set = list(data_set)
    # print(data_set)
    data_set.sort()
    obj1 = data_set
    print(obj1)
    Order_Data = {}

    for i in obj1:
        print("=============")
        print(i)
        recd_data = {}

        data = StoreDetails.objects.get(StoreName=str(i))
        # recd_data['stnm'] = data.StoreName

        obj_data = ProductDetails.objects.filter(
            status=True, store_person=data)

        f_total = 0
        prod_price = 0
        prod_qty = 0
        qty = 0
        show = False
        for i in obj_data:
            print(i)
            qty += 1
            print(qty)

            prod_qty += int(i.productquantity)
            print(prod_qty)
            print("\n\n===================================---")
            print(i.productname)
            print("===================================---\n\n")
            data = StockDetails.objects.get(productName=str(i.productname))
            print(data, i.productquantity)
            print(data.price)
            rec = float(data.price * i.productquantity)
            print(rec)
            prod_price += rec
            f_total += prod_price
            print(prod_price)
            for i in obj_data:
                if not i.Bills_id == "":
                    show = True

        print("=============")

        recd_data["prod_price"] = f_total
        recd_data["prod_qty"] = prod_qty
        recd_data["qty"] = qty
        recd_data['show'] = show
        Order_Data[str(i.store_person)] = recd_data
        print(Order_Data)
    return render(request, 'admin/Confirm_orders.html', {'orders': Order_Data})


def billdata(request, dt):
    # print(dt)
    sp = str(dt)
    print(sp)
    SD = StoreDetails.objects.get(StoreName=str(sp))
    print("======================")
    print(SD)
    Order_Data = {}

    obj_data = ProductDetails.objects.filter(status=True, store_person=SD)
    show = False
    for i in obj_data:
        if not i.Bills_id == "":
            show = True

    prod_price = 0
    prod_qty = 0
    qty = 0
    new = {}
    grand_tot = 0
    for i in obj_data:
        recd_data = {}
        print(i)
        qty += 1
        print(qty)

        prod_qty += int(i.productquantity)
        print(prod_qty)

        data = StockDetails.objects.get(productName=i.productname)
        print(data, i.productquantity)
        print(data.price)
        rec = float(data.price * i.productquantity)
        print(rec)
        prod_price += rec
        print(prod_price)

        print("=============")
        # recd_data['prod_nm'] = data
        recd_data["prod_price"] = prod_price
        grand_tot += prod_price
        recd_data["prod_qty"] = prod_qty
        recd_data['real_price'] = data.price
        new[str(data.productName)] = recd_data
        print(new)
    Order_Data[SD] = new
    print(Order_Data)
    print("======================")

    return render(request, 'admin/billdata.html', {'data': Order_Data, 'grand_tot': grand_tot, 'show': show})


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


def Create_Pdf(request, dt):
    if request.session.has_key('auser'):
        tz = pytz.timezone('Asia/Kolkata')
        time_now = datetime.datetime.now(timezone.utc).astimezone(tz)
        millis = int(time.mktime(time_now.timetuple()))
        order_id = 'SKBill_Id'+str(millis)
        print(order_id)

        # request.session['Order_id'] = order_id

        Bill_timestamp_no = order_id
        print(Bill_timestamp_no)

        sp = str(dt)
        print(sp)
        SD = StoreDetails.objects.get(StoreName=str(sp))
        print("======================")
        print(SD)
        Order_Data = {}

        obj_data = ProductDetails.objects.filter(status=True, store_person=SD)

        prod_price = 0
        prod_qty = 0
        qty = 0
        new = {}
        grand_tot = 0
        for i in obj_data:
            recd_data = {}
            print(i)
            qty += 1
            print(qty)

            prod_qty += int(i.productquantity)
            print(prod_qty)

            data = StockDetails.objects.get(productName=i.productname)
            print(data, i.productquantity)
            print(data.price)
            rec = float(data.price * i.productquantity)
            print(rec)
            prod_price += rec
            print(prod_price)

            print("=============")
            # recd_data['prod_nm'] = data
            recd_data["prod_price"] = prod_price
            grand_tot += prod_price
            recd_data["prod_qty"] = prod_qty
            recd_data['real_price'] = data.price
            new[str(data.productName)] = recd_data
            print(new)

            skObj = SK_Bills()
            skObj.store_person = SD
            skObj.Bill_No = str(Bill_timestamp_no)
            skObj.pd_nm = i.productname
            skObj.pd_price = data.price
            skObj.pd_qty = prod_qty
            skObj.pd_tot = prod_price
            skObj.date_data = i.date
            skObj.save()
            i.delete()
        Order_Data[SD] = new
        print(Order_Data)
        print("======================")

        data = {'data': Order_Data, 'grand_tot': grand_tot}

        pdf = render_to_pdf('admin/Create_Pdf.html', data)
        return HttpResponse(pdf, content_type='application/pdf')
    else:
        return redirect('Adminlogin')

# def Create_Pdf(request,dt):
    # return render(request,'admin/pdf.html')


def SalefilterView(request):
    if request.session.has_key('auser'):
        tdate = date.today()
        filterqty = 0
        totalearning = 0
        model = ProductDetails.objects.all()

        if request.method == "POST":
            saledata = SaleFilter.objects.get(id=1)
            saledata.ProductName = request.POST['ProductName']
            saledata.save()
            filterdata = SalesDetails.objects.filter(
                productname=request.POST['ProductName']).filter(date=date.today())

            for value in filterdata:
                filterqty += value.qty
                totalearning += int(value.totalprice)
        else:
            salemodel = SalesDetails.objects.filter(date=date.today())

            for i in salemodel:
                filterqty += i.qty
                totalearning += int(i.totalprice)
        return render(request, 'admin/salefilter.html', {'data': model, 'filter': filterqty, 'total': totalearning, 'date': tdate})
    else:
        return redirect('Adminlogin')


def salespredictionview(request):
    if request.session.has_key('auser'):
        try:
            tdate = date.today()
            model = SalesDetails.objects.all()
            filterqty = 0
            filterearning = 0
            datefilter = SalesDetails.objects.filter(date=tdate)
            datefiltercount = SalesDetails.objects.filter(date=tdate).count()
            for fdata in datefilter:
                filterqty += fdata.qty
                filterearning += int(fdata.totalprice)
            filteravgqty = int(filterqty/datefiltercount)
            filteravgearning = int(filterearning/datefiltercount)
            countdata = SalesDetails.objects.count()

            totalearning = 0
            totalqty = 0

            for i in model:
                totalqty += i.qty
                totalearning += int(i.totalprice)
            avgqty = int(totalqty/countdata)
            avgearning = int(totalearning/countdata)
            return render(request, 'admin/saleprediction.html',
                          {
                              'totalearning': totalearning,
                              'totalqty': totalqty,
                              'avgqty': avgqty,
                              'avgearning': avgearning,
                              'date': tdate,
                              'filterqty': filterqty,
                              'filterearning': filterearning,
                              'filteravgqty': filteravgqty,
                              'filteravgearning': filteravgearning

                          })
        except:
            return render(request, 'admin/nosale.html')
    else:
        return redirect('Adminlogin')


def monthsaleview(request):
    if request.session.has_key('auser'):
        tdate = datetime.today()
        tmonth = tdate.month
        tyear = tdate.year
        model = SalesDetails.objects.filter(date=date.today())
        print(model)
        totaldata = SalesDetails.objects.all()
        product = ProductDetails.objects.all()
        totalqty = 0
        for qty in totaldata:
            totalqty += qty.qty
        tqty = 0
        tearning = 0
        for p in product:
            for i in model:
                tqty += i.qty
                tearning += int(i.totalprice)
            print(p)
            print(tqty)
        avgqty = tqty * 30
        avgearning = tearning * 30
        return render(request, 'admin/monthsale.html', {'p': p, 't': tqty, 'date': tdate, 'avgqty': avgqty, 'avgearning': avgearning, 'totalqty': totalqty, 'totaldata': totaldata})
    else:
        return redirect('Adminlogin')


def totallistview(request):
    totaldata = SalesDetails.objects.all()
    return render(request, 'admin/totallist.html', {'data': totaldata})


def todaylistview(request):
    todaydata = SalesDetails.objects.filter(date=date.today())

    return render(request, 'admin/todaysale_list.html', {'todaydata': todaydata})


def adminlogout(request):
    if request.session.has_key('auser'):
        del request.session['auser']
        return redirect('Adminlogin')
    else:
        return redirect('Adminlogin')
