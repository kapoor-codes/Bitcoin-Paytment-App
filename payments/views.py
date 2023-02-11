from django.shortcuts import render, HttpResponseRedirect, HttpResponse, reverse, redirect, get_object_or_404
from .models import *
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django_email_verification import send_email

import datetime
import json
import requests
import uuid
import os

# Create your views here.

def home(request):
    products = product.objects.all()
    context = {
        "products":products,
    }
    return render(request, 'index.html', context)

def exchanged_rate(amount):
    url = "https://www.blockonomics.co/api/price?currency=USD"
    r = requests.get(url)
    response = r.json()
    return amount/response['price']

@login_required
def track_invoice(request, pk):
    try:
        customer = invoice.objects.filter(pk=pk).get(user=request.user)
        invoice_id = pk
        Invoice = invoice.objects.get(id=invoice_id)
        data = {
                'order_id':Invoice.invoiceOrderId,
                'bits':Invoice.invoiceBtcValue/1e8,
                'value':Invoice.productName.productPrice,
                'addr':Invoice.invoiceAddress,
                'status':Invoice.STATUS_CHOICES[Invoice.invoiceStatus+1][1],
                'invoice_status':Invoice.invoiceStatus,
                'product_name':Invoice.productName,
                'product_desc':Invoice.productName.productDesc,
                'product_disp':Invoice.productName.productDisp.url,
                'invoice_user':Invoice.user,
                'customer':customer,
            }
        if (Invoice.invoiceReceived):
            data['paid'] =  Invoice.invoiceReceived/1e8
            if (int(Invoice.invoiceBtcValue) <= int(Invoice.invoiceReceived)):
                return redirect('final',invoice_id=invoice_id)
        else:
            data['paid'] = 0
        return render(request, 'product.html', context=data)
    except:
        data = {'Transaction':'This is not your Transcation'}
        return render(request, 'product.html', context=data)

def create_payment(request, pk):
    if request.user.is_authenticated:        
        product_id = pk
        prod = product.objects.get(id=product_id)
        url = 'https://www.blockonomics.co/api/new_address'
        headers = {'Authorization': "Bearer " + settings.API_KEY}
        r = requests.post(url, headers=headers)
        if r.status_code == 200:
            address = r.json()['address']
            bits = exchanged_rate(prod.productPrice)
            order_id = uuid.uuid1()
            Invoice = invoice.objects.create(invoiceOrderId=order_id,invoiceAddress=address,invoiceBtcValue=bits*1e8,productName=prod,user=request.user)
            return HttpResponseRedirect(reverse('track', kwargs={'pk':Invoice.id}))
        else:
            print(r.status_code, r.text)
            return HttpResponse("Some Error, Try Again!")
    else:
        return redirect('register')

@login_required
def receive_payment(request):
    if (request.method != 'GET'):
        return
    txid  = request.GET.get('txid')
    value = request.GET.get('value')
    status = request.GET.get('status')
    addr = request.GET.get('addr')
    print(status,txid,addr,value)
    if invoice.objects.filter(invoiceAddress = addr):
        Invoice = invoice.objects.get(invoiceAddress = addr)
    Invoice.invoiceStatus = int(status)
    if (int(status) == 2):
        Invoice.invoiceReceived = value
    Invoice.invoiceTxid = txid
    Invoice.save()
    return redirect(request.META['HTTP_REFERER'])

@login_required
def final_payment(request, *args, **kwargs):
    pk = kwargs["invoice_id"]
    try:
        customer = invoice.objects.filter(pk=pk).get(user=request.user)
        context = {'customer':customer}
    except:
        context = {'error': 'Are you sure if that\'s your invoice?'}
    finally:
        return render(request, 'final.html', context)

def validate(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        username=request.POST['username']
        password=request.POST['pass']
        user = authenticate(request, username=username, password=password)
        context = {
            'errorsignin':'Invalid User/Password',
        }
        if user is None:
            return render(request, 'login.html', context)
        else:
            login(request, user)
            return redirect('home')

def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    else:
        username = request.POST['username']
        email = request.POST['email']
        pass1 = request.POST['password1']
        pass2 = request.POST['password2']
        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'register.html', {'emailErr':'Hmm.. Did you enter a valid email?'})
        try:
            validate_password(pass1)
            validate_password(pass2)
        except ValidationError:
            return render(request, 'register.html', {'passErr':'Please enter an eight digit strong password!'})
        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error1':'Email already exists'})
        else:
            if pass1 == pass2:
                try:
                    user = User.objects.create_user(username=username, password=pass1, email=email)
                    user.save()
                    login(request,user)
                    sendConfirm(user)
                    return render(request, 'confirm_please.html')
                except IntegrityError:
                    return render(request, 'register.html', {'error2':'User already exists'})
            else:
                return render(request, 'register.html', {'error3':'Make sure the passwords are same'})

@login_required
def logoutuser(request):
    logout(request)
    return redirect('home')
