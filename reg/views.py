from django.shortcuts import render,redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login,authenticate,logout
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .forms import SighUpForm
from datetime import datetime
from datetime import date
from .models import usersSub,subPlan
from sslcommerz_python.payment import SSLCSession
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.models import User

# Create your views here.
def sign_up(request):
    form = SighUpForm
    registered = False
    if request.method == 'POST':
        form = SighUpForm(data=request.POST)
        if form.is_valid():
            form.save()
            registered = True
    dict = {'form':form, 'registered':registered}
    return render(request,'reg/signup.html',context=dict)


def login_page(request):
    form = AuthenticationForm
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username,password=password)
            if user is not None:
                login(request,user)
                return HttpResponseRedirect(reverse('home'))

    return render(request,'reg/login.html',context={'form':form})

@login_required
def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))

@login_required
def home(request):
    userSub = usersSub.objects.filter(user=request.user)
    subsPlan = subPlan.objects.all()
    subscribed=False
    can_pur_new_sub=True
    if userSub.exists():
        #This variable is for tracking monthly subscription
        subscribed=True
        D_now=date.today()
        compareM = D_now-date(userSub[0].subscribeY,userSub[0].subscribeM,userSub[0].subscribeD)
        if compareM.days == 30:
            subscribed = False

        #----------------

        #This variable is for tracking if a user can purchase a new subscription or not
        can_pur_new_sub=False
        if userSub[0].subP.title=="Globalnet Gold":
            can_pur_new_sub=True
        else:
            compareY= D_now-date(userSub[0].subscribeY,userSub[0].subscribeM,userSub[0].subscribeD)
            if compareY.days == 365:
                can_pur_new_sub = True
        #---------------------------
        return render(request,'home.html',context={'userSub':userSub[0],'subPlan':subsPlan,'subscribed':subscribed,'can_pur_new_sub':can_pur_new_sub})
    else:
        return render(request,'home.html',context={'userSub':False,'subPlan':subsPlan,'subscribed':subscribed,'can_pur_new_sub':can_pur_new_sub})


@login_required
def subDetail(request,id):
    subsPlan=subPlan.objects.filter(pk=id)
    return render(request,'subsDetails.html',context={"subPlan":subsPlan[0]})



@login_required
def payment(request,id):
    store_id='abc62f3a45eec4c4'
    API_key = 'abc62f3a45eec4c4@ssl'
    mypayment = SSLCSession(sslc_is_sandbox=True,sslc_store_id=store_id,sslc_store_pass=API_key)

    status_url = request.build_absolute_uri(reverse("complete",kwargs={'id':id}))
    mypayment.set_urls(success_url=status_url,fail_url=status_url,cancel_url=status_url,ipn_url=status_url)


    subP=subPlan.objects.filter(pk=id)
    sPlan = subPlan.objects.filter(pk=id)

    #deleting old subscription
    uOldsub=usersSub.objects.filter(user=request.user)
    uOldsub.delete()
    #--------------

    #creating new subscription
    usubPlan = usersSub.objects.create(user=request.user,subP=sPlan[0],subscribeY=datetime.now().year,subscribeM=datetime.now().month,subscribeD=datetime.now().day)
    usubPlan.save()
    #---------------

    mypayment.set_product_integration(total_amount=Decimal(subP[0].price),currency='BDT',product_category='Mixed',product_name=subP[0].title,num_of_item=1,shipping_method='online',product_profile='None')

    mypayment.set_customer_info(name=request.user.username,email=request.user.email,address1="Feni",address2="Dhaka",city="Feni",postcode="3900",country="Bangladesh",phone="Phone")
    

    mypayment.set_shipping_info(shipping_to=request.user.username,address="address",city="city",postcode="postcode",country="Bangladesh")
    response_data = mypayment.init_payment()
    return redirect(response_data['GatewayPageURL'])


#Payment complete
@csrf_exempt
def complete(request,id):
    if request.method == 'POST' or request.method == 'post':
        payment_data = request.POST
        status = payment_data['status']

        if status == 'VALID':
            messages.success(request,f"Your Payment Completed Successfully!! Page will be redirected!!")
            return HttpResponseRedirect(reverse("home"))
        elif status == 'FAILED':
            messages.warning(request,f"Your Payment Failed! Please Try Again!! Page will be redirected!!")
    
    
    return render(request,'complete.html',context={})
